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


# Every command amssymb and amsfonts define (TeX Live 2026), less the ones that
# take an argument (\mathbb and \mathfrak are typeset separately below).
AMS_NAMES = """
Bbbk Box Bumpeq Cap Cup Diamond Doteq Finv Game Join Lleftarrow Lsh Rrightarrow Rsh
Subset Supset Vdash Vvdash angle approxeq backepsilon backprime backsim backsimeq
barwedge because beth between bigstar blacklozenge blacksquare blacktriangle
blacktriangledown blacktriangleleft blacktriangleright boxdot boxminus boxplus
boxtimes bumpeq centerdot checkmark circeq circlearrowleft circlearrowright
circledR circledS circledast circledcirc circleddash complement curlyeqprec
curlyeqsucc curlyvee curlywedge curvearrowleft curvearrowright daleth dashleftarrow
dashrightarrow diagdown diagup digamma divideontimes doteqdot dotplus
doublebarwedge doublecap doublecup downdownarrows downharpoonleft downharpoonright
eqcirc eqsim eqslantgtr eqslantless eth fallingdotseq geqq geqslant ggg gggtr gimel
gnapprox gneq gneqq gnsim gtrapprox gtrdot gtreqless gtreqqless gtrless gtrsim
gvertneqq hbar hslash intercal leadsto leftarrowtail leftleftarrows leftrightarrows
leftrightharpoons leftrightsquigarrow leftthreetimes leqq leqslant lessapprox
lessdot lesseqgtr lesseqqgtr lessgtr lesssim lhd llcorner lll llless lnapprox lneq
lneqq lnsim looparrowleft looparrowright lozenge lrcorner ltimes lvertneqq maltese
measuredangle mho multimap nLeftarrow nLeftrightarrow nRightarrow nVDash nVdash
ncong nexists ngeq ngeqq ngeqslant ngtr nleftarrow nleftrightarrow nleq nleqq
nleqslant nless nmid nparallel nprec npreceq nrightarrow nshortmid nshortparallel
nsim nsubseteq nsubseteqq nsucc nsucceq nsupseteq nsupseteqq ntriangleleft
ntrianglelefteq ntriangleright ntrianglerighteq nvDash nvdash pitchfork precapprox
preccurlyeq precnapprox precneqq precnsim precsim restriction rhd rightarrowtail
rightleftarrows rightleftharpoons rightrightarrows rightsquigarrow rightthreetimes
risingdotseq rtimes shortmid shortparallel smallfrown smallsetminus smallsmile
sphericalangle sqsubset sqsupset square subseteqq subsetneq subsetneqq succapprox
succcurlyeq succnapprox succneqq succnsim succsim supseteqq supsetneq supsetneqq
therefore thickapprox thicksim triangledown trianglelefteq triangleq
trianglerighteq twoheadleftarrow twoheadrightarrow ulcorner unlhd unrhd
upharpoonleft upharpoonright upuparrows urcorner vDash varkappa varnothing
varpropto varsubsetneq varsubsetneqq varsupsetneq varsupsetneqq vartriangle
vartriangleleft vartriangleright veebar yen
""".split()
# A math font each engine must use for these symbols (the class's font choice).
AMS_FONTS = {"pdflatex": ("NewTXMI", "txsy"), "xelatex": ("TeXGyreTermesMath",),
             "lualatex": ("TeXGyreTermesMath",)}
AMS_DOC = r"""\documentclass{rpi-thesis}
%s
\thesissetup{title={T}, author={A}, degree=doctoral, department={Department of X},
  graduation-month=May, graduation-year={2027}}
\committeemember[Chair]{C}
\begin{document}
\tracinglostchars=2
\thesismainmatter
\chapter{AMS}
$x\in\mathbb{R}$, $\mathbb{N}\to\mathbb{Z}$, $\mathfrak{g}$, $a\leqslant b$,
$a\nleqslant b$, $\square$, $\blacktriangleright$.
%s
\end{document}
"""


def make_ams(engine):
    def case(proj, work):
        """Audit: AMS commands such as \\square and \\nleqslant were undefined on
        LuaLaTeX and XeLaTeX (amssymb was marked loaded but never read)."""
        guard = "\\ifcsname %s\\endcsname $\\csname %s\\endcsname$\\else\\typeout{AMSUNDEF:%s}\\fi"
        body = "\n".join(guard % (name, name, name) for name in AMS_NAMES)
        # As students write it (pasting the packages) and without the packages.
        for variant, packages in (("pasted", "\\usepackage{amssymb}\n\\usepackage{amsfonts}"),
                                  ("bare", "")):
            name = "ams-%s.tex" % variant
            (proj / name).write_text(AMS_DOC % (packages, body), encoding="utf-8")
            code, out = latex(proj, work, engine, name=name)
            log = read(proj / name.replace(".tex", ".log"))
            check(code == 0, "%s (%s) exited %d: %s" % (engine, variant, code, tail(out)))
            undefined = set(re.findall(r"AMSUNDEF:(\w+)", log))
            check(not undefined, "%s (%s): undefined AMS commands: %s"
                  % (engine, variant, " ".join(sorted(undefined))))
            lost = re.findall(r"Missing character: There is no (.*?)!", log)
            check(not lost, "%s (%s): glyphs missing from the font: %s" % (engine, variant, lost[:5]))
            pdf = proj / name.replace(".tex", ".pdf")
            if PdfReader is None:
                raise Skip("font check needs pypdf (commands and glyphs were checked)")
            fonts = set()
            for page in PdfReader(str(pdf)).pages:
                for font in (page["/Resources"].get("/Font") or {}).values():
                    fonts.add(str(font.get_object()["/BaseFont"]))
            for wanted in AMS_FONTS[engine]:
                check(any(wanted in font for font in fonts),
                      "%s (%s): no %s font in the PDF (%s)" % (engine, variant, wanted, sorted(fonts)))
    return case


# ---- verify.py behaviour (no TeX needed) ---------------------------------------

def _verify_module():
    sys.path.insert(0, str(ROOT / "scripts"))
    import verify
    return verify


def case_verify_auto_mode(proj, work):
    """Audit: auto verify chose quick when git failed, on a clean tree, and could
    miss staged or renamed files."""
    verify = _verify_module()
    repo = work / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "scripts").mkdir()
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")

    def git(*args):
        done = subprocess.run(["git", *args], cwd=repo, env=env, capture_output=True, text=True)
        check(done.returncode == 0, "fixture git %s failed: %s" % (args[0], done.stderr[-200:]))

    def expect(mode, why):
        got, reason = verify.auto_mode(repo)
        check(got == mode, "%s: auto chose %s (%s), expected %s" % (why, got, reason, mode))

    expect("full", "not a git checkout")
    git("init", "-q", "-b", "trunk")
    (repo / "docs/page.md").write_text("text\n")
    (repo / "scripts/tool.py").write_text("x = 1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    expect("full", "no main branch")
    git("branch", "-m", "main")
    expect("full", "clean main")
    git("checkout", "-q", "-b", "feature")
    expect("full", "clean feature branch")
    (repo / "docs/page.md").write_text("changed\n")
    expect("quick", "unstaged guide change")
    git("commit", "-q", "-am", "guide")
    expect("quick", "committed guide change")
    (repo / "scripts/tool.py").write_text("x = 2\n")
    expect("full", "unstaged script change")
    git("add", "scripts/tool.py")
    expect("full", "staged script change")
    git("reset", "-q", "--hard")
    (repo / "scripts/new.py").write_text("")
    expect("full", "untracked script")
    git("add", "scripts/new.py")
    expect("full", "staged new script")
    git("reset", "-q", "--hard")
    (repo / "docs/new.md").write_text("new\n")
    expect("quick", "untracked guide page")
    (repo / "docs/new.md").unlink()
    git("mv", "scripts/tool.py", "docs/tool.md")
    git("commit", "-q", "-m", "rename")
    expect("full", "script renamed to a guide page")
    git("reset", "-q", "--hard", "HEAD~1")
    (repo / "docs/bring-your-draft.md").write_text("recipe\n")
    expect("full", "guide page that a regression case compiles")
    (repo / "docs/bring-your-draft.md").unlink()
    (repo / "docs/page.md").write_text("again\n")
    real = verify.git
    for failing in ("diff", "ls-files"):
        def broken(*args, cwd=verify.ROOT, failing=failing):
            if args[0] == failing:
                return subprocess.CompletedProcess(args, 128, "", "simulated failure")
            return real(*args, cwd=cwd)
        verify.git = broken
        try:
            expect("full", "git %s failing" % failing)
        finally:
            verify.git = real


def case_verify_exact_zips(proj, work):
    """Audit: archive checks sorted dist/ by name, so v0.9.0 beat v0.10.0 and an
    old ZIP could be compiled instead of the one just built."""
    verify = _verify_module()
    for current, older in (("0.10.0", "0.9.0"), ("0.5.10", "0.5.9")):
        root = work / current
        (root / "dist").mkdir(parents=True)
        (root / "rpi-thesis.cls").write_text(
            "\\ProvidesClass{rpi-thesis}[2026/10/16 v%s RPI community thesis starter]\n" % current)
        for version in (older, current):
            for kind in ("starter", "overleaf"):
                (root / ("dist/rpi-thesis-%s-v%s.zip" % (kind, version))).write_bytes(b"")
        got = {kind: path.name for kind, path in verify.current_zips(root).items()}
        check(got == {kind: "rpi-thesis-%s-v%s.zip" % (kind, current) for kind in ("starter", "overleaf")},
              "current_zips picked %s for version %s" % (got, current))
    # Without a package step in this run there is nothing to test or compare.
    saved = dict(verify.PACKAGED)
    verify.PACKAGED.clear()
    try:
        for step in (verify.archives, verify.reproducible):
            ok, note = step()
            check(ok is False, "%s passed without ZIPs from this run: %s" % (step.__name__, note))
    finally:
        verify.PACKAGED.update(saved)


# ---- registry -----------------------------------------------------------------

def case_class_alone(proj, work):
    """The 'use just the class' recipe in docs/bring-your-draft.md compiles with
    only rpi-thesis.cls and a .bib file: no starter preamble, metadata or latexmkrc.
    Without biblatex, \\thesisreferences stops with a clear message."""
    doc = (ROOT / "docs/bring-your-draft.md").read_text(encoding="utf-8")
    section = doc[doc.index("## Already have a LaTeX thesis? Use just the class"):]
    recipe = section[section.index("```latex") + 8: section.index("```", section.index("```latex") + 8)]
    alone = work / "alone"
    alone.mkdir()
    for name in ("rpi-thesis.cls", "references.bib"):
        (alone / name).write_bytes((proj / name).read_bytes())
    (alone / "main.tex").write_text(recipe, encoding="utf-8")
    code, out = latexmk(alone, work)
    check(code == 0 and (alone / "main.pdf").is_file(), "recipe does not compile: " + tail(out))
    bare = "\n".join(l for l in recipe.splitlines() if "biblatex" not in l and "addbibresource" not in l)
    plain = work / "no-biblatex"   # a clean folder: no aux files from the run above
    plain.mkdir()
    (plain / "rpi-thesis.cls").write_bytes((proj / "rpi-thesis.cls").read_bytes())
    (plain / "main.tex").write_text(bare, encoding="utf-8")
    code, out = latex(plain, work)
    check(code != 0 and "needs biblatex" in out, "missing biblatex gave no clear error: " + tail(out))


# ---- class and citation cases (audit) ----------------------------------------
# One compile per citation style; each reads the real PDF: the vertical gap
# between reference-list entries (manual 2.1, p. 16: single spaced, one blank
# line between), the order of the list, repeated and organization authors,
# printed access dates, and citations in a caption and a \chapterattribution.

BIBOUT_BIB = r"""
@article{zkey,
  author = {Zimmerman, Alicia and Brandt, Carl},
  title = {Quixotic Zymurgy of Thin Films under Unusually Long Titles That Wrap},
  journaltitle = {Journal of Odd Results},
  date = {2019}, volume = {12}, pages = {1--9},
}
@book{whit1,
  author = {Whitfield, Odessa},
  title = {Wombat Cartography Handbook for Field Surveys in Difficult Terrain},
  publisher = {Fictional Press}, location = {Troy}, date = {2017},
}
@book{whit2,
  author = {Whitfield, Odessa},
  title = {Xylophone Badger Atlas of Northern Regions and Their Many Valleys},
  publisher = {Fictional Press}, location = {Troy}, date = {2021},
}
@online{okey,
  author = {{Vexillology Institute}},
  title = {Pennant Archive Guidelines for Long-Term Preservation of Flags},
  url = {https://example.org/pennants/archive/guidelines/long-term-preservation},
  urldate = {2026-10-14}, date = {2020},
}
@article{akey,
  author = {Abbott, Mira},
  title = {Aardvark Kinematics in Shallow Burrows with Several Exits},
  journaltitle = {Journal of Odd Results},
  date = {2015}, volume = {3}, pages = {10--20},
}
"""

# Fixture keys in the order they are first cited in the source.
BIBOUT_CITED = ["okey", "zkey", "whit1", "whit2", "akey"]
# A word from each entry, to find it in the reference list.
BIBOUT_WORD = {"okey": "pennant", "zkey": "zymurgy", "whit1": "wombat",
               "whit2": "xylophone", "akey": "aardvark"}
# How each style prints the access date of okey (spaces removed, lower case).
BIBOUT_URLDATE = {"numeric": "visitedon10/14/2026", "apa": "retrievedoctober14,2026",
                  "mla": "accessed14oct.2026", "chicago": "accessedoctober14,2026"}
BIBOUT_PROBE = r"""
\AtBeginDocument{\typeout{RPI-BIBOUT bibitemsep=\the\bibitemsep;
  lc=\the\value{biburllcpenalty}; uc=\the\value{biburlucpenalty};
  num=\the\value{biburlnumpenalty}}}
"""


def pdf_lines(path, first, last):
    """Text lines (y, x of first glyph, text) on PDF pages first..last (0-based),
    top to bottom, from pypdf's text positions."""
    if PdfReader is None:
        raise Skip("needs pypdf")
    pages = []
    for page in PdfReader(str(path)).pages[first:last + 1]:
        chunks = []

        def visit(text, cm, tm, *_):
            if text.strip():
                x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
                y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
                chunks.append((round(y, 1), x, text))
        page.extract_text(visitor_text=visit)
        rows = {}
        for y, x, text in chunks:
            rows.setdefault(y, []).append((x, text))
        pages.append([(y, min(x for x, _ in row), "".join(t for _, t in row))
                      for y, row in sorted(rows.items(), reverse=True)])
    return pages


def reference_entries(pdf):
    """The reference list as entries: (text, [(page, y), ...] per line)."""
    pages = [" ".join((p.extract_text() or "").split()).lower() for p in PdfReader(str(pdf)).pages]
    starts = [i for i, t in enumerate(pages) if t.startswith("references") and "zymurgy" in t]
    check(starts, "no page that starts with the REFERENCES heading and lists a fixture entry")
    lines = []
    for number, page in enumerate(pdf_lines(pdf, starts[0], len(pages) - 1)):
        body = [l for l in page if 80 < l[0] < 712]  # inside the 1 in margins
        heading = body and body[0][1] > 100        # a centered heading on top
        if number == 0:
            body = body[1:]                         # drop REFERENCES
        elif heading:
            break                                   # the next chapter or appendix
        lines += [(number, y, x, text) for y, x, text in body]
    check(lines, "the reference list is empty")
    left = min(x for _, _, x, _ in lines)
    indents = [round(x) for _, _, x, _ in lines if x - left > 1.5]
    check(indents, "no hanging indent in the reference list")
    hang = max(set(indents), key=indents.count)      # continuation lines start here
    entries = []
    for number, y, x, text in lines:
        # A line that is not at the hanging indent starts an entry; Chicago's
        # repeated-author dash is a rule, so that entry's text starts further in.
        if abs(x - hang) > 1.5 or not entries:
            entries.append(["", []])
        entries[-1][0] += text
        entries[-1][1].append((number, y))
    return [(re.sub(r"\s+", "", t).lower(), where) for t, where in entries]


def bib_gaps(entries):
    """(line pitch inside entries, gaps between entries), same page only, in pt."""
    inside, between = [], []
    for index, (_, where) in enumerate(entries):
        for (p1, y1), (p2, y2) in zip(where, where[1:]):
            if p1 == p2:
                inside.append(y1 - y2)
        if index + 1 < len(entries):
            (p1, y1), (p2, y2) = where[-1], entries[index + 1][1][0]
            if p1 == p2:
                between.append(y1 - y2)
    check(inside and between, "too few multi-line entries to measure spacing")
    return inside, between


def make_bib_output(style, own_setting=False):
    def case(proj, work):
        """Audit: reference-list spacing, order, authors, access dates, caption and attribution cites."""
        pre = proj / "preamble.tex"
        package_line = BIBLATEX_LINE
        if style in ("apa", "mla"):
            package_line = "\\usepackage[backend=biber,style=%s]{biblatex}" % style
        elif style == "chicago":
            package_line = CHICAGO_PREAMBLE
        own = ("\n\\setlength{\\bibitemsep}{0pt}\\setcounter{biburllcpenalty}{100}"
               if own_setting else "")
        replace_once(pre, BIBLATEX_LINE, package_line + own)
        append(pre, BIBOUT_PROBE)
        append(proj / "references.bib", BIBOUT_BIB)
        chapter = proj / "chapters/02-research.tex"
        text = read(chapter)
        match = re.search(r"\\label\{[^}]*\}\n", text)
        check(match is not None, "fixture drift: no \\label in 02-research.tex")
        attribution = ("\\chapterattribution{Portions of this chapter have previously "
                       "appeared in work by an institute~\\parencite{okey}.}\n")
        body = ("Reverse order: \\parencite{zkey}, then \\parencite{whit1}.\n\n"
                "\\begin{figure}[h]\\centering\n"
                "\\includegraphics[width=0.2\\linewidth]{example-image-a}\n"
                "\\caption{A figure reproduced from \\textcite{whit2}.}\n"
                "\\end{figure}\n\n"
                "Last: \\parencite{akey}.\n\n")
        chapter.write_text(text[:match.end()] + attribution + body + text[match.end():])

        code, out = latexmk(proj, work)
        check(code == 0, "latexmk (%s) exited %d: %s" % (style, code, tail(out)))
        log = read(proj / "main.log")
        check(not re.search(r"Citation .+ undefined|There were undefined references", log),
              "unresolved citations in the log")
        probe = re.search(r"RPI-BIBOUT bibitemsep=([^;]+);\s*lc=(\d+); uc=(\d+); num=(\d+)",
                          log.replace("\n", ""))
        check(probe, "no RPI-BIBOUT line in the log")
        lc = int(probe.group(2))
        check(lc == (100 if own_setting else 9000),
              "biburllcpenalty is %d: the %s" % (lc, "student's own setting was overwritten"
                                                 if own_setting else "class default did not apply"))

        text = re.sub(r"\s+", "", pdf_text(proj / "main.pdf")).lower()
        head = text.rpartition("references")[0]
        attribution_at = head.find("workbyaninstitute")
        check(attribution_at >= 0, "attribution not found")
        caption_at = head.find("afigurereproducedfrom")
        check(caption_at >= 0, "caption not found")

        entries = reference_entries(proj / "main.pdf")
        position = {}
        for key, word in BIBOUT_WORD.items():
            found = [i for i, (t, _) in enumerate(entries) if word in t]
            check(len(found) == 1, "%s: found in %d reference entries, expected 1" % (key, len(found)))
            position[key] = found[0]
        if style == "numeric":   # sorting=none: order of first citation
            expected = BIBOUT_CITED
            check(head[attribution_at:].startswith("workbyaninstitute[%d]" % (position["okey"] + 1)),
                  "attribution citation number does not match okey's place in the list")
            check("[%d]" % (position["whit2"] + 1) in head[caption_at:caption_at + 60],
                  "caption citation number does not match whit2's place in the list")
        else:                    # author, then year: Abbott, Vexillology, Whitfield x2, Zimmerman
            expected = ["akey", "okey", "whit1", "whit2", "zkey"]
            check("vexillologyinstitute" in head[attribution_at:attribution_at + 80],
                  "attribution citation does not name the organization")
            check("whitfield" in head[caption_at:caption_at + 60],
                  "caption citation does not name the author")
        order = sorted(BIBOUT_WORD, key=position.get)
        check(order == expected, "reference order %s, expected %s" % (order, expected))
        org = entries[position["okey"]][0]
        check("vexillologyinstitute" in org and "institute,v" not in org,
              "organization author printed as a person: " + org[:80])
        check(BIBOUT_URLDATE[style] in org, "access date missing from the web entry: " + org[:200])
        second = entries[position["whit2"]][0]
        # MLA's dash is text; Chicago's is a rule, so its text starts at the "."
        check("whitfield" in second or re.match(r"(\[\d+\])?([\u2014\u2013\u2015-]{2,}|\.)", second),
              "repeated author neither named nor dashed: " + second[:80])

        inside, between = bib_gaps(entries)
        pitch = sorted(inside)[len(inside) // 2]
        want = pitch if own_setting else 2 * pitch
        bad = [round(g, 2) for g in between if abs(g - want) > 0.5]
        check(not bad, "%s: gaps between entries %s pt; expected %.2f (line pitch %.2f%s)"
              % (style, bad, want, pitch, ", student's 0pt" if own_setting else " + one blank line"))
    return case


def case_class_alone_order(proj, work):
    """Audit: the 'use just the class' recipe sorted numbers alphabetically, unlike the starter."""
    doc = read(ROOT / "docs/bring-your-draft.md")
    section = doc[doc.index("## Already have a LaTeX thesis? Use just the class"):]
    begin = section.index("```latex") + 8
    recipe = section[begin: section.index("```", begin)]
    check("\\thesisreferences" in recipe, "fixture drift: no \\thesisreferences in the recipe")
    recipe = recipe.replace("\\thesisreferences",
                            "Cited \\parencite{zkey} then \\parencite{akey}.\n\\thesisreferences", 1)
    alone = work / "alone"
    alone.mkdir()
    (alone / "rpi-thesis.cls").write_bytes((proj / "rpi-thesis.cls").read_bytes())
    (alone / "references.bib").write_text(BIBOUT_BIB, encoding="utf-8")
    (alone / "main.tex").write_text(recipe, encoding="utf-8")
    code, out = latexmk(alone, work)
    check(code == 0, "recipe with citations does not compile: " + tail(out))
    text = re.sub(r"\s+", "", pdf_text(alone / "main.pdf")).lower()
    check("cited[1]then[2]" in text, "the in-text numbers are not [1] then [2]")
    refs = text.rpartition("references")[2]
    check(0 <= refs.find("zymurgy") < refs.find("aardvark"),
          "the recipe lists references alphabetically; the starter lists them in citation order")


CASES = {}


def register(name, function, tools=("latexmk", "pdflatex", "biber"), needs_pdf_text=False):
    CASES[name] = (function, tools, needs_pdf_text)


register("deep-include", case_deep_include)
for _style in ("numeric", "apa", "mla", "chicago"):  # numeric: the starter's own preamble
    register("fullcite-styles:" + _style, make_fullcite(_style), needs_pdf_text=True)
register("portrait-figure", case_portrait_figure, tools=("pdflatex",))
for _engine in ("pdflatex", "xelatex", "lualatex"):
    register("ams-symbols:" + _engine, make_ams(_engine), tools=(_engine,), needs_pdf_text=True)
register("verify-auto-mode", case_verify_auto_mode, tools=("git",))
register("verify-exact-zips", case_verify_exact_zips, tools=())
register("verbatim-input", case_verbatim_input)
register("missing-chapter", case_missing_chapter)
register("urldate-hint", case_urldate_hint)
register("package-completeness", case_package_completeness, tools=())
register("class-alone", case_class_alone)
for _style in ("numeric", "apa", "mla", "chicago"):
    register("bib-output:" + _style, make_bib_output(_style), needs_pdf_text=True)
register("bib-output:chicago-own-setting", make_bib_output("chicago", own_setting=True),
         needs_pdf_text=True)
register("class-alone-order", case_class_alone_order, needs_pdf_text=True)


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
                        nargs="+", help="Run only these cases (a group name such as fullcite-styles runs its parts)")
    parser.add_argument("--jobs", type=int, default=max(1, os.cpu_count() or 1))
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
