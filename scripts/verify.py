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

A step whose tools are missing here (TeX Live, Pandoc, pypdf) is reported as
SKIP with the reason, not as a failure, so a new contributor without them can
still check guide and script changes; CI has every tool and runs them all.
Release mode, and any run on CI (GITHUB_ACTIONS or CI set to true), instead
fails when a needed tool is missing or a unit test skips itself. The unit-test
line counts tests run and skipped apart in every mode. Release mode also fails
when no Chrome or Chromium is found, because the layout sweep cannot run.
Where no browser can run (the CI container), set VERIFY_ALLOW_NO_BROWSER=1:
the sweep is then reported as SKIP, never as passed, and unit tests that need
a browser may skip, labelled "no browser, allowed in CI".

Each step's full output goes to build/verify/<step>.log; the screen shows one
line per step, and the summary line names what passed, what was skipped and
why, and what failed. CI runs the same command. Steps run with a fixed date,
time zone, and locale, so results do not depend on the machine. The full run
uses Python 3, TeX Live, Pandoc, and pypdf for the PDF checks (the script finds
.venv/bin/python, or tells you how to make it); the release sweep also needs
Chrome or Chromium.
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True  # importing the other scripts must not leave __pycache__
from common import ROOT, class_version, find_chrome, missing
from previews import missing_tools as missing_preview_tools
from site_checks import validate
LOGS = ROOT / "build" / "verify"
PY = sys.executable
ENV = dict(os.environ, SOURCE_DATE_EPOCH="1767225600", TZ="UTC", LC_ALL="C.UTF-8",
           PYTHONHASHSEED="0")
# The exact LaTeX Workshop recipe from .vscode/settings.json, run on a fresh copy.
EDITOR = ["latexmk", "-pdf", "-no-shell-escape", "-synctex=1", "-interaction=nonstopmode",
          "-halt-on-error", "-file-line-error", "-outdir=build", "main.tex"]
MISSING_INPUT = re.compile(r"No file .+\.(tex|bib)|File .[^ ]+. not found|Package biblatex Warning: File")
TEX = ("latexmk", "pdflatex", "lualatex", "xelatex", "biber")
# Release mode and CI fail on a missing tool instead of skipping (main sets it).
STRICT = {"on": False}


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


def unavailable(*tools, pypdf=False):
    """None when the tools are here, else a short reason such as
    'Pandoc not installed' or 'TeX Live and pypdf not installed'."""
    gone = missing(*tools)
    tex = [tool for tool in gone if tool in TEX]
    whole = tex and len(tex) == len([tool for tool in tools if tool in TEX])
    names = (["TeX Live" if whole else "TeX Live's " + ", ".join(tex)] if tex else []) + \
        ["Pandoc" if tool == "pandoc" else tool for tool in gone if tool not in TEX]
    if pypdf and not pypdf_python():
        names.append("pypdf")
    if not names:
        return None
    return " and ".join(names) + " not installed"


def skip(reason):
    """A step that cannot run here: SKIP, or FAIL in release mode and on CI."""
    if STRICT["on"]:
        return False, f"{reason}; this mode needs it"
    return None, f"{reason}; CI runs it"


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
    reason = unavailable("latexmk", "pdflatex", "biber")
    if reason:
        return skip(reason)
    return run("thesis", [PY, "scripts/build.py", "--fresh"])


def pdf_checks():
    reason = unavailable(*TEX, pypdf=True)
    if reason:
        return skip(reason + (" (python3 -m venv .venv && .venv/bin/pip install pypdf)"
                              if reason == "pypdf not installed" else ""))
    return run("pdf_checks", [pypdf_python(), "scripts/check.py"])


def regressions():
    reason = unavailable(*TEX)
    if reason:
        return skip(reason)
    return run("regressions", [pypdf_python() or PY, "scripts/regressions.py"])


def site(previews=True, publish=False):
    reason = unavailable("pandoc")
    if reason:
        return skip(reason)
    gaps = missing_preview_tools() if previews else []
    if gaps and STRICT["on"]:
        return False, ", ".join(gaps) + " not installed (page previews and cheat sheet); this mode needs it"
    command = [PY, "scripts/build_site.py"] + (["--previews"] if previews and not gaps else []) \
        + (["--publish"] if publish else [])
    ok, note = run("site_publish" if publish else "site", command)
    if ok and gaps:
        PARTIAL.append(f"site without page previews or cheat sheet ({', '.join(gaps)} not installed)")
        note = "no previews or cheat sheet: " + ", ".join(gaps) + " not installed; " + note
    return ok, note


# The ZIPs the package step wrote in this run, by kind. Later steps test exactly
# these, never "the newest-looking" file in dist/: old versions may remain there,
# and names do not sort by version (v0.9.0 sorts after v0.10.0).
PACKAGED = {}
# Steps that passed with a part left out, for the summary line.
PARTIAL = []


def current_zips(root=ROOT):
    """dist/ paths of this version's starter and Overleaf ZIPs, named from the
    \\ProvidesClass line of root/rpi-thesis.cls as scripts/package.py names them."""
    version = class_version(root)[0]
    return {kind: root / f"dist/rpi-thesis-{kind}-v{version}.zip" for kind in ("starter", "overleaf")}


def package_blocked():
    """Why the ZIPs cannot be made here (they hold the rendered guide, the
    compiled cheat sheet, and the sample pictures), or None."""
    reason = unavailable("pandoc", "pdflatex", "biber")
    if reason or STRICT["on"]:
        return reason
    gaps = missing_preview_tools()
    return ", ".join(gaps) + " not installed" if gaps else None


def package():
    PACKAGED.clear()
    reason = package_blocked()
    if reason:
        return skip(reason)
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
    reason = package_blocked() or unavailable("latexmk")
    if reason:
        return skip(reason)
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
    if not find_chrome():
        if os.environ.get("VERIFY_ALLOW_NO_BROWSER") == "1":
            return None, "no Chrome; layout NOT checked (VERIFY_ALLOW_NO_BROWSER=1)"
        return False, ("no Chrome or Chromium: install one or set CHROME=/path/to/chrome"
                       " (VERIFY_ALLOW_NO_BROWSER=1 skips the sweep where no browser can run)")
    return run("ui", [PY, "scripts/ui_check.py"])


# The skip reason of tests that need Chrome (scripts/tests/test_pdf_check.py).
BROWSER_SKIP = re.compile(r"no Chrome or Chromium")


def unit_test_result(text, exit_ok, strict, allow_no_browser):
    """(ok, note) for a `unittest -v` log: executed and skipped tests counted
    apart. In strict mode any skip fails, except tests that need a browser
    when allow_no_browser (VERIFY_ALLOW_NO_BROWSER=1) says none can run here."""
    ran = re.search(r"^Ran (\d+) tests? in", text, re.M)
    if not exit_ok or not ran or not int(ran[1]):
        return False, (f"{ran[1]} test(s) ran: " if ran else "") + (
            "failures, see build/verify/unit_tests.log" if ran and int(ran[1]) else "no tests ran")
    reasons = re.findall(r" \.\.\. skipped '(.*)'$", text, re.M)
    total = re.search(r"\bskipped=(\d+)", text)
    skipped = max(int(total[1]) if total else 0, len(reasons))
    browser = sum(1 for why in reasons if BROWSER_SKIP.search(why))
    other = skipped - browser
    counts = f"{int(ran[1]) - skipped} run, {skipped} skipped"
    whys = sorted({why for why in reasons if not BROWSER_SKIP.search(why)})
    if strict and other:
        return False, f"{counts}: this mode runs every test ({'; '.join(whys) or 'see the log'})"
    if strict and browser and not allow_no_browser:
        return False, (f"{counts}: no Chrome or Chromium; install one or set CHROME=/path/to/chrome"
                       " (VERIFY_ALLOW_NO_BROWSER=1 allows this where no browser can run)")
    if strict and browser:
        return True, f"{counts} (no browser, allowed in CI)"
    if skipped:
        whys = sorted(set(reasons)) or ["see the log"]
        return True, f"{counts} ({'; '.join(whys)})"
    return True, counts


def unit_tests():
    """Standard-library unit tests in scripts/tests/. Tests that need TeX Live
    or Chrome skip themselves when it is missing; strict mode fails on a skip."""
    ok, _ = run("unit_tests", [pypdf_python() or PY, "-B", "-m", "unittest", "discover", "-v",
                               "-s", "scripts/tests", "-p", "test_*.py"])
    text = (LOGS / "unit_tests.log").read_text(encoding="utf-8")
    return unit_test_result(text, ok, STRICT["on"],
                            os.environ.get("VERIFY_ALLOW_NO_BROWSER") == "1")


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


def strict_mode(mode):
    """Release mode and CI (GitHub Actions sets both variables) fail on a
    missing tool or a skipped test instead of skipping."""
    return mode == "release" or "true" in (os.environ.get("GITHUB_ACTIONS"), os.environ.get("CI"))


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
    STRICT["on"] = strict_mode(args.mode)
    passed, failed, skipped, start = [], [], {}, time.time()
    steps = [entry if isinstance(entry, list) else [entry] for entry in MODES[args.mode]]
    done = 0
    for group in steps:
        with ThreadPoolExecutor(max_workers=len(group)) as pool:
            results = list(pool.map(lambda item: timed(item[1]), group))
        done += 1
        for (name, _), (ok, note, seconds) in zip(group, results):
            mark = "SKIP" if ok is None else "PASS" if ok else "FAIL"
            print(f"{mark}  {name:<14} {seconds:6.1f}s  {note}"[:160], flush=True)
            if ok is None:
                skipped.setdefault(note, []).append(name)
            else:
                (passed if ok else failed).append(name)
        if failed and not args.keep_going:
            break
    not_run = [name for group in steps[done:] for name, _ in group]
    print(f"verify {args.mode}: {summary(passed, failed, skipped, not_run)} in {time.time() - start:.0f}s"
          " (logs: build/verify/)")
    sys.exit(1 if failed else 0)


def summary(passed, failed, skipped, not_run):
    """One line: what failed, what passed, and what was skipped and why."""
    parts = ["FAILED " + ", ".join(failed)] if failed else []
    if passed:
        parts.append(", ".join(passed) + " passed")
    parts += PARTIAL
    parts += [", ".join(names) + f" skipped ({reason})" for reason, names in skipped.items()]
    if not_run:
        parts.append(", ".join(not_run) + " not run")
    return "; ".join(parts) or "nothing ran"


if __name__ == "__main__":
    main()
