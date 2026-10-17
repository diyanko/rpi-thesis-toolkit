"""Small helpers the maintainer scripts share. Python standard library only.

Maintainer tooling only: scripts/build.py ships to students as a standalone
file and must never import this module, nor may anything else in the student
ZIP.
"""
from datetime import date
import json
import os
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent

# The class line every version number comes from:
# \ProvidesClass{rpi-thesis}[YYYY/MM/DD vX.Y.Z description]
CLASS_LINE = re.compile(r"\\ProvidesClass\{rpi-thesis\}\[(\d{4})/(\d\d)/(\d\d) v([\w.-]+)")

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
]


def site_config(root=None):
    """The settings in site/site.json (repository and website addresses)."""
    return json.loads(((root or ROOT) / "site/site.json").read_text(encoding="utf-8"))


def class_version(root=None):
    """(version, date) from the \\ProvidesClass line of rpi-thesis.cls."""
    text = ((root or ROOT) / "rpi-thesis.cls").read_text(encoding="utf-8")
    match = CLASS_LINE.search(text)
    if not match:
        raise SystemExit(
            "rpi-thesis.cls: keep the line \\ProvidesClass{rpi-thesis}[YYYY/MM/DD vX.Y.Z ...]; "
            "the website and the ZIP name read the version from it."
        )
    return match[4], date(int(match[1]), int(match[2]), int(match[3]))


def find_chrome():
    """Path or command name of Chrome or Chromium ($CHROME first), or None."""
    env = os.environ.get("CHROME")
    if env and (shutil.which(env) or Path(env).exists()):
        return env
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).is_absolute():
            if Path(candidate).exists():
                return candidate
        elif shutil.which(candidate):
            return candidate
    return None


def missing(*tools):
    """The programs among `tools` that are not on PATH."""
    return [tool for tool in tools if not shutil.which(tool)]
