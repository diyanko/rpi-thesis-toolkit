#!/usr/bin/env python3
"""Monthly health check (.github/workflows/health.yml). Stdlib only.

    python3 scripts/health.py            check external links and RPI's pages
    python3 scripts/health.py --update   after re-reading RPI's pages, record
                                         what they say now

1. Every external link in the guide, README, CONTRIBUTING, and home page must
   answer. Sites that block robots (403, 429) are listed, not failed.
2. RPI's thesis pages are compared with scripts/oge-watch.json: the links in
   the page's <main> content (relative links resolved against the page) and a
   fingerprint of its text. A change means: read the page and the manual
   again, update docs/project/requirements.md if a rule moved, then run
   --update and commit the new oge-watch.json.

What this cannot see: a manual or checklist replaced at the same address.
The documents sit behind Box links that need a browser (Box answers with a
script-driven page, not the file), so only their links are compared, not their
contents. The yearly review in docs/project/maintenance.md re-reads them.

--update records every watched page or nothing: if any page does not answer,
answers with an error, or has no <main> content, the old oge-watch.json stays
as it was and the command exits 1. The file is replaced in one step.
A check with no recorded baseline for a watched page fails rather than passes.
Prints a Markdown report; exits 1 when something needs a person.
"""

import hashlib
from html.parser import HTMLParser
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent
WATCH_FILE = ROOT / "scripts" / "oge-watch.json"
WATCHED = ["https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation"]
SOURCES = ["docs/*.md", "README.md", "CONTRIBUTING.md", "site/index.html"]
AGENT = "Mozilla/5.0 (compatible; rpi-thesis-toolkit health check)"
TIMEOUT = 30
ACT = ("To act on an RPI page change: read the page and the manual again, update "
       "docs/project/requirements.md if a rule moved, then run "
       "`python3 scripts/health.py --update` and commit scripts/oge-watch.json.")


def skip_prefixes():
    """Our own addresses (site/site.json) and the page-count script are not checked."""
    config = json.loads((ROOT / "site/site.json").read_text(encoding="utf-8"))
    own = [config.get(key, "").strip().rstrip("/") for key in ("site_url", "repository_url")]
    return tuple(url for url in own if url) + ("https://static.cloudflareinsights.com",)


def skipped(url, prefixes):
    return any(url.rstrip("/") == prefix or url.startswith(prefix + "/") for prefix in prefixes)


def get(url):
    """Return (status, body text); status 0 means no answer."""
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, ""
    except Exception:  # DNS, TLS, timeout
        return 0, ""


def links():
    found, skip = set(), skip_prefixes()
    for pattern in SOURCES:
        for path in sorted(ROOT.glob(pattern)):
            for url in re.findall(r"https?://[^\s)<>\"'}`\]]+", path.read_text(encoding="utf-8")):
                url = url.rstrip(".,;:")
                if not skipped(url, skip) and "localhost" not in url:
                    found.add(url.split("#")[0])
    return sorted(found)


class MainLinks(HTMLParser):
    """The href of every <a> inside <main>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth, self.seen_main, self.hrefs = 0, False, []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.depth += 1
            self.seen_main = True
        elif tag == "a" and self.depth:
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href.strip())

    def handle_endtag(self, tag):
        if tag == "main" and self.depth:
            self.depth -= 1


def fingerprint(url, html):
    """{'links': [...], 'text': sha256} for the page's <main> content.
    Raises ValueError when there is no <main> content to compare."""
    start, end = html.find("<main"), html.find("</main>")
    if start < 0 or end < start:
        raise ValueError("no <main> ... </main> content (page layout changed or answer is not the page)")
    parser = MainLinks()
    parser.feed(html)
    parser.close()
    if not parser.seen_main:
        raise ValueError("no <main> element")
    hrefs = set()
    for href in parser.hrefs:
        absolute = urljoin(url, href).split("#")[0]
        if urlsplit(absolute).scheme in ("http", "https") and absolute != url:
            hrefs.add(absolute)
    main = html[start:end]
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", main, flags=re.S)
    text = " ".join(re.sub(r"<[^>]+>|&nbsp;", " ", text).split())
    if not text:
        raise ValueError("<main> has no text")
    return {"links": sorted(hrefs), "text": hashlib.sha256(text.encode()).hexdigest()}


def read_baseline():
    """(baseline dict, problem or None)."""
    if not WATCH_FILE.exists():
        return {}, f"{WATCH_FILE.name} is missing"
    try:
        data = json.loads(WATCH_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return {}, f"{WATCH_FILE.name} cannot be read ({error})"
    if not isinstance(data, dict):
        return {}, f"{WATCH_FILE.name} is not a JSON object"
    return data, None


def write_baseline(data):
    """Replace oge-watch.json in one step: write a temporary file beside it, then rename."""
    handle, temp = tempfile.mkstemp(dir=WATCH_FILE.parent, prefix=".oge-watch-", suffix=".json")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
        os.replace(temp, WATCH_FILE)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise


def watch(update):
    """Compare (or with update, record) RPI's pages. Returns (report lines, problems)."""
    report, problems = [], 0
    watched, baseline_problem = read_baseline()
    now = {}
    for url in WATCHED:
        status, html = get(url)
        if status != 200:
            report.append(f"- RPI page did not answer ({status or 'no answer'}): {url}")
            problems += 1
            continue
        try:
            now[url] = fingerprint(url, html)
        except ValueError as error:
            report.append(f"- RPI page could not be read ({error}): {url}")
            problems += 1
            continue
        before = watched.get(url)
        if not isinstance(before, dict) or not {"links", "text"} <= before.keys():
            if not update:
                report.append(f"- **No recorded baseline** for {url}"
                              + (f" ({baseline_problem})" if baseline_problem else "")
                              + ": read the page and the manual, then run "
                              "`python3 scripts/health.py --update` and commit scripts/oge-watch.json.")
                problems += 1
        elif before != now[url]:
            added = sorted(set(now[url]["links"]) - set(before["links"]))
            gone = sorted(set(before["links"]) - set(now[url]["links"]))
            report.append(f"- **RPI page changed:** {url}" + (" (text only)" if not added + gone else ""))
            report += [f"  - new link: {link}" for link in added] + [f"  - removed link: {link}" for link in gone]
            if not update:
                problems += 1
    if update:
        if problems:
            report.append(f"- {WATCH_FILE.name} was left unchanged: every watched page must be "
                          "read before the record is replaced. Try again later.")
        else:
            write_baseline(now)
            report.append(f"- Recorded {len(now)} RPI page(s) in scripts/{WATCH_FILE.name}.")
    return report, problems


def main(argv=None):
    update = "--update" in (sys.argv[1:] if argv is None else argv)
    report, problems = watch(update)
    if update:
        print("\n".join(report))
        return 1 if problems else 0

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
    print("\nNot covered: a manual or checklist replaced at the same Box address; the "
          "yearly requirement review re-reads them.")
    print("\n" + ACT)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
