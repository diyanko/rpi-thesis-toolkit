#!/usr/bin/env python3
"""Set a new version everywhere it appears, for a release.

    python3 scripts/bump.py X.Y.Z

Edits the class line (version and today's date), main.tex's requested date,
the release the website links, the README and Get started download links,
CITATION.cff, and turns the change log's "Unreleased" heading into the
version. Touches only files; then run verify.py release and follow
docs/project/maintenance.md ("Make a release").
"""

import re
import sys
from datetime import date

from common import CLASS_LINE, ROOT


def plan(new, today):
    """Validate every source and prepare its replacement before changing any file."""
    source = (ROOT / "rpi-thesis.cls").read_text(encoding="utf-8")
    found = list(CLASS_LINE.finditer(source))
    if len(found) != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", found[0][4]):
        raise ValueError("rpi-thesis.cls: no class version found")
    match, old = found[0], found[0][4]
    if tuple(map(int, new.split("."))) <= tuple(map(int, old.split("."))):
        raise ValueError(f"Choose a version newer than {old}; {new} would reuse or lower the release version.")
    prepared = {"rpi-thesis.cls": source[:match.start()]
                 + f"\\ProvidesClass{{rpi-thesis}}[{today:%Y/%m/%d} v{new}" + source[match.end():]}
    edits = [
        ("main.tex", r"(\\documentclass\{rpi-thesis\}\[)\d{4}/\d\d/\d\d\]", rf"\g<1>{today:%Y/%m/%d}]"),
        ("scripts/build_site.py", r'RELEASE_VERSION = "[\d.]+"', f'RELEASE_VERSION = "{new}"'),
        *[(name, rf"v{re.escape(old)}(/|%2F)rpi-thesis-(starter|overleaf)-v{re.escape(old)}",
           rf"v{new}\1rpi-thesis-\2-v{new}") for name in ("README.md", "docs/get-started.md")],
        ("CITATION.cff", r"version: [\d.]+\ndate-released: [\d-]+", f"version: {new}\ndate-released: {today}"),
        ("CHANGELOG.md", r"^## Unreleased[ \t]*$",
         f"## {new} (beta), {today.day} {today:%b %Y}\n\nPublished as the pre-release `v{new}`."),
    ]
    for name, pattern, replacement in edits:
        text, count = re.subn(pattern, replacement, (ROOT / name).read_text(encoding="utf-8"), flags=re.M)
        if not count or (name not in {"README.md", "docs/get-started.md"} and count != 1):
            raise ValueError(f"{name}: expected release text is missing or repeated; check it before bumping.")
        prepared[name] = text
    return old, prepared


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", sys.argv[1]):
        sys.exit(__doc__)
    new, today = sys.argv[1], date.today()
    try:
        old, prepared = plan(new, today)
    except (OSError, ValueError) as error:
        sys.exit(str(error))
    for name, text in prepared.items():
        (ROOT / name).write_text(text, encoding="utf-8")
    print(f"{old} -> {new}. Next: python3 scripts/verify.py release")


if __name__ == "__main__":
    main()
