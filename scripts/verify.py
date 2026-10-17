#!/usr/bin/env python3
"""Run every maintainer check in one fixed order and print a short summary.

    python3 scripts/verify.py           auto: quick or full, from the files
                                        changed since main (see below)
    python3 scripts/verify.py quick     guide or website text (seconds)
    python3 scripts/verify.py full      thesis, PDF checks, regressions, unit
                                        tests, website, ZIPs, archive compiles
    python3 scripts/verify.py release   full + strict publish build, browser
                                        layout sweep, reproducible-ZIP check

Auto mode compares this checkout (committed, staged, unstaged, and untracked
files) with its merge base with origin/main, or main. It picks quick only when
something changed and every changed file is guide or website text. It picks
full when anything else changed, when nothing changed (a clean checkout, as on
a new machine: the run then tests this computer's TeX setup, which quick would
not), and whenever a git command fails. Name a mode to choose it yourself.

Release mode fails when no Chrome or Chromium is found, because the layout
sweep cannot run. Where no browser can run (the CI container), set
VERIFY_ALLOW_NO_BROWSER=1: the sweep is then reported as SKIP, never as passed.

Each step's full output goes to build/verify/<step>.log; the screen shows one
line per step, and the summary names any skipped step. CI runs the same
command. Steps run with a fixed date, time zone, and locale, so results do not
depend on the machine. Needs Python 3, TeX Live, Pandoc, and pypdf for the PDF
checks (the script finds .venv/bin/python, or tells you how to make it); the
release sweep also needs Chrome or Chromium.
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True  # importing build_site must not leave __pycache__
LOGS = ROOT / "build" / "verify"
PY = sys.executable
ENV = dict(os.environ, SOURCE_DATE_EPOCH="1767225600", TZ="UTC", LC_ALL="C.UTF-8",
           PYTHONHASHSEED="0")
# The exact LaTeX Workshop recipe from .vscode/settings.json, run on a fresh copy.
EDITOR = ["latexmk", "-pdf", "-no-shell-escape", "-synctex=1", "-interaction=nonstopmode",
          "-halt-on-error", "-file-line-error", "-outdir=build", "main.tex"]
MISSING_INPUT = re.compile(r"No file .+\.(tex|bib)|File .[^ ]+. not found|Package biblatex Warning: File")


def run(step, command, cwd=ROOT, env=None):
    """Run a command, log its output, and return (ok, last useful line)."""
    LOGS.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(command, cwd=cwd, env=env or ENV, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (LOGS / f"{step}.log").write_text(result.stdout, encoding="utf-8")
    lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
    useful = [l for l in lines if re.search(r"PASS|FAIL|passed|failed|[Ee]rror|archive|PDF ready", l)]
    return result.returncode == 0, ((useful or lines or [""])[-1]).strip()


def git(*args, cwd=ROOT):
    """Run git; a missing git counts as a failed command (exit 127)."""
    # CI containers check out as another user; trust this checkout explicitly.
    try:
        return subprocess.run(["git", "-c", f"safe.directory={cwd}", *args], cwd=cwd,
                              capture_output=True, text=True)
    except OSError as error:
        return subprocess.CompletedProcess(args, 127, "", str(error))


def pypdf_python():
    for candidate in (os.environ.get("VERIFY_PYTHON"), str(ROOT / ".venv/bin/python"), PY):
        if candidate and Path(candidate).exists() and subprocess.run(
                [candidate, "-c", "import pypdf"], capture_output=True).returncode == 0:
            return candidate
    return None


# ---- steps: each returns (ok, note); ok None means skipped ------------------

def hygiene():
    """Whitespace, emoji, local paths, and files that must never be tracked."""
    problems = []
    if not (ROOT / ".git").exists():
        return None, "not a git checkout"
    check = git("diff", "--check", "HEAD")
    if check.returncode >= 128:
        return False, "git failed: " + check.stderr.strip()[:120]
    if check.returncode:
        problems.append("trailing whitespace or conflict markers: " + check.stdout.strip()[:120])
    tracked = git("ls-files").stdout.split()
    tracked += git("ls-files", "--others", "--exclude-standard").stdout.split()  # new, not yet committed
    forbidden = [f for f in tracked if f.startswith(("_local/", "build/", "dist/", ".claude/", ".codex/"))
                 or re.match(r"assets/rpi-seal\.", f)]
    if forbidden:
        problems.append("tracked but private or generated: " + ", ".join(forbidden[:5]))
    emoji = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]")
    local = re.compile(r"/Users/[A-Za-z]|/home/[a-z]|[A-Z]:\\Users\\|/private/tm[p]/")
    for name in tracked:
        path = ROOT / name
        if path.suffix.lower() in {".png", ".jpg", ".pdf", ".woff2", ".zip", ".webp"} or not path.is_file():
            continue
        if name.startswith("site/pdf-check/pdfjs/"):  # vendored pdf.js, unchanged from its release
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if emoji.search(text):
            problems.append(f"emoji in {name}")
        if local.search(text):
            problems.append(f"local path in {name}")
    (LOGS / "hygiene.log").write_text("\n".join(problems) or "clean", encoding="utf-8")
    return not problems, problems[0] if problems else f"{len(tracked)} tracked files clean"


def thesis():
    return run("thesis", [PY, "scripts/build.py", "--fresh"])


def pdf_checks():
    python = pypdf_python()
    if not python:
        return False, "pypdf missing: python3 -m venv .venv && .venv/bin/pip install pypdf"
    return run("pdf_checks", [python, "scripts/check.py"])


def regressions():
    if not (ROOT / "scripts/regressions.py").exists():
        return None, "scripts/regressions.py not present"
    python = pypdf_python() or PY
    return run("regressions", [python, "scripts/regressions.py"])


def site(previews=True, publish=False):
    command = [PY, "scripts/build_site.py"] + (["--previews"] if previews else []) + (["--publish"] if publish else [])
    return run("site_publish" if publish else "site", command)


# The ZIPs the package step wrote in this run, by kind. Later steps test exactly
# these, never "the newest-looking" file in dist/: old versions may remain there,
# and names do not sort by version (v0.9.0 sorts after v0.10.0).
PACKAGED = {}


def current_zips(root=ROOT):
    """dist/ paths of this version's starter and Overleaf ZIPs, named from the
    \\ProvidesClass line of root/rpi-thesis.cls as scripts/package.py names them."""
    text = (root / "rpi-thesis.cls").read_text(encoding="utf-8")
    match = re.search(r"\\ProvidesClass\{rpi-thesis\}\[\d{4}/\d\d/\d\d v([\w.-]+)", text)
    if not match:
        raise SystemExit("rpi-thesis.cls: no version in the \\ProvidesClass line")
    return {kind: root / f"dist/rpi-thesis-{kind}-v{match[1]}.zip" for kind in ("starter", "overleaf")}


def package():
    PACKAGED.clear()
    began = time.time()
    ok, note = run("package", [PY, "scripts/package.py"])
    if not ok:
        return ok, note
    zips = current_zips()
    # 2 s of slack for file systems with coarse timestamps.
    stale = [p.name for p in zips.values() if not p.is_file() or p.stat().st_mtime < began - 2]
    if stale:
        return False, "package.py did not write " + ", ".join(stale) + " in this run"
    PACKAGED.update(zips)
    return True, note


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archives():
    """Extract this run's two ZIPs into empty folders and compile them the way students will."""
    if not PACKAGED:
        return False, "no ZIPs from this run's package step to test"
    zips = dict(PACKAGED)
    log = [f"{p.name} sha256 {sha(p)}" for p in zips.values()]
    with tempfile.TemporaryDirectory() as work:
        for kind, command, out in (("starter", EDITOR, "build"),
                                   ("overleaf", ["latexmk", "-pdf", "-interaction=nonstopmode",
                                                 "-halt-on-error", "main.tex"], ".")):
            folder = Path(work) / kind
            with zipfile.ZipFile(zips[kind]) as archive:
                archive.extractall(folder)
            env = dict(ENV, HOME=str(folder))  # no personal ~/.latexmkrc
            result = subprocess.run(command, cwd=folder, env=env, capture_output=True, text=True)
            log.append(f"== {kind}: exit {result.returncode}\n{result.stdout[-3000:]}")
            pdf, tex_log = folder / out / "main.pdf", folder / out / "main.log"
            if result.returncode or not pdf.is_file():
                (LOGS / "archives.log").write_text("\n".join(log), encoding="utf-8")
                return False, f"{kind} ZIP does not compile on the first run"
            missing = MISSING_INPUT.findall(tex_log.read_text(encoding="utf-8", errors="replace"))
            if missing:
                (LOGS / "archives.log").write_text("\n".join(log), encoding="utf-8")
                return False, f"{kind} ZIP builds without a file main.tex asks for"
        sys.path.insert(0, str(ROOT / "scripts"))
        from build_site import validate
        errors, warnings, pages = validate(Path(work) / "starter" / "guide",
                                           beside=("rpi-thesis-cheatsheet.pdf",))
        if errors or warnings:
            log += errors + warnings
            (LOGS / "archives.log").write_text("\n".join(log), encoding="utf-8")
            return False, f"offline guide: {(errors + warnings)[0]}"
    (LOGS / "archives.log").write_text("\n".join(log), encoding="utf-8")
    return True, (f"{zips['starter'].name} and {zips['overleaf'].name} compile fresh;"
                  f" offline guide {pages} pages clean")


def reproducible():
    """Package again; this run's two ZIPs must come out byte-identical."""
    if not PACKAGED:
        return False, "no ZIPs from this run's package step to compare"
    first = {kind: sha(path) for kind, path in PACKAGED.items()}
    ok, note = package()
    if not ok:
        return False, note
    differ = [PACKAGED[kind].name for kind in first if sha(PACKAGED[kind]) != first[kind]]
    if differ:
        return False, "differ between two builds of the same sources: " + ", ".join(differ)
    return True, " and ".join(p.name for p in PACKAGED.values()) + " byte-identical across two builds"


def ui():
    """Browser layout sweep. Only release mode runs it, so a missing browser
    fails unless VERIFY_ALLOW_NO_BROWSER=1 says no browser can run here."""
    if not (ROOT / "scripts/ui_check.py").exists():
        return False, "scripts/ui_check.py not present"
    ok, note = run("ui", [PY, "scripts/ui_check.py"])
    if not note.startswith("SKIP"):
        return ok, note
    if os.environ.get("VERIFY_ALLOW_NO_BROWSER") == "1":
        return None, "no Chrome; layout NOT checked (VERIFY_ALLOW_NO_BROWSER=1)"
    return False, ("no Chrome or Chromium: install one or set CHROME=/path/to/chrome"
                   " (VERIFY_ALLOW_NO_BROWSER=1 skips the sweep where no browser can run)")


def unit_tests():
    """Standard-library unit tests in scripts/test_*.py, when there are any."""
    if not sorted((ROOT / "scripts").glob("test_*.py")):
        return None, "no scripts/test_*.py files"
    ok, note = run("unit_tests", [pypdf_python() or PY, "-B", "-m", "unittest", "discover",
                                  "-s", "scripts", "-p", "test_*.py"])
    text = (LOGS / "unit_tests.log").read_text(encoding="utf-8")
    ran = re.search(r"Ran (\d+) tests? in", text)
    if ok and ran and int(ran[1]):
        skipped = re.search(r"\bskipped=(\d+)", text)
        return True, (f"{ran[1]} unit test(s) ran, {skipped[1]} skipped" if skipped
                      else f"{ran[1]} unit test(s) passed")
    return False, (f"{ran[1]} test(s) ran: " if ran else "") + note


# A list inside a mode runs its steps at the same time (they use separate folders).
MODES = {
    "quick": [("hygiene", hygiene), ("site", lambda: site(previews=False))],
    "full": [("hygiene", hygiene), ("thesis", thesis),
             [("pdf checks", pdf_checks), ("regressions", regressions)],
             ("unit tests", unit_tests),
             ("site", site), ("package", package), ("archives", archives)],
}
MODES["release"] = MODES["full"] + [("publish build", lambda: site(publish=True)),
                                    ("reproducible", reproducible), ("ui sweep", ui)]


# Changes that only touch these can skip the LaTeX steps ...
QUICK_ONLY = re.compile(r"(docs/(?!diagrams/).*\.md|[^/]+\.md|site/.*|\.github/(ISSUE_TEMPLATE/.*|pull_request_template\.md))$")
# ... except guide pages that full-mode steps compile: the class-alone recipe
# (regressions.py) and the class-swap example (page previews, skipped in quick).
NEEDS_FULL = {"docs/bring-your-draft.md", "docs/how-it-works.md"}


def auto_mode(root=ROOT):
    """Return (mode, reason): quick only when something changed and all of it is
    guide or website text; full otherwise, on a clean tree, or when git fails."""
    def names(*args):
        result = git(*args, cwd=root)
        if result.returncode:
            raise RuntimeError(f"git {args[0]} failed: " + (result.stderr.strip() or "no message")[:100])
        return {name for name in result.stdout.split("\0") if name}

    for ref in ("origin/main", "main"):
        base = git("merge-base", "HEAD", ref, cwd=root)
        if base.returncode == 0:
            break
    else:
        return "full", "git cannot compare with main (no checkout, no main branch, or no git)"
    try:
        base = base.stdout.strip()
        # --no-renames lists both sides of a rename, so a moved script still counts.
        changed = names("diff", "--name-only", "--no-renames", "-z", base)  # committed + unstaged
        changed |= names("diff", "--cached", "--name-only", "--no-renames", "-z", base)  # staged
        changed |= names("ls-files", "--others", "--exclude-standard", "-z")  # untracked
    except RuntimeError as error:
        return "full", str(error)
    if not changed:
        return "full", "nothing changed since main, so check the whole setup"
    slow = sorted(f for f in changed if f in NEEDS_FULL or not QUICK_ONLY.match(f))
    if slow:
        return "full", f"{len(slow)} changed file(s) need it, e.g. {slow[0]}"
    return "quick", f"{len(changed)} changed file(s), all guide or website text"


def timed(step):
    began = time.time()
    ok, note = step()
    return ok, note, time.time() - began


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", nargs="?", default="auto", choices=["auto", *MODES])
    parser.add_argument("--keep-going", action="store_true", help="run every step even after a failure")
    args = parser.parse_args()
    LOGS.mkdir(parents=True, exist_ok=True)
    if args.mode == "auto":
        args.mode, why = auto_mode()
        print(f"verify {args.mode}: {why}", flush=True)
    failed, skipped, start = [], [], time.time()
    for entry in MODES[args.mode]:
        group = entry if isinstance(entry, list) else [entry]
        with ThreadPoolExecutor(max_workers=len(group)) as pool:
            results = list(pool.map(lambda item: timed(item[1]), group))
        for (name, _), (ok, note, seconds) in zip(group, results):
            mark = "SKIP" if ok is None else "PASS" if ok else "FAIL"
            print(f"{mark}  {name:<14} {seconds:6.1f}s  {note}"[:160], flush=True)
            if ok is False:
                failed.append(name)
            elif ok is None:
                skipped.append(name)
        if failed and not args.keep_going:
            break
    total = time.time() - start
    result = ("FAILED " + ", ".join(failed) if failed
              else f"passed, {len(skipped)} skipped ({', '.join(skipped)})" if skipped
              else "all passed")
    print(f"verify {args.mode}: {result} in {total:.0f}s (logs: build/verify/)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
