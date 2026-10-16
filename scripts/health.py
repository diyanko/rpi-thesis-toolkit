#!/usr/bin/env python3
"""Monthly health check (.github/workflows/health.yml). Stdlib only.

    python3 scripts/health.py            check external links and RPI's pages
    python3 scripts/health.py --update   after re-reading RPI's pages, record
                                         what they say now

1. Every external link in the guide, README, CONTRIBUTING, and home page must
   answer. Sites that block robots (403, 429) are listed, not failed.
2. RPI's thesis pages are compared with scripts/oge-watch.json: the links in
   the page's main content (the manual and checklists live behind them) and a
   fingerprint of its text. A change means: read the page and the manual
   again, update docs/project/requirements.md if a rule moved, then run
   --update and commit the new oge-watch.json.
Prints a Markdown report; exits 1 when something needs a person.
"""

import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCH_FILE = ROOT / "scripts" / "oge-watch.json"
WATCHED = ["https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation"]
SOURCES = ["docs/*.md", "README.md", "CONTRIBUTING.md", "site/index.html"]
SKIP = ("https://diyanko.github.io/", "https://github.com/diyanko/", "https://static.cloudflareinsights.com/")
AGENT = "Mozilla/5.0 (compatible; rpi-thesis-toolkit health check)"


def get(url):
    """Return (status, body text); status 0 means no answer."""
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, ""
    except Exception:  # DNS, TLS, timeout
        return 0, ""


def links():
    found = set()
    for pattern in SOURCES:
        for path in sorted(ROOT.glob(pattern)):
            for url in re.findall(r"https?://[^\s)<>\"'}`\]]+", path.read_text(encoding="utf-8")):
                url = url.rstrip(".,;:")
                if not url.startswith(SKIP) and "localhost" not in url:
                    found.add(url.split("#")[0])
    return sorted(found)


def fingerprint(html):
    main = html[html.find("<main"):html.find("</main>")] if "<main" in html else html
    hrefs = sorted(set(re.findall(r'href="(https?://[^"]+)"', main)))
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", main, flags=re.S)
    text = " ".join(re.sub(r"<[^>]+>|&nbsp;", " ", text).split())
    return {"links": hrefs, "text": hashlib.sha256(text.encode()).hexdigest()}


def main():
    update = "--update" in sys.argv[1:]
    report, problems = [], 0
    watched = json.loads(WATCH_FILE.read_text()) if WATCH_FILE.exists() else {}
    now = {}
    for url in WATCHED:
        status, html = get(url)
        if status != 200:
            report.append(f"- RPI page did not answer ({status}): {url}")
            problems += 1
            continue
        now[url] = fingerprint(html)
        before = watched.get(url)
        if before and before != now[url]:
            added = sorted(set(now[url]["links"]) - set(before["links"]))
            gone = sorted(set(before["links"]) - set(now[url]["links"]))
            report.append(f"- **RPI page changed:** {url}" + (" (text only)" if not added + gone else ""))
            report += [f"  - new link: {l}" for l in added] + [f"  - removed link: {l}" for l in gone]
            problems += 1
    if update:
        WATCH_FILE.write_text(json.dumps(now, indent=2, sort_keys=True) + "\n")
        print(f"Recorded {len(now)} RPI page(s) in {WATCH_FILE.relative_to(ROOT)}")
        return

    urls = links()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda u: (u, get(u)[0]), urls))
    blocked = [u for u, s in results if s in (401, 403, 429)]
    broken = [(u, s) for u, s in results if s not in (200, 401, 403, 429)]
    report += [f"- Broken link ({s or 'no answer'}): {u}" for u, s in broken]
    problems += len(broken)
    print("## Monthly health check\n")
    print("\n".join(report) or "- Nothing needs attention.")
    print(f"\nChecked {len(urls)} external links ({len(blocked)} block robots and were not checked: "
          + ", ".join(blocked) + ")." if blocked else f"\nChecked {len(urls)} external links.")
    print("\nTo act on an RPI page change: read the page and the manual again, update "
          "docs/project/requirements.md if a rule moved, then run "
          "`python3 scripts/health.py --update` and commit scripts/oge-watch.json.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
