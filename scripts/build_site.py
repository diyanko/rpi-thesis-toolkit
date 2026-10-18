#!/usr/bin/env python3
"""Build the guide website from the Markdown files and check every local link.

    python3 scripts/build_site.py                website in dist/site/
    python3 scripts/build_site.py --previews     also add pictures of the sample
                                                 thesis (needs LaTeX, plus poppler
                                                 or Ghostscript; see previews.py)
                                                 and the cheat sheet PDF
    python3 scripts/build_site.py --cheatsheet   only the cheat sheet PDF (needs LaTeX)
    python3 scripts/build_site.py --previews --publish
                                                 strict mode for deployment: also fails
                                                 when the class version is not the
                                                 published release, a guide page or
                                                 diagram is missing, or the pictures or
                                                 cheat sheet were not built

The site is built in a sibling folder (dist/site.tmp-PID) and replaces dist/site only
after every check passes, so a failed build keeps the previous good site.
Needs Pandoc (CI uses 3.11). Nothing is published or uploaded. package.py calls
build_site(offline=True) to put the same guide into the starter ZIP.
"""
import argparse
import contextlib
from datetime import date
from html import escape, unescape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote, unquote, urlsplit
from xml.etree import ElementTree

import settings
import rules  # scripts/rules.py: the OGE rules in docs/project/requirements.md

from common import ROOT, class_version, site_config
from site_checks import (BUILD_FILE, CHEATSHEET_PDF, CLASS_DOWNLOAD, CONVERT, EXPLAIN, PDF_CHECK, BIB_CHECK, SearchSections,
                         checker_ids, search_route_problems, validate)
import build as build_helper  # scripts/build.py: KNOWN_PROBLEMS, shared with "Explain my error"

SITE = ROOT / "site"
NAME = "RPI Thesis Toolkit"
HOME_TITLE = NAME + " · LaTeX thesis and dissertation starter for RPI"
HOME_DESCRIPTION = (
    "Unofficial, community-made LaTeX starter, plain-language guide, and browser tools for RPI "
    "master's theses and doctoral dissertations. Not affiliated with or endorsed by RPI."
)

# The guide, in reading order, grouped into stages: (stage, [(file in docs/,
# label, also in the header?), ...]). The sidebar, header, previous/next links
# and every page list come from here.
NAV = [
    ("Core path", [
        ("get-started", "Get started", True),
        ("writing", "Writing basics", True),
        ("citations", "Citations", True),
        ("troubleshooting", "Fixing problems", True),
        ("submission", "Submitting", True),
    ]),
    ("Go further", [
        ("how-it-works", "How it works", False),
        ("bring-your-draft", "Bring your draft", False),
        ("going-further", "Going further", False),
        ("reviewer-checklist", "Reviewer checklist", False),
    ]),
    # Only tools that exist; each is also linked from the page where it helps most.
    ("Tools", [
        ("settings-builder", "Settings builder", False),
        ("bring-your-work-in", "Bring your work in", False),
        ("check-references", "Check your references", False),
        ("explain-my-error", "Explain my error", False),
        ("check-pdf", "Check your PDF", False),
    ]),
]
# The first stage is the numbered road most visitors follow; the sidebar numbers
# only its pages (site.css), and the previous/next links follow NAV in order.
GUIDE = [page for _, pages in NAV for page in pages]  # the same pages, in one list
# Quick answers: a guide page outside the stages and the previous/next chain.
# It sits above the stages in the sidebar, last in the header, and in the
# Help card on the landing page.
QUICK = ("how-do-i", "How do I…?", True)
# When a student needs each page, shown as a small tag under the page title.
# The sidebar lists pages without tags (SIDEBAR_TAGS is empty): its numbers and
# stage names already give the order, and tags of different widths made the
# list re-wrap. The landing-page cards leave tags out for the same reason.
# Tag -> (CSS class in site.css, pages). Every guide page has exactly one tag.
TAGS = {
    "Start here": ("start", ["get-started"]),
    "Need now": ("now", ["writing", "citations"]),
    "If you have a draft": ("draft", ["bring-your-draft", "bring-your-work-in"]),
    "When stuck": ("stuck", ["troubleshooting", "how-do-i", "explain-my-error"]),
    "Need later": ("later", ["submission"]),
    "Optional": ("optional", ["settings-builder", "how-it-works", "going-further", "check-pdf", "check-references", "reviewer-checklist"]),
}
PAGE_TAGS = {page: (tag, css) for tag, (css, pages) in TAGS.items() for page in pages}
SIDEBAR_TAGS = set()
# Guide pages with at least this many ## sections get an "On this page" list.
TOC_MIN = 5
# Project pages: source -> (name in project/, footer label or None). Pages
# with None are built and linked from other pages, but are not in the footer.
# docs/project/ pages are for maintainers and stay out of the starter ZIP.
PROJECT = {
    "README.md": ("readme", "About"),
    "CREDITS.md": ("credits", "Credits"),
    "CONTRIBUTING.md": ("contributing", "Contribute"),
    "CHANGELOG.md": ("changelog", "Changes"),
    "LICENSE.md": ("license", "License"),
    "docs/project/requirements.md": ("requirements", "Requirements map"),
    "CODE_OF_CONDUCT.md": ("code-of-conduct", None),
    "docs/project/attribution.md": ("attribution", None),
    "docs/project/components.md": ("components", None),   # design review: every component on one page
}
# Footer "Ask for help or suggest a change" link: the one place the help/feedback form URL lives.
FEEDBACK = ("docs/troubleshooting.md", "Ask for help")
# Scripts that only one guide page loads: page -> script.
PAGE_SCRIPTS = {"check-pdf": "pdf-check/ui.js", "bring-your-work-in": "convert/ui.js",
                 "settings-builder": "settings/ui.js", "check-references": "bibcheck/ui.js",
                 "explain-my-error": "explain/ui.js"}
# Page scripts that also run in the offline guide (file: pages).
OFFLINE_SCRIPTS = {"bring-your-work-in", "explain-my-error"}
# The release the website links: its version, tag (always "v" + version; beta status is
# GitHub's pre-release flag, never part of the name), and ZIP names
# (rpi-thesis-starter-v<version>.zip). The home page's "Get the starter" button downloads
# from it; README.md and docs/get-started.md link the same files by hand, and the build
# stops if they differ. --publish also requires the class version to match, so the site
# never describes files the download does not contain (docs/project/maintenance.md).
RELEASE_VERSION = "0.9.0"
RELEASE_TAG = "v" + RELEASE_VERSION
# Pictures the guide pages ask for; --publish fails without them.
REQUIRED_PREVIEWS = ["compile-pass-1-chapter", "compile-pass-2-chapter", "class-demo-ams", "class-demo-ieee"]
OFFLINE_CHEATSHEET = "rpi-thesis-cheatsheet.pdf"
CHEATSHEET_SOURCES = {"cheatsheet", "cheatsheet/cheatsheet.tex", "cheatsheet/README.md"}
OG_ALT = ("RPI Thesis Toolkit, an unofficial community starter: write your RPI thesis or "
          "dissertation in LaTeX, even if you've never used it.")
FENCE = "`" * 12
SVG_SCHEME = re.compile(r"@media\s*\(\s*prefers-color-scheme\s*:\s*(light|dark)\s*\)")


def svg_appearance(text, theme):
    """Freeze only our SVG's appearance queries; keep the authored file intact."""
    return SVG_SCHEME.sub(lambda match: "@media " + ("all" if match[1] == theme else "not all"), text)


def pandoc(args, text):
    result = subprocess.run(
        ["pandoc", *args], input=text, encoding="utf-8", capture_output=True
    )
    if result.returncode:
        raise SystemExit("Pandoc failed:\n" + result.stderr)
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result.stdout


def check_pandoc():
    if not shutil.which("pandoc"):
        raise SystemExit(
            "Building the website needs Pandoc 3.11 or newer: "
            "https://pandoc.org/installing.html\n"
            "You do not need it to write a thesis or edit the guide; CI builds the site."
        )
    options = subprocess.run(["pandoc", "--help"], capture_output=True, text=True).stdout
    if "--variable-json" not in options or "--syntax-highlighting" not in options:
        raise SystemExit("Your Pandoc is too old for this script. Install Pandoc 3.11 or newer.")


def plain(markdown):
    """Markdown inline text -> plain text, for titles and descriptions."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", markdown)
    text = re.sub(r"<[^>]+>|[*`]", "", text)
    return " ".join(text.split())


def source_path(source):
    """Refuse linked inputs, including a link in an input's parent folders."""
    path = ROOT / source
    for part in (path, *path.parents):
        if part == ROOT:
            break
        if part.is_symlink():
            raise SystemExit(f"Website input must not be a symlink or inside a linked folder: {source}")
    return path


def read_markdown(source):
    """Return (title, description, Markdown text). Optional front matter:
    a leading '---' block with 'title:' or 'description:' lines."""
    text = source_path(source).read_text(encoding="utf-8")
    front = {}
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if match:
        text = text[match.end() :]
        for line in match[1].splitlines():
            key, _, value = line.partition(":")
            front[key.strip()] = value.strip().strip("\"'")
    heading = re.search(r"(?m)^# (.+)$", text)
    if not heading:
        raise SystemExit(f"{source}: start the page with a title line such as '# Get started'.")
    description = front.get("description", "")
    for block in re.split(r"\n\s*\n", text[heading.end() :]):
        block = block.strip()
        if not description and block and not re.match(r"#|>|!\[|<|\||```|[*+-]\s|\d+\.\s", block):
            description = plain(block)
    if len(description) > 160:
        description = description[:157].rsplit(" ", 1)[0] + "…"
    return front.get("title") or plain(heading[1]), description, text


def edition():
    sources = json.loads((ROOT / "docs/project/sources.json").read_text(encoding="utf-8"))
    manual = sources["documents"][0]
    name = Path(manual["title"]).stem.removesuffix(manual["version"]).strip()
    reviewed = date.fromisoformat(sources["last_reviewed"])
    return (
        f"Based on the RPI OGE {name} ({manual['version']}) · "
        f"last reviewed {reviewed.day} {reviewed:%b %Y} · template v{class_version()[0]}"
        + (" (beta)" if class_version()[0].startswith("0.") else "")
    )


def last_commit(source):
    """Date of the last commit that changed `source`; None without Git history."""
    try:
        day = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", source],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
        ).stdout.strip()
        return date.fromisoformat(day) if day else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def build_id():
    """The full commit SHA being built: GITHUB_SHA in CI, else `git rev-parse HEAD`;
    '' without either. The same commit always gives the same identifier (local
    uncommitted edits do not change it)."""
    sha = os.environ.get("GITHUB_SHA", "").strip().lower()
    if not sha:
        try:
            sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                 text=True, timeout=20).stdout.strip().lower()
        except (OSError, subprocess.SubprocessError):
            sha = ""
    return sha if re.fullmatch(r"[0-9a-f]{40}", sha) else ""


def whats_new():
    """The home page's "What's new" line: the release the website links, its date,
    and the start of its first change-log item, read from CHANGELOG.md."""
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section = re.search(rf"(?ms)^## {re.escape(RELEASE_VERSION)}\b[^\n]*?,\s*([^\n]+)\n(.*?)(?=^## |\Z)", text)
    if not section:
        return None
    item = re.search(r"(?ms)^- (.*?)(?=^- |^\S|\Z)", section[2])
    if not item:
        return None
    plain = re.sub(r"[*`]", "", " ".join(item[1].split()))
    plain = re.sub(r"^[^:]{1,40}:\s*", lambda m: m[0] if len(plain) < 30 else "", plain)
    cut = re.search(r"[,;.](\s|$)", plain[20:])
    plain = plain[: 20 + cut.start()] if cut else plain
    return {"version": RELEASE_VERSION, "date": escape(section[1].strip()),
            "highlight": escape(plain[0].upper() + plain[1:])}


def last_updated(source):
    """'14 Oct 2026' from the last commit that changed `source`; '' without Git history."""
    day = last_commit(source)
    return f"{day.day} {day:%b %Y}" if day else ""


def svg_size(path):
    """(width, height) from an SVG's viewBox, so the page reserves its space; None if unknown."""
    try:
        match = re.search(r'viewBox="\s*[\d.-]+[\s,]+[\d.-]+[\s,]+([\d.]+)[\s,]+([\d.]+)',
                          path.read_text(encoding="utf-8"))
    except OSError:
        return None
    return (round(float(match[1])), round(float(match[2]))) if match else None


def slug(heading):
    """GitHub-style heading id, as Pandoc's gfm reader makes it."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def viewer_link(css_class, dialog_id, back_id, file_url, text):
    """The link that opens a full-size picture. Its address is the picture file, so
    without JavaScript it simply shows the picture; viewer.js opens the dialog
    named by data-viewer instead."""
    return (f'<a class="{css_class}" id="{back_id}" href="{escape(file_url)}" '
            f'data-viewer="{dialog_id}">{text}</a>')


def viewer_dialog(dialog_id, back_id, label, picture):
    """A full-size picture on the same page, closed until viewer.js opens it as a
    modal dialog (Escape, Close or a click outside closes it, and focus returns to
    the link). Without JavaScript the dialog stays hidden and the link goes to the
    picture file."""
    return (f'<dialog class="viewer" id="{dialog_id}" aria-label="{label}">'
            f'<a class="viewer-close" href="#{back_id}">Close<span class="visually-hidden"> the full-size picture</span></a>'
            '<p class="viewer-hint">Scroll sideways to see the whole picture.</p>'
            f'{picture}</dialog>')


def size_attrs(size):
    return f' width="{size[0]}" height="{size[1]}"' if size else ""


def responsive_tables(body):
    """A scroll box lets wide tables scroll on phones without losing table semantics.
    In a table, code with spaces (a whole error message) is marked so it may wrap,
    and a long token such as an \\includegraphics line may break anywhere; names
    and keys such as graduation-month stay on one line (site.css)."""
    def table_code(code):
        text = code[1]
        style = "phrase" if re.search(r"\s", text) else "long" if len(text) > 32 else ""
        return f'<code class="{style}">{text}</code>' if style else code[0]

    def label_cells(table):
        # data-label repeats each column header on phones, where rows stack (site.css)
        head = re.search(r"<thead>(.*?)</thead>", table, flags=re.S)
        if not head:
            return table
        labels = [re.sub(r"<[^>]+>", "", th).strip()
                  for th in re.findall(r"<th\b[^>]*>(.*?)</th>", head[1], flags=re.S)]

        def row(match):
            index = iter(range(len(labels) + 99))

            def cell(td):
                column = next(index)
                if column == 0 or column >= len(labels) or not labels[column]:
                    return td[0]
                return f'<td data-label="{escape(unescape(labels[column]))}"{td[1]}'
            return re.sub(r"<td\b([^>]*>)", cell, match[0])
        return re.sub(r"<tbody>.*?</tbody>",
                      lambda part: re.sub(r"<tr\b.*?</tr>", row, part[0], flags=re.S), table, flags=re.S)

    return re.sub(r"<table\b.*?</table>",
                  lambda m: '<div class="table-wrap" tabindex="0" role="group" aria-label="Table, scroll horizontally if needed">'
                  + label_cells(re.sub(r"<code>([^<]*)</code>", table_code, m[0]))
                  + "</div>", body, flags=re.S)


def keep_short_code(body):
    """Short code such as rpi-thesis.cls or graduation-month never breaks at a hyphen.
    A path such as chapters/01-introduction.tex may still break after a slash, so
    it cannot push a phone screen wider than the screen."""
    def keep(match):
        if match[1]:
            return match[0]
        text = match[2]
        if "/" in text:
            parts = text.split("/")
            pieces = [f'<span class="nowrap">{part}</span>' if part else "" for part in parts]
            return '<code class="keep-path">' + "/<wbr>".join(pieces) + "</code>"
        return f'<code class="keep">{text}</code>'

    return re.sub(r"(<pre\b[^>]*>)?<code>([^<\s]{1,28})</code>", keep, body)


# LaTeX highlighting for ```tex, ```latex and ```bibtex blocks, done here so it
# needs no JavaScript. site/tools-highlight.js uses the same pattern and class
# names for tool output; the colors are the --code-* tokens in site/site.css.
LATEX_TOKENS = re.compile(
    r"(\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]|\$\$[\s\S]*?\$\$|\$(?:[^$\\\n]|\\.)+\$)"  # math
    r"|(\\(?:[A-Za-z@]+\*?|[^A-Za-z@\n]))"   # a command, or an escaped character such as \%
    r"|(%[^\n]*)"                             # a comment
    r"|([{}])|(\[)|(\])"                      # braces; brackets around options
    r"|(@[A-Za-z]+)")                          # a BibTeX entry type
BIBTEX_FIELD = re.compile(r"([A-Za-z][\w-]*)(?=\s*=)")


def highlight_latex(text, bibtex=False):
    """Plain LaTeX -> HTML with tok-* spans. Text inside [ ] on one line is an option."""
    out, depth, pos = [], 0, 0

    def span(name, piece):
        out.append(f'<span class="tok-{name}">{escape(piece, quote=False)}</span>')

    def plain(piece):
        nonlocal depth
        for index, line in enumerate(piece.split("\n")):
            if index:
                out.append("\n")
                depth = 0
            if not line:
                continue
            if depth:
                span("opt", line)
            elif bibtex:
                last = 0
                for match in BIBTEX_FIELD.finditer(line):
                    out.append(escape(line[last:match.start()], quote=False))
                    span("opt", match[1])
                    last = match.end()
                out.append(escape(line[last:], quote=False))
            else:
                out.append(escape(line, quote=False))

    for match in LATEX_TOKENS.finditer(text):
        plain(text[pos:match.start()])
        pos = match.end()
        math, command, comment, brace, opening, closing, entry = match.groups()
        if opening:
            depth += 1
            span("opt", opening)
        elif closing:
            span("opt", closing)
            depth = max(0, depth - 1)
        elif math:
            span("math", math)
        elif command or entry:
            span("cmd", command or entry)
        elif comment:
            span("com", comment)
        else:
            span("brace", brace)
    plain(text[pos:])
    return "".join(out)


def home_tool(name):
    """(doodle, one-line description) of a tool from the home page's list
    (site/index.html), so the header's Tools menu says what the home page says."""
    home = (ROOT / "site/index.html").read_text(encoding="utf-8")
    found = re.search(r'<li>(<svg class="doodle tk-icon"(?:(?!</svg>).)*</svg>)<p><a href="docs/'
                      + re.escape(name) + r'\.md">[^<]*</a> <span>([^<]*)</span>', home, flags=re.S)
    if not found:
        raise SystemExit(f"site/index.html: the toolkit list has no entry for docs/{name}.md; "
                         "add it there (its doodle and one line), so the header's Tools menu can show it.")
    return found[1].replace('class="doodle tk-icon"', 'class="doodle nav-menu-icon"', 1), found[2]


def tool_mark(body, name):
    """Put the tool's doodle from the home page's toolkit list (site/index.html)
    before its title, so each tool is drawn the same way in both places."""
    home = (ROOT / "site/index.html").read_text(encoding="utf-8")
    found = re.search(r'<li>(<svg class="doodle tk-icon"(?:(?!</svg>).)*</svg>)<p><a href="docs/'
                      + re.escape(name) + r'\.md">', home, flags=re.S)
    if not found:
        return body
    mark = found[1].replace('class="doodle tk-icon"', 'class="doodle tool-mark"', 1)
    return re.sub(r"(<h1\b[^>]*>)", lambda m: m[1] + mark, body, count=1)


def highlight_code(body):
    """Color the LaTeX and BibTeX examples Pandoc left as plain code."""
    def paint(match):
        return f'{match[1]}<code>{highlight_latex(unescape(match[3]), match[2] == "bibtex")}</code></pre>'
    return re.sub(r'(<pre class="(tex|latex|bibtex)">)<code>(.*?)</code></pre>', paint, body, flags=re.S)


class SearchText(HTMLParser):
    """Visible text from a small rendered fragment (never interpret markup)."""
    def __init__(self, html):
        super().__init__()
        self.parts = []
        self.ids = set()
        self.feed(html)
        self.text = " ".join("".join(self.parts).split())

    def handle_data(self, text):
        self.parts.append(text)

    def handle_starttag(self, tag, attrs):
        value = dict(attrs).get("id")
        if value:
            self.ids.add(value)


def search_disclosures(body):
    """Give optional examples stable destinations without changing source prose."""
    used = SearchText(body).ids

    def identify(match):
        attrs, opening, label = match.groups()
        if re.search(r"\bid\s*=", attrs):
            return match[0]
        stem = "example-" + re.sub(r"[^a-z0-9]+", "-", SearchText(label).text.lower()).strip("-")[:100]
        anchor, number = stem, 2
        while anchor in used:
            anchor, number = f"{stem}-{number}", number + 1
        used.add(anchor)
        return f'<details{attrs} id="{anchor}">{opening}{label}</summary>'

    return re.sub(r"<details\b([^>]*)>(\s*<summary\b[^>]*>)(.*?)</summary>", identify, body, flags=re.S)


class Site:
    def __init__(self, offline):
        source_path("site/site.json")  # refuses a linked settings file
        config = site_config()
        self.repo = config.get("repository_url", "").rstrip("/")
        self.url = "" if offline else config.get("site_url", "").rstrip("/")
        self.site_url = config.get("site_url", "").rstrip("/")  # the offline check-pdf page links it
        # Cookie-less page counts on the website only; empty turns them off,
        # and the offline guide never counts anything.
        self.analytics = "" if offline else config.get("cloudflare_analytics_token", "")
        self.offline = offline
        # The exact commit this website was built from, on every online page and
        # in build.txt, so a live check can tell which build is being served.
        # The offline guide carries none: it is frozen with its release.
        self.build_id = "" if offline else build_id()
        self.settings = settings.load()
        self.errors, self.warnings = [], []
        self.previews = {}       # name -> {width, height, page}, from previews.make()
        self.cheatsheet = ""     # where the cheat sheet PDF is, relative to the site root
        self.edition = edition()
        self.meta = {}           # output page -> (title, description), checked after the build
        self.search = []         # guide sections only; never project or local files
        self.search_tasks = []   # task-link labels also describe their destinations
        guide = "" if offline else "guide/"
        self.pages = {"site/index.html": "index.html"}
        # A guide page in NAV whose Markdown file is not written yet is left
        # out with a warning, and links to it keep only their text.
        self.planned = set()
        for name, _, _ in GUIDE + [QUICK]:
            if name not in PAGE_TAGS:
                self.errors.append(f"docs/{name}.md: give the page a tag in TAGS in scripts/build_site.py.")
            if (ROOT / f"docs/{name}.md").is_file():
                self.pages[f"docs/{name}.md"] = f"{guide}{name}.html"
            else:
                self.planned.add(f"docs/{name}.md")
                self.warnings.append(f"docs/{name}.md is in NAV but not written yet; left out of the guide.")
        for source, (name, _) in PROJECT.items():
            if not (offline and source.startswith("docs/project/")):
                self.pages[source] = f"project/{name}.html"
        self.assets = {"site/site.css": "site.css", "site/logo.svg": "logo.svg",
                       "site/copy.js": "copy.js",       # optional "Copy" buttons on code blocks
                       "site/viewer.js": "viewer.js",   # optional: full-size pictures open as a dialog
                       "site/theme.js": "theme.js",     # optional: saved System/Light/Dark appearance
                       "site/search.js": "search.js",   # optional: offline section search
                       "site/share.js": "share.js",     # optional: the home page's "Share this guide" button
                       "site/tools-highlight.js": "tools-highlight.js"}   # optional: colored LaTeX in tool output
        self.assets.update({f"site/{name}": name for name in EXPLAIN})  # optional: "Explain my error" page
        if not offline:  # optional: "Check your PDF" page; online only (see PDF_CHECK)
            self.assets.update({f"site/{name}": name for name in PDF_CHECK})
            self.assets.update({f"site/{name}": name for name in BIB_CHECK})
            self.assets.update({f"site/settings/{name}.js": f"settings/{name}.js" for name in ("core", "ui")})
        self.assets.update({f"site/{name}": name for name in CONVERT})  # "Bring your work in", online and offline
        self.starter_zip = self.overleaf = ""
        if not offline and self.repo:
            version = RELEASE_VERSION
            base = f"{self.repo}/releases/download/{RELEASE_TAG}"
            self.starter_zip = f"{base}/rpi-thesis-starter-v{version}.zip"
            overleaf = "https://www.overleaf.com/docs?snip_uri=" + quote(f"{base}/rpi-thesis-overleaf-v{version}.zip", safe="")
            self.overleaf = overleaf   # the home page's "Open in Overleaf" button
            for source, links in (("README.md", [self.starter_zip]), ("docs/get-started.md", [self.starter_zip, overleaf])):
                text = (ROOT / source).read_text(encoding="utf-8")
                for link in links:
                    if link not in text:
                        self.errors.append(f"{source}: link the release files of {RELEASE_TAG} "
                                           f"(RELEASE_TAG and RELEASE_VERSION in scripts/build_site.py): {link}")
        if not offline:  # GitHub Pages serves /404.html; the link-preview picture is online only
            self.pages["site/404.html"] = "404.html"
            self.assets["site/og-image.png"] = "og-image.png"
        for folder, output, suffixes in (
            ("site/fonts", "fonts", {".woff2", ".txt"}),
            ("site/art", "art", {".svg"}),  # landing-page drawings
            ("docs/diagrams", "diagrams", {".svg"}),
        ):
            for path in sorted(source_path(folder).glob("*")):
                if path.is_file() and path.suffix in suffixes:
                    self.assets[f"{folder}/{path.name}"] = f"{output}/{path.name}"
        self.theme_assets = {
            output for source, output in self.assets.items()
            if Path(source).suffix == ".svg"
            and SVG_SCHEME.search(source_path(source).read_text(encoding="utf-8"))
        }
        source, heading = FEEDBACK
        # The form's address is written once, in that section; a link marked
        # data-form elsewhere points there in Markdown and at the form here.
        form = re.search(r"\[help and feedback form\]\((https://[^)\s]+)\)", (ROOT / source).read_text(encoding="utf-8"))
        self.form_url = form[1] if form else ""
        self.feedback = self.pages[source]
        if re.search(rf"(?m)^#+ {re.escape(heading)}\s*$", (ROOT / source).read_text(encoding="utf-8")):
            self.feedback += "#" + slug(heading)
        else:
            self.warnings.append(
                f"{source} has no '## {heading}' section; "
                "the footer Ask for help link opens the top of that page."
            )

    @staticmethod
    def relative(here, target):
        return posixpath.relpath(target, posixpath.dirname(here) or ".")

    def theme_pictures(self, html, here, absolute=False):
        """Manual choices use fixed SVG copies, including Safari and offline files.
        Original SVG URLs remain the no-JavaScript and System fallback."""
        def url(path):
            return (self.url or "") + "/" + path if absolute else self.relative(here, path)

        variants = {url(path): (url(f"themes/light/{path}"), url(f"themes/dark/{path}"))
                    for path in self.theme_assets}

        def picture(match):
            tag = match[0]
            attribute = "srcset" if tag.startswith("<source") else "src"
            if tag.startswith("<link"):
                if not re.search(r'\brel="icon"', tag):
                    return tag
                attribute = "href"
            source = re.search(rf'\b{attribute}="([^"]+)"', tag)
            if not source or unescape(source[1]) not in variants:
                return tag
            original = unescape(source[1])
            light, dark = variants[original]
            attributes = (f' data-theme-asset="{attribute}" data-theme-system="{escape(original)}"'
                          f' data-theme-light="{escape(light)}" data-theme-dark="{escape(dark)}"')
            ending = "/>" if tag.endswith("/>") else ">"
            return tag[:-len(ending)] + attributes + ending

        return re.sub(r"<(?:img|source|link)\b[^>]*>", picture, html)

    def link(self, href, source, here, base):
        """Rewrite a link from `source` for output page `here`. None = keep the text only."""
        parts = urlsplit(unescape(href))
        if parts.scheme or parts.netloc or not parts.path:
            return unescape(href)
        target = posixpath.normpath(posixpath.join(base, unquote(parts.path)))
        # Keep ?query and #fragment (an SVG's #id, a PDF's #page=2) on every kind of link.
        fragment = ("?" + parts.query if parts.query else "") + (
            "#" + parts.fragment if parts.fragment else "")
        if target in self.pages:
            return quote(self.relative(here, self.pages[target])) + fragment
        if target in self.assets:
            return quote(self.relative(here, self.assets[target])) + fragment
        if target in CHEATSHEET_SOURCES and self.cheatsheet:  # the PDF, when built
            return self.relative(here, self.cheatsheet) + fragment
        if target.startswith("docs/diagrams/"):  # planned diagram, not drawn yet
            return quote(self.relative(here, "diagrams/" + posixpath.basename(target))) + fragment
        if target in self.planned:  # planned guide page, not written yet
            self.warnings.append(f"{source}: link to a guide page not written yet: {href}")
            return None
        if target.startswith("..") or not (ROOT / target).exists():
            self.errors.append(f"{source}: link to a missing file: {href}")
            return None
        if self.repo:  # a file outside the website, e.g. main.tex: link to GitHub
            kind = "tree" if (ROOT / target).is_dir() else "blob"
            # The offline guide is frozen with its release: link that release's files,
            # not the moving main branch. The website follows main.
            ref = "v" + class_version()[0] if self.offline else "main"
            return f"{self.repo}/{kind}/{ref}/{quote(target)}{fragment}"
        return None

    def rewrite(self, html, source, here, base, markdown_only=False):
        def anchor(match):
            before, href, after, text = match.groups()
            if markdown_only and not re.search(r"\.md(#|$)", href):
                return match[0]
            new = self.link(href, source, here, base)
            if new is None:
                return text
            return f'<a{before} href="{escape(new)}"{after}>{text}</a>'

        html = re.sub(r'<a\b([^>]*?)\shref="([^"]*)"([^>]*)>(.*?)</a>', anchor, html, flags=re.S)
        if not markdown_only:
            html = re.sub(
                r'(<img\b[^>]*?\ssrc=")([^"]*)(")',
                lambda m: m[1] + escape(self.link(m[2], source, here, base) or m[2]) + m[3],
                html,
            )
            # Authored picture sources use one URL, like the generated diagrams.
            html = re.sub(
                r'(<source\b[^>]*?\ssrcset=")([^"\s,]+)(")',
                lambda m: m[1] + escape(self.link(m[2], source, here, base) or m[2]) + m[3],
                html,
            )
        return html

    @staticmethod
    def diagrams(html):
        """Each diagram from docs/diagrams/ becomes a figure with a "View larger"
        link under it that shows the drawing large on the same page (viewer_dialog).
        If docs/diagrams/NAME-narrow.svg exists, phones get that taller drawing
        instead (the <picture> element picks it)."""
        seen = {}

        def figure(match):
            tag, src, name = match[1], match[2], match[3]
            seen[name] = seen.get(name, 0) + 1
            key = name if seen[name] == 1 else f"{name}-{seen[name]}"
            alt = re.search(r'\salt="([^"]*)"', tag)
            wide = svg_size(ROOT / f"docs/diagrams/{name}.svg")
            if wide and not re.search(r"\swidth=", tag):  # reserve the space before the drawing loads
                tag = tag[:-1].rstrip("/").rstrip() + size_attrs(wide) + ">"
            big = f'<img src="{src}" alt="{alt[1] if alt else ""}"{size_attrs(wide)} loading="lazy">'
            narrow_path = ROOT / f"docs/diagrams/{name}-narrow.svg"
            narrow_file = narrow_path.is_file()
            if narrow_file:
                narrow = src[: -len(".svg")] + "-narrow.svg"
                tag = (f'<picture><source media="(max-width: 600px)" srcset="{narrow}"'
                       f'{size_attrs(svg_size(narrow_path))}>{tag}</picture>')
            return (
                f'<figure class="diagram{" has-narrow" if narrow_file else ""}" id="fig-{key}">{tag}'
                + viewer_link("diagram-open", f"view-{key}", f"open-{key}", src, "View larger")
                + viewer_dialog(f"view-{key}", f"open-{key}", "Diagram, full size", big)
                + "</figure>"
            )

        return re.sub(r'<p>(<img\b[^>]*?\ssrc="([^"]*?diagrams/([\w-]+)\.svg)"[^>]*>)</p>', figure, html)

    def pictures(self, html, source, here):
        """A guide page asks for a picture from previews.py with a Markdown comment
        on its own line:  <!-- preview compile-pass-1-chapter: alt text -->
        The comment becomes that picture when this build made it (--previews) and
        disappears otherwise. GitHub hides comments, so the page reads the same
        there, which is why the text around each comment must not need it."""
        def figure(match):
            name, alt = match[1], " ".join(match[2].split())
            size = self.previews.get(name)
            if not size:
                if self.previews:
                    self.warnings.append(f"{source}: no preview picture named {name}")
                return ""
            src = self.relative(here, f"previews/{name}.png")
            # The alt text's first clause ("Chapter 1 after step 1") is also the
            # visible caption, so similar pictures side by side can be told apart.
            caption = re.match(r"(.+?)[.:](?:\s|$)", alt)
            caption = f"<figcaption>{escape(caption[1])}</figcaption>" if caption else ""
            return (f'<figure class="shot"><div class="shot-scroll" tabindex="0" role="region" '
                    f'aria-label="PDF example, scroll sideways if needed"><img src="{src}" alt="{escape(alt)}" '
                    f'width="{size["width"]}" height="{size["height"]}" loading="lazy"></div>{caption}</figure>')

        html = html.replace("<!-- class-demo -->", self.class_demo(here))
        return re.sub(r"<!--\s*preview ([\w-]+):(.*?)-->", figure, html, flags=re.S)

    def class_demo(self, here):
        """CSS-only class switcher, absent when its previews were not made.
        Native radios provide keyboard selection without JavaScript; without
        CSS both labeled versions remain visible.
        """
        variants = (("ams", "amsart"), ("ieee", "IEEEtran"))
        if not all("class-demo-" + key in self.previews for key, _ in variants):
            return ""
        controls, panels = [], []
        for key, cls in variants:
            name = "class-demo-" + key
            size = self.previews[name]
            crop = name + "-crop"
            inline = self.previews.get(crop, size)
            selected = ' checked' if key == "ams" else ""
            controls.append(f'<input type="radio" name="class-demo" id="choose-{name}"{selected}>'
                            f'<label for="choose-{name}">{cls}</label>')
            src = self.relative(here, f"previews/{name}.png")
            inline_src = self.relative(here, f"previews/{crop if crop in self.previews else name}.png")
            count = size["pages"]
            caption = (f'Top of page 1 of {count}.' if crop in self.previews
                       else f'Page 1 of {count}.') + ' Same source; only the class name changes.'
            alt = (f'First page of the shared teaching example in {cls}: '
                   + ("one column, centered headings." if key == "ams" else "two columns, Roman-numbered headings."))
            picture = (f'<img src="{src}" alt="{escape(alt)}" width="{size["width"]}" '
                       f'height="{size["height"]}" loading="eager">')
            inline_picture = (f'<img src="{inline_src}" alt="{escape(alt)}" width="{inline["width"]}" '
                              f'height="{inline["height"]}" loading="eager">')
            panels.append(
                f'<div class="class-demo-panel class-demo-{key}">'
                f'<p class="class-demo-line"><code>\\documentclass{{<mark>{cls}</mark>}}</code></p>'
                f'<figure>{inline_picture}<figcaption>{caption}</figcaption></figure>'
                + viewer_link("diagram-open", f"view-{name}", f"open-{name}", src,
                              f'View larger<span class="visually-hidden">: {cls} example</span>')
                + viewer_dialog(f"view-{name}", f"open-{name}", f"{cls} example, full size", picture)
                + '</div>')
        return ('<fieldset class="class-demo"><legend>Change the class name</legend>'
                + ''.join(controls) + '<div class="class-demo-panels">' + ''.join(panels)
                + '</div></fieldset>')

    @staticmethod
    def page_top(body, name):
        """Put the page's tag under its title and, on a page with TOC_MIN or more
        ## sections, an "On this page" list after the opening paragraph. Returns
        (body, [{href, label}]); the template also shows the list beside the
        text on wide screens."""
        if name in PAGE_TAGS:
            tag, css = PAGE_TAGS[name]
            badge = (f'<p class="page-tag"><span class="tag tag-{css}">'
                     f'<span class="visually-hidden">When you need this page: </span>{escape(tag)}</span></p>')
            body = re.sub(r"</h1>", lambda m: m[0] + "\n" + badge, body, count=1)
        toc = [
            {"href": "#" + anchor, "label": escape(unescape(re.sub(r"<[^>]+>", "", text)).strip())}
            for anchor, text in re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', body, flags=re.S)
        ]
        if len(toc) < TOC_MIN:
            return body, []
        links = "".join(f'<li><a href="{entry["href"]}">{entry["label"]}</a></li>' for entry in toc)
        box = (f'<details class="page-toc"><summary>On this page</summary>'
               f'<nav aria-label="On this page"><ol role="list">{links}</ol></nav></details>')
        opening = re.search(r'</h1>\s*(?:<p class="page-tag">.*?</p>\s*)?(?:<p>.*?</p>)?', body, flags=re.S)
        if opening:
            body = body[: opening.end()] + "\n" + box + body[opening.end() :]
        return body, toc

    def external_links(self, html):
        """Keep the guide available when students visit a tool or official resource.
        Internal navigation, email links and downloads keep their normal behavior."""
        def external_tab(match):
            before, href, after, text = match.groups()
            url = unescape(href)
            parts = urlsplit(url)
            internal = self.url and (url == self.url or url.startswith(self.url + "/"))
            download = (re.search(r"\bdownload(?:\s|=|$)", before + after)
                        or parts.path.lower().endswith(".zip")
                        or "/releases/download/" in parts.path)
            if parts.scheme not in ("http", "https") or internal or download:
                return match[0]
            attrs = re.sub(r'\s+(?:target|rel)="[^"]*"', "", before + after)
            # The last word carries the new-tab arrow (site.css), so the arrow never wraps alone.
            last = re.search(r"(<code\b[^>]*>[^<]*</code>|[^\s<>]+)(\s*)$", text)
            if re.search(r'class="[^"]*\bbutton\b', attrs):   # a button's label is one piece, its arrow after it
                text = f'<span class="ext-last">{text}</span>'
            elif last and len(last[1]) <= 30:  # a long address may wrap (site.css)
                text = text[:last.start()] + f'<span class="ext-last">{last[1]}</span>' + last[2]
            return (f'<a{attrs} href="{href}" target="_blank" rel="noopener">{text}'
                    '<span class="visually-hidden"> (opens in a new tab)</span></a>')

        return re.sub(r'<a\b([^>]*?)\shref="([^"]*)"([^>]*)>(.*?)</a>',
                      external_tab, html, flags=re.S)

    def search_messages(self, body, here, title):
        """Make each troubleshooting row a precise, searchable destination."""
        context, used = title, set()

        def row(match):
            nonlocal context
            html = match[0]
            if html.startswith("<h"):
                context = SearchText(html).text
                return html
            cells = re.findall(r"<td\b[^>]*>(.*?)</td>", html, flags=re.S)
            if len(cells) < 2:
                return html
            label = SearchText(cells[0]).text
            stem = "message-" + re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:100]
            anchor, number = stem, 2
            while anchor in used:
                anchor, number = f"{stem}-{number}", number + 1
            used.add(anchor)
            self.search.append({"page": title, "title": label, "context": context,
                                "href": here + "#" + anchor, "kind": "message",
                                "signatures": [SearchText(code).text for code in re.findall(
                                    r"<code>(.*?)</code>", cells[0], flags=re.S)
                                    if len(SearchText(code).text) >= 10],
                                "text": " ".join(SearchText(cell).text for cell in cells[1:])})
            return html.replace("<tr", f'<tr id="{anchor}"', 1)

        return re.sub(r"<h[1-6]\b[^>]*>.*?</h[1-6]>|<tr\b[^>]*>.*?</tr>", row, body, flags=re.S)

    def explain_page(self, body, source):
        """Put the known problems (KNOWN_PROBLEMS in scripts/build.py) into the
        "Explain my error" page twice: as the table everyone sees, with or
        without JavaScript, and as JSON for site/explain/ui.js."""
        marker = '<div class="explain-known" data-explain-known></div>'
        if marker not in body:
            self.errors.append(f"{source}: keep the line {marker}; the table of known messages goes there.")
            return body
        rows = []
        for entry in build_helper.KNOWN_PROBLEMS:
            page, anchor, section = entry["guide"]
            rows.append(f"<tr><td><code>{escape(entry['message'])}</code></td><td>{escape(entry['means'])}</td>"
                        f"<td>{escape(entry['fix'])} More: <a href=\"{page}.html#{anchor}\">{escape(section)}</a>.</td></tr>")
        table = ("<table>\n<thead>\n<tr><th>What you see</th><th>What it means</th><th>What to try</th></tr>\n"
                 "</thead>\n<tbody>\n" + "\n".join(rows) + "\n</tbody>\n</table>")
        fields = ("id", "pattern", "means", "fix", "editor", "overleaf", "guide")
        payload = json.dumps([{key: entry[key] for key in fields if key in entry}
                              for entry in build_helper.KNOWN_PROBLEMS],
                             ensure_ascii=True, separators=(",", ":"))
        return (body.replace(marker, table, 1) + '\n<script type="application/json" id="explain-problems">'
                + payload.replace("<", "\\u003c") + "</script>\n")

    def offline_checker(self, body, source):
        """The offline guide has no PDF checker (see PDF_CHECK): drop its form and
        say where it runs, keeping the paragraph that points to the checklist."""
        widget = re.compile(r'<div class="[^"]*\bpdf-check\b[^"]*" data-pdf-check\b.*?<div class="pdf-check-results[^"]*"></div></div>\s*', re.S)
        intro = re.compile(r'<p class="pdf-check-nojs[^"]*" data-pdf-check-nojs>The checker needs JavaScript[^.]*\.')
        if not self.site_url or not widget.search(body) or not intro.search(body):
            self.errors.append(f"{source}: the offline guide replaces the checker form and the paragraph starting "
                               "\"The checker needs JavaScript\" with a link to the website (site_url in "
                               "site/site.json); keep both, or update offline_checker in scripts/build_site.py.")
            return body
        link = escape(self.site_url + "/guide/check-pdf.html", quote=True)
        note = ('<p class="pdf-check-nojs tool-nojs tool-offline">The checker runs on the toolkit\'s website, not in this offline copy '
                f'of the guide: open <a href="{link}">Check your PDF</a> there. Your PDF still stays on your '
                'computer.')
        return intro.sub(lambda _: note, widget.sub("", body, count=1), count=1)

    def offline_bibcheck(self, body, source):
        """Replace online-only reference controls with the website route."""
        interactive = re.compile(r"<!-- bibcheck-interactive-start -->.*?<!-- bibcheck-interactive-end -->", re.S)
        if not self.site_url or not interactive.search(body):
            self.errors.append(f"{source}: keep the bibcheck-interactive markers and site_url in site/site.json "
                               "so the offline guide can link the online checker.")
            return body
        link = escape(self.site_url + "/guide/check-references.html", quote=True)
        note = ('<p>This offline copy includes the checklist below. For the interactive check, '
                f'open <a href="{link}">Check your references on the toolkit website</a>. '
                'Your files stay in your browser; nothing is uploaded.</p>')
        return interactive.sub(lambda _: note, body, count=1)

    def offline_settings(self, body, source):
        """The offline guide has no settings form: say where it runs, not that JavaScript is off."""
        intro = re.compile(r'<p class="tool-nojs" data-settings-nojs>The form needs JavaScript[^.]*\.')
        if not self.site_url or not intro.search(body):
            self.errors.append(f"{source}: the offline guide replaces the sentence starting \"The form needs "
                               "JavaScript\" with a link to the website (site_url in site/site.json); keep it, "
                               "or update offline_settings in scripts/build_site.py.")
            return body
        link = escape(self.site_url + "/guide/settings-builder.html", quote=True)
        note = ('<p class="tool-nojs tool-offline" data-settings-nojs>The form runs on the toolkit\'s website, not in this offline '
                f'copy of the guide: open <a href="{link}">Settings builder</a> there.')
        return intro.sub(lambda _: note, body, count=1)

    def changelog_page(self, body):
        """The change log on the website: each release's "Changes your PDF?" answer
        as a tag students can scan, and under each heading its download and its
        code changes on GitHub, for anyone who wants the detail."""
        versions = re.findall(r'<h2 id="[^"]*">(\d+\.\d+\.\d+) \(beta\)', body)
        def meta(match):
            # During the beta, many versions share a day: the heading is just the
            # version (a short "On this page" list); its date leads the line under it.
            anchor, version, date = match[1], match[2], match[3]
            later = versions.index(version) + 1
            links = [escape(date), f'Pre-release <code>v{version}</code>']
            if self.repo:
                links.append(f'<a href="{self.repo}/releases/download/v{version}/rpi-thesis-starter-v{version}.zip">'
                             'Download</a>')
                if later < len(versions):
                    links.append(f'<a href="{self.repo}/compare/v{versions[later]}...v{version}">Code changes</a>')
                else:
                    links.append(f'<a href="{self.repo}/tree/v{version}">Code</a>')
            return (f'<h2 id="{anchor}">{version}</h2><p class="release-meta">'
                    + '<span class="sep" aria-hidden="true">·</span>'.join(links) + '</p>')
        body = re.sub(r'<h2 id="([^"]*)">(\d+\.\d+\.\d+) \(beta\), ([^<]*)</h2>\s*'
                      r'<p>Published as the pre-release <code[^>]*>v\2</code>\.</p>', meta, body)
        def answer(match):
            text = match[1].strip()
            if re.match(r"No\b", text):   # "No." alone, or "No visible change." kept as written
                kind, word, rest = "no", "No", re.sub(r"^No(?:[.,:]\s*|\s*$)", "", text)
                rest = rest or "Only the guide, the website, scripts, or examples changed; your thesis looks the same."
            elif re.match(r"Yes\b", text):
                kind, word, rest = "yes", "Yes", re.sub(r"^Yes[.,:]?\s*", "", text)
            elif text.startswith("Not applicable"):
                kind, word, rest = "first", "New", "The first version."
            else:   # "Only if ...": some theses
                kind, word, rest = "some", "Some", text
            rest = rest[:1].upper() + rest[1:]
            return (f'<div class="release-pdf release-pdf-{kind}"><p class="release-pdf-word" aria-hidden="true">{word}</p>'
                    f'<div><p class="release-pdf-q">Changes your PDF?<span class="visually-hidden"> {word}.</span></p>'
                    f'<p>{rest}</p></div></div>')
        body = re.sub(r'<p><strong>Changes your PDF\?</strong> (?!<)(.*?)</p>', answer, body, flags=re.S)
        # Unreleased work: say what it means; "**Version:**" only steers scripts/bump.py.
        body = re.sub(r'<p><strong>Version:</strong>[^<]*</p>\s*', "", body)
        return re.sub(r'(<h2 id="unreleased">)Unreleased(</h2>)',
                      r'\1Coming next\2<p class="release-meta">Guide and website changes are already live;'
                      r' changes to the starter files arrive with the next download.</p>', body)

    def render(self, source):
        here = self.pages[source]
        if source == "site/index.html":
            kind, title, description, body = "home", NAME, HOME_DESCRIPTION, ""
        elif source == "site/404.html":
            kind, title, description = "notfound", "Page not found", HOME_DESCRIPTION
            body = (ROOT / source).read_text(encoding="utf-8")
        else:
            kind = "guide" if source.startswith("docs/") and source.count("/") == 1 else "project"
            title, description, text = read_markdown(source)
            if title == NAME:
                title = PROJECT[source][1]
            # {{rule:id}} and {{cite:id}} name a row of the requirements map (scripts/rules.py).
            text = text.replace("{{settings-table}}", self.settings["table"])
            text, problems, _ = rules.expand(text, source)
            self.errors.extend(problems)
            body = pandoc(["--from=gfm", "--to=html5", "--wrap=none", "--syntax-highlighting=none"], text)
            if self.form_url:
                body = re.sub(r'(<a\b[^>]*\bdata-form\b[^>]*\bhref=")[^"]*(")|(<a\b[^>]*\bhref=")[^"]*("[^>]*\bdata-form\b)',
                              lambda m: (m[1] or m[3]) + escape(self.form_url, quote=True) + (m[2] or m[4]), body)
            body = self.rewrite(body, source, here, posixpath.dirname(source))
            if source == "docs/explain-my-error.md":
                body = self.explain_page(body, source)
            if source == "CHANGELOG.md":
                body = self.changelog_page(body)
            if source == "docs/troubleshooting.md":
                body = self.search_messages(body, here, title)
            if source == f"docs/{QUICK[0]}.md":
                for href, label in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', body, flags=re.S):
                    address = urlsplit(unescape(href))
                    if not address.scheme and not address.netloc:
                        target = posixpath.normpath(posixpath.join(posixpath.dirname(here), address.path))
                        self.search_tasks.append((target, address.fragment, SearchText(label).text))
            body = self.diagrams(body)
            body = self.pictures(body, source, here)
            body = responsive_tables(body)
            body = keep_short_code(body)
            body = highlight_code(body)
            if Path(source).stem in PAGE_SCRIPTS:
                body = tool_mark(body, Path(source).stem)
            if Path(source).stem == "check-pdf" and not self.offline:  # the page script reads rules and measurements
                body += rules.embed()
            if Path(source).stem == "check-pdf" and self.offline:
                body = self.offline_checker(body, source)
            if Path(source).stem == "check-references" and self.offline:
                body = self.offline_bibcheck(body, source)
            if Path(source).stem == "settings-builder" and self.offline:
                body = self.offline_settings(body, source)
            # The PDF checker compares a PDF's class version with the release the website links.
            body = body.replace('data-pdf-check data-version=""', f'data-pdf-check data-version="{RELEASE_VERSION}"')
            # Keyboard users must also be able to pan long code lines without
            # JavaScript, including Safari's non-focusable scroll containers.
            body = re.sub(r"<pre\b", '<pre tabindex="0"', body)
            # Safari drops list semantics from lists without bullets unless told.
            body = re.sub(r'<ul class="task-list"', '<ul role="list" class="task-list"', body)
            toc = []
            if kind == "guide":
                body = search_disclosures(body)
                self.search.extend(SearchSections(body, here, title).entries)
                body, toc = self.page_top(body, Path(source).stem)
            elif kind == "project":   # long reference pages (change log, requirements map) get the same list
                body, toc = self.page_top(body, Path(source).stem)

        def item(path, label, name=None):
            entry = {"href": self.relative(here, path), "label": escape(label)}
            if name in PAGE_TAGS and PAGE_TAGS[name][0] in SIDEBAR_TAGS:
                entry.update(tag=escape(PAGE_TAGS[name][0]), tagclass=PAGE_TAGS[name][1])
            return {**entry, "current": True} if path == here else entry

        def guide_item(name, label):
            source = f"docs/{name}.md"
            return item(self.pages[source], label, name) if source in self.pages else None

        chain = [(name, label, top) for name, label, top in GUIDE if f"docs/{name}.md" in self.pages]
        nav = [guide_item(name, label) for name, label, _ in chain]
        quick = guide_item(*QUICK[:2])
        groups = []
        for stage, pages in NAV:
            entries = [entry for entry in (guide_item(name, label) for name, label, _ in pages) if entry]
            groups.append({"label": escape(stage), "pages": entries})
        header = [entry for entry, (_, _, top) in zip(nav, chain) if top]
        if quick and QUICK[2]:
            header.append(quick)
        # The header: Get started, a Guide menu, a Tools menu, How do I...?
        groups_by_name = dict(NAV)
        start = guide_item(*groups_by_name["Core path"][0][:2])
        guide_menu = [entry for entry in (guide_item(name, label) for name, label, _ in
                      groups_by_name["Core path"][1:] + groups_by_name["Go further"]) if entry]
        tools_menu = []
        for name, label, _ in groups_by_name["Tools"]:
            entry = guide_item(name, label)
            if entry:
                icon, blurb = home_tool(name)
                tools_menu.append({**entry, "icon": icon, "blurb": blurb})
        values = {
            "lang": "en",
            "kind": kind,
            "title": escape(title),
            "pagetitle": escape(HOME_TITLE if kind == "home" else f"{title} · {NAME}"),
            "description": escape(description),
            "root": self.relative(here, "x")[:-1],
            "search_root": (self.url or "") + "/" if kind == "notfound" else self.relative(here, "x")[:-1],
            "nav": nav + ([quick] if quick else []),
            "navgroups": groups,
            "header": header,
            "menu_start": start,
            "menu_guide": guide_menu,
            "menu_guide_current": any(entry.get("current") for entry in guide_menu),
            "menu_tools": tools_menu,
            "menu_tools_current": any(entry.get("current") for entry in tools_menu),
            "menu_quick": quick,
            "project": [
                item(self.pages[path], label)
                for path, (_, label) in PROJECT.items()
                if label and path in self.pages
            ],
            # Footer "Tools" column: the sidebar's Tools group in its order, then the
            # reviewer checklist (and the cheat sheet, in the template).
            "tools": [entry for entry in (guide_item(name, label) for name, label in
                      [(name, label) for name, label, _ in dict(NAV)["Tools"]]
                      + [("reviewer-checklist", "Reviewer checklist")]) if entry],
            "edition": escape(self.edition),
            "feedback_url": self.relative(here, self.feedback),
            "search_field": search_field("dialog-search"),
        }
        if quick:
            values["quick"] = quick
        if kind == "home":
            values["home"] = True
            news = whats_new()
            if news:
                values["whats_new"] = news
            if self.site_url:  # "Share this guide": an e-mail link; share.js adds share or copy, no trackers
                values["share_link"] = escape(self.site_url + "/")
                values["share_url"] = escape("mailto:?subject=" + quote("RPI Thesis Toolkit")
                                             + "&body=" + quote("A free, unofficial LaTeX starter and guide for "
                                                                "RPI theses and dissertations: " + self.site_url + "/"))
            if self.starter_zip:
                values["starter_zip"] = self.starter_zip
            if self.overleaf:
                values["overleaf_url"] = escape(self.overleaf)
        if kind == "guide":
            names = [name for name, _, _ in chain]
            if Path(source).stem in names:
                index = names.index(Path(source).stem)
                if index > 0:
                    values["prev"] = nav[index - 1]
                if index + 1 < len(nav):
                    values["next"] = nav[index + 1]
                    next_tag = PAGE_TAGS[chain[index + 1][0]][0]
                    if next_tag == "If you have a draft":
                        values["next_label"] = next_tag
                    elif next_tag == "Optional":
                        values["next_label"] = "Optional next page"
            # Quick answers are a task index, not a step in the linear guide.
            values["pager"] = bool(values.get("prev") or values.get("next"))
            values["updated"] = last_updated(source)
            # Tool pages use a wider column and no "On this page" rail (the box
            # in the text stays), so forms, the converter and results have room.
            if Path(source).stem in PAGE_SCRIPTS:
                values["tool"] = True
            elif toc:
                values["toc"] = toc
            if Path(source).stem in PAGE_SCRIPTS and (not self.offline or Path(source).stem in OFFLINE_SCRIPTS):
                values["page_script"] = PAGE_SCRIPTS[Path(source).stem]
        if kind == "project" and toc:   # long reference pages: the same "On this page" list
            values["toc"] = toc
        if kind == "notfound":
            values["notfound"] = True
        else:  # every indexed page needs its own title and description
            self.meta[here] = (values["pagetitle"], values["description"])
        if self.url and (ROOT / "site/og-image.png").exists():
            values.update(og_image=self.url + "/og-image.png", og_image_alt=escape(OG_ALT))
        if self.url and kind != "notfound":
            values["canonical"] = self.url + "/" + ("" if here == "index.html" else here)
        if self.repo:
            values["repo_url"] = self.repo
            values["edit_url"] = f"{self.repo}/edit/main/{source}"
        if self.offline:
            values["offline"] = True
        if self.build_id:
            values["build_id"] = self.build_id
        if self.analytics:
            values["analytics_token"] = self.analytics
        if self.cheatsheet:
            values.update(cheatsheet_url=self.relative(here, self.cheatsheet), cheatsheet_pdf=True)
        elif self.repo:
            values["cheatsheet_url"] = f"{self.repo}/tree/main/cheatsheet"
        args = ["--from=markdown", "--to=html5", "--quiet"]
        args.append("--template=" + str(source_path("site/guide-template.html")))
        args += [f"--variable-json={key}:{json.dumps(value)}" for key, value in values.items()]
        html = pandoc(args, f"{FENCE}{{=html}}\n{body}\n{FENCE}\n")
        if kind in ("home", "notfound"):  # these link guide pages by their Markdown file
            html = self.rewrite(html, source, here, "", markdown_only=True)
        if kind == "notfound":  # served at any depth, so every local link starts from the site root
            base = (self.url or "") + "/"
            html = re.sub(r'((?:href|src)=")(?![a-z]+:|/|#)', r"\g<1>" + base, html)
        html = self.external_links(html)
        return self.theme_pictures(html, here, absolute=kind == "notfound")


def search_field(name):
    """The dialog's ordinary input and real result links."""
    return ('<section class="guide-search" data-search hidden aria-label="Search the guide">'
            f'<label for="{name}" class="visually-hidden">Search the guide</label>'
            f'<input id="{name}" type="search" placeholder="Try a topic or paste an error" '
            f'autocomplete="off" spellcheck="false" maxlength="4000" '
            f'aria-describedby="{name}-hint {name}-status" aria-controls="{name}-results">'
            f'<p class="search-hint" id="{name}-hint">Keywords, questions, commands, or pasted errors.</p>'
            f'<p class="search-status" id="{name}-status" role="status" aria-live="polite" '
            'aria-atomic="true"></p>'
            f'<ol class="search-results" id="{name}-results" role="list"></ol></section>')


def make_previews(destination):
    """Pictures of the sample thesis (scripts/previews.py); {} without LaTeX."""
    from previews import make

    return make(destination / "previews")


def reuse_previews(destination, final):
    """Builds without --previews (quick website builds and the offline guide) reuse
    the pictures of the last build_site.py --previews run (dist/site/previews),
    as package.py reuses its cheat sheet; {} if none.
    Each picture records a hash of the thesis files and of previews.py it was
    made from (previews.fingerprint); pictures made from anything else are
    stale and left out."""
    from previews import fingerprint, read

    source = ROOT / "dist/site/previews"
    if not source.is_dir() or source.is_symlink():
        return {}
    pictures = [path for path in source.glob("*.png") if path.is_file() and not path.is_symlink()]
    current = fingerprint()
    made = read(source)
    if pictures and any(made.get(path.stem, {}).get("fingerprint") != current for path in pictures):
        print("WARNING: the sample-thesis pictures in dist/site/previews were made from other thesis "
              "files (or an older previews.py), so the offline guide leaves them out. Run "
              "build_site.py --previews first.")
        return {}
    (destination / "previews").mkdir()
    for path in pictures:
        shutil.copyfile(path, destination / "previews" / path.name)
    return read(destination / "previews")


def reuse_cheatsheet(destination):
    """Copy the last built cheat sheet into a build without --cheatsheet, if it is
    newer than its source; False otherwise (the website then links the source)."""
    pdf = ROOT / "dist/site" / CHEATSHEET_PDF
    if not pdf.is_file() or pdf.stat().st_mtime < (ROOT / "cheatsheet/cheatsheet.tex").stat().st_mtime:
        return False
    target = destination / CHEATSHEET_PDF
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf, target)
    return True


def build_cheatsheet(destination):
    """Compile cheatsheet/cheatsheet.tex into the website; False without pdfLaTeX.
    pdfLaTeX is run directly, so a personal latexmkrc cannot move the output."""
    if not shutil.which("pdflatex"):
        print("SKIP cheat sheet: pdflatex not found. The website links to its source instead.")
        return False
    with tempfile.TemporaryDirectory() as temp:
        shutil.copyfile(ROOT / "cheatsheet/cheatsheet.tex", Path(temp) / "cheatsheet.tex")
        for _ in range(2):  # the second pass settles TikZ positions
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape",
                 "cheatsheet.tex"],
                cwd=temp, capture_output=True, text=True, errors="replace", timeout=300,
            )
            if result.returncode:
                tail = "\n".join(result.stdout.splitlines()[-20:])
                raise SystemExit(f"cheatsheet/cheatsheet.tex did not compile:\n{tail}")
        if "(1 page" not in result.stdout:
            print("WARNING: the cheat sheet is longer than one page; see cheatsheet/README.md.")
        target = destination / CHEATSHEET_PDF
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(temp) / "cheatsheet.pdf", target)
    print(f"Cheat sheet: {target}")
    return True


def write_sitemap(site, destination):
    """sitemap.xml (every page but 404.html, with its canonical address) and a
    robots.txt that allows everything and points to it."""
    entries = []
    for source, output in site.pages.items():
        if source == "site/404.html":
            continue
        address = site.url + "/" + ("" if output == "index.html" else output)
        day = last_commit(source)
        lastmod = f"<lastmod>{day.isoformat()}</lastmod>" if day else ""
        entries.append(f"  <url><loc>{escape(address)}</loc>{lastmod}</url>")
    (destination / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries) + "\n</urlset>\n",
        encoding="utf-8",
    )
    (destination / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {site.url}/sitemap.xml\n", encoding="utf-8"
    )


@contextlib.contextmanager
def build_lock(destination):
    """Hold an OS lock for the build; process exit releases it after a crash.

    Keep the lock file in place: unlinking or renaming it can let concurrent
    builders lock different files at the same pathname. Its PID is advisory.
    """
    lock = destination.parent / f".{destination.name}.lock"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(lock, os.O_CREAT | os.O_RDWR, 0o644), "r+b") as handle:
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise SystemExit(f"Cannot take the build lock for {destination.name}: {error}. "
                             "Wait for any other build to finish, then retry.") from None
        try:
            handle.seek(0)
            handle.write(str(os.getpid()).encode("ascii"))
            handle.truncate()
            handle.flush()
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def build_site(destination=None, offline=False, previews=False, cheatsheet=False, publish=False,
               complete=False):
    """Build the website, or with offline=True the guide for the starter ZIP.
    Offline, cheatsheet=True means the caller puts OFFLINE_CHEATSHEET beside
    the destination folder, so the guide links to it. The build happens in a
    sibling folder, which replaces `destination` only after every check passes.
    publish=True is the strict mode for deployment (see the module docstring).
    complete=True is the content gate the starter ZIP uses: every guide page in
    NAV, every referenced diagram and every sample-thesis picture must exist
    and the build must produce no warnings. It does not check the release
    version (that is publish's job)."""
    check_pandoc()
    destination = Path(destination or ROOT / "dist/site").absolute()
    with build_lock(destination):
        for old in destination.parent.glob(f"{destination.name}.tmp-*"):  # left by a killed build
            if old.is_dir() and not old.is_symlink():
                shutil.rmtree(old, ignore_errors=True)
        stage = destination.parent / f"{destination.name}.tmp-{os.getpid()}"
        try:
            shutil.rmtree(stage, ignore_errors=True)
            stage.mkdir()
            build_into(stage, destination, offline, previews, cheatsheet, publish, complete)
            old = destination.parent / f"{destination.name}.old-{os.getpid()}"
            moved = destination.exists()
            if moved:
                destination.rename(old)
            try:
                stage.rename(destination)
            except OSError:
                if moved:  # put the previous site back; it is still the good one
                    if destination.exists():
                        shutil.rmtree(destination, ignore_errors=True)
                    old.rename(destination)
                raise
            shutil.rmtree(old, ignore_errors=True)
        finally:
            shutil.rmtree(stage, ignore_errors=True)
    print(f"Site ready: {destination}")
    return destination


def drawing_colors():
    """Every color in the drawings (docs/diagrams, site/art, the logo and the
    link-preview card) must be a color of site/site.css, so a palette change
    there cannot leave a drawing behind."""
    tokens = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", (SITE / "site.css").read_text(encoding="utf-8"))}
    errors = []
    drawings = sorted((ROOT / "docs/diagrams").glob("*.svg")) + sorted((SITE / "art").glob("*.svg")) + \
        [SITE / "logo.svg", SITE / "og-card.svg"]
    for path in drawings:
        stray = sorted({h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", path.read_text(encoding="utf-8"))} - tokens)
        if stray:
            errors.append(f"{path.relative_to(ROOT)}: {', '.join(stray)} is not a color in site/site.css; "
                          "use the matching token's color (section 2) so the drawing follows the palette.")
    return errors


def drawing_code_style():
    """The code classes every drawing's <style> carries: the LaTeX colors of
    site/site.css (the --code-* tokens and tok-* rules), c-cmd for tok-cmd."""
    css = (SITE / "site.css").read_text(encoding="utf-8")
    lines = ["    .c-tex, .c-bib, .c-md { fill: var(--ink); }"]
    for name, token in re.findall(r"--code-(\w+):\s*var\(--([\w-]+)\)", css):
        rule = re.search(r"\.tok-" + name + r"\s*\{\s*color:\s*var\(--code-" + name + r"\);\s*([^}]*?)\s*\}", css)
        lines.append(f"    .c-{name} {{ fill: var(--{token}); {rule[1] + ' ' if rule and rule[1] else ''}}}")
    return "\n".join(lines) + "\n"


def drawing_code(text, bibtex=False):
    """One line of LaTeX (or BibTeX) as the tspans a drawing draws it with:
    highlight_latex's coloring, so a drawing matches the website's code."""
    return highlight_latex(text, bibtex).replace('<span class="tok-', '<tspan class="c-').replace("</span>", "</tspan>")


def drawing_code_colors():
    """Code in the drawings is colored as on the website. A line or bit of code
    is a <text> or <tspan> with class c-tex (LaTeX), c-bib (BibTeX) or c-md
    (Markdown) holding only plain text and c-* tspans; for LaTeX and BibTeX the
    pieces must be exactly drawing_code's."""
    style = drawing_code_style()
    kinds = {"c-tex", "c-bib", "c-md"}
    colors = {"c-cmd", "c-brace", "c-opt", "c-math", "c-com"}

    def classes(element):
        return set(element.get("class", "").split())

    def pieces(element):
        """[(color or "", text)] of a code element, or None if a child is not a bare c-* tspan."""
        out = [("", element.text or "")]
        for child in element:
            if child.tag.rpartition("}")[2] != "tspan" or set(child.attrib) != {"class"} or len(child) \
                    or not classes(child) <= colors or len(classes(child)) != 1:
                return None
            out += [(child.get("class"), child.text or ""), ("", child.tail or "")]
        merged = []
        for color, text in out:
            if merged and merged[-1][0] == color:
                merged[-1] = (color, merged[-1][1] + text)
            elif text:
                merged.append((color, text))
        return merged

    errors = []
    drawings = sorted((ROOT / "docs/diagrams").glob("*.svg")) + sorted((SITE / "art").glob("*.svg"))
    for path in drawings:
        svg, name = path.read_text(encoding="utf-8"), path.relative_to(ROOT)
        if style not in svg:
            errors.append(f"{name}: its <style> lacks the code classes; paste these lines before </style> "
                          f"(made from the LaTeX colors in site/site.css):\n{style}")
        for rule in re.findall(r"[^{}]*\{[^{}]*monospace[^{}]*\}|style=\"[^\"]*monospace[^\"]*\"", svg):
            if "font-variant-ligatures: none" not in rule:
                errors.append(f"{name}: {rule.strip()[:60]}... sets a code font; add font-variant-ligatures: none "
                              "so code shows the characters typed, as on the website.")
        try:
            root = ElementTree.fromstring(svg)
        except ElementTree.ParseError as problem:
            errors.append(f"{name}: not well-formed SVG ({problem}); fix the markup there.")
            continue
        inside = set()
        for element in root.iter():
            kind = classes(element) & kinds
            if not kind:
                continue
            inside.update(element.iter())
            code = "".join(element.itertext())
            found = pieces(element)
            if found is None:
                errors.append(f"{name}: in the code {code!r}, use only plain text and "
                              '<tspan class="c-cmd|c-brace|c-opt|c-math|c-com"> with no other attributes.')
            elif kind != {"c-md"}:
                expected = drawing_code(code, kind == {"c-bib"})
                if found != pieces(ElementTree.fromstring(f"<t>{expected}</t>")):
                    errors.append(f"{name}: the code {code!r} is not colored as on the website; "
                                  f"write it as {expected}")
        for element in root.iter():
            if element in inside:
                continue
            if classes(element) & colors:
                errors.append(f"{name}: {element.text!r} has a c-* code color outside a <text> or <tspan> "
                              "with class c-tex, c-bib or c-md.")
            elif classes(element) & {"code", "m"} and re.search(r"\\[A-Za-z]", "".join(element.itertext())):
                errors.append(f"{name}: the code {''.join(element.itertext())!r} needs class c-tex and the "
                              "website's colors on its tspans (scripts/build_site.py, drawing_code).")
    return errors


def stylesheet_colors():
    """Colors live in one place: the tokens before "3. Base" in site/site.css.
    After it, a rule may use a token, or neutral black, white or gray (print,
    shadows); any other color there is an error, so the palette cannot split."""
    css = (SITE / "site.css").read_text(encoding="utf-8")
    start = css.index("/* ---------- 3. Base")
    errors = []
    for match in re.finditer(r"#([0-9a-fA-F]{3,8})\b", css[start:]):
        digits = match[1].lower()
        rgb = [digits[i] * 2 for i in range(3)] if len(digits) in (3, 4) else [digits[i:i + 2] for i in (0, 2, 4)]
        if len(set(rgb)) > 1:   # not a gray
            line = css[:start + match.start()].count("\n") + 1
            errors.append(f"site/site.css line {line}: {match[0]} is a color outside the tokens; "
                          "add or use a token in section 2 instead.")
    return errors


def build_into(destination, final, offline, previews, cheatsheet, publish, complete=False):
    """Write and check the site in `destination` (the staging folder); `final` is
    where it will end up."""
    site = Site(offline)
    site.errors.extend(checker_ids())
    site.errors.extend(drawing_colors())
    site.errors.extend(drawing_code_colors())
    site.errors.extend(stylesheet_colors())
    checks = (SITE / "pdf-check/core.js").read_text(encoding="utf-8")
    pinned = re.search(r'PDFJS_VERSION = "([^"]+)"', checks)
    for name in PDF_CHECK[3:]:
        if not pinned or f'"{pinned.group(1)}"' not in (SITE / name).read_text(encoding="utf-8"):
            site.errors.append(f"site/{name} is not the pdf.js version in PDFJS_VERSION (site/pdf-check/core.js); "
                               "set it to the version you vendored, as the comment there says.")
    if publish:
        version = class_version()[0]
        if version != RELEASE_VERSION:
            site.errors.append(
                f"rpi-thesis.cls is v{version} but the website links release {RELEASE_TAG} "
                f"(v{RELEASE_VERSION}): publish the matching release first, then update "
                "RELEASE_TAG and RELEASE_VERSION in scripts/build_site.py.")
    for source, output in site.assets.items():
        source_path(source)
        (destination / output).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, destination / output)
        if output in site.theme_assets:
            text = (destination / output).read_text(encoding="utf-8")
            for theme in ("light", "dark"):
                target = destination / "themes" / theme / output
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(svg_appearance(text, theme), encoding="utf-8")
    if not offline:
        (destination / "settings/data.js").write_text(settings.javascript(site.settings), encoding="utf-8")
    if previews:
        site.previews = make_previews(destination)
    else:  # reuse the last --previews pictures if they still match their sources
        site.previews = reuse_previews(destination, final)
    if cheatsheet and offline:  # package.py adds the PDF beside guide/
        site.cheatsheet = "../" + OFFLINE_CHEATSHEET
    elif cheatsheet and build_cheatsheet(destination):
        site.cheatsheet = CHEATSHEET_PDF
    elif not offline and reuse_cheatsheet(destination):  # quick builds keep a current PDF
        site.cheatsheet = CHEATSHEET_PDF
    if not offline:  # the starter ZIP already contains the class
        (destination / CLASS_DOWNLOAD).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "rpi-thesis.cls", destination / CLASS_DOWNLOAD)
    strict = publish or complete  # missing content stops the build instead of warning
    if strict:
        missing = [name for name in REQUIRED_PREVIEWS if name not in site.previews]
        if missing:
            site.errors.append(("--publish" if publish else "The complete guide")
                               + " needs every sample-thesis picture (run build_site.py --previews with "
                               "LaTeX, after your last change to the thesis files); missing: "
                               + ", ".join(missing))
    if publish and not offline:
        if not site.cheatsheet:
            site.errors.append("--publish needs the cheat sheet PDF (run with --previews or --cheatsheet and LaTeX).")
    for source, output in site.pages.items():
        source_path(source)
        (destination / output).parent.mkdir(parents=True, exist_ok=True)
        (destination / output).write_text(site.render(source), encoding="utf-8")
    by_link = {entry["href"]: entry for entry in site.search}
    for page, anchor, task in site.search_tasks:
        target = by_link.get(page + "#" + anchor) if anchor else next(
            (entry for entry in site.search if entry["href"].split("#")[0] == page), None)
        if target is not None:
            target["tasks"] = (target.get("tasks", "") + " " + task).strip()
    site.warnings.extend(search_route_problems(site.search))
    # A classic script also loads from file: URLs, with no fetch or server.
    index = json.dumps(site.search, ensure_ascii=True, separators=(",", ":"))
    (destination / "search-index.js").write_text("window.GUIDE_SEARCH = " + index + ";\n", encoding="utf-8")
    for position, label in ((0, "title"), (1, "description")):
        seen = {}
        for page, meta in site.meta.items():
            if not meta[position]:
                site.errors.append(f"{page}: no {label}; add a first paragraph or a 'description:' line.")
            elif meta[position] in seen:
                problem = f"{page} and {seen[meta[position]]} share the {label} {meta[position]!r}"
                (site.errors if label == "title" else site.warnings).append(problem)
            seen.setdefault(meta[position], page)
    if site.url:  # search engines only; the offline guide has no address
        write_sitemap(site, destination)
    if site.build_id:  # read by scripts/release.py live
        (destination / BUILD_FILE).write_text(f"commit={site.build_id}\nrelease={RELEASE_TAG}\n", encoding="utf-8")
    elif publish:
        site.errors.append("--publish needs the commit SHA for build.txt: build inside a Git "
                           "checkout or set GITHUB_SHA.")
    beside = {OFFLINE_CHEATSHEET} if site.cheatsheet.startswith("../") else set()
    errors, warnings, count = validate(destination, beside, site.search)
    problems = site.warnings + warnings
    for warning in problems:
        print(("ERROR (" + ("--publish" if publish else "complete guide") + "): " if strict
               else "WARNING: ") + warning)
    if strict:  # a missing page, diagram or picture must stop a deployment or a release ZIP
        errors = errors + problems
    if site.errors or errors:
        raise SystemExit("Website check failed (the previous site, if any, is untouched):\n- "
                         + "\n- ".join(site.errors + errors))
    print(f"PASS: {count} pages; local links, anchors and ids work; no LaTeX sources, archives, "
          "RPI artwork, or PDFs other than the cheat sheet staged.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--previews", action="store_true",
        help="add pictures of the sample thesis and the cheat sheet PDF "
        "(needs LaTeX, plus poppler or Ghostscript)",
    )
    parser.add_argument(
        "--cheatsheet", action="store_true",
        help="compile cheatsheet/cheatsheet.tex into the website (needs LaTeX)",
    )
    parser.add_argument(
        "--publish", action="store_true",
        help="strict mode for deployment: fail when the class version is not the published "
        f"release (v{RELEASE_VERSION}), a guide page or diagram is missing, or the sample-thesis "
        "pictures or cheat sheet were not built (use with --previews)",
    )
    args = parser.parse_args()
    destination = build_site(previews=args.previews, cheatsheet=args.cheatsheet or args.previews,
                             publish=args.publish)
    print("Open in a browser: " + str(destination / "index.html"))


if __name__ == "__main__":
    main()
