#!/usr/bin/env python3
"""Isolated graduate examples and structural checks; not an OGE approval test."""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    from pypdf import PdfReader
    from pypdf.generic import ContentStream
except ImportError:
    sys.exit("Maintainer checks require pypdf in your chosen Python environment.")
from build import ROOT, build


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def fixture(folder):
    folder.mkdir()
    for name in [
        "main.tex",
        "metadata.tex",
        "preamble.tex",
        "rpi-thesis.cls",
        "references.bib",
    ]:
        shutil.copy2(ROOT / name, folder / name)
    for name in ["chapters", "frontmatter", "appendices", "assets"]:
        shutil.copytree(ROOT / name, folder / name)
    # Students often paste these lines; the class must tolerate them on every
    # engine (its math fonts already provide the symbols).
    with (folder / "preamble.tex").open("a", encoding="utf-8") as preamble:
        preamble.write("\\usepackage{amssymb}\n\\usepackage{amsfonts}\n")


def multiply(m, n):
    """Product of two PDF matrices [a b c d e f]."""
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return [
        a * A + b * C,
        a * B + b * D,
        c * A + d * C,
        c * B + d * D,
        e * A + f * C + E,
        e * B + f * D + F,
    ]


def text_origins(page):
    """Where each piece of text starts on the page, in points from the
    bottom-left corner: the text matrix times the current transformation
    matrix, read from the content stream itself.

    pypdf's visitor_text matrices are not used: they depend on the pypdf
    version. pypdf 6.10, for example, reports the identity text matrix for a
    run that continues a line in a new BT block, which XeTeX writes for every
    run (such as contents dot leaders), placing that run at the wrong height.
    x is None for text that follows other text without a new position; only
    the font's glyph widths would tell where it starts."""
    origins = []

    def run(operations, ctm, resources):
        stack, tm, x_known, leading = [], [1, 0, 0, 1, 0, 0], False, 0.0
        tlm = tm
        for operands, operator in operations:
            if operator == b"q":
                stack.append(ctm)
            elif operator == b"Q" and stack:
                ctm = stack.pop()
            elif operator == b"cm":
                ctm = multiply([float(v) for v in operands], ctm)
            elif operator == b"BT":
                tm = tlm = [1, 0, 0, 1, 0, 0]
                x_known = True
            elif operator == b"TL":
                leading = float(operands[0])
            elif operator in (b"Td", b"TD"):
                if operator == b"TD":
                    leading = -float(operands[1])
                move = [1, 0, 0, 1, float(operands[0]), float(operands[1])]
                tm = tlm = multiply(move, tlm)
                x_known = True
            elif operator == b"Tm":
                tm = tlm = [float(v) for v in operands]
                x_known = True
            if operator in (b"T*", b"'", b'"'):
                tm = tlm = multiply([1, 0, 0, 1, 0, -leading], tlm)
                x_known = True
            if operator in (b"Tj", b"TJ", b"'", b'"'):
                m = multiply(tm, ctm)
                origins.append((m[4] if x_known else None, m[5]))
                x_known = False  # the glyphs moved the start of the next text
            elif operator == b"Do" and resources is not None:
                xobjects = resources.get("/XObject")
                form = xobjects.get_object().get(operands[0]) if xobjects else None
                form = form.get_object() if form is not None else None
                if form is not None and form.get("/Subtype") == "/Form":
                    matrix = [float(v) for v in form.get("/Matrix", [1, 0, 0, 1, 0, 0])]
                    inner = form.get("/Resources")
                    run(
                        ContentStream(form, page.pdf).operations,
                        multiply(matrix, ctm),
                        inner.get_object() if inner is not None else resources,
                    )

    contents = page.get_contents()
    if contents is not None:
        resources = page.get("/Resources")
        run(
            contents.operations,
            [1, 0, 0, 1, 0, 0],
            resources.get_object() if resources is not None else None,
        )
    return origins


def roman(number):
    """Lowercase roman numeral, as LaTeX's \\roman prints it."""
    result = ""
    for value, letters in [
        (1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
        (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"),
    ]:
        while number >= value:
            result += letters
            number -= value
    return result


def check_pdf(folder, degree, copyright=False, minimal=False):
    reader = PdfReader(folder / "build/main.pdf")
    texts = [norm(p.extract_text()) for p in reader.pages]
    require(
        degree in texts[0] and texts[0].endswith("[May 2027]"),
        "Title details/hidden number",
    )
    # RPI's seal is never distributed; without it a placeholder holds its place.
    seal = any((folder / name).is_file() for name in SEAL_FILES)
    require(
        ("RPI seal:" in texts[0]) != seal,
        "Seal placeholder must appear exactly when assets/ has no seal",
    )
    toc = 2 if copyright else 1
    require(
        texts[toc].startswith("CONTENTS")
        and texts[toc].endswith("iii" if copyright else "ii"),
        "Front-matter pagination",
    )
    require("Copyright" not in texts[toc], "Copyright must not be listed in contents")
    require(
        "1. INTRODUCTION" in texts[toc] and "REFERENCES" in texts[toc],
        "Contents entries must match body headings, including the number's period",
    )
    if copyright:
        require(
            "All rights reserved" in texts[1] and texts[1].endswith("ii"),
            "Copyright page ii",
        )
    body = next(i for i, t in enumerate(texts) if t.startswith("1. INTRODUCTION"))
    require(
        texts[body].endswith("1") and "[1]" in texts[body].replace(" ", ""),
        "Body number/citation",
    )
    bibliography = next(
        i for i, t in enumerate(texts) if t.startswith("REFERENCES") and "Lamport" in t
    )
    if minimal:
        require(
            not any(t.startswith("LIST OF ") for t in texts),
            "Disabled lists still appear",
        )
        require(
            not any(t.startswith("A. ADDITIONAL MATERIAL") for t in texts),
            "Removed appendix remains",
        )
    else:
        require(
            texts[toc + 1].startswith("LIST OF TABLES")
            and texts[toc + 2].startswith("LIST OF FIGURES"),
            "List ordering",
        )
        for caption, index in [
            ("Illustrative values for three example groups.", toc + 1),
            ("A sample image demonstrating the position of a figure caption.", toc + 2),
            ("An example caption for a reproduced figure.", toc + 2),
        ]:
            # Text extraction may drop word spaces in tightly set lines.
            caption = caption.replace(" ", "")
            require(
                caption in texts[index].replace(" ", "")
                and any(caption in t.replace(" ", "") for t in texts[body:]),
                "Full caption mismatch between list and body",
            )
        appendix = next(
            i for i, t in enumerate(texts) if t.startswith("A. ADDITIONAL MATERIAL")
        )
        require(bibliography < appendix, "Appendix must follow references")
        require(
            "APPENDICES" in texts[toc] and "A. ADDITIONAL MATERIAL" in texts[toc],
            "Appendix entries missing from contents",
        )
    # A level-1 heading (front-matter section, chapter, references, appendix)
    # starts its page; the page text then begins with that heading.
    level_one = re.compile(r"(?:[0-9]+|[A-Z])\. [A-Z]|[A-Z]{4,}")
    for i, page in enumerate(reader.pages):
        require(
            abs(float(page.mediabox.width) - 612) < 0.1
            and abs(float(page.mediabox.height) - 792) < 0.1,
            "Paper must be US letter",
        )
        if i == 0:
            continue
        # Text outside the 1 in margins (with a little tolerance) is the page
        # number; everything else sits inside the text block.
        origins = text_origins(page)
        margin = [(x, y) for x, y in origins if y < 70 or y > 722]
        lines = [y for x, y in origins if 70 <= y <= 722]
        label = roman(i + 1) if i < body else str(i - body + 1)

        def number_at(height, columns):
            """Only the page number is in the margins, at this height; its
            first piece starts in these columns."""
            placed = [x for x, y in margin if x is not None]
            return (
                bool(placed)
                and all(abs(y - height) < 1.5 for x, y in margin)
                and columns(placed[0])
            )

        heading = level_one.match(texts[i])
        if i < body or heading:
            # Bottom center, 0.75 in from the bottom edge; heading at the top
            # margin, the same height on every such page.
            require(
                number_at(54, lambda x: 250 < x < 340)
                and texts[i].endswith(" " + label),
                f"Bottom-center page number {label} on PDF page {i+1}",
            )
            if heading:
                require(
                    lines and abs(792 - max(lines) - 84) < 1.5,
                    f"Level-1 heading not at the top margin on PDF page {i+1}",
                )
        else:
            # Other body pages: top right, 0.75 in from the top edge.
            require(
                number_at(738, lambda x: x > 500) and texts[i].startswith(label + " "),
                f"Top-right page number {label} on PDF page {i+1}",
            )
    # Contents links and top-level PDF bookmarks (level-1 entries) open at
    # their heading: on the heading's page, at or above its baseline.
    for item in reader.outline:
        if isinstance(item, list):
            continue  # entries nested under a level-1 entry
        i = reader.get_destination_page_number(item)
        lines = [y for x, y in text_origins(reader.pages[i]) if 70 <= y <= 722]
        require(
            level_one.match(texts[i])
            and item.top is not None
            and float(item.top) >= max(lines) - 0.5,
            f"Link target for {item.title} is not at its heading (PDF page {i+1})",
        )
    log = (folder / "build/main.log").read_text(encoding="utf-8", errors="replace")
    require(
        not re.search(
            r"Overfull \\[hv]box|There were undefined references|Citation .* undefined|Empty bibliography|Please \(re\)run Biber",
            log,
        ),
        "Overflow or unresolved references in final log",
    )
    return len(reader.pages), texts


# Maintainers keep RPI's original template in _local/legacy/ (ignored by Git;
# never committed). Its hashes are compared only when that copy exists.
LEGACY = ROOT / "_local/legacy"
SEAL_FILES = ("assets/rpi-seal.jpg", "assets/rpi-seal.png")


def check_legacy_copy():
    if not LEGACY.is_dir():
        print(
            "SKIP: legacy hash check (no maintainer-local copy in _local/legacy/)",
            flush=True,
        )
        return
    record = json.loads(
        (ROOT / "docs/project/upstream-files.json").read_text(encoding="utf-8")
    )
    for item in record["files"]:
        path = ROOT / item["path"]
        require(path.is_file(), "Missing from the local legacy copy: " + item["path"])
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"],
            "Local legacy copy differs from its recorded hash: " + item["path"],
        )
    print("PASS: _local/legacy/ matches its recorded hashes", flush=True)


def run_pdf_case(tmp, case):
    name, engine, choice, degree, copyright, minimal = case
    folder = tmp / name
    fixture(folder)
    text = (
        (folder / "metadata.tex")
        .read_text(encoding="utf-8")
        .replace("degree = doctoral", "degree = " + choice)
    )
    if copyright:
        text = text.replace("copyright-page = false", "copyright-page = true")
        text += "\n\\committeemember[Co-Chair]{An additional co-chair}\n"
        for n in range(4, 8):
            text += f"\\committeemember{{Committee member {n}}}\n"
    if name.startswith("unicode"):
        text = text.replace("Your full name", "Zoë García")
    if copyright:
        chapter = folder / "chapters/02-research.tex"
        chapter.write_text(
            chapter.read_text(encoding="utf-8").replace(
                "\\label{chap:research}\n",
                "\\label{chap:research}\n"
                "\\chapterattribution{Attribution check text.}\n",
                1,
            ),
            encoding="utf-8",
        )
    if minimal:
        text = text.replace(
            "list-of-tables = true", "list-of-tables = false"
        ).replace("list-of-figures = true", "list-of-figures = false")
        (folder / "chapters/02-research.tex").write_text(
            "\\chapter{RESEARCH AND FINDINGS}\n\\label{chap:research}\nText only.\n",
            encoding="utf-8",
        )
        main = (
            (folder / "main.tex")
            .read_text(encoding="utf-8")
            .replace("\\appendix", "% no appendix")
            .replace(
                "\\include{appendices/additional-material}",
                "% no appendix input",
            )
            .replace("\\input{frontmatter/acknowledgments}", "% no acknowledgments")
        )
        (folder / "main.tex").write_text(main, encoding="utf-8")
    (folder / "metadata.tex").write_text(text, encoding="utf-8")
    require(build(folder, engine=engine) == 0, "Build failed: " + name)
    pages, texts = check_pdf(folder, degree, copyright, minimal)
    if copyright:
        first = next(t for t in texts if t.startswith("2. RESEARCH AND FINDINGS"))
        require(
            "Attribution check text." in first and "1Attribution" not in first,
            "Chapter attribution must sit unmarked on the chapter's first page",
        )
    return f"PASS: {name}, {engine}, {pages} pages"


def run_rejection(tmp, case):
    name, before, after, error = case
    folder = tmp / name
    fixture(folder)
    (folder / "metadata.tex").write_text(
        (folder / "metadata.tex").read_text(encoding="utf-8").replace(before, after),
        encoding="utf-8",
    )
    (folder / "build").mkdir()
    result = subprocess.run(
        [
            "pdflatex",
            "-no-shell-escape",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-output-directory=build",
            "main.tex",
        ],
        cwd=folder,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    require(
        result.returncode != 0 and error in norm(result.stdout),
        "Expected rejection: " + name,
    )
    return "PASS: correctly rejects " + name


def main():
    check_legacy_copy()
    seal = any((ROOT / name).is_file() for name in SEAL_FILES)
    print(
        "Seal: "
        + ("present (title page shows it)" if seal else "absent (title page shows the placeholder)"),
        flush=True,
    )
    cases = [
        ("masters", "pdflatex", "masters", "MASTER OF SCIENCE", False, False),
        (
            "doctoral-copyright",
            "pdflatex",
            "doctoral",
            "DOCTOR OF PHILOSOPHY",
            True,
            False,
        ),
        ("minimal", "pdflatex", "engineering-doctorate", "DOCTOR OF ENGINEERING", False, True),
        ("unicode-lua", "lualatex", "doctoral", "DOCTOR OF PHILOSOPHY", False, False),
        ("unicode-xe", "xelatex", "masters", "MASTER OF SCIENCE", False, False),
    ]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        action="append",
        choices=[case[0] for case in cases],
        help="Run a selected PDF case; can be repeated",
    )
    args = parser.parse_args()
    if args.case:
        cases = [case for case in cases if case[0] in args.case]
    rejections = [
        ("invalid-year", "{2027}", "{27}", "Graduation year must have four digits"),
        ("missing-chair", "[Chair]", "", "Committee chair is missing"),
        ("blank-member", "[Chair]{Your committee chair}", "[Chair]{}", "Blank committee member name"),
        ("invalid-degree", "degree = doctoral", "degree = unknown", "Unknown degree choice"),
        (
            "invalid-month",
            "graduation-month = May",
            "graduation-month = January",
            "Unknown graduation month",
        ),
    ]
    with tempfile.TemporaryDirectory(prefix="rpi-thesis-check-") as tmp:
        tmp = Path(tmp)
        jobs = [(run_pdf_case, tmp, case) for case in cases]
        jobs += [(run_rejection, tmp, case) for case in rejections]
        workers = max(1, min(6, os.cpu_count() or 1))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(fn, *rest) for fn, *rest in jobs]
            failed = None
            for future in futures:  # fixed order, whatever finishes first
                try:
                    print(future.result(), flush=True)
                except Exception as error:
                    failed = failed or error
            if failed:
                raise failed
    print(
        (
            "Selected structural checks passed."
            if args.case
            else "All structural checks passed."
        ),
        flush=True,
    )
    print("Visual and OGE review remain separate.", flush=True)


if __name__ == "__main__":
    main()
