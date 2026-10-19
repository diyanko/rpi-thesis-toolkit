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
import posixpath
import re
import subprocess
import tempfile
from urllib.parse import quote, unquote, urlsplit
import zipfile

from build import active_sources
from build_site import OFFLINE_CHEATSHEET, build_site
from common import ROOT, class_version, site_config

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
    "AGENTS.md", "CLAUDE.md", "docs/", "site/", "_local/", "build/", "dist/",
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
"Update the formatting safely" in the guide (Going further page). Before
version 1.0, anything may change, and the changelog says what to do.

This is an unofficial, community-made starter. It does not include RPI's
seal or original template. Check the current requirements of RPI's Office of
Graduate Education (OGE) before you submit.
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


# Reproducible archives: every entry gets the same timestamp and plain permissions
# (0755 only for files that are executable in the checkout), so the same sources
# always give byte-identical ZIPs.
ZIP_DATE = (2026, 1, 1, 0, 0, 0)


def add_text(archive, name, text, mode=0o644):
    info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = mode << 16
    archive.writestr(info, text)


def add_file(archive, path, name, shipped=(), version=""):
    mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
    data = path.read_bytes()
    if name.endswith(".md") and shipped:
        data = shipped_markdown(name, data.decode("utf-8"), shipped, version)
    add_text(archive, name, data, mode)


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
guide (Going further page). Before version 1.0, anything may change, and
the changelog says what to do.
This is an unofficial, community-made starter. Check the current requirements
of RPI's Office of Graduate Education (OGE) before you submit.
"""


def site_setting(key, what):
    """An address from site/site.json, the one place to change it."""
    config = site_config(ROOT)
    url = config.get(key)
    if not isinstance(url, str) or not url.strip().startswith("https://"):
        raise SystemExit(f"site/site.json: set {key} to {what} (an https:// address) before packaging.")
    return url.strip().rstrip("/")


def guide_url():
    """The public guide address."""
    return site_setting("site_url", "the published guide address") + "/"


def repository_url():
    """The public repository address."""
    return site_setting("repository_url", "the public repository address")


def pandoc_json(text):
    """Pandoc's GFM reading of `text`: the same Markdown reader as the guide's."""
    try:
        result = subprocess.run(["pandoc", "--from=gfm", "--to=json"], input=text, text=True,
                                capture_output=True, encoding="utf-8")
    except OSError as error:
        raise SystemExit(f"Packaging shipped Markdown needs Pandoc: {error}") from None
    if result.returncode:
        raise SystemExit("Pandoc could not read shipped Markdown: " + result.stderr.strip())
    return json.loads(result.stdout)


def link_targets(text):
    """The destination of every link and image Pandoc reads in the Markdown
    `text`. Code, escaped brackets, and unused reference definitions are not
    links, so they are not here."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("t") in ("Link", "Image"):
                found.append(node["c"][-1][0])
            walk(node.get("c"))
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(pandoc_json(text)["blocks"])
    return found


def shipped_markdown(name, text, shipped, version):
    """A Markdown file as it goes into a ZIP: a relative link or image to a
    file the ZIP leaves out (CREDITS.md from LICENSE.md, say) points to that
    file in the repository at this release instead, so no such link inside
    the ZIP is broken. Only those destinations change; the rest of the file
    stays exactly as written."""
    new = {}
    for target in link_targets(text):
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        path = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parts.path)))
        if path in shipped:
            continue
        if path.startswith("..") or not (ROOT / path).exists():
            raise SystemExit(f"{name}: link to a missing file: {target}")
        kind = "tree" if (ROOT / path).is_dir() else "blob"
        fragment = "#" + parts.fragment if parts.fragment else ""
        new[target] = f"{repository_url()}/{kind}/v{version}/{quote(path)}{fragment}"
    if not new:
        return text
    # Where is each destination written? Put a numbered mark at every place
    # its text appears; the marks Pandoc then reads as a whole link
    # destination are the links (the others are in code or other words).
    spots, taken = [], set()
    for target in sorted(new, key=len, reverse=True):
        for m in re.finditer(re.escape(target), text):
            if not taken & set(range(m.start(), m.end())):
                spots.append((m.start(), m.end(), target))
                taken |= set(range(m.start(), m.end()))
    spots.sort()
    marked = text
    for index, (start, end, _) in reversed(list(enumerate(spots))):
        marked = f"{marked[:start]}rpi-link-{index}-mark{marked[end:]}"
    links = {int(m[1]) for m in (re.fullmatch(r"rpi-link-(\d+)-mark", t) for t in link_targets(marked)) if m}
    unplaced = sorted(set(new) - {spots[index][2] for index in links})
    if unplaced:
        raise SystemExit(f"{name}: could not find where the link to {unplaced[0]} is written; write it plainly,"
                         f" as [text]({unplaced[0]}), so packaging can point it at the repository.")
    for index in sorted(links, reverse=True):
        start, end, target = spots[index]
        text = text[:start] + new[target] + text[end:]
    return text


def check_links(label, archive):
    """Every relative link and image Pandoc reads in the ZIP's Markdown files,
    and every href or url= in its top-level HTML files, must name a file inside
    the ZIP (the guide checks its own links as it builds). Raw HTML inside
    Markdown is not checked."""
    names = set(archive.namelist())
    folders = {posixpath.dirname(n) for n in names}
    broken = []
    for name in sorted(names):
        if name.endswith(".md"):
            targets = link_targets(archive.read(name).decode("utf-8"))
        elif name.endswith(".html") and "/" not in name:
            targets = re.findall(r'(?:href="|url=)([^"\s>]+)', archive.read(name).decode("utf-8"))
        else:
            continue
        for target in targets:
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            path = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parts.path)))
            if path not in names and path not in folders:
                broken.append(f"{name}: {target}")
    if broken:
        raise SystemExit(f"The {label} has links to files it does not contain:\n- " + "\n- ".join(broken))


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


def verify_files():
    """Check source files before writing either ZIP, including linked folders."""
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError("Starter files missing: " + ", ".join(missing))
    for name in FILES:
        path = Path(name)
        if any((ROOT / part).is_symlink() for part in (path, *path.parents)):
            raise ValueError("Starter files must not be symlinks or inside linked folders: " + name)


def package_overleaf(version):
    verify_files()
    public_guide = guide_url()
    destination = ROOT / f"dist/rpi-thesis-overleaf-v{version}.zip"
    temp = destination.with_suffix(".tmp")
    with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
        shipped = {name for name in FILES if not name.startswith(OVERLEAF_SKIP)} | {"README.md"}
        for name in FILES:
            if not name.startswith(OVERLEAF_SKIP):
                add_file(archive, ROOT / name, name, shipped, version)
        add_text(archive, "README.md", OVERLEAF_README.format(guide_url=public_guide))
        names = archive.namelist()
    try:
        with zipfile.ZipFile(temp) as archive:
            check_links("Overleaf ZIP", archive)
        verify_archive("Overleaf ZIP", names)
    except SystemExit:
        temp.unlink()
        raise
    temp.replace(destination)
    return destination


def package(dev=False):
    verify_files()
    guide_url()  # fail before replacing either archive if Overleaf's guide link is unset
    repository_url()  # shipped Markdown links files the ZIP leaves out to the repository
    verify_archive("starter ZIP", set(FILES))  # before the slow guide build
    version, released = class_version()
    # main.tex asks for the class date, so LaTeX warns when rpi-thesis.cls is dated earlier
    # (a date check only; it says nothing about which versions work together).
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
            shipped = set(FILES) | {"README.md", "START-HERE.html", CHEATSHEET_NAME}
            for name in FILES:
                add_file(archive, ROOT / name, name, shipped, version)
            add_text(archive, ".gitignore", STUDENT_GITIGNORE)
            readme = STUDENT_README
            if with_cheatsheet:
                add_file(archive, cheatsheet, CHEATSHEET_NAME)
                readme += CHEATSHEET_NOTE
            add_text(archive, "README.md", readme)
            add_text(archive, "START-HERE.html", START_HERE)
            for path in sorted(guide.rglob("*")):
                if path.is_file():
                    add_file(archive, path, "guide/" + path.relative_to(guide).as_posix())
            names = archive.namelist()
    leaked = [
        n for n in names
        if n.startswith(NOT_FOR_STUDENTS) or (n.endswith(".pdf") and n != CHEATSHEET_NAME)
    ]
    if leaked:
        temp.unlink()
        raise RuntimeError("Not for the student ZIP: " + ", ".join(leaked))
    try:
        with zipfile.ZipFile(temp) as archive:
            check_links("starter ZIP", archive)
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
