#!/usr/bin/env python3
"""Release helpers for CI (.github/workflows/build.yml). Stdlib only.

    python3 scripts/release.py notes        print the GitHub release notes for
                                            the version in scripts/build_site.py
    python3 scripts/release.py deployable   exit 0 if the website may deploy:
                                            the release exists and its class
                                            file equals rpi-thesis.cls here
    python3 scripts/release.py live         wait for the live website to serve
                                            this version, then check its links

A maintainer releases with: python3 scripts/bump.py X.Y.Z, verify, commit, and
push the commit with the tag vX.Y.Z (docs/project/maintenance.md).
"""

import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_site import RELEASE_TAG, RELEASE_VERSION  # noqa: E402

REPO = "https://github.com/diyanko/rpi-thesis-toolkit"
SITE = "https://diyanko.github.io/rpi-thesis-toolkit/"
ZIPS = [f"rpi-thesis-{kind}-{RELEASE_TAG}.zip" for kind in ("starter", "overleaf")]
HEADER = (
    "Beta pre-release of the RPI Thesis Toolkit, an unofficial, community-made LaTeX "
    "starter and guide for RPI master's theses and doctoral dissertations. Not affiliated "
    "with or endorsed by RPI or its Office of Graduate Education.\n\n"
    f"**Guide:** {SITE}\n\n"
    f"**Downloads:** `{ZIPS[0]}` (thesis files, offline guide, cheat sheet), `{ZIPS[1]}` "
    "(thesis files only, for Overleaf), and `rpi-thesis.cls` (the class alone, to update "
    "an existing thesis). The RPI seal is a separate download from RPI.\n\n")


def fetch(url):
    """Return the body of url, or None for a 404."""
    request = urllib.request.Request(url, headers={"User-Agent": "rpi-thesis-release-check"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def notes():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(RELEASE_VERSION)} .*?\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not match:
        sys.exit(f"CHANGELOG.md has no entry for {RELEASE_VERSION}; run scripts/bump.py first.")
    print(HEADER + match[1].strip())


def deployable():
    released = fetch(f"{REPO}/releases/download/{RELEASE_TAG}/rpi-thesis.cls")
    if released is None:
        sys.exit(f"Not deploying: release {RELEASE_TAG} does not exist yet (its tag deploys the site).")
    if released != (ROOT / "rpi-thesis.cls").read_bytes():
        sys.exit(f"Not deploying: rpi-thesis.cls differs from release {RELEASE_TAG}. "
                 "Release a new version to publish class changes.")
    print(f"OK: release {RELEASE_TAG} matches this rpi-thesis.cls")


def live():
    want = (ROOT / "rpi-thesis.cls").read_bytes()
    for _ in range(30):  # GitHub Pages can take a few minutes
        if fetch(SITE + "downloads/rpi-thesis.cls") == want:
            break
        time.sleep(20)
    else:
        sys.exit("FAIL: the live site's downloads/rpi-thesis.cls is not this version")
    home = (fetch(SITE) or b"").decode("utf-8", "replace")
    problems = [] if ZIPS[0] in home else [f"home page does not link {ZIPS[0]}"]
    for name in ZIPS + ["rpi-thesis.cls"]:
        if fetch(f"{REPO}/releases/download/{RELEASE_TAG}/{name}") is None:
            problems.append(f"release asset missing: {name}")
    if problems:
        sys.exit("FAIL: " + "; ".join(problems))
    print(f"PASS: live site serves {RELEASE_TAG}; downloads and newest class link work")


if __name__ == "__main__":
    commands = {"notes": notes, "deployable": deployable, "live": live}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        sys.exit(__doc__)
    commands[sys.argv[1]]()
