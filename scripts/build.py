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
    skip = {"build", "dist", "output", "tmp", "reference", "_local", ".git"}
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


def active_sources(root, main="main.tex"):
    """Follow literal \\input{...} and \\include{...} lines from main.tex.

    Only the document being compiled is read, so unused drafts elsewhere in
    the folder cannot stop a build. Not followed: references built from
    macros, \\import, \\subfile, and files TeX finds in its own installation
    (such as \\input{glyphtounicode}). Returns (files, include_dirs,
    problems); each problem is (where, message, stops_build).
    """
    root = root.resolve()
    files, include_dirs, problems = [], set(), []
    pending, seen = [(root / main, "The project folder")], set()
    while pending:
        source, origin = pending.pop()
        if source in seen:
            continue  # already read; this also stops \\input cycles
        seen.add(source)
        name = source.relative_to(root).as_posix()
        try:
            text = read_source(source)
        except OSError:
            problems.append((origin, "cannot read " + name, source == root / main))
            continue
        files.append(source)
        for number, line in enumerate(text.splitlines(), 1):
            line = re.sub(r"(?<!\\)%.*", "", line)
            for command, target in re.findall(r"\\(input|include)\s*\{([^}]+)\}", line):
                target, where = target.strip(), f"{name}, line {number}"
                path = (root / target).resolve()
                if not path.is_relative_to(root):
                    # TeX may read a file outside the project, but an \\include
                    # also writes an .aux file there, which TeX refuses.
                    if command == "include":
                        problems.append((where, f"\\include{{{target}}} points outside"
                                         " the project folder. Move that file into the"
                                         " project.", True))
                    continue
                if command == "include":
                    include_dirs.add(Path(target).parent)
                candidates = (path.with_name(path.name + ".tex"), path)
                found = next((c for c in candidates if c.is_file()), None)
                if found:
                    pending.append((found, where))
                elif command == "include" or "/" in target:
                    problems.append((where, f"\\{command}{{{target}}}: there is no file"
                                     f" {target}.tex in the project. Check the spelling"
                                     " and the folder.", False))
    return files, include_dirs, problems


def prepare_output(root, output):
    """Mirror \\include folders in the output folder, preventing first-pass
    .aux write errors. Returns (active .tex files, warnings), or None if the
    build cannot start: main.tex unreadable, or an \\include outside the project.
    """
    output.mkdir(parents=True, exist_ok=True)
    files, include_dirs, problems = active_sources(root)
    if any(stops for _, _, stops in problems):
        for where, message, _ in problems:
            print(f"{where}: {message}", file=sys.stderr)
        return None
    for folder in include_dirs:
        (output / folder).mkdir(parents=True, exist_ok=True)
    return files, [f"{where}: {message}" for where, message, _ in problems]


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
    """Warn about common revision comments. Advice only; never fails a build."""
    hints = list(warnings) + biber_warnings(output)
    log = output / "main.log"
    log_text = ""
    if log.is_file():
        log_text = log.read_text(encoding="utf-8", errors="replace")
    if "RPI seal not found" in log_text:
        hints.append(
            "The title page shows a placeholder box instead of the RPI seal. "
            "Download the seal from RPI's Thesis Preparation page (" + SEAL_PAGE
            + ") and save it as assets/rpi-seal.jpg; see assets/README.md."
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
            + guide(root, "workflows") + " (Update the formatting safely)."
        )
    if hints:
        print(
            "\nPre-submission hints (your PDF was built; check these before submitting):"
        )
        for hint in hints:
            print("- " + hint)


# Known problems outside the thesis itself: (text to find, what to tell the student).
KNOWN_PROBLEMS = [
    (
        "lipo",
        "Biber, the bibliography tool, could not start: older Mac builds of Biber"
        " fail on newer macOS. Update TeX Live, then build again. On macOS"
        " (MacTeX), use TeX Live Utility, Update all packages, or run"
        " 'sudo tlmgr update --self --all'. On Linux with apt, update with your"
        " package manager, for example 'sudo apt update' then 'sudo apt upgrade'.",
    ),
    (
        "biblatex control file version",
        "This is most often a stale control file left by an earlier build. Clean"
        " compile first: python3 scripts/build.py --fresh (or your editor's clean"
        " command), then build again. If it still fails, Biber and biblatex come"
        " from different TeX installations or years: use one TeX distribution,"
        " update it completely, and make sure 'biber' is the one it installed.",
    ),
    (
        "script engine",
        "latexmk needs Perl, which MiKTeX does not include. Install TeX Live"
        " instead (https://tug.org/texlive/), or install Perl and restart.",
    ),
    (
        "You have requested release",
        "Your LaTeX is older than this class needs (TeX Live " + str(MIN_TEXLIVE)
        + " or newer). Install a current TeX Live.",
    ),
]


def known_problem(text):
    return [advice for pattern, advice in KNOWN_PROBLEMS if pattern in text]


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
    sources, warnings = prepared
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
        print("Build failed. Read the first error in " + str(log), file=sys.stderr)
        print(
            "See " + guide(root, "troubleshooting")
            + ". Your source files have not been changed.",
            file=sys.stderr,
        )
        text = log.read_text(encoding="utf-8", errors="replace")
        blg = output / "main.blg"
        if blg.exists():
            text += blg.read_text(encoding="utf-8", errors="replace")
        print("\n".join(text.splitlines()[-20:]), file=sys.stderr)
        for advice in known_problem(text):
            print("\nLikely cause: " + advice, file=sys.stderr)
        for note in warnings:
            print("\nCheck: " + note, file=sys.stderr)
        for note in location_notes(root):
            print("\nNote: " + note, file=sys.stderr)
    else:
        print("PDF ready: " + str(output / "main.pdf"))
        presubmission_hints(root, output, sources, warnings)
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
        check = subprocess.run(
            [path, "--version"], capture_output=True, text=True, errors="replace"
        )
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
