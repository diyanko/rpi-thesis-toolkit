#!/usr/bin/env python3
"""Fast regression tests for bugs found by past audits.

    python3 scripts/regressions.py [--list] [--case NAME ...] [--jobs N] [--keep]

Each case copies the starter thesis into its own temporary folder, applies a
small mutation, runs a real command (latexmk, pdflatex, or scripts/build.py),
and checks the exit code, the log, or the PDF text. Nothing in the repository
is changed, and dist/ and build/ are never touched. Needs TeX Live (latexmk,
pdflatex, lualatex, xelatex, biber). PDF text checks need pypdf (or pdftotext);
without either, those checks are skipped rather than failed.

Exit status: 0 all passed (or skipped), 1 a case failed, 2 a tool is missing.
"""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True  # never leave __pycache__ in the repository

TIMEOUT = 420  # seconds for any one command

COPY_FILES = ["main.tex", "metadata.tex", "preamble.tex", "rpi-thesis.cls",
              "references.bib", "latexmkrc"]
COPY_DIRS = ["frontmatter", "chapters", "appendices", "figures", "assets"]
# build.py is run from inside the copy, as a student runs it from the ZIP.
COPY_SCRIPTS = ["scripts/build.py"]

EPOCH = "1767225600"

try:
    from pypdf import PdfReader
except ImportError:  # optional: PDF-text checks are skipped without it
    PdfReader = None


class Skip(Exception):
    """A check that cannot run here (reported as SKIP, not as a failure)."""


class Fail(Exception):
    pass


def check(condition, message):
    if not condition:
        raise Fail(message)


# ---- helpers ----------------------------------------------------------------

def child_env(home):
    env = os.environ.copy()
    env.update(SOURCE_DATE_EPOCH=EPOCH, TZ="UTC", LC_ALL="C", HOME=str(home))
    env.pop("TEXMFHOME", None)
    return env


def make_project(work):
    """Copy the starter inputs into work/proj and return that folder."""
    proj = work / "proj"
    proj.mkdir(parents=True)
    for name in COPY_FILES + COPY_SCRIPTS:
        src = ROOT / name
        if src.is_file():
            (proj / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, proj / name)
    for name in COPY_DIRS:
        if (ROOT / name).is_dir():
            shutil.copytree(ROOT / name, proj / name, symlinks=False,
                            ignore=shutil.ignore_patterns(".*", "*.pdf~"))
    return proj


def run(command, cwd, work, timeout=TIMEOUT):
    """Run a command with the deterministic environment; return (code, output)."""
    try:
        done = subprocess.run(
            command, cwd=cwd, env=child_env(work), stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise Fail("timed out after %d s: %s" % (timeout, " ".join(map(str, command[:3]))))
    return done.returncode, done.stdout.decode("utf-8", errors="replace")


def read(path):
    return Path(path).read_text(encoding="utf-8", errors="replace")


def replace_once(path, old, new):
    text = read(path)
    check(old in text, "fixture drift: %r not found in %s" % (old[:50], Path(path).name))
    Path(path).write_text(text.replace(old, new, 1), encoding="utf-8")


def append(path, text):
    with open(path, "a", encoding="utf-8") as stream:
        stream.write(text)


def editor_command(proj):
    """The VS Code recipe command from .vscode/settings.json, as the editor
    would run it: %OUTDIR% = <project>/build and %DOC% = <project>/main."""
    settings = json.loads(read(ROOT / ".vscode/settings.json"))
    tool = next(t for t in settings["latex-workshop.latex.tools"] if t["name"] == "rpi-latexmk")
    out = str(proj / "build")
    args = [a.replace("%OUTDIR%", out).replace("%DOC%", str(proj / "main")) for a in tool["args"]]
    return [tool["command"]] + args


def editor_build(proj, work):
    return run(editor_command(proj), proj, work)


def latex(proj, work, engine="pdflatex", name="main.tex"):
    """One engine run with no latexmk: fast, and fine when citations may stay unresolved."""
    return run([engine, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
                "-file-line-error", name], proj, work)


def latexmk(proj, work):
    return run(["latexmk", "-pdf", "-no-shell-escape", "-interaction=nonstopmode",
                "-halt-on-error", "-file-line-error", "main.tex"], proj, work)


def pdf_text(path):
    """Whitespace-normalised text of a PDF, or raise Skip when nothing can read it."""
    if PdfReader is not None:
        text = " ".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)
    elif shutil.which("pdftotext"):
        text = subprocess.run(["pdftotext", str(path), "-"], stdout=subprocess.PIPE,
                              check=True).stdout.decode("utf-8", errors="replace")
    else:
        raise Skip("needs pypdf")
    return " ".join(text.split())


def tail(output, lines=12):
    return " | ".join(output.strip().splitlines()[-lines:])


# ---- cases --------------------------------------------------------------------

def case_editor_first_run(proj, work):
    """Audit: the first editor compile stopped with 'I can't write on file chapters/...aux'."""
    check(not (proj / "build").exists(), "fixture drift: build/ already exists")
    code, out = editor_build(proj, work)
    check(code == 0, "editor recipe exited %d on the first run: %s" % (code, tail(out)))
    check((proj / "build/main.pdf").is_file(), "build/main.pdf was not made")


def case_deep_include(proj, work):
    """Audit: latexmkrc did not create output folders for deeply nested chapters."""
    deep = proj / "chapters/a/b/c/d/e"
    deep.mkdir(parents=True)
    (deep / "deep.tex").write_text("\\chapter{DEEPCHAPTER}\nDeep text.\n")
    replace_once(proj / "main.tex", "\\thesisreferences",
                 "\\include{chapters/a/b/c/d/e/deep}\n\\thesisreferences")
    code, out = editor_build(proj, work)
    check(code == 0, "first editor run with a 5-deep include exited %d: %s" % (code, tail(out)))
    check((proj / "build/main.pdf").is_file(), "build/main.pdf was not made")
    check((proj / "build/chapters/a/b/c/d/e/deep.aux").is_file(), "no .aux for the deep chapter")


def case_blank_committee(proj, work):
    """Audit: an empty \\committeemember name must stop with a clear message."""
    replace_once(proj / "metadata.tex", "\\committeemember[Chair]{Your committee chair}",
                 "\\committeemember[Chair]{}")
    code, out = latex(proj, work)
    log = read(proj / "main.log") if (proj / "main.log").exists() else ""
    check(code != 0, "a blank committee member did not stop the build")
    check("Blank committee member name" in log + out,
          "log lacks 'Blank committee member name': " + tail(out))


AMS_MATH = r"""
\section{AMS symbols}
Real numbers $x\in\mathbb{R}$, $a\leqslant b$, the empty set $\varnothing$,
$\nexists$, $A\subsetneq B$, and $\mathbb{N}\to\mathbb{Z}$.
\begin{equation}
  \sum_{i=1}^{n} i \geqslant \varnothing \quad\text{AMSMARK}
\end{equation}
"""


def make_ams(engine):
    def case(proj, work):
        """Audit: amssymb clashed with unicode-math on the Unicode engines."""
        replace_once(proj / "preamble.tex", "% ---- Your packages ----",
                     "% ---- Your packages ----\n\\usepackage{amssymb}")
        append(proj / "chapters/01-introduction.tex", AMS_MATH)
        code, out = latex(proj, work, engine)
        check(code == 0, "%s with amssymb exited %d: %s" % (engine, code, tail(out)))
        check((proj / "main.pdf").is_file(), "main.pdf was not made")
    return case


FULLCITE_BIB = r"""
@article{zkey,
  author = {Zimmerman, Alicia and Brandt, Carl},
  title = {Quixotic Zymurgy of Thin Films},
  journaltitle = {Journal of Odd Results},
  date = {2019},
  volume = {12},
  pages = {1--9},
}
@book{wkey,
  author = {Whitfield, Odessa},
  title = {Wombat Cartography Handbook},
  publisher = {Fictional Press},
  address = {Troy},
  date = {2017},
}
@online{okey,
  author = {{Vexillology Institute}},
  title = {Pennant Archive Guidelines},
  url = {https://example.org/pennants},
  urldate = {2026-10-14},
  date = {2020},
}
"""

# Each (author surname, title word) must reach the attribution, caption, and list of figures.
FULLCITE_KEYS = [("zkey", "Zimmerman", "Zymurgy"), ("wkey", "Whitfield", "Wombat"),
                 ("okey", "Vexillology", "Pennant")]

CHICAGO_PREAMBLE = r"""\usepackage[authordate,backend=biber]{biblatex-chicago}"""
CHICAGO_MACRO = r"""
\DeclareCiteCommand{\fullcite}{\usebibmacro{prenote}}
  {\usedriver{\DeclareNameAlias{sortname}{default}}{\thefield{entrytype}}}
  {\multicitedelim}{\usebibmacro{postnote}}
"""
MLA_MACRO = r"""
\DeclareCiteCommand{\fullcite}{\usebibmacro{prenote}}
  {\csgundef{bbx@lasthash}%
   \usedriver{\DeclareNameAlias{sortname}{default}}{\thefield{entrytype}}%
   \csgundef{bbx@lasthash}}
  {\multicitedelim}{\usebibmacro{postnote}}
"""
BIBLATEX_LINE = "\\usepackage[backend=biber,style=numeric,sorting=none]{biblatex}"


def make_fullcite(style):
    def case(proj, work):
        """Audit: \\fullcite printed nothing, 'id.', or a dash after an earlier cite of the key."""
        pre = proj / "preamble.tex"
        if style == "apa":
            replace_once(pre, BIBLATEX_LINE, "\\usepackage[backend=biber,style=apa]{biblatex}")
        elif style == "mla":
            replace_once(pre, BIBLATEX_LINE, "\\usepackage[backend=biber,style=mla]{biblatex}")
            replace_once(pre, "\\addbibresource{references.bib}",
                         "\\addbibresource{references.bib}" + MLA_MACRO)
        elif style == "chicago":
            replace_once(pre, BIBLATEX_LINE, CHICAGO_PREAMBLE)
            replace_once(pre, "\\addbibresource{references.bib}",
                         "\\addbibresource{references.bib}" + CHICAGO_MACRO)
        append(proj / "references.bib", FULLCITE_BIB)
        chapter = proj / "chapters/02-research.tex"
        body = ["\\section{Fullcite regression}", "Earlier ordinary citations:"]
        for key, _, _ in FULLCITE_KEYS:
            body.append("\\parencite{%s}" % key)
        body.append("\\par")
        for index, (key, _, _) in enumerate(FULLCITE_KEYS):
            body += ["\\begin{figure}[htbp]\\centering",
                     "\\includegraphics[width=0.2\\linewidth]{example-image-a}",
                     "\\caption{Reproduced from \\fullcite{%s}.}" % key,
                     "\\end{figure}"]
        append(chapter, "\n" + "\n".join(body) + "\n")
        # Attribution goes directly under the chapter's \chapter and \label lines.
        text = read(chapter)
        match = re.search(r"\\label\{[^}]*\}\n", text)
        check(match is not None, "fixture drift: no \\label in 02-research.tex")
        attribution = "\\chapterattribution{Portions of this chapter have previously appeared as: %s.}\n" % (
            "; ".join("\\fullcite{%s}" % key for key, _, _ in FULLCITE_KEYS))
        chapter.write_text(text[:match.end()] + attribution + text[match.end():])

        code, out = latexmk(proj, work)
        check(code == 0, "latexmk (%s) exited %d: %s" % (style, code, tail(out)))
        log = read(proj / "main.log")
        check(not re.search(r"Citation .+ undefined|There were undefined references", log),
              "unresolved citations in the log")
        # pypdf drops some spaces and styles change case (APA lower-cases titles),
        # so compare with spaces removed and in lower case.
        text = re.sub(r"\s+", "", pdf_text(proj / "main.pdf")).lower()
        head, _, _ = text.rpartition("references")  # the reference list follows the last heading
        check(head, "no REFERENCES heading in the PDF text")
        marker = "havepreviouslyappearedas:"
        start = head.find(marker)
        check(start >= 0, "attribution text not found")
        snippet = head[start + len(marker):][:700]
        check(not re.match(r"(id\.|[\u2014\u2013\u2015-]{2,})", snippet),
              "attribution starts with 'id.' or a dash: " + snippet[:80])
        for key, surname, word in FULLCITE_KEYS:
            surname, word = surname.lower(), word.lower()
            check(surname in snippet and word in snippet,
                  "%s: author or title missing from the attribution (%s)" % (key, snippet[:120]))
            # attribution + figure caption + list of figures entry
            for term in (surname, word):
                count = head.count(term)
                check(count >= 3, "%s: %s appears %d times before the reference list; expected"
                      " at least 3 (attribution, caption, list of figures)" % (key, term, count))
    return case


def case_portrait_figure(proj, work):
    """Audit: a tall image with the documented portrait recipe gave 'Float too large'."""
    append(proj / "chapters/01-introduction.tex", r"""
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth,height=0.7\textheight,keepaspectratio]{example-image-9x16}
  \caption{A tall portrait image with a caption long enough to wrap across a couple of
  lines so that the caption height counts too.}
  \label{fig:portrait-regression}
\end{figure}
""")
    code, out = latex(proj, work)
    log = read(proj / "main.log")
    check(code == 0, "pdflatex exited %d: %s" % (code, tail(out)))
    check("Float too large" not in log, "log contains 'Float too large'")


def case_verbatim_input(proj, work):
    """Audit: an \\input shown inside verbatim was treated as a real, missing file."""
    append(proj / "chapters/01-introduction.tex", "\n\\begin{verbatim}\n\\input{no-such-file}\n"
           "\\include{chapters/no-such-chapter}\n\\end{verbatim}\n")
    code, out = run([sys.executable, "scripts/build.py"], proj, work)
    check(code == 0, "scripts/build.py exited %d: %s" % (code, tail(out)))
    check("WITHOUT" not in out and "no-such-file" not in out,
          "build.py complained about text inside verbatim: " + tail(out))
    check((proj / "build/main.pdf").is_file(), "build/main.pdf was not made")


def case_missing_chapter(proj, work):
    """Audit: a deleted \\include'd chapter left a PDF that silently lacked it."""
    (proj / "chapters/02-research.tex").unlink()
    code, out = run([sys.executable, "scripts/build.py"], proj, work)
    check(code != 0, "build.py exited 0 although chapters/02-research.tex is missing")
    check("WITHOUT" in out and "02-research" in out,
          "build.py output lacks 'WITHOUT' and the file name: " + tail(out))


def case_urldate_hint(proj, work):
    """Audit: a month-name urldate was not flagged, though OGE needs an access date."""
    append(proj / "references.bib", """
@online{badate,
  author  = {{Date Test Org}},
  title   = {Access Date Page},
  url     = {https://example.org/page},
  urldate = {October 15, 2026}
}
""")
    append(proj / "chapters/01-introduction.tex", "\nA web source~\\parencite{badate}.\n")
    code, out = run([sys.executable, "scripts/build.py"], proj, work)
    check("badate" in out and "YYYY-MM-DD" in out and "access date" in out.lower(),
          "no access-date hint for the month-name urldate (exit %d): %s" % (code, tail(out)))


PACKAGE_PROBE = r"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import package
from pathlib import Path
proj = Path(sys.argv[2])
package.ROOT = proj   # read the copy, never the real repository
names = set(package.FILES)
package.verify_archive("starter ZIP", names)  # the unmodified sample is complete
extra = "chapters/04-extra.tex"
(proj / extra).write_text("\\chapter{EXTRA}\nText.\n")
main = proj / "main.tex"
main.write_text(main.read_text().replace(
    "\\thesisreferences", "\\include{chapters/04-extra}\n\\thesisreferences", 1))
assert extra not in names
try:
    package.verify_archive("starter ZIP", names)  # \\include'd chapter missing from FILES
except SystemExit as stop:
    assert extra in str(stop), str(stop)
    print("OK " + extra)
else:
    raise AssertionError("verification passed although %s is not in FILES" % extra)
package.verify_archive("starter ZIP", names | {extra})  # once added, it passes
"""


def case_package_completeness(proj, work):
    """Audit: a ZIP that lacked an \\include'd chapter could still ship."""
    code, out = run([sys.executable, "-B", "-c", PACKAGE_PROBE, str(ROOT / "scripts"), str(proj)],
                    proj, work, timeout=120)
    check(code == 0, "package probe exited %d: %s" % (code, tail(out)))
    check("OK chapters/04-extra.tex" in out, "probe did not confirm the failure: " + tail(out))


# ---- registry -----------------------------------------------------------------

CASES = {}


def register(name, function, tools=("latexmk", "pdflatex", "biber"), needs_pdf_text=False):
    CASES[name] = (function, tools, needs_pdf_text)


register("editor-first-run", case_editor_first_run)
register("deep-include", case_deep_include)
register("blank-committee", case_blank_committee, tools=("pdflatex",))
for _engine in ("pdflatex", "lualatex", "xelatex"):
    register("ams-symbols:" + _engine, make_ams(_engine), tools=(_engine,))
for _style in ("numeric", "apa", "mla", "chicago"):
    register("fullcite-styles:" + _style, make_fullcite(_style), needs_pdf_text=True)
register("portrait-figure", case_portrait_figure, tools=("pdflatex",))
register("verbatim-input", case_verbatim_input)
register("missing-chapter", case_missing_chapter)
register("urldate-hint", case_urldate_hint)
register("package-completeness", case_package_completeness, tools=())


def selected(patterns):
    if not patterns:
        return list(CASES)
    chosen = []
    for pattern in patterns:
        found = [n for n in CASES if n == pattern or n.split(":")[0] == pattern]
        if not found:
            raise SystemExit("Unknown case %r. Run with --list to see the names." % pattern)
        chosen += [n for n in found if n not in chosen]
    return chosen


def run_case(name, keep):
    function, _, _ = CASES[name]
    work = Path(tempfile.mkdtemp(prefix="rpi-regress-")).resolve()
    started = time.time()
    status, detail = "PASS", ""
    try:
        function(make_project(work), work)
    except Skip as skipped:
        status, detail = "SKIP", str(skipped)
    except Fail as failure:
        status, detail = "FAIL", str(failure)
    except Exception as error:  # a bug in the case itself still must not hide the others
        status, detail = "FAIL", "%s: %s" % (type(error).__name__, error)
    elapsed = time.time() - started
    if status == "FAIL":
        detail += " [kept %s]" % work
    elif not keep:
        shutil.rmtree(work, ignore_errors=True)
    return name, status, detail, elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--list", action="store_true", help="List the cases and exit")
    parser.add_argument("--case", action="append", default=[], metavar="NAME",
                        nargs="+", help="Run only these cases (a group name such as ams-symbols runs its parts)")
    parser.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--keep", action="store_true", help="Keep the temporary folders")
    args = parser.parse_args()
    patterns = [name for group in args.case for name in group]
    if args.list:
        for name, (function, _, _) in CASES.items():
            print("%-28s %s" % (name, (function.__doc__ or "").strip().splitlines()[0] if function.__doc__ else ""))
        return 0
    names = selected(patterns)
    needed = {tool for name in names for tool in CASES[name][1]}
    missing = sorted(tool for tool in needed if not shutil.which(tool))
    if missing:
        print("Missing TeX tools: " + ", ".join(missing) + ". Install a full TeX Live "
              "(it includes latexmk and biber) and try again.", file=sys.stderr)
        return 2
    if not (PdfReader or shutil.which("pdftotext")) and any(CASES[n][2] for n in names):
        print("Note: pypdf is not installed; PDF-text checks will be skipped.")
    failures = 0
    started = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        for name, status, detail, elapsed in pool.map(lambda n: run_case(n, args.keep), names):
            if status == "PASS":
                print("PASS %s (%.1fs)" % (name, elapsed))
            elif status == "SKIP":
                print("SKIP %s (%s)" % (name, detail))
            else:
                failures += 1
                print("FAIL %s: %s" % (name, detail))
            sys.stdout.flush()
    print("%d case(s), %d failed, %.0fs total" % (len(names), failures, time.time() - started))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
