#!/usr/bin/env python3
"""Run every maintainer check in one fixed order and print a short summary.

    python3 scripts/verify.py           picks quick or full from the files
                                        changed since main (the usual way)
    python3 scripts/verify.py quick     guide or website text (seconds)
    python3 scripts/verify.py full      thesis, PDF checks, regressions,
                                        website, ZIPs, archive compiles
    python3 scripts/verify.py release   full + strict publish build, browser
                                        layout sweep, reproducible-ZIP check

Each step's full output goes to build/verify/<step>.log; the screen shows one
line per step. CI runs the same command, so a local pass means a CI pass.
Steps run with a fixed date, time zone, and locale, so results do not depend on
the machine. Needs Python 3, TeX Live, Pandoc, and pypdf for the PDF checks
(the script finds .venv/bin/python, or tells you how to make it).
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


def git(*args):
    # CI containers check out as another user; trust this checkout explicitly.
    return subprocess.run(["git", "-c", f"safe.directory={ROOT}", *args], cwd=ROOT,
                          capture_output=True, text=True)


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


def package():
    return run("package", [PY, "scripts/package.py"])


def archives():
    """Extract both ZIPs into empty folders and compile them the way students will."""
    zips = {kind: sorted(ROOT.glob(f"dist/rpi-thesis-{kind}-v*.zip")) for kind in ("starter", "overleaf")}
    if not all(zips.values()):
        return False, "no ZIPs in dist/ (run the package step)"
    log = []
    with tempfile.TemporaryDirectory() as work:
        for kind, command, out in (("starter", EDITOR, "build"),
                                   ("overleaf", ["latexmk", "-pdf", "-interaction=nonstopmode",
                                                 "-halt-on-error", "main.tex"], ".")):
            folder = Path(work) / kind
            with zipfile.ZipFile(zips[kind][-1]) as archive:
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
    return True, f"both ZIPs compile fresh; offline guide {pages} pages clean"


def reproducible():
    """Package twice; the ZIPs must be byte-identical."""
    def digest():
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob("dist/*.zip"))}
    first = digest()
    ok, note = package()
    if not ok:
        return False, note
    return (first == digest(), "ZIPs byte-identical across builds" if first == digest()
            else "ZIPs differ between two builds of the same sources")


def ui():
    if not (ROOT / "scripts/ui_check.py").exists():
        return None, "scripts/ui_check.py not present"
    ok, note = run("ui", [PY, "scripts/ui_check.py"])
    return (None if note.startswith("SKIP") else ok), note


# A list inside a mode runs its steps at the same time (they use separate folders).
MODES = {
    "quick": [("hygiene", hygiene), ("site", lambda: site(previews=False))],
    "full": [("hygiene", hygiene), ("thesis", thesis),
             [("pdf checks", pdf_checks), ("regressions", regressions)],
             ("site", site), ("package", package), ("archives", archives)],
}
MODES["release"] = MODES["full"] + [("publish build", lambda: site(publish=True)),
                                    ("reproducible", reproducible), ("ui sweep", ui)]


# Changes that only touch these can skip the LaTeX steps.
QUICK_ONLY = re.compile(r"(docs/(?!diagrams/).*\.md|[^/]+\.md|site/.*|\.github/(ISSUE_TEMPLATE/.*|pull_request_template\.md))$")


def auto_mode():
    """quick when every file changed since main (committed or not) is guide or
    website text; full otherwise, or when git cannot tell."""
    base = git("merge-base", "HEAD", "origin/main")
    if base.returncode:
        base = git("merge-base", "HEAD", "main")
    if base.returncode:
        return "full", "no main branch to compare with"
    changed = set(git("diff", "--name-only", base.stdout.strip()).stdout.split())
    changed |= set(git("ls-files", "--others", "--exclude-standard").stdout.split())
    slow = sorted(f for f in changed if not QUICK_ONLY.match(f))
    if slow:
        return "full", f"{len(slow)} changed file(s) need it, e.g. {slow[0]}"
    return "quick", f"{len(changed)} changed file(s), all guide or website text"


def timed(step):
    began = time.time()
    ok, note = step()
    return ok, note, time.time() - began


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("mode", nargs="?", default="auto", choices=["auto", *MODES])
    parser.add_argument("--keep-going", action="store_true", help="run every step even after a failure")
    args = parser.parse_args()
    LOGS.mkdir(parents=True, exist_ok=True)
    if args.mode == "auto":
        args.mode, why = auto_mode()
        print(f"verify {args.mode}: {why}", flush=True)
    failed, start = [], time.time()
    for entry in MODES[args.mode]:
        group = entry if isinstance(entry, list) else [entry]
        with ThreadPoolExecutor(max_workers=len(group)) as pool:
            results = list(pool.map(lambda item: timed(item[1]), group))
        for (name, _), (ok, note, seconds) in zip(group, results):
            mark = "SKIP" if ok is None else "PASS" if ok else "FAIL"
            print(f"{mark}  {name:<14} {seconds:6.1f}s  {note}"[:160], flush=True)
            if ok is False:
                failed.append(name)
        if failed and not args.keep_going:
            break
    total = time.time() - start
    print(f"verify {args.mode}: {'FAILED ' + ', '.join(failed) if failed else 'all passed'} "
          f"in {total:.0f}s (logs: build/verify/)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
