"""Checks of the built website, for build_site.py and verify.py.

What the website may hold (the allowed file types and the named scripts and
downloads), offline checks of every local link, anchor, and referenced file
(validate), the guide sections the search index is made from
(SearchSections), the section titles site/search.js names, and the rule and
measurement ids the PDF checker uses. Python standard library only.
"""
from html import unescape
from html.parser import HTMLParser
import json
import re
from urllib.parse import quote, unquote, urlsplit

from common import ROOT
import rules  # scripts/rules.py: the OGE rules in docs/project/requirements.md

# ---- what the website may hold ----------------------------------------------

ALLOWED = {".html", ".css", ".svg", ".woff2"}  # plus fonts/*.txt, previews/*.png|webp, og-image.png,
                                              # sitemap.xml, robots.txt, build.txt and the named scripts below
# Online only: "commit=<SHA>" and "release=<RELEASE_TAG>", one per line. Every online
# page also carries <meta name="rpi-thesis-build" content="SHA">; release.py reads both.
BUILD_FILE = "build.txt"
# The "Check your PDF" page (docs/check-pdf.md) reads a student's PDF in the
# browser: ui.js (the page), core.js (the checks), and Mozilla's pdf.js, kept
# unchanged with its license. core.js lists every rule and measurement id it
# uses in RULE_IDS and MEASURE_IDS (checker_ids); each must be a row of
# docs/project/requirements.md, whose rules and measurements the page carries
# as JSON (rules.embed()). core.js says how to update pdf.js; its PDFJS_VERSION
# must match the vendored files. The offline guide leaves all of these out
# (browsers such as Chrome refuse to start the reader from a file: page) and
# its check-pdf page links the website's checker instead.
PDF_CHECK = ["pdf-check/ui.js", "pdf-check/core.js", "pdf-check/pdfjs/LICENSE",
             "pdf-check/pdfjs/pdf.min.mjs", "pdf-check/pdfjs/pdf.worker.min.mjs"]
# The "Bring your work in" page (docs/bring-your-work-in.md) converts pasted
# text to LaTeX in the browser: ui.js (the page) and core.js (the readers and
# the LaTeX writer). Both run in the offline guide too.
CONVERT = ["convert/ui.js", "convert/core.js"]
SITE_SCRIPTS = {"copy.js", "viewer.js", "theme.js", "search.js", "search-index.js", "share.js", *PDF_CHECK, *CONVERT}
# The one PDF the website may hold: the cheat sheet (no RPI artwork), built
# from cheatsheet/cheatsheet.tex with --previews or --cheatsheet. The offline
# guide never holds it; package.py puts it at the ZIP root, beside guide/, as
# OFFLINE_CHEATSHEET, and the offline guide links there.
CHEATSHEET_PDF = "downloads/rpi-thesis-cheatsheet.pdf"
# The newest class file, at a permanent address: students update by replacing
# their copy with this one (docs/going-further.md). Only the website carries it;
# --publish keeps it equal to the released class.
CLASS_DOWNLOAD = "downloads/rpi-thesis.cls"
FORBIDDEN_FOLDERS = {".git", "_local", "reference", "assets", "build"}


# ---- the search index --------------------------------------------------------

SEARCH_STRING = r"\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*'"


def search_route_problems(search):
    """Section titles that site/search.js names (routes, answers for pasted
    log lines, fallbacks) must still exist, or those searches quietly degrade."""
    script = (ROOT / "site/search.js").read_text(encoding="utf-8")
    named = []
    for block in re.findall(r"var (?:routes|logRoutes) = \[(.*?)\n  \];", script, flags=re.S):
        for array in re.findall(rf"\[\s*((?:{SEARCH_STRING})(?:\s*,\s*(?:{SEARCH_STRING}))*)\s*\]", block):
            named += re.findall(SEARCH_STRING, array)
    named += re.findall(rf"\btitle === ({SEARCH_STRING})", script)
    for array in re.findall(rf"\[((?:{SEARCH_STRING})(?:\s*,\s*(?:{SEARCH_STRING}))*)\]"
                            r"\.(?:includes\(entry\.source\.title\)|map\(function \(page\))", script):
        named += re.findall(SEARCH_STRING, array)
    titles = {entry["title"] for entry in search}
    return [f"site/search.js names the section {title!r}, which no guide page has; "
            "update the title there to match the renamed heading"
            for title in sorted({re.sub(r"\\(.)", r"\1", literal[1:-1]) for literal in named} - titles)]


class SearchSections(HTMLParser):
    """Read guide sections before navigation is added; Pandoc owns heading IDs.

    Keep full section text so commands and errors near the end are searchable.
    """
    def __init__(self, body, page, title):
        super().__init__()
        self.entries, self.words, self.heading = [], [], []
        self.page, self.title = page, title
        self.anchor, self.label = "", title
        self.level, self.parents, self.skip = 0, {}, 0
        self.details, self.summary = [], None
        self.feed(body)
        self.flush()
        # Text before and after an optional example belongs to the same
        # section, but the example itself has its own direct destination.
        merged = {}
        for entry in self.entries:
            if entry["href"] in merged:
                merged[entry["href"]]["text"] += " " + entry["text"]
            else:
                merged[entry["href"]] = entry
        self.entries = list(merged.values())

    def flush(self):
        text = " ".join("".join(self.words).split())   # block tags add the spaces; inline code does not
        if self.label and (text or self.anchor):
            self.entries.append({"page": self.title, "title": self.label,
                                 "context": " / ".join(self.parents.values()),
                                 "href": self.page + ("#" + quote(self.anchor) if self.anchor else ""),
                                 "text": text})
        self.words = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "svg"}:
            self.skip += 1
        if self.skip:
            return
        if tag == "details":
            self.flush()
            self.details.append((self.anchor, self.label, self.parents.copy()))
            self.anchor, self.label = dict(attrs).get("id", ""), ""
        elif tag == "summary" and self.details:
            self.summary = []
        elif re.fullmatch(r"h[1-6]", tag):
            self.flush()
            self.level, self.heading = int(tag[1]), []
            self.anchor = dict(attrs).get("id", "")
            self.parents = {level: label for level, label in self.parents.items() if level < self.level}
        elif tag in {"p", "li", "tr", "td", "th", "pre", "br", "summary"}:
            self.words.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "svg"}:
            self.skip = max(0, self.skip - 1)
        elif not self.skip and tag == "summary" and self.summary is not None:
            self.label = " ".join("".join(self.summary).split())
            self.summary = None
        elif not self.skip and tag == "details" and self.details:
            self.flush()
            self.anchor, self.label, self.parents = self.details.pop()
        elif not self.skip and re.fullmatch(r"h[1-6]", tag):
            self.label = " ".join("".join(self.heading).split())
            self.parents[self.level] = self.label
            self.level = 0
        elif tag in {"p", "li", "tr", "td", "th", "pre", "summary"}:
            self.words.append(" ")

    def handle_data(self, data):
        if not self.skip:
            (self.summary if self.summary is not None else self.heading if self.level else self.words).append(data)


# ---- links, anchors, and files -----------------------------------------------

class PageLinks(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links, self.ids, self.duplicates = [], set(), set()
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("id"):
            if attributes["id"] in self.ids:
                self.duplicates.add(attributes["id"])
            self.ids.add(attributes["id"])
        if tag == "a" and attributes.get("name"):
            self.ids.add(attributes["name"])
        for name in ("href", "src", "data-theme-light", "data-theme-dark", "data-theme-system"):
            if attributes.get(name):
                self.links.append(attributes[name])
        for candidate in (attributes.get("srcset") or "").split(","):
            if candidate.strip():
                self.links.append(candidate.split()[0])


CSS_URL = re.compile(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)")
SVG_REF = re.compile(r'\b(?:xlink:)?href="([^"]*)"')
SVG_ID = re.compile(r'\bid="([^"]*)"')


def validate(destination, beside=(), search=()):
    """Check links and anchors offline, and that nothing private or binary is staged.
    `beside` names files the caller puts next to the website folder (the offline
    cheat sheet); links to them are allowed. Returns (errors, warnings, page count); missing
    diagrams/ files are only warnings."""
    errors, warnings, parsed = [], [], {}
    root = destination.resolve()

    def parse(path):
        if path not in parsed:
            parsed[path] = PageLinks(path)
        return parsed[path]

    svg_ids = {}

    def ids_of(svg):
        if svg not in svg_ids:
            svg_ids[svg] = set(SVG_ID.findall(svg.read_text(encoding="utf-8")))
        return svg_ids[svg]

    pages = sorted(root.rglob("*.html"))
    # Generated search links need the same anchor checks as page links.
    for entry in search:
        address = urlsplit(entry["href"])
        target = (root / unquote(address.path)).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            errors.append(f"search-index.js: missing guide page: {entry['href']}")
        elif address.fragment and unquote(address.fragment) not in parse(target).ids:
            errors.append(f"search-index.js: missing heading: {entry['href']}")
    for page in pages:
        name = page.relative_to(root).as_posix()
        for duplicate in sorted(parse(page).duplicates):
            errors.append(f"{name}: the id {duplicate!r} is used more than once")
        for link in parse(page).links:
            address = urlsplit(link)
            if address.scheme or address.netloc:
                continue
            folder = root if address.path.startswith("/") else page.parent
            target = (folder / unquote(address.path).lstrip("/")).resolve() if address.path else page
            if target.parent == root.parent and target.name in beside:
                continue
            if not target.is_relative_to(root):
                errors.append(f"{name}: link leaves the website: {link}")
                continue
            # Web servers serve index.html for the home URL and directory
            # links; check that page and its anchors rather than the folder.
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                planned = target.relative_to(root).parts[:1] == ("diagrams",)
                (warnings if planned else errors).append(f"{name}: missing file: {link}")
            elif address.fragment and target.suffix == ".html":
                if unquote(address.fragment) not in parse(target).ids:
                    errors.append(f"{name}: missing heading or anchor: {link}")
            elif address.fragment and target.suffix == ".svg" and not target.is_symlink():
                if unquote(address.fragment) not in ids_of(target):
                    errors.append(f"{name}: missing id in the picture: {link}")
    # Files that other files load: fonts and pictures named in CSS url(...), and
    # local files or #fragments named by an SVG's href / xlink:href / url(...).
    # Root-relative addresses start at the website folder.
    for path in sorted(root.rglob("*")):
        if path.suffix not in (".css", ".svg") or path.is_symlink():
            continue
        name = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        references = [match[2] for match in CSS_URL.finditer(text)]
        if path.suffix == ".svg":
            references += SVG_REF.findall(text)
        for reference in references:
            address = urlsplit(unescape(reference.strip()))
            if address.scheme or address.netloc or (not address.path and not address.fragment):
                continue  # data: URIs, web addresses
            if address.path.startswith("/"):
                target = (root / unquote(address.path).lstrip("/")).resolve()
            else:
                target = (path.parent / unquote(address.path)).resolve() if address.path else path.resolve()
            if not target.is_relative_to(root):
                errors.append(f"{name}: reference leaves the website: {reference}")
            elif not target.is_file():
                errors.append(f"{name}: missing file: {reference}")
            elif address.fragment and target.suffix == ".svg":
                if unquote(address.fragment) not in ids_of(target):
                    errors.append(f"{name}: missing id: {reference}")
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        top, suffix = relative.parts[0], path.suffix.lower()
        if path.is_symlink():
            errors.append(f"Symlink not allowed in the website: {relative}")
        elif FORBIDDEN_FOLDERS.intersection(relative.parts):
            errors.append(f"Private or source folder in the website: {relative}")
        elif path.is_dir() or suffix in ALLOWED:
            pass
        elif relative.as_posix() in {"og-image.png", CHEATSHEET_PDF, CLASS_DOWNLOAD, "sitemap.xml", "robots.txt",
                                     BUILD_FILE} | SITE_SCRIPTS:
            pass
        elif not (top == "previews" and suffix in {".png", ".webp"}) and not (
            top == "fonts" and suffix == ".txt"
        ):
            errors.append(
                f"Not allowed in the website: {relative} (PDFs, LaTeX sources, archives, "
                "and pictures outside previews/ stay out)"
            )
        if suffix == ".svg" and re.search(r"<image\b|data:image", path.read_text(encoding="utf-8")):
            errors.append(f"{relative}: embedded picture in a diagram; draw it with vector shapes")
    return errors, warnings, len(pages)


# ---- the PDF checker's rule ids ------------------------------------------------

def checker_ids(script="pdf-check/core.js", text=None):
    """Problems with the rule and measurement ids the PDF checker uses (PDF_CHECK).
    core.js lists them all in RULE_IDS and MEASURE_IDS (one JSON list each) and
    refuses any other id when it runs; each must be a row of the requirements map."""
    known_rules, known_measures = rules.load()
    text = (ROOT / "site" / script).read_text(encoding="utf-8") if text is None else text
    problems = []
    for name, kind, known in (("RULE_IDS", "rule", known_rules), ("MEASURE_IDS", "measurement", known_measures)):
        found = re.findall(rf"^\s*var {name} = (\[.*\]);\s*$", text, re.M)
        try:
            keys = json.loads(found[0]) if len(found) == 1 else None
        except ValueError:
            keys = None
        if not isinstance(keys, list) or not keys or not all(isinstance(key, str) for key in keys):
            problems.append(f"site/{script}: write {name} once, on one line, as a JSON list of ids in double quotes,"
                            f' such as var {name} = ["page-size"];')
            continue
        for key in keys:
            if key not in known:
                problems.append(f"site/{script}: the {kind} id {key!r} in {name} is not in {rules.SOURCE}; use an id"
                                f" from its {'Measurements table' if kind == 'measurement' else 'rule rows'}, or add the row there.")
    return problems
