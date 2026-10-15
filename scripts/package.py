#!/usr/bin/env python3
"""Make the student starter ZIP in dist/: thesis files plus the offline guide.

    python3 scripts/package.py

Needs Pandoc (the guide is rendered by build_site.py). Nothing is uploaded.
A release needs a current cheat sheet and current sample-thesis pictures: run
build_site.py --previews (needs TeX) first. The guide must be complete (every page
and picture); for a quick local test that tolerates gaps, add --dev.
"""
import argparse
from pathlib import Path
import json
import re
import tempfile
import zipfile

from build import active_sources
from build_site import OFFLINE_CHEATSHEET, ROOT, build_site, class_version

# Everything a student needs, and nothing for maintainers (no AGENTS.md,
# CLAUDE.md, site tooling, docs/ Markdown, or docs/project/). RPI's seal and
# original template are never included: assets/README.md tells each student
# where to download the seal.
FILES = [
    "main.tex",
    "metadata.tex",
    "preamble.tex",
    "rpi-thesis.cls",
    "references.bib",
    "frontmatter/abstract.tex",
    "frontmatter/acknowledgments.tex",
    "chapters/01-introduction.tex",
    "chapters/02-research.tex",
    "chapters/03-conclusion.tex",
    "appendices/additional-material.tex",
    "figures/README.md",
    "assets/README.md",
    "scripts/build.py",
    "latexmkrc",
    ".vscode/settings.json",
    ".vscode/extensions.json",
    "LICENSE.md",
]
NOT_FOR_STUDENTS = (
    "AGENTS.md", "CLAUDE.md", "docs/", "site/", "reference/", "_local/", "build/", "dist/",
    "assets/rpi-seal",
)
# The printable cheat sheet, once build_site.py --previews or --cheatsheet has
# compiled it.
# It is the only PDF allowed in the ZIP.
CHEATSHEET = "dist/site/downloads/rpi-thesis-cheatsheet.pdf"
CHEATSHEET_NAME = OFFLINE_CHEATSHEET  # beside guide/; the offline guide links to it
STUDENT_GITIGNORE = """\
# Files LaTeX makes while compiling. They are rebuilt every time.
/build/
*.aux
*.bbl
*.bcf
*.blg
*.fdb_latexmk
*.fls
*.lof
*.lot
*.log
*.out
*.run.xml
*.synctex.gz
*.toc
*.xdv
# A PDF compiled next to main.tex. PDFs in figures/ are kept.
/*.pdf
.DS_Store
__pycache__/
# RPI's seal belongs to RPI; keep it out of shared repositories. In a private
# repository you may delete this line to keep the seal with your project.
/assets/rpi-seal.*
"""
# The repository README links to docs/ Markdown, which the ZIP leaves out.
STUDENT_README = """\
# RPI Thesis Toolkit: starter files

1. Open START-HERE.html in a web browser. The guide works offline.
2. Compile main.tex once to see the sample PDF with a seal placeholder.
3. Add the RPI seal: see assets/README.md.
4. Put your details in metadata.tex, then write in chapters/.

Formatting lives in rpi-thesis.cls. To update the formatting later, follow
"Update the formatting safely" in the guide (workflows page). During the beta,
a new version can change more than that one file; its changelog lists every
other edit to make.

This is an unofficial, community-made starter. It is not affiliated with or
endorsed by Rensselaer Polytechnic Institute or its Office of Graduate
Education (OGE), and it does not include RPI's seal or original template.
Check the current OGE requirements before you submit.
"""
CHEATSHEET_NOTE = """
For a one-page printable reference, open rpi-thesis-cheatsheet.pdf.
"""
START_HERE = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=guide/index.html">
<title>Start here · RPI Thesis Toolkit</title>
</head>
<body>
<p><a href="guide/index.html">Open the RPI Thesis Toolkit guide</a> (it works offline).</p>
</body>
</html>
"""


def add_text(archive, name, text):
    info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, text)


# For "Open in Overleaf": only what the thesis needs, so the Overleaf file tree
# stays short. Overleaf opens it from a link (overleaf.com/docs?snip_uri=...).
OVERLEAF_SKIP = ("scripts/", ".vscode/", "latexmkrc")
OVERLEAF_README = """\
# RPI Thesis Toolkit: Overleaf starter

1. Compile main.tex (the green Recompile button) to see the sample PDF.
2. Add the RPI seal: see assets/README.md.
3. Put your details in metadata.tex, then write in chapters/.

The full guide: {guide_url}
To update the formatting later, follow "Update the formatting safely" in the
guide (workflows page); the changelog lists any other files a version changes.
This is a community project, not approved by RPI or the Office of Graduate
Education. Check the current OGE requirements before you submit.
"""


def guide_url():
    """The public guide address, from site/site.json (one place to change it)."""
    config = json.loads((ROOT / "site/site.json").read_text(encoding="utf-8"))
    return config["site_url"].rstrip("/") + "/"


def cheatsheet_state(path):
    """'missing', 'stale' (older than its TeX sources), or 'fresh'."""
    if not path.is_file() or path.is_symlink():
        return "missing"
    sources = [p for p in (ROOT / "cheatsheet").glob("*.tex") if p.is_file()]
    newest = max((p.stat().st_mtime for p in sources), default=0)
    return "stale" if path.stat().st_mtime < newest else "fresh"


def document_inputs():
    """What main.tex needs, read the way build.py reads it: every \\include and
    \\input target (and the files those load), local .cls/.sty files, .bib files
    from \\addbibresource, and graphics with literal paths. Returns (needed file
    names, problems). Example images from TeX Live's mwe package are not files."""
    scan = active_sources(ROOT)
    needed = {path.relative_to(ROOT).as_posix() for path in scan.files} | set(scan.assets)
    problems = [f"{where}: {message}" for where, message, _ in scan.problems]
    for where, target, kind in scan.missing_assets:
        if kind == "graphic" and re.match(r"example-(image|grid)", target):
            continue
        problems.append(f"{where}: {target} ({kind}) does not exist in the repository")
    return needed, problems


def verify_archive(label, names, skip=()):
    """Fail if the archive lacks a file the sample thesis needs, so a ZIP that
    compiles with 'No file x.tex' warnings never ships."""
    needed, problems = document_inputs()
    absent = sorted(n for n in needed if n not in names and not n.startswith(skip))
    absent_text = "".join(f"\n- {n}: used by the sample thesis but not in the {label}; add it to FILES"
                          " in scripts/package.py" for n in absent)
    problems_text = "".join(f"\n- {p}" for p in problems)
    if absent or problems:
        raise SystemExit(f"The {label} would not build the whole sample thesis:"
                         + absent_text + problems_text)


def package_overleaf(version):
    destination = ROOT / f"dist/rpi-thesis-overleaf-v{version}.zip"
    temp = destination.with_suffix(".tmp")
    with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            if not name.startswith(OVERLEAF_SKIP):
                archive.write(ROOT / name, name)
        add_text(archive, "README.md", OVERLEAF_README.format(guide_url=guide_url()))
        names = archive.namelist()
    try:
        verify_archive("Overleaf ZIP", names)
    except SystemExit:
        temp.unlink()
        raise
    temp.replace(destination)
    return destination


def package(dev=False):
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError("Starter files missing: " + ", ".join(missing))
    verify_archive("starter ZIP", set(FILES))  # before the slow guide build
    version, released = class_version()
    # main.tex asks for the class date, so LaTeX warns students whose rpi-thesis.cls is older.
    wanted = re.search(r"\\documentclass\{rpi-thesis\}\[(\d{4})/(\d\d)/(\d\d)\]", (ROOT / "main.tex").read_text(encoding="utf-8"))
    if not wanted or wanted.groups() != (f"{released:%Y}", f"{released:%m}", f"{released:%d}"):
        raise SystemExit(f"main.tex: write \\documentclass{{rpi-thesis}}[{released:%Y/%m/%d}], the date in rpi-thesis.cls's \\ProvidesClass line.")
    destination = ROOT / f"dist/rpi-thesis-starter-v{version}.zip"
    destination.parent.mkdir(exist_ok=True)
    temp = destination.with_suffix(".tmp")
    cheatsheet = ROOT / CHEATSHEET
    state = cheatsheet_state(cheatsheet)
    if state != "fresh" and not dev:
        raise SystemExit(
            f"The cheat sheet PDF is {state} ({CHEATSHEET}). Run"
            " python3 scripts/build_site.py --cheatsheet (needs TeX) to rebuild it,"
            " or add --dev to package without it for a local test."
        )
    with_cheatsheet = state == "fresh"
    with tempfile.TemporaryDirectory() as folder:
        guide = build_site(Path(folder) / "guide", offline=True, cheatsheet=with_cheatsheet,
                           complete=not dev)
        # The archive replaces the old one only after everything is in place.
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
            for name in FILES:
                if (ROOT / name).is_symlink():
                    raise ValueError("Starter files must not be symlinks: " + name)
                archive.write(ROOT / name, name)
            add_text(archive, ".gitignore", STUDENT_GITIGNORE)
            readme = STUDENT_README
            if with_cheatsheet:
                archive.write(cheatsheet, CHEATSHEET_NAME)
                readme += CHEATSHEET_NOTE
            add_text(archive, "README.md", readme)
            add_text(archive, "START-HERE.html", START_HERE)
            for path in sorted(guide.rglob("*")):
                if path.is_file():
                    archive.write(path, "guide/" + path.relative_to(guide).as_posix())
            names = archive.namelist()
    leaked = [
        n for n in names
        if n.startswith(NOT_FOR_STUDENTS) or (n.endswith(".pdf") and n != CHEATSHEET_NAME)
    ]
    if leaked:
        temp.unlink()
        raise RuntimeError("Not for the student ZIP: " + ", ".join(leaked))
    try:
        verify_archive("starter ZIP", names)
    except SystemExit:
        temp.unlink()
        raise
    temp.replace(destination)
    print(f"Local test archive ({len(names)} files): {destination}")
    overleaf = package_overleaf(version)
    print(f"Overleaf archive (thesis files only): {overleaf}")
    if CHEATSHEET_NAME not in names:
        print(f"Cheat sheet PDF not included ({state}): run build_site.py --cheatsheet (needs TeX) first.")
    print("No RPI seal or original template included; students download the seal (assets/README.md).")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--dev", action="store_true",
        help="allow a missing or stale cheat sheet, missing guide pages, diagrams or pictures; not for releases",
    )
    package(parser.parse_args().dev)
