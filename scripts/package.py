#!/usr/bin/env python3
"""Make the student starter ZIP in dist/: thesis files plus the offline guide.

    python3 scripts/package.py

Needs Pandoc (the guide is rendered by build_site.py). Nothing is uploaded.
"""
from pathlib import Path
import tempfile
import zipfile

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
2. Add the RPI seal: see assets/README.md.
3. Compile main.tex once to see the sample PDF.
4. Put your details in metadata.tex, then write in chapters/.

Formatting lives in rpi-thesis.cls. To update the formatting later, replace
that one file; your writing stays untouched.

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


def package():
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError("Starter files missing: " + ", ".join(missing))
    version = class_version()[0]
    destination = ROOT / f"dist/rpi-thesis-starter-v{version}.zip"
    destination.parent.mkdir(exist_ok=True)
    temp = destination.with_suffix(".tmp")
    cheatsheet = ROOT / CHEATSHEET
    with_cheatsheet = cheatsheet.is_file() and not cheatsheet.is_symlink()
    with tempfile.TemporaryDirectory() as folder:
        guide = build_site(Path(folder) / "guide", offline=True, cheatsheet=with_cheatsheet)
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
    temp.replace(destination)
    print(f"Local test archive ({len(names)} files): {destination}")
    if CHEATSHEET_NAME not in names:
        print("Cheat sheet PDF not included: run build_site.py --cheatsheet (needs TeX) first.")
    print("No RPI seal or original template included; students download the seal (assets/README.md).")
    return destination


if __name__ == "__main__":
    package()
