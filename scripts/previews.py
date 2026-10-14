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
- one picture of each page in PAGES, from the finished PDF (the landing page).

It never pictures the title page, which carries the RPI seal. Needs pdflatex
and biber, plus either poppler (pdftoppm and pdftotext) or Ghostscript (gs).
"""
from html import unescape
from pathlib import Path
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
CROP_DPI = 144   # about 940 pixels across the text column
PAGE_DPI = 90    # whole-page pictures, 765 pixels wide


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
        return [name for name in names if Path(folder) == ROOT and name in NOT_THESIS]

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


def save_png(path, width, height, rgb, box=None):
    """Write the pixels (cropped to box = left, top, right, bottom) as a PNG.
    Grey-only pictures are saved as greyscale, which makes them much smaller."""
    if box:
        left, top, right, bottom = (int(round(n)) for n in box)
        left, top = max(left, 0), max(top, 0)
        right, bottom = min(right, width), min(bottom, height)
        rgb = b"".join(rgb[(y * width + left) * 3:(y * width + right) * 3] for y in range(top, bottom))
        width, height = right - left, bottom - top
    grey = rgb[0::3] == rgb[1::3] == rgb[2::3]
    pixels, channels, kind = (rgb[0::3], 1, 0) if grey else (rgb, 3, 2)
    stride = width * channels
    raw = b"".join(b"\0" + pixels[y * stride:(y + 1) * stride] for y in range(height))

    def chunk(tag, body):
        return (len(body).to_bytes(4, "big") + tag + body
                + zlib.crc32(tag + body).to_bytes(4, "big"))

    header = width.to_bytes(4, "big") + height.to_bytes(4, "big") + bytes([8, kind, 0, 0, 0])
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
                           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    return width, height


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


def make(folder):
    """Save the pictures in `folder`. Returns {name: {"width", "height", "page"}}; {} if skipped."""
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
                                         [n * CROP_DPI / 72 for n in box])
                made[name] = {"width": width, "height": height, "page": page + 1}
        final = pdfs[-1]
        pages = text_lines(final)
        for name, test in PAGES.items():
            index = find_page(pages, test)
            if index is None:
                print(f"SKIP preview '{name}': no page of the sample thesis matched.")
                continue
            width, height = save_png(folder / f"{name}.png", *render(final, index + 1, PAGE_DPI, temp))
            made[name] = {"width": width, "height": height, "page": index + 1}
    print(f"Previews: {len(made)} pictures of the sample thesis in {folder}")
    return made


if __name__ == "__main__":
    make(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build/previews")
