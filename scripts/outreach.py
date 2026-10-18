"""Print the outreach pages (outreach/**/*.html) to PDF in build/outreach/.

Usage, from the repository root:

    python3 scripts/outreach.py

Each page sets its own paper size with CSS @page; headless Chrome prints it
at that size (preferCSSPageSize), with backgrounds. Files whose name starts
with an underscore are skipped. The handout also gets a two-up print version,
handout-2up.pdf: each side twice on US letter landscape, built from
outreach/handout.html on the fly, so the words live in one file. What each
file is, and how to print it: outreach/README.md.

Python standard library only; pypdf, when installed, checks the page sizes.
Maintainer tooling only.
"""
import argparse
import base64
from pathlib import Path
import re
import sys

from chrome import Chrome, LocalServer
from common import ROOT, find_chrome

OUTREACH = ROOT / "outreach"
OUT = ROOT / "build" / "outreach"
HANDOUT = "handout.html"
TWO_UP = "handout-2up.html"

# One side of the handout: from its "<!-- page: name -->" comment to the
# </section> that closes the page (the last one before the next side).
SIDE = re.compile(r"<!-- page: (\w+) -->\s*(<section class=\"page .*?</section>)\s*(?=<!-- page:|</body>)", re.S)


# The first page (1-based) whose content reaches into its bottom or right
# padding, the print-safe margin; 0 when everything fits.
CROWDED = """(() => {
  const pages = [...document.querySelectorAll('.page')];
  for (const [i, page] of pages.entries()) {
    const box = page.getBoundingClientRect(), style = getComputedStyle(page);
    const bottom = box.bottom - parseFloat(style.paddingBottom) + 1;
    const right = box.right - parseFloat(style.paddingRight) + 1;
    for (const el of page.querySelectorAll('*')) {
      const r = el.getBoundingClientRect();
      if (r.height && (r.bottom > bottom || r.right > right)) return i + 1;
    }
  }
  return 0;
})()"""


def two_up(html):
    """The handout as US letter landscape sheets, two copies of each side."""
    sides = SIDE.findall(html)
    if not sides:
        raise SystemExit(f"outreach/{HANDOUT}: no sides found; keep a <!-- page: name --> comment "
                         "before each <section class=\"page ...\">.")
    cut = '<span class="cut cut-top" aria-hidden="true"></span><span class="cut cut-bottom" aria-hidden="true"></span>'
    sheets = "\n".join(f'<div class="sheet" aria-label="{name}, two copies">\n{page}\n{page}\n{cut}\n</div>'
                       for name, page in sides)
    head, _, _ = html.partition("<body")
    head = head.replace("<title>RPI Thesis Toolkit handout</title>",
                        "<title>RPI Thesis Toolkit handout, two-up</title>")
    return f'{head}<body class="handout imposed">\n{sheets}\n</body>\n</html>\n'


def pages(only=None):
    """(published path under outreach/, output PDF name) for every page to print."""
    found = []
    for path in sorted(OUTREACH.rglob("*.html")):
        rel = path.relative_to(OUTREACH)
        if any(part.startswith("_") for part in rel.parts):
            continue
        found.append((rel.as_posix(), rel.with_suffix(".pdf").as_posix()))
        if rel.as_posix() == HANDOUT:
            found.append((TWO_UP, "handout-2up.pdf"))
    if only:
        found = [item for item in found if any(word in item[0] for word in only)]
    return found


def pdf_pages(path):
    """[(width in, height in), ...] for each page, or None without pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    sizes = []
    for page in PdfReader(str(path)).pages:
        box = page.mediabox
        sizes.append((round(float(box.width) / 72, 2), round(float(box.height) / 72, 2)))
    return sizes


def describe(sizes):
    """'2 pages, 5.5 x 8.5 in' (sizes grouped in order)."""
    groups = []
    for size in sizes:
        if groups and groups[-1][0] == size:
            groups[-1][1] += 1
        else:
            groups.append([size, 1])
    count = len(sizes)
    return f"{count} page{'s' if count != 1 else ''}, " + ", ".join(
        f"{w:g} x {h:g} in" + (f" (x{n})" if len(groups) > 1 else "") for (w, h), n in groups)


def main():
    parser = argparse.ArgumentParser(description="Print outreach/*.html to PDF in build/outreach/.")
    parser.add_argument("only", nargs="*", help="print only pages whose path contains one of these words")
    args = parser.parse_args()

    chrome = find_chrome()
    if not chrome:
        sys.exit("Chrome or Chromium was not found. Install one, or set CHROME to its path, "
                 "then run python3 scripts/outreach.py again.")
    todo = pages(args.only)
    if not todo:
        sys.exit("No outreach pages to print (outreach/**/*.html, names not starting with _).")

    handout = (OUTREACH / HANDOUT).read_text(encoding="utf-8") if (OUTREACH / HANDOUT).exists() else ""

    def dynamic(path, _query):
        if path == f"/outreach/{TWO_UP}" and handout:
            return two_up(handout).encode("utf-8"), "text/html; charset=utf-8"
        return None

    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    with LocalServer(ROOT, dynamic) as server, Chrome(chrome) as browser:
        for page, pdf_name in todo:
            browser.open(f"{server.url}/outreach/{page}")
            browser.evaluate("document.fonts.ready.then(() => Promise.all([...document.images]"
                             ".map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }))))"
                             ".then(() => true)")
            crowded = browser.evaluate(CROWDED)
            if crowded:
                print(f"  Warning: outreach/{page}: text runs into the margin on page {crowded}; "
                      "shorten the words or reduce a size in outreach/outreach.css.")
            data = browser.call("Page.printToPDF", preferCSSPageSize=True, printBackground=True,
                                marginTop=0, marginBottom=0, marginLeft=0, marginRight=0)["data"]
            target = OUT / pdf_name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(base64.b64decode(data))
            written.append(target)

    print(f"Wrote {len(written)} PDF{'s' if len(written) != 1 else ''} to build/outreach/:")
    for target in written:
        sizes = pdf_pages(target)
        note = describe(sizes) if sizes else "page size not checked (pypdf not installed)"
        print(f"  {target.relative_to(ROOT).as_posix()}: {note}")


if __name__ == "__main__":
    main()
