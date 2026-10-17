#!/usr/bin/env python3
"""Run the "Check your PDF" checks on every PDF in a folder, in headless Chrome.

    python3 scripts/check_pdfs.py [FOLDER] [--details] [--json FILE]

FOLDER defaults to _local/pdf-samples/ (ignored by Git): put PDFs there that
OGE accepted or returned, to see how the checker does on them. Never copy
those PDFs into tracked files; they are someone's thesis. Each PDF is read in
the browser exactly as the page reads it (site/pdf-check/core.js and the
vendored pdf.js, served from site/ on a localhost port); nothing leaves this
computer.

Output: one row per PDF with a letter per check (. looks right, ~ differs
from the manual's wording, X look at this, ? could not tell, i information),
then a key. --details also prints
every flagged point. --json saves the full results. For screenshots of the
page with a result, use scripts/ui_check.py --pdf-result.

Needs Chrome or Chromium ($CHROME, as for ui_check.py). Python standard
library only; Chrome is driven through its DevTools protocol (scripts/chrome.py).
"""
import argparse
import json
import re
import sys
from pathlib import Path

from chrome import Chrome, LocalServer
from common import ROOT, class_version, find_chrome
import rules

SAMPLES = ROOT / "_local" / "pdf-samples"
ORDER = ["paper", "same-size", "numbering", "position", "distance", "headings", "margins", "contents", "listed",
         "fonts", "blank", "size", "version"]
MARK = {"ok": ".", "differs": "~", "check": "X", "unknown": "?", "info": "i"}
# The harness page carries the same rules block as the guide page (scripts/rules.py);
# RULES is the expression that reads it, as ui.js does.
HARNESS = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>check_pdfs</title>
<script src="/pdf-check/core.js"></script></head><body>%s</body></html>"""
RULES = 'JSON.parse(document.getElementById("oge-rules").textContent)'
# The page part (ui.js) with the guide page's own checker markup, for
# scripts/tests/test_pdf_check.py. It counts the pdf.js workers that are running.
UI_HARNESS = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>check_pdfs ui</title>
<script>
window.liveWorkers = 0;
window.Worker = class extends Worker {
  constructor(...args) { super(...args); this.counted = true; window.liveWorkers++; }
  terminate() { if (this.counted) { this.counted = false; window.liveWorkers--; } super.terminate(); }
};
</script></head><body><main class="guide-content">%s</main>%s<script src="/pdf-check/ui.js"></script></body></html>"""


def checker_markup():
    """The checker's markup from docs/check-pdf.md (one line starting <div class="pdf-check")."""
    found = re.search(r'(?m)^<div class="pdf-check" .*$', (ROOT / "docs/check-pdf.md").read_text(encoding="utf-8"))
    if not found:
        raise RuntimeError("docs/check-pdf.md has no <div class=\"pdf-check\" ...> line")
    return found[0].replace('data-version=""', f'data-version="{class_version()[0]}"', 1)

RUN = """(async function () {
  const pdfjs = await import("/pdf-check/pdfjs/pdf.min.mjs");
  pdfjs.GlobalWorkerOptions.workerSrc = "/pdf-check/pdfjs/pdf.worker.min.mjs";
  if (pdfjs.version !== PdfCheckCore.PDFJS_VERSION) throw new Error("pdf.js " + pdfjs.version + " is not PDFJS_VERSION");
  const bytes = new Uint8Array(await (await fetch(%(url)s)).arrayBuffer());
  const data = await PdfCheckCore.read(pdfjs, bytes);
  return PdfCheckCore.analyse(data, { current: %(current)s, rules: %(rules)s });
})()"""


def server(folder, pdfs=()):
    """Serve folder on a localhost port, plus the harness pages and the PDFs
    under /__pdf__/N, without touching the folder."""
    pdfs = list(pdfs)

    def dynamic(path, query):
        page = "text/html; charset=utf-8"
        if path == "/__pdf_check__.html":
            return (HARNESS % rules.embed()).encode(), page
        if path == "/__pdf_ui__.html":
            return (UI_HARNESS % (checker_markup(), rules.embed())).encode(), page
        if path.startswith("/__pdf__/"):
            return Path(pdfs[int(path.rsplit("/", 1)[1])]).read_bytes(), "application/pdf"
        return None
    return LocalServer(folder, dynamic)


def check(pdfs, current=None, chrome=None):
    """Results for each PDF: (path, list of checks) or (path, error text)."""
    chrome = chrome or find_chrome()
    if not chrome:
        raise RuntimeError("no Chrome found")
    current = class_version()[0] if current is None else current
    out = []
    with server(ROOT / "site", pdfs) as site, Chrome(chrome) as browser:
        browser.open(site.url + "/__pdf_check__.html")
        for index, pdf in enumerate(pdfs):
            try:
                found = browser.evaluate(RUN % {"url": json.dumps(f"/__pdf__/{index}"), "current": json.dumps(current), "rules": RULES})
                out.append((pdf, found))
            except RuntimeError as error:
                out.append((pdf, str(error).splitlines()[0]))
    return out


def table(results, details=False):
    width = max([len(Path(p).name) for p, _ in results] + [4])
    lines = ["PDF".ljust(width) + "  " + " ".join(f"{k + 1:>2}" for k in range(len(ORDER)))]
    for pdf, found in results:
        name = Path(pdf).name.ljust(width)
        if isinstance(found, str):
            lines.append(f"{name}  could not be read: {found}")
            continue
        by = {f["id"]: f for f in found}
        lines.append(name + "  " + " ".join(f"{MARK.get(by[k]['state'], '-') if k in by else '-':>2}" for k in ORDER))
        if details:
            for f in found:
                if f["state"] in ("check", "differs", "unknown"):
                    lines.append(f"    {MARK[f['state']]} {f['title']}: {f['summary']}")
                    lines += [f"        {text}" for text in f["pages"][:20]]
    lines.append("Checks: " + ", ".join(f"{k + 1} {name}" for k, name in enumerate(ORDER)))
    lines.append("Key: . looks right, ~ differs from the manual's wording, X look at this, ? could not tell, i information")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("folder", nargs="?", help="folder of PDFs (default _local/pdf-samples/)")
    parser.add_argument("--details", action="store_true", help="print every flagged point")
    parser.add_argument("--json", metavar="FILE", help="save the full results as JSON")
    args = parser.parse_args()
    chrome = find_chrome()
    if not chrome:
        print("SKIP check_pdfs: no Chrome found (set $CHROME)")
        return 0
    folder = Path(args.folder) if args.folder else SAMPLES
    pdfs = sorted(p for p in folder.glob("*.pdf") if p.is_file()) if folder.is_dir() else []
    if not pdfs:
        print(f"check_pdfs: no PDFs in {folder}; put PDFs there (never in tracked files).")
        return 1
    results = check([str(p) for p in pdfs], chrome=chrome)
    print(table(results, args.details))
    if args.json:
        Path(args.json).write_text(json.dumps([{"pdf": Path(p).name, "result": r} for p, r in results], indent=2) + "\n",
                                   encoding="utf-8")
    return 1 if any(isinstance(r, str) for _, r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
