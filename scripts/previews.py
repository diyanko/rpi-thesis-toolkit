#!/usr/bin/env python3
"""Pictures of the sample thesis for the website. Python standard library only.

    python3 scripts/previews.py [folder]     default folder: build/previews

build_site.py --previews calls make(). It compiles a scratch copy of the sample
one step at a time: pdfLaTeX, Biber, pdfLaTeX, pdfLaTeX. The programs are run
directly, not through latexmk, so a personal latexmkrc cannot move the output.
It saves:

- compile-pass-N-chapter.png and compile-pass-N-contents.png: crops of the
  chapter 1 paragraph with a citation and of the contents page after each pass
  (shown in docs/how-it-works.md);
- for each page in PAGES, from the finished PDF, three pictures for "Anatomy of
  your thesis" on the landing page: anatomy-NAME.png (the whole page, small),
  anatomy-NAME-lens.png (a close-up of the part LENSES picks, sharp enough to
  read) and anatomy-NAME-full.png (the whole page, large, opened from the card).

Every picture is a greyscale PNG (16 shades for the anatomy pictures, which
keeps them small) and carries its details (page number, alt text, where the
close-up sits on the page) in a text chunk, so read() can find them again: the
offline guide reuses the pictures of an earlier website build that way.

It never pictures the title page, which carries the RPI seal. Needs pdflatex
and biber, plus either poppler (pdftoppm and pdftotext) or Ghostscript (gs).
"""
from html import unescape
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
# Top-level folders that are not part of the thesis.
NOT_THESIS = {".git", ".github", ".vscode", "_local", "build", "dist", "docs", "site",
              "scripts", "reference", "cheatsheet", "__pycache__"}
# Files an earlier editor or build.py run leaves behind. They are not copied,
# so the first pass starts clean: unresolved citations and an empty contents page.
GENERATED = (".aux", ".bbl", ".bcf", ".blg", ".toc", ".lof", ".lot", ".out", ".run.xml",
             ".fls", ".fdb_latexmk", ".synctex.gz", ".log")
CROP_DPI = 144   # about 940 pixels across the text column
THUMB_DPI = 40   # anatomy-NAME.png: whole page, 340 pixels wide (shown about 90 wide)
LENS_DPI = 200   # anatomy-NAME-lens.png: 12 pt text stays sharp at 2x on screen
FULL_DPI = 120   # anatomy-NAME-full.png: whole page, 1020 pixels wide
LENS_PAD = 7     # points of white above and below a close-up
META = b"rpi-thesis-preview"   # PNG text chunk keyword for the picture's details


def first_line(lines):
    return lines[0].text if lines else ""


# Landing-page pictures: name -> test on the lines of one page (top to bottom).
PAGES = {
    "contents": lambda lines: norm(first_line(lines)) in {"contents", "tableofcontents"},
    "chapter": lambda lines: re.match(r"(CHAPTER\s+)?1\.?\s+[A-Za-z]", first_line(lines)),
    "figure-table": lambda lines: sum(
        bool(re.match(r"(Table|Figure)\s*\d+\.\d+:", line.text)) for line in lines) >= 2,
    "references": lambda lines: norm(first_line(lines)) in {"references", "bibliography"},
    "appendix": lambda lines: re.match(r"(APPENDIX\s+)?[A-Z]\.\s+[A-Za-z]", first_line(lines)),
}


def first_sentence(lines):
    text = re.sub(r"(\w)- (\w)", r"\1\2", " ".join(line.text for line in lines))
    found = re.match(r".+?[.!?](?=\s|$)", text)
    return found[0] if found else text


def heading_lens(lines, count=2):
    """The heading and the first `count` lines under it."""
    if len(lines) < count + 1:
        return None
    heading = lines[0].text
    return (lines[0], lines[count],
            f'the heading {heading}, then the paragraph that begins "{first_sentence(lines[1:6])}"')


def contents_lens(lines):
    """Two entries before the first chapter, the chapter, and its first section:
    roman and arabic page numbers, dot leaders, and the indent of a section."""
    entries = [line for line in lines[1:] if re.search(r"(\.\s*){4,}", line.text)]
    first = next((i for i, line in enumerate(entries) if re.match(r"1\.?\s", line.text)), None)
    if first is None:
        return None
    shown = entries[max(first - 2, 0):first + 2]
    parts = []
    for line in shown:
        found = re.match(r"(.*?)\s*(?:\.\s*){4,}\s*(\S*)$", line.text)
        title, number = (found[1], found[2]) if found else (line.text, "")
        parts.append(f"{title} ({number})" if number else title)
    listed = ", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]
    return shown[0], shown[-1], f"the entries {listed}, each with dot leaders out to its page number"


def table_lens(lines):
    """The first table caption and the table under it."""
    start = next((i for i, line in enumerate(lines) if re.match(r"Table\s*\d+(\.\d+)*:", line.text)), None)
    if start is None:
        return None
    end = start
    while end + 1 < len(lines) and lines[end + 1].top - lines[end].bottom < 24:
        end += 1
    if end == start:
        return None
    rows = end - start - 1
    return (lines[start], lines[end],
            f'the caption "{lines[start].text}" above the table it describes: '
            f'a header row and {rows} row{"s" if rows != 1 else ""} of values')


def references_lens(lines):
    """The first two entries. An entry starts at the left edge; the lines after
    its first one are indented."""
    body = [line for line in lines[1:] if not re.fullmatch(r"[ivxlc]+|\d+", line.text)]
    if not body:
        return None
    edge = min(line.left for line in body)
    starts = [i for i, line in enumerate(body) if line.left - edge < 2]
    if len(starts) < 2:
        return None
    end = (starts[2] if len(starts) > 2 else len(body)) - 1
    while end > starts[1] and body[end].top - body[end - 1].bottom > 30:   # stop at a big gap
        end -= 1

    def opening(line):
        return re.sub(r"\s+(url|doi|isbn|issn):?$", "", line.text, flags=re.I)

    return (body[0], body[end],
            f'the first two entries, "{opening(body[starts[0]])}" and "{opening(body[starts[1]])}"')


# Close-up of each landing-page picture: name -> lines of the page -> (first
# line, last line, what it shows) or None. The close-up spans the text block.
LENSES = {
    "contents": contents_lens,
    "chapter": heading_lens,
    "figure-table": table_lens,
    "references": references_lens,
    "appendix": heading_lens,
}
WHAT = {   # how the alt text names each page
    "contents": "the Contents page",
    "chapter": "the opening page of Chapter 1",
    "figure-table": "a page with a table",
    "references": "the References page",
    "appendix": "the first page of Appendix A",
}


class Line:
    def __init__(self, top, bottom, left, right, text):
        self.top, self.bottom, self.left, self.right, self.text = top, bottom, left, right, text


def norm(text):
    """Lower-case letters and digits only, so spacing differences do not matter."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def missing_tools():
    missing = [tool for tool in ("pdflatex", "biber") if not shutil.which(tool)]
    if not (shutil.which("pdftoppm") and shutil.which("pdftotext")) and not shutil.which("gs"):
        missing.append("pdftoppm and pdftotext (poppler), or gs (Ghostscript)")
    return missing


def run(command, cwd, what):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                            errors="replace", timeout=300)
    if result.returncode:
        tail = "\n".join(result.stdout.splitlines()[-25:])
        raise SystemExit(f"Previews: {what} failed while compiling the sample thesis.\n{tail}")


def compile_passes(work):
    """Copy the sample into `work` and return the PDF after each pdfLaTeX pass."""
    def skip(folder, names):
        top = Path(folder) == ROOT
        # PDFs are skipped only at the top level: figures may be PDFs.
        return [name for name in names
                if (top and (name in NOT_THESIS or name.endswith(".pdf")))
                or name == "build" or name.endswith(GENERATED)]

    shutil.copytree(ROOT, work, ignore=skip, dirs_exist_ok=True)
    latex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape", "main.tex"]
    pdfs = []
    for step in ("pdflatex", "biber", "pdflatex", "pdflatex"):
        if step == "biber":
            run(["biber", "main"], work, "Biber")
            continue
        run(latex, work, f"pdfLaTeX pass {len(pdfs) + 1}")
        pdfs.append(Path(work) / f"pass-{len(pdfs) + 1}.pdf")
        shutil.copyfile(Path(work) / "main.pdf", pdfs[-1])
    return pdfs


def text_lines(pdf):
    """The text lines of each page, with positions in points from the top left.
    Both tools give pieces of text (words or runs); pieces at the same height
    are joined into one line, left to right."""
    pages = []   # per page: pieces as (top, bottom, left, right, text)
    if shutil.which("pdftotext"):
        xml = subprocess.run(["pdftotext", "-bbox-layout", "-enc", "UTF-8", str(pdf), "-"],
                             capture_output=True, text=True, check=True).stdout
        for page in xml.split("<page ")[1:]:
            pages.append([])
            for box, word in re.findall(r"<word ([^>]*)>(.*?)</word>", page, re.S):
                get = dict(re.findall(r'(\w+)="([\d.]+)"', box))
                pages[-1].append((float(get["yMin"]), float(get["yMax"]), float(get["xMin"]),
                                  float(get["xMax"]), unescape(word)))
    else:
        xml = subprocess.run(
            ["gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=txtwrite", "-dTextFormat=0",
             "-sOutputFile=-", str(pdf)],
            capture_output=True, text=True, errors="replace", check=True,
        ).stdout
        for page in xml.split("<page>")[1:]:
            pages.append([])
            for box, size, chars in re.findall(
                r'<span bbox="([\d. -]+)"[^>]*?size="([\d.]+)">(.*?)</span>', page, re.S
            ):
                left, baseline, right, _ = (float(n) for n in box.split())
                size = float(size)   # Ghostscript gives the baseline, not the top
                text = "".join(unescape(c) for c in re.findall(r'c="([^"]*)"', chars))
                pages[-1].append((baseline - 0.8 * size, baseline + 0.25 * size, left, right, text))
    result = []
    for pieces in pages:
        rows = []
        for piece in sorted(pieces, key=lambda piece: (piece[1], piece[2])):
            if rows and abs(rows[-1][0][1] - piece[1]) < 2.5:
                rows[-1].append(piece)
            else:
                rows.append([piece])
        lines = []
        for row in rows:
            row.sort(key=lambda piece: piece[2])
            text, end = "", None
            for top, bottom, left, right, chunk in row:
                if end is not None and left - end > 0.15 * (bottom - top):
                    text += " "
                text, end = text + chunk, right
            lines.append(Line(min(p[0] for p in row), max(p[1] for p in row),
                              row[0][2], end, text.strip()))
        result.append(sorted(lines, key=lambda line: line.top))
    return result


def render(pdf, number, dpi, folder):
    """Page `number` (from 1) as (width, height, RGB bytes)."""
    out = Path(folder) / "page"
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-f", str(number), "-l", str(number), "-r", str(dpi),
                        "-singlefile", str(pdf), str(out)], check=True)
    else:
        subprocess.run(
            ["gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=ppmraw", f"-r{dpi}",
             f"-dFirstPage={number}", f"-dLastPage={number}", "-dTextAlphaBits=4",
             "-dGraphicsAlphaBits=4", f"-sOutputFile={out}.ppm", str(pdf)],
            check=True,
        )
    data = (out.with_suffix(".ppm")).read_bytes()
    match = re.match(rb"P6\s+(?:#[^\n]*\n\s*)*(\d+)\s+(\d+)\s+255\s", data)
    width, height = int(match[1]), int(match[2])
    return width, height, data[match.end():]


def save_png(path, width, height, rgb, box=None, shades=256, meta=None):
    """Write the pixels (cropped to box = left, top, right, bottom) as a PNG.
    Grey-only pictures are saved as greyscale, which makes them much smaller;
    shades=16 stores 4 bits a pixel. `meta` (a dict) goes in a text chunk."""
    if box:
        left, top, right, bottom = (int(round(n)) for n in box)
        left, top = max(left, 0), max(top, 0)
        right, bottom = min(right, width), min(bottom, height)
        rgb = b"".join(rgb[(y * width + left) * 3:(y * width + right) * 3] for y in range(top, bottom))
        width, height = right - left, bottom - top
    grey = rgb[0::3] == rgb[1::3] == rgb[2::3]
    pixels, channels, kind = (rgb[0::3], 1, 0) if grey else (rgb, 3, 2)
    stride, depth = width * channels, 8
    rows = [pixels[y * stride:(y + 1) * stride] for y in range(height)]
    if grey and shades == 16:   # two pixels a byte: the high and low four bits
        depth = 4
        level = bytes((v * 15 + 127) // 255 for v in range(256))
        high = bytes((v * 15 + 127) // 255 << 4 for v in range(256))
        packed = []
        for row in rows:
            row += b"\xff" * (width % 2)
            first, second = row[0::2].translate(high), row[1::2].translate(level)
            # No byte carries: high nibble + low nibble, added as big numbers
            packed.append((int.from_bytes(first, "big") + int.from_bytes(second, "big"))
                          .to_bytes(len(first), "big"))
        rows = packed
    raw = b"".join(b"\0" + row for row in rows)

    def chunk(tag, body):
        return (len(body).to_bytes(4, "big") + tag + body
                + zlib.crc32(tag + body).to_bytes(4, "big"))

    header = width.to_bytes(4, "big") + height.to_bytes(4, "big") + bytes([depth, kind, 0, 0, 0])
    text = chunk(b"tEXt", META + b"\0" + json.dumps(meta).encode("ascii")) if meta else b""
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + text
                           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    return width, height


def read(folder):
    """Details of the pictures in `folder` that save_png wrote, as make() returns them."""
    found = {}
    for path in sorted(Path(folder).glob("*.png")):
        data = path.read_bytes()
        if path.is_symlink() or not data.startswith(b"\x89PNG\r\n\x1a\n"):
            continue
        details = {"width": int.from_bytes(data[16:20], "big"),
                   "height": int.from_bytes(data[20:24], "big")}
        at = 8
        while at + 8 <= len(data):
            size, tag = int.from_bytes(data[at:at + 4], "big"), data[at + 4:at + 8]
            body = data[at + 8:at + 8 + size]
            if tag == b"tEXt" and body.startswith(META + b"\0"):
                details.update(json.loads(body[len(META) + 1:]))
            if tag == b"IDAT":
                break
            at += 12 + size
        found[path.stem] = details
    return found


def find_page(pages, test):
    """Index of the first page after the title page that passes `test`."""
    for index, lines in enumerate(pages):
        if index and not any("partialfulfillment" in norm(line.text) for line in lines) and test(lines):
            return index
    return None


def crops(pages):
    """Crop boxes in points: {"chapter": (page, box), "contents": (page, box)}."""
    found = {}
    chapter = find_page(pages, lambda lines: any("starterusesabook" in norm(l.text) for l in lines))
    contents = find_page(pages, PAGES["contents"])
    if chapter is None or contents is None:
        return found
    body = [line for line in pages[chapter] if len(line.text) > 40]
    left = min(line.left for line in body) - 10
    right = max(line.right for line in body) + 10
    lines = pages[chapter]
    start = next(i for i, line in enumerate(lines) if "starterusesabook" in norm(line.text))
    end = next((i for i in range(start, len(lines)) if "document" in norm(lines[i].text)), start)
    found["chapter"] = (chapter, (left, lines[start].top - 7, right, lines[end].bottom + 7))
    lines = pages[contents]
    start = next((i for i, line in enumerate(lines) if "conclusion" in norm(line.text)), None)
    end = max((i for i, line in enumerate(lines) if "additionalmaterial" in norm(line.text)), default=None)
    if start is None or end is None:   # empty contents: the heading and the blank space under it
        found["contents"] = (contents, (left, lines[0].top - 14, right, lines[0].bottom + 50))
    else:
        found["contents"] = (contents, (left, lines[start].top - 8, right, lines[end].bottom + 8))
    return found


def anatomy(pdf, folder, temp):
    """The three pictures of each page in PAGES (see the top of this file)."""
    made = {}
    pages = text_lines(pdf)
    # Every close-up spans the same text block, so its text shows at one size.
    chapter = find_page(pages, PAGES["chapter"])
    body = [line for line in pages[chapter or 0] if len(line.text) > 40] or [Line(0, 0, 72, 540, "")]
    left, right = min(line.left for line in body) - 8, max(line.right for line in body) + 8
    for name, test in PAGES.items():
        index = find_page(pages, test)
        if index is None:
            print(f"SKIP preview '{name}': no page of the sample thesis matched.")
            continue
        lines = pages[index]
        printed = lines[-1].text if lines and re.fullmatch(r"[ivxlc]+|\d+", lines[-1].text) else str(index + 1)
        lens = LENSES[name](lines)
        if lens is None:
            print(f"SKIP preview '{name}': the part to show close up was not found.")
            continue
        first, last, shows = lens
        width, height, rgb = render(pdf, index + 1, LENS_DPI, temp)
        page_w, page_h = width * 72 / LENS_DPI, height * 72 / LENS_DPI
        box = (left, first.top - LENS_PAD, right, last.bottom + LENS_PAD)
        spot = [round(100 * n, 2) for n in (box[0] / page_w, box[1] / page_h,
                                              (box[2] - box[0]) / page_w, (box[3] - box[1]) / page_h)]
        details = {"page": index + 1, "printed": printed}
        pictures = {
            f"anatomy-{name}-lens": (width, height, rgb, [n * LENS_DPI / 72 for n in box],
                                     {**details, "spot": spot, "alt": f"Close-up of {WHAT[name]}: {shows}"}),
            f"anatomy-{name}": (*render(pdf, index + 1, THUMB_DPI, temp), None, details),
            f"anatomy-{name}-full": (*render(pdf, index + 1, FULL_DPI, temp), None, details),
        }
        for picture, (w, h, pixels, crop, meta) in pictures.items():
            w, h = save_png(folder / f"{picture}.png", w, h, pixels, crop, shades=16, meta=meta)
            made[picture] = {"width": w, "height": h, **meta}
    return made


def make(folder):
    """Save the pictures in `folder`. Returns {name: {"width", "height", "page", ...}};
    {} if skipped."""
    missing = missing_tools()
    if missing:
        print("SKIP previews: missing " + ", ".join(missing) + ". The website is built "
              "without pictures of the sample thesis.")
        return {}
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    made = {}
    with tempfile.TemporaryDirectory() as temp:
        pdfs = compile_passes(Path(temp) / "thesis")
        # The crop shows what changes on each pass; pass 3 needs only the contents.
        wanted = {1: ("chapter", "contents"), 2: ("chapter", "contents"), 3: ("contents",)}
        for number, pdf in enumerate(pdfs, start=1):
            boxes = crops(text_lines(pdf))
            for part in wanted[number]:
                if part not in boxes:
                    print(f"SKIP preview compile-pass-{number}-{part}: page not found.")
                    continue
                page, box = boxes[part]
                width, height, rgb = render(pdf, page + 1, CROP_DPI, temp)
                name = f"compile-pass-{number}-{part}"
                width, height = save_png(folder / f"{name}.png", width, height, rgb,
                                         [n * CROP_DPI / 72 for n in box], meta={"page": page + 1})
                made[name] = {"width": width, "height": height, "page": page + 1}
        made.update(anatomy(pdfs[-1], folder, temp))
    print(f"Previews: {len(made)} pictures of the sample thesis in {folder}")
    return made


if __name__ == "__main__":
    make(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build/previews")
