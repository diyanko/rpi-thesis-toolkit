#!/usr/bin/env python3
"""Set a new version everywhere it appears, for a release.

    python3 scripts/bump.py          choose the version from the change log
    python3 scripts/bump.py X.Y.Z    use this version

Without a version it reads "## Unreleased" in CHANGELOG.md: minor when its
"Changes your PDF?" line says anything but No (Yes, "Only if ...") or it
mentions a new setting, else patch. A line "**Version:** minor" (or patch) in
the section overrides the choice, for example for a new setting.
(docs/project/maintenance.md, "Versions and compatibility").
Edits the class line (version and today's date), main.tex's requested date,
the release the website links, the README and Get started download links,
the cheat sheet's version line, CITATION.cff, and turns the change log's
"Unreleased" heading into the version. Touches only files; then run
verify.py release and follow docs/project/maintenance.md ("Make a release").
"""

import re
import sys
from datetime import date

from common import CLASS_LINE, ROOT, class_version


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
        ("cheatsheet/cheatsheet.tex", r"\\newcommand\{\\sheetversion\}\{[\d.]+\}",
         rf"\\newcommand{{\\sheetversion}}{{{new}}}"),
        ("CITATION.cff", r"version: [\d.]+\ndate-released: [\d-]+", f"version: {new}\ndate-released: {today}"),
        ("CHANGELOG.md", r"^## Unreleased[ \t]*$",
         f"## {new} (beta), {today.day} {today:%b %Y}\n\nPublished as the pre-release `v{new}`."),
    ]
    # The "**Version:**" line only steers this script; the released entry leaves it out.
    log = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section = re.search(r"(?ms)^## Unreleased[ \t]*$.*?(?=^## |\Z)", log)
    if section:
        cleaned = re.sub(r"(?m)^\*\*Version:\*\*[^\n]*\n\n?", "", section[0], count=1)
        log = log[:section.start()] + cleaned + log[section.end():]
    for name, pattern, replacement in edits:
        source = log if name == "CHANGELOG.md" else (ROOT / name).read_text(encoding="utf-8")
        text, count = re.subn(pattern, replacement, source, flags=re.M)
        if not count or (name not in {"README.md", "docs/get-started.md"} and count != 1):
            raise ValueError(f"{name}: expected release text is missing or repeated; check it before bumping.")
        prepared[name] = text
    return old, prepared


def choose(old, changelog):
    """(new version, why) from the Unreleased section of the change log."""
    if len(re.findall(r"(?m)^## Unreleased[ \t]*$", changelog)) > 1:
        raise ValueError("CHANGELOG.md: more than one '## Unreleased' section; merge them into one.")
    section = re.search(r"(?ms)^## Unreleased[ \t]*$(.*?)(?=^## |\Z)", changelog)
    if not section:
        raise ValueError("CHANGELOG.md: no '## Unreleased' section; add the change-log lines first.")
    text = section[1]
    pdf = re.search(r"\*\*Changes your PDF\?\*\*\s*\**\s*(\w+)", text)
    major, minor, patch = map(int, old.split("."))
    if not pdf:
        raise ValueError("CHANGELOG.md: the Unreleased section needs a '**Changes your PDF?**' line.")
    forced = re.search(r"(?im)^\*\*Version:\*\*\s*(minor|patch)\b", text)   # an explicit override
    if forced:
        bumped = f"{major}.{minor + 1}.0" if forced[1].lower() == "minor" else f"{major}.{minor}.{patch + 1}"
        return bumped, f"{forced[1].lower()}: **Version:** line in the change log"
    if pdf[1].lower() != "no":  # Yes, or "Only if ...": some PDFs change
        return f"{major}.{minor + 1}.0", f"minor: Changes your PDF? {pdf[1]}"
    if re.search(r"(?i)\bnew settings?\b", text):
        return f"{major}.{minor + 1}.0", "minor: a new setting"
    return f"{major}.{minor}.{patch + 1}", "patch: no PDF change and no new setting"


def main():
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not re.fullmatch(r"\d+\.\d+\.\d+", sys.argv[1])):
        sys.exit(__doc__)
    today = date.today()
    try:
        if len(sys.argv) == 2:
            new = sys.argv[1]
        else:
            old, _ = class_version(ROOT)
            new, why = choose(old, (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
            print(f"version {new} ({why})")
        old, prepared = plan(new, today)
    except (OSError, ValueError) as error:
        sys.exit(str(error))
    for name, text in prepared.items():
        (ROOT / name).write_text(text, encoding="utf-8")
    print(f"{old} -> {new}. Next: python3 scripts/verify.py release")


if __name__ == "__main__":
    main()
