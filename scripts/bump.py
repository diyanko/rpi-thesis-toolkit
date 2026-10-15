#!/usr/bin/env python3
"""Set a new version everywhere it appears, for a release.

    python3 scripts/bump.py 0.3.0

Edits the class line (version and today's date), main.tex's requested date,
the release the website links, the README and Get started download links,
CITATION.cff, and turns the change log's "Unreleased" heading into the
version. Touches only files; then run verify.py release and follow
docs/project/maintenance.md ("Make a release").
"""

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def edit(name, pattern, replacement, count=1):
    path = ROOT / name
    text, n = re.subn(pattern, replacement, path.read_text(encoding="utf-8"))
    if n < count:
        sys.exit(f"{name}: expected text not found ({pattern})")
    path.write_text(text, encoding="utf-8")


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", sys.argv[1]):
        sys.exit(__doc__)
    new, today = sys.argv[1], date.today()
    old = re.search(r"v(\d+\.\d+\.\d+)", (ROOT / "rpi-thesis.cls").read_text(encoding="utf-8"))[1]
    edit("rpi-thesis.cls", r"(\\ProvidesClass\{rpi-thesis\}\[)\d{4}/\d\d/\d\d v[\d.]+",
         rf"\g<1>{today:%Y/%m/%d} v{new}")
    edit("main.tex", r"(\\documentclass\{rpi-thesis\}\[)\d{4}/\d\d/\d\d\]", rf"\g<1>{today:%Y/%m/%d}]")
    edit("scripts/build_site.py", r'RELEASE_VERSION = "[\d.]+"', f'RELEASE_VERSION = "{new}"')
    for name in ("README.md", "docs/get-started.md"):  # plain and URL-encoded links
        edit(name, rf"v{re.escape(old)}(/|%2F)rpi-thesis-(starter|overleaf)-v{re.escape(old)}",
             rf"v{new}\1rpi-thesis-\2-v{new}")
    edit("CITATION.cff", r"version: [\d.]+\ndate-released: [\d-]+", f"version: {new}\ndate-released: {today}")
    edit("CHANGELOG.md", r"## Unreleased", f"## {new} (beta), {today.day} {today:%b %Y}\n\nPublished as the pre-release `v{new}`.")
    print(f"{old} -> {new}. Next: python3 scripts/verify.py release")


if __name__ == "__main__":
    main()
