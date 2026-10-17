#!/usr/bin/env python3
"""Make the test PDFs for the "Check your PDF" page (site/pdf-check/).

    python3 scripts/tests/pdf_fixtures.py OUT_FOLDER [NAME ...]

Compiles the starter, a few variants of it that break one formatting point
each, and small documents from other classes, in parallel, in a temporary
folder, and copies each PDF to OUT_FOLDER/NAME.pdf. test_pdf_check.py (beside it)
uses them; nothing here is tracked. Needs TeX Live (latexmk, pdfLaTeX,
LuaLaTeX, Biber). Python standard library only.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
from common import ROOT  # noqa: E402

STARTER = ["main.tex", "metadata.tex", "preamble.tex", "rpi-thesis.cls", "references.bib", "latexmkrc"]
STARTER_FOLDERS = ["chapters", "frontmatter", "appendices", "assets", "figures"]

ROWS = "\n".join(f"Row {k} & {k * 3} & {k * 7} \\\\" for k in range(1, 46))
FILLER = ("This paragraph is ordinary body text, written only to fill the page. " * 6).strip()

# name -> (engine, starter?, {file: text to append}, {file: (old, new)}) or
# (engine, None, main.tex text) for a document from another class.
FIXTURES = {
    "starter": ("pdf", True, {}, {}),
    "starter-lualatex": ("lua", True, {}, {
        "metadata.tex": [("degree = doctoral", "degree = masters"),
                         ("copyright-page = false", "copyright-page = true")]}),
    "a4-paper": ("pdf", True, {"preamble.tex": "\\geometry{a4paper}\n"}, {}),
    "narrow-margins": ("pdf", True, {"preamble.tex": "\\geometry{left=0.6in,right=0.6in}\n"}, {}),
    "number-moved": ("pdf", True, {"preamble.tex": r"""\makeatletter
\renewcommand{\ps@plain}{\renewcommand{\@oddhead}{}\renewcommand{\@evenhead}{}%
  \renewcommand{\@oddfoot}{\normalfont\thepage\hfil}\renewcommand{\@evenfoot}{\@oddfoot}}
\renewcommand{\ps@rpibody}{\let\@mkboth\@gobbletwo
  \renewcommand{\@oddhead}{\normalfont\thepage\hfil}\renewcommand{\@evenhead}{\@oddhead}%
  \renewcommand{\@oddfoot}{}\renewcommand{\@evenfoot}{}}
\makeatother
"""}, {}),
    "sideways-table": ("pdf", True, {
        "preamble.tex": "\\usepackage{rotating}\n",
        "chapters/02-research.tex": "\\begin{sidewaystable}\n\\centering\n\\caption{A long sideways table}\n"
                                    "\\begin{tabular}{lrr}\n" + ROWS + "\n\\end{tabular}\n\\end{sidewaystable}\n"}, {}),
    "section-at-top": ("pdf", True, {
        "chapters/01-introduction.tex": "\\clearpage\n\\section{METHODS AT THE TOP}\n" + FILLER + "\n"}, {}),
    "unlisted-heading": ("pdf", True, {
        "chapters/03-conclusion.tex": "\\chapter*{AN UNLISTED CHAPTER}\n" + FILLER + "\n"}, {}),
    "blank-page": ("pdf", True, {
        "chapters/01-introduction.tex": "\\clearpage\\thispagestyle{empty}\\null\\clearpage\n" + FILLER + "\n"}, {}),
    # A chapter title with an accented letter, a superscript, and a year at
    # the end, long enough to wrap in the contents.
    "heading-details": ("pdf", True, {}, {
        "chapters/02-research.tex": [("\\chapter{RESEARCH AND FINDINGS}",
                                      "\\chapter{RÉSULTATS: HOW $R^2$ CHANGED ACROSS THE FIELD SEASONS OF 2026 WITHIN STUDY 2}")]}),
    # Layouts the checker once misread, and small differences from the
    # manual's wording that it reports as such (docs/check-pdf.md).
    # "CHAPTER 1" over the title in the body, "1. TITLE" in the contents.
    "chapter-label": ("pdf", True, {"preamble.tex": r"""\titleformat{\chapter}[display]
  {\vskip-\baselinestretch\dimexpr18pt\relax\centering\normalfont\large\bfseries}
  {\MakeUppercase{\chaptertitlename}\ \thechapter}{0pt}{}
"""}, {}),
    # A title of four lines in the body that wraps at other words in the contents.
    "wrapped-heading": ("pdf", True, {}, {
        "chapters/02-research.tex": [("\\chapter{RESEARCH AND FINDINGS}",
                                      "\\chapter{" + " ".join(["RESEARCH AND FINDINGS ON A LONG SUBJECT"] * 6) + "}")]}),
    # A contents page that begins with the first line of an entry that wraps.
    "contents-continuation": ("pdf", True, {}, {
        "chapters/02-research.tex": [("\\chapter{RESEARCH AND FINDINGS}",
                                      "\\addtocontents{toc}{\\protect\\clearpage}\n\\chapter{RESEARCH AND FINDINGS "
                                      "WITH A TITLE LONG ENOUGH TO WRAP ONTO A SECOND LINE OF THE CONTENTS}")]}),
    # Capitals in tiny type inside a figure at the top of a body page.
    "figure-caps": ("pdf", True, {
        "chapters/01-introduction.tex": "\\clearpage\n\\begin{figure}[t]\n\\centering\n"
                                        "{\\tiny AXIS LABELS IN CAPITALS INSIDE A FIGURE}\n"
                                        "\\caption{A figure whose labels are tiny capitals}\n\\end{figure}\n" + FILLER + "\n"}, {}),
    # An unnumbered notice page after the thesis, as ProQuest adds.
    "extra-last-page": ("pdf", True, {}, {
        "main.tex": [("\\end{document}", "\\clearpage\\thispagestyle{empty}\n"
                      "A notice page added to the end of a distributed copy.\n\\end{document}")]}),
    # Page numbers 0.58 in from the edge.
    "number-distance": ("pdf", True, {"preamble.tex": "\\geometry{footskip=0.42in,headsep=0.42in}\n"}, {}),
    # Bottom page numbers 0.2 in from the edge: far off, still flagged.
    "number-far": ("pdf", True, {"preamble.tex": "\\geometry{footskip=0.8in}\n"}, {}),
    # One line 0.05 in into the right margin.
    "margin-overrun-small": ("pdf", True, {
        "chapters/01-introduction.tex": "\n\\noindent\\hbox to \\dimexpr\\textwidth+0.05in\\relax"
                                        "{A line set a little wider than the text block\\hfil and ending past the margin.}\\par\n"}, {}),
    # Long enough to cancel while it is read.
    "many-pages": ("pdf", None, "\\documentclass[letterpaper,12pt]{article}\n\\begin{document}\n"
                   + "\n\n".join([FILLER] * 1500) + "\n\\end{document}\n"),
    # Half-size pages with /UserUnit 2: US letter in physical size.
    "user-unit": ("pdf", None, r"""\documentclass{article}
\pdfpagewidth=4.25in \pdfpageheight=5.5in
\pdfpageattr{/UserUnit 2}
\pagestyle{empty}
\begin{document}
Text on a page whose user unit is two points.
\end{document}
"""),
    "font-not-embedded": ("pdf", None, r"""\documentclass[letterpaper,12pt]{article}
\usepackage{times}
\pdfmapline{=ptmr8r Times-Roman "TeXBase1Encoding ReEncodeFont" <8r.enc}
\begin{document}
Times Roman is used here without its font file, so the PDF names the font
but does not contain it.
\end{document}
"""),
    "report-class": ("pdf", None, r"""\documentclass[letterpaper,12pt]{report}
\usepackage[margin=1in]{geometry}
\usepackage{hyperref}
\title{A Report From Another Class}\author{Someone}
\begin{document}
\maketitle
\tableofcontents
\chapter{Introduction}
""" + FILLER + r"""
\section{Background}
""" + FILLER + r"""
\chapter{Results}
""" + FILLER + r"""
\end{document}
"""),
    "no-text": ("pdf", None, r"""\documentclass[letterpaper]{article}
\pagestyle{empty}
\begin{document}
\rule{3in}{3in}
\newpage
\rule{1in}{1in}
\end{document}
"""),
}


def write(folder, spec):
    engine, starter, *rest = spec
    folder.mkdir(parents=True)
    if starter is None:
        (folder / "main.tex").write_text(rest[0], encoding="utf-8")
        return engine
    for name in STARTER:
        shutil.copy2(ROOT / name, folder / name)
    for name in STARTER_FOLDERS:
        if (ROOT / name).is_dir():
            shutil.copytree(ROOT / name, folder / name)
    appends, replaces = rest
    for name, pairs in replaces.items():
        path = folder / name
        text = path.read_text(encoding="utf-8")
        for old, new in pairs:
            if old not in text:
                raise SystemExit(f"pdf_fixtures.py: {name} no longer contains {old!r}; update the fixture.")
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")
    for name, extra in appends.items():
        with (folder / name).open("a", encoding="utf-8") as handle:
            handle.write("\n" + extra)
    return engine


def compile_one(name, work, out):
    folder = work / name
    engine = write(folder, FIXTURES[name])
    command = ["latexmk", "-pdflua" if engine == "lua" else "-pdf", "-interaction=nonstopmode",
               "-halt-on-error", "-no-shell-escape", "-outdir=out", "main.tex"]
    result = subprocess.run(command, cwd=folder, capture_output=True, text=True, timeout=600)
    pdf = folder / "out" / "main.pdf"  # an explicit folder, whatever a personal latexmkrc says
    if result.returncode or not pdf.exists():
        tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-15:])
        return name, f"latexmk failed:\n{tail}"
    shutil.copyfile(pdf, out / f"{name}.pdf")
    return name, None


def tex_available():
    return all(shutil.which(tool) for tool in ("latexmk", "pdflatex", "lualatex", "biber"))


def make(out, names=None, jobs=6):
    """Compile the named fixtures (default: all) into out/NAME.pdf.
    Returns {name: error message} for the ones that failed."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    names = list(names or FIXTURES)
    with tempfile.TemporaryDirectory(prefix="pdf_fixtures_") as tmp:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            results = list(pool.map(lambda n: compile_one(n, Path(tmp), out), names))
    return {name: error for name, error in results if error}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("out", metavar="OUT_FOLDER", help="where each NAME.pdf goes")
    parser.add_argument("names", nargs="*", metavar="NAME",
                        help="fixtures to make (default: all): " + ", ".join(FIXTURES))
    args = parser.parse_args()
    unknown = [name for name in args.names if name not in FIXTURES]
    if unknown:
        parser.error("unknown fixture(s): " + ", ".join(unknown))
    if not tex_available():
        print("pdf_fixtures.py: needs latexmk, pdflatex, lualatex and biber (TeX Live).")
        return 1
    errors = make(args.out, args.names or None)
    for name, error in errors.items():
        print(f"FAIL {name}: {error}")
    print(f"pdf_fixtures: {len(args.names or FIXTURES) - len(errors)} PDFs in {args.out}, {len(errors)} failed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
