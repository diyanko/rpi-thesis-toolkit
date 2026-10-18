#!/usr/bin/env python3
"""Compile the thesis locally; never install, upload, or publish anything."""
import argparse
import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import types

if sys.version_info < (3, 9):
    sys.exit(
        "This helper needs Python 3.9 or newer. Update Python, or compile from"
        " your editor instead (it does not need Python)."
    )
# A Windows console or redirected output may not handle every character in a
# folder name; print a replacement character rather than crash.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")

ROOT = Path(__file__).resolve().parents[1]
ENGINES = {"pdflatex": "-pdf", "xelatex": "-xelatex", "lualatex": "-lualatex"}
# rpi-thesis.cls asks for LaTeX 2022-06-01 (\NeedsTeXFormat), first in TeX Live 2022.
MIN_TEXLIVE = 2022


def student_files(root, pattern):
    """The student's own sources, skipping generated output and archived copies."""
    skip = {"build", "dist", "output", "tmp", "_local", ".git"}
    for path in sorted(root.rglob(pattern)):
        if not skip.intersection(path.relative_to(root).parts):
            yield path


def guide(root, page):
    """Point to the guide that exists here: docs/ in the repository, or the
    offline HTML guide (opened from START-HERE.html) in the downloaded ZIP."""
    if (root / "docs" / (page + ".md")).exists():
        return "docs/" + page + ".md"
    return "guide/" + page + ".html (open START-HERE.html)"


def read_source(path):
    """Read a .tex file as UTF-8, falling back to Latin-1 for older files."""
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


VERBATIM_ENVS = (r"verbatim\*?|Verbatim\*?|lstlisting|minted|comment|filecontents\*?|alltt"
                 r"|tcblisting|BVerbatim|LVerbatim|VerbatimOut")
GRAPHIC_EXTENSIONS = ("", ".pdf", ".png", ".jpg", ".jpeg", ".eps")


def clean_tex(text):
    """The text with everything TeX does not run as commands blanked out:
    %-comments, \\verb, verbatim-like environments (verbatim, lstlisting,
    minted, comment, ...) and \\iffalse ... \\fi. Line breaks are kept so line
    numbers stay true."""
    def blank(match):
        return re.sub(r"[^\n]", " ", match[0])

    lines = []
    for line in text.split("\n"):
        line = re.sub(r"\\(?:verb\*?|lstinline)\s*([^a-zA-Z\s*])(.*?)\1", blank, line)
        lines.append(re.sub(r"((?:\\.|[^\\%])*)%.*", r"\1", line))
    text = "\n".join(lines)
    text = re.sub(r"\\begin\{(" + VERBATIM_ENVS + r")\}.*?\\end\{\1\}", blank, text, flags=re.S)
    return re.sub(r"\\iffalse\b.*?\\fi\b", blank, text, flags=re.S)


def active_sources(root, main="main.tex"):
    """Follow literal \\input{...} and \\include{...} commands from main.tex.

    Only the document being compiled is read, so unused drafts elsewhere in
    the folder cannot stop a build. Comments, verbatim-like environments and
    \\iffalse blocks are ignored. Not followed: references built from macros,
    \\import, \\subfile, and files TeX finds in its own installation (such as
    \\input{glyphtounicode}). The scan is a best guess, so only an unreadable
    main.tex stops a build; everything else is advice.

    Local .cls and .sty files are followed too, including the packages,
    classes and \\input files they load. TeX resolves their literal paths from
    the project folder.

    Returns a namespace: files (the local TeX source files read), include_dirs, problems
    [(where, message, stops_build)], missing_includes [(where, target)],
    includeonly (a set of targets, or None), and, for packaging, assets (other
    project files the document loads: graphics with literal paths, .bib files,
    a local .cls or .sty) and missing_assets [(where, target, kind)].
    """
    root = root.resolve()
    scan = types.SimpleNamespace(
        files=[], include_dirs=set(), problems=[], missing_includes=[],
        includeonly=None, assets=[], missing_assets=[])
    pending, seen = [(root / main, "The project folder")], set()
    graphics_dirs = [""]
    texts = []
    while pending:
        source, origin = pending.pop()
        if source in seen:
            continue  # already read; this also stops \\input cycles
        seen.add(source)
        name = source.relative_to(root).as_posix()
        try:
            text = read_source(source)
        except OSError:
            if source == root / main and not source.exists():
                scan.problems.append((str(root), f"there is no {main} in this folder. The"
                                      f" helper always builds {main}: restore it, or rename"
                                      f" your main file to {main}.", True))
            else:
                scan.problems.append((origin, f"cannot read {name}. Close any program that"
                                      " has it open, check that it is a file and not a"
                                      " folder, then build again.", source == root / main))
            continue
        scan.files.append(source)
        text = clean_tex(text)
        texts.append((name, text))
        for found in re.finditer(r"\\includeonly\s*\{([^}]*)\}", text):
            scan.includeonly = (scan.includeonly or set()) | {
                t.strip().removesuffix(".tex") for t in found[1].split(",") if t.strip()}
        for found in re.finditer(r"\\graphicspath\s*\{((?:\s*\{[^}]*\})+)\s*\}", text):
            graphics_dirs += re.findall(r"\{([^}]*)\}", found[1])
        patterns = (
            r"\\(input|include)\s*\{([^}]+)\}",
            r"\\includegraphics\*?\s*(\[[^\]]*\])?\s*\{([^}]+)\}",
            r"\\(addbibresource|bibliography)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}",
            r"\\(documentclass|usepackage|RequirePackage(?:WithOptions)?|LoadClass(?:WithOptions)?)"
            r"\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}",
        )
        matches = ((kind, match) for kind, pattern in enumerate(patterns)
                   for match in re.finditer(pattern, text))
        for kind, match in matches:
            number = text.count("\n", 0, match.start()) + 1
            where = f"{name}, line {number}"
            command, target = match.groups()
            if kind == 0:
                target = target.strip()
                if command == "include":
                    target = target.removesuffix(".tex")
                path = (root / target).resolve()
                if not path.is_relative_to(root):
                    # TeX may read a file outside the project, but an \\include
                    # also writes an .aux file there, which TeX normally refuses.
                    if command == "include":
                        scan.problems.append((where, f"\\include{{{target}}} points outside"
                                              " the project folder. Move that file into the"
                                              " project.", False))
                    continue
                if command == "include":
                    scan.include_dirs.add(Path(target).parent)
                candidates = ((path,) if path.name.endswith(".tex") else
                              (path.with_name(path.name + ".tex"), path))
                found = next((c for c in candidates if c.is_file()), None)
                if found:
                    pending.append((found, where))
                elif command == "include" or "/" in target:
                    scan.problems.append((where, f"\\{command}{{{target}}}: there is no file"
                                          f" {target}.tex in the project. Check the spelling"
                                          " and the folder.", False))
                    if command == "include":
                        scan.missing_includes.append((where, target))
            elif kind == 1:
                target = target.strip()
                if "\\" in target or "#" in target:
                    continue  # built from macros: not checked
                scan.assets.append((where, target, "graphic"))
            elif kind == 2:
                for one in target.split(","):
                    one = one.strip()
                    if command == "bibliography" and not one.endswith(".bib"):
                        one += ".bib"
                    if one and "\\" not in one and not re.match(r"[a-z]+://", one):
                        scan.assets.append((where, one, "bib"))
            else:
                for one in target.split(","):
                    one = one.strip()
                    extension = ".cls" if command in ("documentclass", "LoadClass", "LoadClassWithOptions") else ".sty"
                    local = (root / (one + extension)).resolve()
                    if one and local.is_file() and local.is_relative_to(root):
                        scan.assets.append((where, local.relative_to(root).as_posix(), "local"))
                        pending.append((local, where))
    resolved = []
    for where, target, kind in scan.assets:
        options = [target] if kind != "graphic" else [
            prefix + target + ext for prefix in graphics_dirs for ext in GRAPHIC_EXTENSIONS]
        found = next((o for o in options if (root / o).is_file()), None)
        if found:
            if (root / found).resolve().is_relative_to(root):
                resolved.append(found)
        else:
            scan.missing_assets.append((where, target, kind))
    scan.assets = sorted(set(resolved))
    return scan


def prepare_output(root, output):
    """Mirror \\include folders in the output folder, preventing first-pass
    .aux write errors. Returns (active .tex files, advice, scan), or None if
    the build cannot start: main.tex unreadable.
    """
    output.mkdir(parents=True, exist_ok=True)
    scan = active_sources(root)
    if any(stops for _, _, stops in scan.problems):
        for where, message, _ in scan.problems:
            print(f"{where}: {message}", file=sys.stderr)
        return None
    for folder in scan.include_dirs:
        try:
            (output / folder).mkdir(parents=True, exist_ok=True)
        except OSError:
            pass  # the scan is a guess; a real problem shows up in the build
    return scan.files, [f"{where}: {message}" for where, message, _ in scan.problems], scan


def unwrapped_log(output):
    """Join TeX's 79-byte log lines before decoding: a wrap may split UTF-8."""
    log = output / "main.log"
    if not log.is_file():
        return ""
    lines = log.read_bytes().splitlines()
    joined, index = [], 0
    while index < len(lines):
        line = lines[index]
        while len(lines[index]) == 79 and index + 1 < len(lines):
            index += 1
            line += lines[index]
        joined.append(line)
        index += 1
    return b"\n".join(joined).decode("utf-8", errors="replace")


def missing_chapters(scan, log_text, loaded=()):
    """\\include files that the document asks for and LaTeX could not find.
    The scan must say the file is missing, and LaTeX must have reported its
    omission or recorded it as an input on an earlier run. Existing logs and
    recorder files remain useful when latexmk has nothing to redo; a scanned
    include in an inactive conditional is not evidence of missing content.
    """
    logged = set(re.findall(r"No file ([^\r\n]+?\.tex)\.", log_text))
    active = logged | set(loaded)
    return sorted({target for _, target in scan.missing_includes
                   if target + ".tex" in active})


def recorded_inputs(root, output):
    """Project inputs from LaTeX's recorder, including paths containing spaces."""
    recorder = output / "main.fls"
    if not recorder.is_file():
        return set()
    loaded = set()
    for line in recorder.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("INPUT "):
            path = (root / line[6:]).resolve()
            if path.is_relative_to(root):
                loaded.add(path.relative_to(root).as_posix())
    return loaded


def layout_warnings(log_text):
    """Figures and tables LaTeX could not fit, with the file and line when known."""
    stack, found = [], []
    for line in log_text.splitlines():
        problem = re.search(r"Float too large for page by ([\d.]+pt)(?: on input line (\d+))?", line)
        if problem:
            where = next((name for name in reversed(stack) if name), "")
            place = ""
            if where:
                place = f"{where.removeprefix('./')}, line {problem[2]}: " if problem[2] else (
                    where.removeprefix("./") + ": ")
            elif problem[2]:
                place = f"line {problem[2]}: "
            found.append(
                f"{place}a figure or table is {problem[1]} too tall for a page, so it may be"
                " cut off or run into the margin (see build/main.log). Make it smaller, for"
                " example width=0.8\\linewidth or height=0.6\\textheight in \\includegraphics."
            )
        elif re.match(r"Overfull \\vbox \(.*too high\) has occurred while \\output is active", line):
            found.append(
                "a page holds more than fits (Overfull \\vbox while placing a figure or table,"
                " see build/main.log). Make the largest figure or table on that page smaller."
            )
        for token in re.finditer(r"\(([^\s()]*)|\)", line):
            if token[0] == ")":
                if stack:
                    stack.pop()
            else:
                stack.append(token[1] if token[1].endswith(".tex") else "")
    unique = []
    for item in found:
        if item not in unique:
            unique.append(item)
    return unique[:10]


SEAL_PAGE = "https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation"


def install_hint(missing):
    """One next step, for this operating system, when LaTeX tools are missing."""
    if sys.platform == "win32":
        drive = Path(os.environ.get("SystemDrive", "C:") + "\\")
        if list(drive.glob("texlive/*/bin/win*")):
            return (
                "TeX Live is installed, but this window cannot see it yet. Close every"
                " terminal and editor window and open them again; if that does not"
                " help, restart the computer."
            )
        return (
            "Install TeX Live (not MiKTeX): https://tug.org/texlive/windows.html"
            " Then close this window and open a new one."
        )
    if sys.platform == "darwin":
        if Path("/Library/TeX/texbin").is_dir():
            return (
                "MacTeX is installed, but this window cannot see it yet. Quit Terminal"
                " (or your editor) completely and open it again."
            )
        return "Install MacTeX: https://tug.org/mactex/ Then open a new Terminal window."
    if list(Path("/usr/local/texlive").glob("*/bin/*")):
        return (
            "TeX Live is in /usr/local/texlive but not on your PATH. Add its bin"
            " folder to PATH (https://tug.org/texlive/quickinstall.html), then open"
            " a new terminal."
        )
    engine_missing = [name for name in missing if name not in ("latexmk", "biber")]
    if shutil.which("apt-get"):
        if engine_missing:
            return (
                "Install LaTeX with this command:\n"
                "  sudo apt install texlive-full\n"
                "(it includes latexmk and biber)"
            )
        return "Install the missing tools with this command:\n  sudo apt install " + " ".join(missing)
    if shutil.which("dnf"):
        packages = [name for name in missing if name in ("latexmk", "biber")]
        if engine_missing:
            packages = ["texlive-scheme-full", "latexmk", "biber"]
        return "Install LaTeX with this command:\n  sudo dnf install " + " ".join(packages)
    return "Install TeX Live: https://tug.org/texlive/quickinstall.html"


def location_notes(root):
    """Warn about project folders that commonly break builds."""
    notes = []
    parts = root.parts
    # Windows Explorer opens files inside a ZIP from a folder such as Temp1_x.zip.
    if any(part.lower().endswith(".zip") for part in parts):
        notes.append(
            "This folder looks like a temporary copy opened from inside a ZIP file."
            " Extract the ZIP first (Windows: right-click it, Extract All) and work"
            " in the extracted folder, or your changes may be lost."
        )
    cloud = ("onedrive", "icloud drive", "mobile documents", "dropbox", "google drive",
             "cloudstorage")
    if any(part.lower().startswith(cloud) for part in parts):
        notes.append(
            "Your project is in a cloud-synced folder. That works, but set the folder"
            " to 'Always keep on this device' so LaTeX can read every file."
        )
    return notes


def valid_iso_date(value):
    """True for a real calendar date written YYYY-MM-DD."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def biber_warnings(output):
    """Biber warnings about dates or malformed fields, from main.blg."""
    blg = output / "main.blg"
    if not blg.is_file():
        return []
    found = []
    for line in blg.read_text(encoding="utf-8", errors="replace").splitlines():
        if "WARN" in line and re.search(r"(?i)date|invalid|malformed|ignor", line):
            text = re.sub(r"^.*?WARN\s*-\s*", "", line).strip()
            if text not in found:
                found.append(text)
    return ["Biber warning (see build/main.blg): " + text for text in found[:10]]


def presubmission_hints(root, output, sources=None, warnings=()):
    """Warn about common revision comments. Advice only; never fails a build.
    Returns the number of layout warnings (figures or tables that do not fit)."""
    log_text = unwrapped_log(output)
    layout = layout_warnings(log_text)
    hints = list(warnings) + layout + biber_warnings(output)
    hints += known_problem(log_text, "built", root)
    if "RPI seal not found" in log_text:
        hints.append(
            "The title page shows a placeholder box instead of the RPI seal. "
            "Download the seal from RPI's Thesis Preparation page (" + SEAL_PAGE
            + ") and save it as assets/rpi-seal.jpg; see assets/README.md."
        )
    if "Missing character:" in log_text:
        messages = re.findall(r"Missing character:([^!]*)(?:!|$)", log_text)
        codes = sorted(set(re.findall(r"U\+[0-9A-F]+", " ".join(messages))))
        detail = " (" + ", ".join(codes[:10]) + ")" if codes else ""
        hints.append(
            "Some characters are missing from your PDF" + detail + ". Search for "
            "'Missing character:' in build/main.log and check those places in the PDF. "
            "A different compile engine or a font with those characters may be needed; see "
            + guide(root, "troubleshooting") + "."
        )
    if "STIX Two Math font not found" in log_text:
        hints.append(
            "STIX Two Math font not found: some mathematical symbols may be blank. "
            "Update your full TeX Live installation, recompile, and check your equations; see "
            + guide(root, "troubleshooting") + "."
        )
    for bib in student_files(root, "*.bib"):
        text = bib.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"(?m)^[ \t]*%.*$", "", text)
        starts = list(re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text))
        for start, end in zip(starts, starts[1:] + [None]):
            entry = text[start.end() : end.start() if end else None]
            if not re.search(r"(?i)\burl\s*=", entry):
                continue
            line = text.count("\n", 0, start.start()) + 1
            where = f"{bib.relative_to(root)}, line {line}: entry '{start[2]}'"
            date = re.search(r"(?i)\burldate\s*=\s*(?:\{([^{}]*)\}|\"([^\"]*)\"|([^,\s}]+))", entry)
            if not date:
                hints.append(
                    f"{where} has a url but no access date. OGE requires one for every "
                    "URL. Add the line  urldate = {YYYY-MM-DD},  using the date you read "
                    "it (or delete the url line if it only repeats the entry's DOI)."
                )
                continue
            value = next(g for g in date.groups() if g is not None).strip()
            if not valid_iso_date(value):
                what = "an empty urldate" if not value else f"urldate = {{{value}}}"
                hints.append(
                    f"{where} has {what}. Write the access date as YYYY-MM-DD, for "
                    "example  urldate = {2026-10-15},  (not a month name); otherwise "
                    "biblatex cannot read it and the date is left out."
                )
    for tex in sources if sources is not None else student_files(root, "*.tex"):
        lines = read_source(tex).splitlines()
        for number, line in enumerate(lines, 1):
            if re.search(r"\\caption\s*\[", re.sub(r"(?<!\\)%.*", "", line)):
                hints.append(
                    f"{tex.relative_to(root)}, line {number}: \\caption[...] puts a "
                    "different, short caption in the list of tables or figures. "
                    "The list must match the caption word for word: delete [...]."
                )
    if "You have requested release" in log_text:
        hints.append(
            "Your LaTeX is older than this class needs (TeX Live " + str(MIN_TEXLIVE)
            + " or newer). Install a current TeX Live; see "
            + guide(root, "get-started") + "."
        )
    if re.search(r"You have requested,.*?\n.*?document class rpi-thesis", log_text):
        hints.append(
            "Your rpi-thesis.cls is older than your other starter files expect. Copy "
            "rpi-thesis.cls from the newest starter into this folder; see "
            + guide(root, "going-further") + " (Update the formatting safely)."
        )
    if hints:
        print(
            "\nPre-submission hints (your PDF was built; check these before submitting):"
        )
        for hint in hints:
            print("- " + hint)
    return len(layout)


def first_error(log_text):
    """The first error in a LaTeX log, as the lines a student needs: the
    message (file:N: ... with -file-line-error, or ! ...) up to and including
    the l.N line that shows where TeX stopped. Empty if none. The file can be
    any path LaTeX reads (C:/..., C:\\..., ./build/main.aux, .toc, .bbl).
    TeX's generic stop lines (Emergency stop, Fatal error) are reported only
    when no real error comes before them."""
    lines = log_text.splitlines()
    start = re.compile(r"^(?:(?:[A-Za-z]:)?[^:\s][^:]*\.\w+:\d+: |! )")
    generic = re.compile(r"Emergency stop|==> Fatal error occurred|job aborted")
    found = [index for index, line in enumerate(lines) if start.match(line)]
    real = [index for index in found if not generic.search(lines[index])]
    for index in (real or found)[:1]:
        block = lines[index:index + 12]
        for offset, part in enumerate(block):
            if re.match(r"l\.\d+", part):
                block = block[:offset + 2]  # l.N and the rest of that source line
                break
        # Drop TeX's generic help lines; keep the message and its place.
        noise = re.compile(r"See the .* (?:documentation|manual|Companion)|Type +H <return>"
                           r"|\s*\.\.\.\s*$|\s*$")
        return "\n".join(part for part in block if not noise.match(part))
    return ""


# latexmk's note that Biber failed in an earlier build and was not rerun.
BIBER_CACHED = re.compile(r"(?m)^\s*biber\b[^\n]*gave an error in previous invocation")


def biber_errors(output, since, latexmk_text=""):
    """ERROR lines from main.blg when Biber failed in this build, or when
    latexmk reports (in latexmk_text) that the failure from an earlier build
    still stands, so the older main.blg still applies."""
    blg = output / "main.blg"
    if not blg.is_file():
        return []
    if blg.stat().st_mtime < since and not BIBER_CACHED.search(latexmk_text):
        return []
    return [line for line in blg.read_text(encoding="utf-8", errors="replace").splitlines()
            if "ERROR - " in line][:10]


# Known problems: the one table of LaTeX messages and their fixes. build.py
# prints the matching ones after a build; the "Explain my error" page
# (docs/explain-my-error.md, site/explain/) gets the same table as JSON from
# scripts/build_site.py, so the two cannot drift. Each entry:
#   id        a short name, used by scripts/tests/test_explain.py
#   pattern   a regular expression that Python and JavaScript read the same
#             way (no (?P<...>), inline flags, \A or \Z)
#   when      where build.py looks: "failed" (a failed build's output),
#             "built" (the log of a build that made a PDF), or "any";
#             "page" for warnings only the page lists (build.py reports
#             layout in its own words, see layout_warnings)
#   message   the message as a student sees it, for the page's table
#   means     what it means, in plain words
#   fix       what to do, wherever you write
#   editor    optional: the same on your computer, in an editor
#   overleaf  optional: the same on Overleaf
#   guide     (guide page, section anchor, section name) with the details
COMMON = "Common messages, "
KNOWN_PROBLEMS = [
    {
        "id": "biber-mac", "pattern": "biber[^\\n]*\\blipo\\b|\\blipo\\b[^\\n]*biber", "when": "any",
        "message": "biber ... lipo (on a Mac)",
        "means": "Biber, the bibliography tool, could not start: older Mac builds of Biber"
                 " fail on newer macOS. Your thesis is fine.",
        "fix": "Update TeX Live, then compile again.",
        "editor": "On macOS (MacTeX), open TeX Live Utility and choose Update all packages,"
                  " or run 'sudo tlmgr update --self --all'. On Linux with apt, update with"
                  " your package manager, for example 'sudo apt update' then 'sudo apt upgrade'.",
        "overleaf": "Overleaf installs Biber for you; this message comes from a LaTeX"
                    " installation on a computer.",
        "guide": ("troubleshooting", "common-messages", COMMON + "Rare messages"),
    },
    {
        "id": "biblatex-version", "pattern": "biblatex control file version", "when": "any",
        "message": "Found biblatex control file version ..., expected version ...",
        "means": "This is most often a stale control file left by an earlier build.",
        "fix": "Do a clean recompile, then build again. If it still fails, Biber and"
               " biblatex come from different TeX installations or years: use one TeX"
               " distribution, update it completely, and make sure 'biber' is the one it installed.",
        "editor": "In VS Code, run LaTeX Workshop: Clean up auxiliary files; with the build"
                  " helper, python3 scripts/build.py --fresh.",
        "overleaf": "Open the Recompile menu and choose Recompile from scratch.",
        "guide": ("troubleshooting", "clean-recompile", "Clean recompile"),
    },
    {
        "id": "miktex-perl", "pattern": "script engine", "when": "any",
        "message": "latexmk: could not find the script engine 'perl'",
        "means": "latexmk needs Perl, which MiKTeX does not include.",
        "fix": "Install TeX Live instead (https://tug.org/texlive/), or install Perl and restart.",
        "guide": ("troubleshooting", "tools-and-installs", COMMON + "Tools and installs"),
    },
    {
        "id": "old-latex", "pattern": "You have requested release", "when": "any",
        "message": "You have requested release '...' of LaTeX",
        "means": "Your LaTeX is older than this class needs (TeX Live " + str(MIN_TEXLIVE)
                 + " or newer).",
        "fix": "Install a current TeX Live.",
        "overleaf": "Choose the newest TeX Live version in Overleaf's Settings, then recompile.",
        "guide": ("troubleshooting", "common-messages", COMMON + "Rare messages"),
    },
    {
        "id": "tool-missing",
        "pattern": r"(?:latexmk|pdflatex|xelatex|lualatex|biber)['\"]?(?::| is)? (?:command )?not"
                   r" (?:found|recognized)|command not found: (?:latexmk|pdflatex|xelatex|lualatex|biber)"
                   r"|spawn (?:latexmk|pdflatex|xelatex|lualatex|biber) ENOENT|Can't exec \"biber\"",
        "when": "any",
        "message": "latexmk, pdflatex, or biber not found, or spawn latexmk ENOENT",
        "means": "A LaTeX tool (latexmk, the engine, or Biber, the bibliography tool) is not"
                 " installed, or your editor started before the installation finished.",
        "fix": "Finish installing the full LaTeX distribution, then quit your editor completely"
               " and reopen it (on Windows, restart the computer if needed).",
        "overleaf": "Overleaf has every tool; this message comes from a LaTeX installation on a computer.",
        "guide": ("troubleshooting", "tools-and-installs", COMMON + "Tools and installs"),
    },
    {
        "id": "class-missing", "pattern": r"File `rpi-thesis\.cls' not found", "when": "failed",
        "message": "File `rpi-thesis.cls' not found",
        "means": "LaTeX cannot find the class file, so it is not compiling the starter's folder.",
        "fix": "Extract the whole ZIP and open the folder that contains main.tex.",
        "editor": "Open the folder itself (File, Open Folder in VS Code), not only main.tex.",
        "overleaf": "main.tex and rpi-thesis.cls must be at the top of the file list, not inside a folder.",
        "guide": ("troubleshooting", "setup-and-files", COMMON + "Setup and files"),
    },
    # The class's own messages (rpi-thesis.cls, section 10): settings in metadata.tex.
    {
        "id": "thesis-required",
        "pattern": r"rpi-thesis Error: (?:Missing \S+ in metadata\.tex|Blank committee member name"
                   r"|No committee members|Graduation year must have four digits)",
        "when": "failed",
        "message": "Missing title in metadata.tex (or author, department, year, a committee name, ...)",
        "means": "A required thesis setting in metadata.tex is empty or not in the expected form;"
                 " the message names it.",
        "fix": "Fill it in inside \\thesissetup{...} in metadata.tex: the year as four digits, such as"
               " 2027, and a name inside the braces of each \\committeemember line. Save and compile"
               " again. The Settings builder writes a complete block for you.",
        "editor": "Open metadata.tex. The line the log shows, often \\begin{document} in main.tex,"
                  " is only where LaTeX checked the settings.",
        "overleaf": "Open metadata.tex in the file list. The line the log shows, often"
                    " \\begin{document} in main.tex, is only where LaTeX checked the settings.",
        "guide": ("settings-builder", "settings-reference", "Settings builder, Settings reference"),
    },
    {
        "id": "thesis-chair", "pattern": "rpi-thesis Error: Committee chair is missing", "when": "failed",
        "message": "Committee chair is missing",
        "means": "No \\committeemember line is marked as the chair.",
        "fix": "Put [Chair] (or [Co-Chair]) on one \\committeemember line, spelled exactly so:"
               " [chair] is not recognized.",
        "editor": "Open metadata.tex. The line the log shows, often \\begin{document} in main.tex,"
                  " is only where LaTeX checked the settings.",
        "overleaf": "Open metadata.tex in the file list. The line the log shows, often"
                    " \\begin{document} in main.tex, is only where LaTeX checked the settings.",
        "guide": ("troubleshooting", "setup-and-files", COMMON + "Setup and files"),
    },
    {
        "id": "thesis-unknown",
        "pattern": r"rpi-thesis Error: (?:Unknown setting|Unknown degree choice|Unknown graduation month"
                   r"|Unsupported class option)",
        "when": "failed",
        "message": "Unknown setting \"...\", Unknown degree choice, or Unknown graduation month",
        "means": "A setting name or choice in metadata.tex is misspelled, or in the wrong case.",
        "fix": "Compare it with the settings table: names are lower case; degree is masters, doctoral,"
               " or engineering-doctorate; the month is May, August, or December. Keep"
               " \\documentclass{rpi-thesis} in main.tex without options.",
        "editor": "Open metadata.tex. The line the log shows, often \\begin{document} in main.tex,"
                  " is only where LaTeX checked the settings.",
        "overleaf": "Open metadata.tex in the file list. The line the log shows, often"
                    " \\begin{document} in main.tex, is only where LaTeX checked the settings.",
        "guide": ("going-further", "all-thesis-settings", "Going further, All thesis settings"),
    },
    {
        "id": "class-version", "pattern": r"version `[^']*' of document class rpi-thesis", "when": "any",
        "message": "You have requested ... version ... of document class rpi-thesis",
        "means": "Your rpi-thesis.cls is older than the rest of your starter files.",
        "fix": "Copy rpi-thesis.cls from the newest starter into your thesis folder, replacing the old one.",
        "guide": ("going-further", "update-the-formatting-safely", "Update the formatting safely"),
    },
    {
        "id": "seal-missing", "pattern": "rpi-thesis Warning: RPI seal not found", "when": "built",
        "message": "RPI seal not found, or a seal placeholder on the title page",
        "means": "The title page has a box where the seal goes, because the seal file is not in the"
                 " folder the settings name.",
        "fix": "Download the seal from RPI and save it as assets/rpi-seal.jpg, or set seal-file in"
               " metadata.tex to the file's name.",
        "guide": ("get-started", "add-the-rpi-seal-one-minute", "Get started, Add the RPI seal"),
    },
    {
        "id": "bbl-not-biblatex", "pattern": "not created by biblatex", "when": "any",
        "message": "File 'main.bbl' not created by biblatex",
        "means": "A bibliography file left from an earlier build, often one that used BibTeX or"
                 " natbib, is still in the folder.",
        "fix": "Do a clean recompile, then build again.",
        "editor": "In VS Code, run LaTeX Workshop: Clean up auxiliary files; with the build"
                  " helper, python3 scripts/build.py --fresh.",
        "overleaf": "Open the Recompile menu and choose Recompile from scratch.",
        "guide": ("troubleshooting", "clean-recompile", "Clean recompile"),
    },
    {
        # A missing graphic; a missing .sty, .cls, or .tex is another problem.
        "id": "figure-missing",
        "pattern": r"LaTeX Error: File `(?![^']*\.(?:sty|cls|tex)')[^']*' not found"
                   r"|pdftex\.def Error: File `[^']*' not found",
        "when": "failed",
        "message": "LaTeX Error: File `figures/...' not found",
        "means": "A figure file named in \\includegraphics is missing.",
        "fix": "Check the file name, capital letters, extension, and folder (figures/...).",
        "editor": "Compare the name in \\includegraphics with the file in the figures folder.",
        "overleaf": "Upload the picture into the figures folder in the file list, then"
                    " compare its name with the one in \\includegraphics.",
        "guide": ("troubleshooting", "setup-and-files", COMMON + "Setup and files"),
    },
    {
        "id": "package-missing", "pattern": r"LaTeX Error: File `[^']*\.sty' not found", "when": "failed",
        "message": "LaTeX Error: File `....sty' not found",
        "means": "A package named in \\usepackage is not installed, or its name is misspelled.",
        "fix": "Check the spelling in \\usepackage; if it is right, install the full LaTeX"
               " distribution or update it.",
        "overleaf": "Overleaf has nearly every package: check the spelling in \\usepackage.",
        "guide": ("troubleshooting", "tools-and-installs", COMMON + "Tools and installs"),
    },
    {
        "id": "tex-missing", "pattern": r"LaTeX Error: File `[^']*\.tex' not found|I can't find file `",
        "when": "failed",
        "message": "LaTeX Error: File `chapters/....tex' not found",
        "means": "A file named in \\include or \\input does not exist under that name.",
        "fix": "Check the file name and folder in the \\include or \\input line in main.tex:"
               " write it without .tex, with the same capital letters as the file.",
        "guide": ("troubleshooting", "setup-and-files", COMMON + "Setup and files"),
    },
    {
        "id": "undefined-command", "pattern": "Undefined control sequence", "when": "failed",
        "message": "Undefined control sequence",
        "means": "LaTeX does not know a command, usually because of a typo after a backslash,"
                 " such as \\parencit for \\parencite.",
        "fix": "Look at the end of the l. line: the last command there is the one LaTeX does"
               " not know. Correct its spelling, or load the package it comes from.",
        "guide": ("troubleshooting", "read-an-error-message", "Read an error message"),
    },
    {
        "id": "missing-dollar", "pattern": r"Missing \$ inserted", "when": "failed",
        "message": "Missing $ inserted",
        "means": "A math-only character or command, often an underscore _ or ^, is outside $...$.",
        "fix": "Write \\_ for an underscore in text, or put the math between $ signs.",
        "guide": ("troubleshooting", "layout-and-the-pdf", COMMON + "Layout and the PDF"),
    },
    {
        "id": "brace",
        "pattern": r"Runaway argument|File ended while scanning use of|Paragraph ended before \\\S+ was"
                   r" complete|Missing \} inserted|Extra \}, or forgotten",
        "when": "failed",
        "message": "Runaway argument, or a brace error",
        "means": "A { has no matching }, or there is one } too many.",
        "fix": "Check your last edit near the line shown for a missing or extra }.",
        "guide": ("troubleshooting", "layout-and-the-pdf", COMMON + "Layout and the PDF"),
    },
    {
        "id": "environment",
        "pattern": r"Environment \S+ undefined|\\begin\{[^}]*\} on input line \d+ ended by \\end",
        "when": "failed",
        "message": "Environment ... undefined, or \\begin{...} ended by \\end{...}",
        "means": "The name in \\begin{...} is misspelled, its package is not loaded, or a"
                 " \\begin{...} and its \\end{...} do not match.",
        "fix": "Check that each \\begin{name} has an \\end{name} with the same spelling,"
               " in the right order.",
        "guide": ("troubleshooting", "read-an-error-message", "Read an error message"),
    },
    {
        "id": "unicode-char", "pattern": r"Unicode character [^\n]*\s+not set up for use with LaTeX",
        "when": "failed",
        "message": "Unicode character ... not set up for use with LaTeX",
        "means": "pdfLaTeX cannot print one character in your text, often a symbol or letter pasted"
                 " from Word or the web. The message names it, and the l. line ends with it.",
        "fix": "Replace that character with a LaTeX command (for example $\\geq$ for the"
               " greater-than-or-equal sign), or compile with LuaLaTeX and check the PDF: its font"
               " must have the character.",
        "guide": ("going-further", "choose-a-compile-engine", "Going further, Choose a compile engine"),
    },
    {
        "id": "font-missing", "pattern": r'The font "[^"]*" cannot be found', "when": "failed",
        "message": "Package fontspec Error: The font \"...\" cannot be found",
        "means": "LuaLaTeX or XeLaTeX cannot find a font: the LaTeX installation is not the full one,"
                 " or a font name added in preamble.tex is misspelled.",
        "fix": "Install or update the full LaTeX distribution. If you named a font yourself,"
               " check its exact name, or remove that line to use the class's font.",
        "overleaf": "Choose the newest TeX Live version in Overleaf's Settings, then recompile.",
        "guide": ("troubleshooting", "tools-and-installs", COMMON + "Tools and installs"),
    },
    {
        "id": "alignment-tab", "pattern": "Misplaced alignment tab character &", "when": "failed",
        "message": "Misplaced alignment tab character &",
        "means": "An & is outside a table; most often a title in the .bib file contains &.",
        "fix": "Write it as \\&.",
        "guide": ("troubleshooting", "citations-and-references", COMMON + "Citations and references"),
    },
    {
        "id": "biber-not-run", "pattern": r"Please \(re\)run Biber", "when": "built",
        "message": "Please (re)run Biber on the file",
        "means": "The bibliography step has not run since your last change, so citations"
                 " show as keys in bold.",
        "fix": "Compile again.",
        "editor": "VS Code with the starter's settings runs Biber for you; in other editors"
                  " run the bibliography step yourself (Get started, Other editors).",
        "overleaf": "Recompile; Overleaf runs Biber for you.",
        "guide": ("troubleshooting", "citations-and-references", COMMON + "Citations and references"),
    },
    {
        "id": "undefined-reference",
        "pattern": r"Citation [`'][^']*' (?:on page \d+ )?undefined|Reference [`'][^']*'"
                   r" (?:on page \d+ )?undefined|There were undefined (?:references|citations)",
        "when": "built",
        "message": "Citation `...' undefined, or Reference `...' undefined",
        "means": "A citation or cross-reference is undefined: the PDF shows ?? or a citation"
                 " key in bold.",
        "fix": "Check that the key in \\parencite or \\ref matches references.bib or the"
               " \\label exactly, then build again.",
        "guide": ("troubleshooting", "citations-and-references", COMMON + "Citations and references"),
    },
    # Warnings the page lists under the first error (site/explain/core.js, NOTES).
    {
        "id": "rerun", "pattern": r"Label\(s\) may have changed|Rerun to get [a-z -]+ right", "when": "page",
        "message": "Label(s) may have changed. Rerun to get cross-references right",
        "means": "Numbers, references, or bookmarks changed in this run; the next compile settles them.",
        "fix": "Compile again.",
        "guide": ("troubleshooting", "citations-and-references", COMMON + "Citations and references"),
    },
    {
        "id": "missing-character", "pattern": "Missing character: There is no", "when": "page",
        "message": "Missing character: There is no ... in font ...",
        "means": "The font has no such character, so it is left out of the PDF.",
        "fix": "Use a LaTeX command for it (such as an accent command), or remove it. Check the"
               " PDF where it should appear.",
        "guide": ("troubleshooting", "layout-and-the-pdf", COMMON + "Layout and the PDF"),
    },
    {
        "id": "overfull", "pattern": r"Overfull \\[hv]box", "when": "page",
        "message": "Overfull \\hbox (...pt too wide)",
        "means": "Something is wider than the text area and sticks out into the margin: a long URL,"
                 " word, table, equation, or image.",
        "fix": "Find it in the PDF at the lines the log names, then resize or break it.",
        "guide": ("troubleshooting", "layout-and-the-pdf", COMMON + "Layout and the PDF"),
    },
    {
        "id": "underfull", "pattern": r"Underfull \\[hv]box", "when": "page",
        "message": "Underfull \\hbox (badness ...)",
        "means": "LaTeX stretched the spaces in a line or page, often after \\\\ or \\linebreak.",
        "fix": "Usually harmless. Look at those lines in the PDF; remove a manual line break if"
               " the spacing looks wrong.",
        "guide": ("troubleshooting", "layout-and-the-pdf", COMMON + "Layout and the PDF"),
    },
]


def matching_problems(text, when="failed"):
    """The KNOWN_PROBLEMS entries whose pattern is in text, for one build stage."""
    return [entry for entry in KNOWN_PROBLEMS
            if entry["when"] in (when, "any") and re.search(entry["pattern"], text)]


def known_problem(text, when="failed", root=ROOT):
    found = []
    for entry in matching_problems(text, when):
        page, _, section = entry["guide"]
        parts = [entry["means"], entry["fix"], entry.get("editor", "")]
        found.append(" ".join(part for part in parts if part)
                     + f" See {guide(root, page)} ({section}).")
    return found


def build(root=ROOT, engine="pdflatex", fresh=False, output=None):
    root = Path(root).resolve()
    output = Path(output).resolve() if output else root / "build"
    missing = [name for name in ("latexmk", engine, "biber") if not shutil.which(name)]
    if missing:
        print("Missing LaTeX tools: " + ", ".join(missing), file=sys.stderr)
        print("Next step: " + install_hint(missing), file=sys.stderr)
        print("Setup guide: " + guide(root, "get-started"), file=sys.stderr)
        return 2
    prepared = prepare_output(root, output)
    if prepared is None:
        return 2
    sources, warnings, scan = prepared
    command = [
        shutil.which("latexmk"),
        "-norc",
        ENGINES[engine],
        "-no-shell-escape",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        "-synctex=1",
        "-outdir=" + str(output),
    ]
    if fresh:
        command.append("-gg")
    command.append("main.tex")
    log = output / "build-command.log"
    started = time.time() - 2  # a little slack for coarse file-system clocks
    environment = os.environ.copy()
    if engine == "lualatex":
        # Lua's font loader must have a writable cache, including in restricted
        # environments. Keep it with other generated output, not system folders.
        cache = (
            output / "tex-cache"
            if output.is_relative_to(root)
            else root / "build/tex-cache"
        )
        cache.mkdir(parents=True, exist_ok=True)
        # Recent LuaTeX can reject absolute Lua writes with shell escape off.
        # A cache path relative to the project keeps those writes permitted.
        environment["TEXMFCACHE"] = cache.relative_to(root).as_posix()
    print(
        "Building main.tex. References and page numbers may need several passes.",
        flush=True,
    )
    with log.open("w", encoding="utf-8") as stream:
        result = subprocess.run(
            command, cwd=root, env=environment, stdout=stream, stderr=subprocess.STDOUT
        )
    if result.returncode:
        print("Build failed. The full output is in " + str(log), file=sys.stderr)
        print(
            "See " + guide(root, "troubleshooting")
            + ". Your source files have not been changed.",
            file=sys.stderr,
        )
        text = log.read_text(encoding="utf-8", errors="replace")
        main_log = output / "main.log"
        # The log is current if LaTeX ran now, or if latexmk reran nothing
        # because the same error stopped the previous build.
        fresh_log = main_log.is_file() and (
            main_log.stat().st_mtime >= started or "error in previous invocation" in text)
        error = first_error(unwrapped_log(output)) if fresh_log else ""
        if error:
            print("\nFirst error (from build/main.log):\n" + error, file=sys.stderr)
        biber = biber_errors(output, started, text)
        if biber:
            print("\nBiber failed (from build/main.blg):\n" + "\n".join(biber), file=sys.stderr)
        if not error and not biber:
            print("\n".join(text.splitlines()[-20:]), file=sys.stderr)
        for advice in known_problem(text + "\n" + error + "\n" + "\n".join(biber), "failed", root):
            print("\nLikely cause: " + advice, file=sys.stderr)
        for note in warnings:
            print("\nCheck: " + note, file=sys.stderr)
        for note in location_notes(root):
            print("\nNote: " + note, file=sys.stderr)
    else:
        log_text = unwrapped_log(output)
        absent = missing_chapters(scan, log_text, recorded_inputs(root, output))
        logged_missing = set(re.findall(r"No file ([^\r\n]+?\.tex)\.", log_text))
        known = {target + ".tex" for _, target in scan.missing_includes}
        for name in sorted(logged_missing - known):
            warnings.append(f"LaTeX could not find {name}, so it was left out of the PDF."
                            " Check the file name in the \\include or \\input line.")
        layout = presubmission_hints(root, output, sources, warnings)
        if absent:
            names = ", ".join(t + ".tex" for t in absent)
            if all(t + ".tex" in logged_missing for t in absent):
                message = (f"PDF built WITHOUT {names}: the file is missing, so that part of your"
                           " thesis is not in the PDF.")
            else:
                message = (f"Chapter source missing: {names}. The PDF may be from an earlier"
                           " compile and does not confirm the current source files.")
            print(
                "\n" + message + " Restore the file, or delete or comment out its"
                " \\include line in main.tex, then compile again.",
                file=sys.stderr,
            )
            return 1
        print("\nPDF ready: " + str(output / "main.pdf") + (
            " (check the layout hints above: a figure or table does not fit)" if layout else ""))
    return result.returncode


def doctor(engine):
    """Check that each tool exists and starts; print one next step if not."""
    print("Checking the LaTeX tools (Biber's first run can take a minute)...", flush=True)
    missing, working = [], True
    for tool in ("latexmk", engine, "biber"):
        path = shutil.which(tool)
        if not path:
            print(tool + ": MISSING")
            missing.append(tool)
            working = False
            continue
        # Run each tool once: an installed tool can still fail to start.
        try:
            check = subprocess.run(
                [path, "--version"], capture_output=True, text=True, errors="replace"
            )
        except OSError as error:
            working = False
            print(tool + ": " + path + " (cannot start: " + str(error) + ")")
            print("  Reinstall this tool for your operating system and processor, then check again.")
            continue
        output = check.stdout + check.stderr
        first = (check.stdout or check.stderr).strip().splitlines()[:1]
        if check.returncode:
            working = False
            print(tool + ": " + path + " (does not start)")
            for advice in known_problem(output):
                print("  " + advice)
            continue
        print(tool + ": " + path + (" (" + first[0] + ")" if first else ""))
        if tool != engine:
            continue
        year = re.search(r"TeX Live (\d{4})", output)
        if year and int(year[1]) < MIN_TEXLIVE:
            working = False
            print(
                "  This is TeX Live " + year[1] + "; the class needs TeX Live "
                + str(MIN_TEXLIVE) + " or newer. Install a current TeX Live."
            )
        elif "MiKTeX" in output:
            print("  MiKTeX found. This starter is tested with TeX Live; MiKTeX's"
                  " latexmk also needs Perl installed separately.")
    if missing:
        print("Next step: " + install_hint(missing))
    for note in location_notes(ROOT):
        print("Note: " + note)
    print("Setup guide: " + guide(ROOT, "get-started"))
    return 0 if working else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=ENGINES, default="pdflatex")
    parser.add_argument(
        "--fresh", action="store_true", help="Rebuild generated files from scratch"
    )
    parser.add_argument(
        "--doctor", action="store_true", help="Check tool availability without building"
    )
    args = parser.parse_args()
    if args.doctor:
        return doctor(args.engine)
    return build(engine=args.engine, fresh=args.fresh)


if __name__ == "__main__":
    sys.exit(main())
