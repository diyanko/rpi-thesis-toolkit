#!/usr/bin/env python3
"""Compile the thesis locally; never install, upload, or publish anything."""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINES = {"pdflatex": "-pdf", "xelatex": "-xelatex", "lualatex": "-lualatex"}


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


def prepare_output(root, output):
    """Mirror include directories, preventing first-pass .aux write errors."""
    output.mkdir(parents=True, exist_ok=True)
    for source in student_files(root, "*.tex"):
        text = re.sub(r"(?m)(?<!\\)%.*$", "", source.read_text(encoding="utf-8"))
        for included in re.findall(r"\\include\s*\{([^}]+)\}", text):
            target = (output / Path(included).parent).resolve()
            if not target.is_relative_to(output.resolve()):
                raise ValueError("Chapter include paths must stay inside the project.")
            target.mkdir(parents=True, exist_ok=True)


SEAL_PAGE = "https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation"


def presubmission_hints(root, output):
    """Warn about common revision comments. Advice only; never fails a build."""
    hints = []
    log = output / "main.log"
    if log.is_file() and "RPI seal not found" in log.read_text(errors="replace"):
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
            if re.search(r"(?i)\burl\s*=", entry) and not re.search(
                r"(?i)\burldate\s*=", entry
            ):
                line = text.count("\n", 0, start.start()) + 1
                hints.append(
                    f"{bib.relative_to(root)}, line {line}: entry '{start[2]}' has a "
                    "url but no access date. OGE requires one for every URL. Add "
                    "the line  urldate = {YYYY-MM-DD},  using the date you read it "
                    "(or delete the url line if it only repeats the entry's DOI)."
                )
    for tex in student_files(root, "*.tex"):
        lines = tex.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines, 1):
            if re.search(r"\\caption\s*\[", re.sub(r"(?<!\\)%.*", "", line)):
                hints.append(
                    f"{tex.relative_to(root)}, line {number}: \\caption[...] puts a "
                    "different, short caption in the list of tables or figures. "
                    "The list must match the caption word for word: delete [...]."
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
        " fail on newer macOS. Update TeX Live (TeX Live Utility, Update all"
        " packages; or 'sudo tlmgr update --self --all'), then build again.",
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
        print(
            "See " + guide(root, "get-started")
            + "; install a full distribution and restart your terminal.",
            file=sys.stderr,
        )
        return 2
    prepare_output(root, output)
    command = [
        "latexmk",
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
        text = log.read_text(errors="replace")
        blg = output / "main.blg"
        if blg.exists():
            text += blg.read_text(errors="replace")
        print("\n".join(text.splitlines()[-20:]), file=sys.stderr)
        for advice in known_problem(text):
            print("\nLikely cause: " + advice, file=sys.stderr)
    else:
        print("PDF ready: " + str(output / "main.pdf"))
        presubmission_hints(root, output)
    return result.returncode


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
        tools = ("latexmk", args.engine, "biber")
        working = True
        for tool in tools:
            path = shutil.which(tool)
            if not path:
                print(tool + ": MISSING")
                working = False
                continue
            # Run each tool once: an installed tool can still fail to start.
            check = subprocess.run(
                [tool, "--version"], capture_output=True, text=True, errors="replace"
            )
            first = (check.stdout or check.stderr).strip().splitlines()[:1]
            if check.returncode:
                working = False
                print(tool + ": " + path + " (does not start)")
                for advice in known_problem(check.stdout + check.stderr):
                    print("  " + advice)
            else:
                print(tool + ": " + path + (" (" + first[0] + ")" if first else ""))
        print("Setup guide: " + guide(ROOT, "get-started"))
        return 0 if working else 2
    return build(engine=args.engine, fresh=args.fresh)


if __name__ == "__main__":
    sys.exit(main())
