#!/usr/bin/env python3
"""Build the guide website from the Markdown files and check every local link.

    python3 scripts/build_site.py                website in dist/site/
    python3 scripts/build_site.py --previews     also add pictures of the sample
                                                 thesis (needs LaTeX, plus poppler
                                                 or Ghostscript; see previews.py)
                                                 and the cheat sheet PDF
    python3 scripts/build_site.py --cheatsheet   only the cheat sheet PDF (needs LaTeX)

Needs Pandoc (CI uses 3.11). Nothing is published or uploaded. package.py calls
build_site(offline=True) to put the same guide into the starter ZIP.
"""
import argparse
from datetime import date
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
NAME = "RPI Thesis Toolkit"
HOME_TITLE = NAME + " · LaTeX thesis and dissertation starter for RPI"
HOME_DESCRIPTION = (
    "Unofficial, community-made LaTeX starter and plain-language guide for RPI "
    "master's theses and doctoral dissertations. Not affiliated with or endorsed by RPI."
)

# The guide, in reading order, grouped into stages: (stage, [(file in docs/,
# label, also in the header?), ...]). The sidebar, header, previous/next links
# and every page list come from here; the landing page's "Help at your level"
# cards (site/index.html) list each stage's pages from here too.
NAV = [
    ("Start", [
        ("why-latex", "Why LaTeX for your thesis?", False),
        ("get-started", "Get started", True),
        ("bring-your-draft", "Bring your draft", False),
    ]),
    ("Write", [
        ("how-it-works", "How it works", False),
        ("writing", "Writing basics", True),
        ("citations", "Citations", True),
    ]),
    ("Fix and finish", [
        ("troubleshooting", "Fixing problems", True),
        ("submission", "Submitting", True),
    ]),
    ("Go further", [
        ("workflows", "Workflows", False),
        ("advanced", "Advanced use", False),
    ]),
]
GUIDE = [page for _, pages in NAV for page in pages]  # the same pages, in one list
# Quick answers: a guide page outside the stages and the previous/next chain.
# It sits above the stages in the sidebar, last in the header, and in the
# "Stuck, or nearly done" card on the landing page.
QUICK = ("how-do-i", "How do I…?", True)
# When a student needs each page, shown as a small tag beside every link to
# it in the sidebar, and under the page title. The landing-page cards leave
# it out: each card's stage already says when you need its pages.
# Tag -> (CSS class in site.css, pages). Every guide page has exactly one tag.
TAGS = {
    "Start here": ("start", ["why-latex"]),
    "Need now": ("now", ["get-started", "writing", "citations"]),
    "If you have a draft": ("draft", ["bring-your-draft"]),
    "When stuck": ("stuck", ["troubleshooting", "how-do-i"]),
    "Need later": ("later", ["submission"]),
    "Optional": ("optional", ["how-it-works", "workflows", "advanced"]),
}
PAGE_TAGS = {page: (tag, css) for tag, (css, pages) in TAGS.items() for page in pages}
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
}
# Footer "Help & feedback" link: the one place the help/feedback form URL lives.
FEEDBACK = ("docs/troubleshooting.md", "Ask for help")
# "Anatomy of your thesis" on the landing page: (picture name in previews.py,
# label, what you edit, what is automatic). `code` becomes <code>. With
# --previews each row shows the whole page, a close-up you can read, and a
# link to the page at full size; without, the same rows show as a small table.
# The title page, which carries the RPI seal, is never pictured.
ANATOMY = [
    ("contents", "Contents", "nothing; your `\\chapter` and `\\section` headings fill it in",
     "titles, dot leaders and page numbers"),
    ("chapter", "A chapter opening", "`chapters/01-introduction.tex`",
     "the chapter number, heading style and spacing"),
    ("figure-table", "Tables and figures", "`chapters/02-research.tex`; images go in `figures/`",
     "numbers, caption placement, and the lists of tables and figures"),
    ("references", "References", "`references.bib`, and `\\cite{key}` in your text",
     "the order and format of every entry, by Biber"),
    ("appendix", "An appendix", "`appendices/additional-material.tex`",
     "the letters A, B, C and the contents entry"),
]
ALLOWED = {".html", ".css", ".svg", ".woff2"}  # plus fonts/*.txt, previews/*.png|webp, og-image.png,
                                              # sitemap.xml, robots.txt and copy.js
# The one PDF the website may hold: the cheat sheet (no RPI artwork), built
# from cheatsheet/cheatsheet.tex with --previews or --cheatsheet. The offline
# guide never holds it; package.py puts it at the ZIP root, beside guide/, as
# OFFLINE_CHEATSHEET, and the offline guide links there.
CHEATSHEET_PDF = "downloads/rpi-thesis-cheatsheet.pdf"
OFFLINE_CHEATSHEET = "rpi-thesis-cheatsheet.pdf"
CHEATSHEET_SOURCES = {"cheatsheet", "cheatsheet/cheatsheet.tex", "cheatsheet/README.md"}
OG_ALT = ("RPI Thesis Toolkit, an unofficial community starter: write your RPI thesis or "
          "dissertation in LaTeX, even if you've never used it.")
FORBIDDEN_FOLDERS = {".git", "_local", "reference", "assets", "build"}
FENCE = "`" * 12


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


def read_markdown(source):
    """Return (title, description, Markdown text). Optional front matter:
    a leading '---' block with 'title:' or 'description:' lines."""
    text = (ROOT / source).read_text(encoding="utf-8")
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


def class_version():
    """Return (version, date) from the \\ProvidesClass line of rpi-thesis.cls."""
    text = (ROOT / "rpi-thesis.cls").read_text(encoding="utf-8")
    match = re.search(r"\\ProvidesClass\{rpi-thesis\}\[(\d{4})/(\d\d)/(\d\d) v([\w.-]+)", text)
    if not match:
        raise SystemExit(
            "rpi-thesis.cls: keep the line \\ProvidesClass{rpi-thesis}[YYYY/MM/DD vX.Y.Z ...]; "
            "the website and the ZIP name read the version from it."
        )
    return match[4], date(int(match[1]), int(match[2]), int(match[3]))


def edition():
    sources = json.loads((ROOT / "docs/project/sources.json").read_text(encoding="utf-8"))
    manual = sources["documents"][0]
    name = Path(manual["title"]).stem.removesuffix(manual["version"]).strip()
    reviewed = date.fromisoformat(sources["last_reviewed"])
    return (
        f"Checked against the RPI OGE {name} ({manual['version']}) · "
        f"last reviewed {reviewed.day} {reviewed:%b %Y} · template v{class_version()[0]}"
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


class Site:
    def __init__(self, offline):
        config = json.loads((SITE / "site.json").read_text(encoding="utf-8"))
        self.repo = config.get("repository_url", "").rstrip("/")
        self.url = "" if offline else config.get("site_url", "").rstrip("/")
        self.offline = offline
        self.errors, self.warnings = [], []
        self.previews = {}       # name -> {width, height, page}, from previews.make()
        self.cheatsheet = ""     # where the cheat sheet PDF is, relative to the site root
        self.edition = edition()
        self.meta = {}           # output page -> (title, description), checked after the build
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
                       "site/copy.js": "copy.js"}  # optional "Copy" buttons on code blocks
        if not offline:  # GitHub Pages serves /404.html; the link-preview picture is online only
            self.pages["site/404.html"] = "404.html"
            self.assets["site/og-image.png"] = "og-image.png"
        for folder, output, suffixes in (
            ("site/fonts", "fonts", {".woff2", ".txt"}),
            ("site/art", "art", {".svg"}),  # landing-page drawings
            ("docs/diagrams", "diagrams", {".svg"}),
        ):
            for path in sorted((ROOT / folder).glob("*")):
                if path.is_file() and path.suffix in suffixes:
                    self.assets[f"{folder}/{path.name}"] = f"{output}/{path.name}"
        source, heading = FEEDBACK
        self.feedback = self.pages[source]
        if re.search(rf"(?m)^#+ {re.escape(heading)}\s*$", (ROOT / source).read_text(encoding="utf-8")):
            self.feedback += "#" + slug(heading)
        else:
            self.warnings.append(
                f"{source} has no '## {heading}' section; "
                "the footer Help & feedback link opens the top of that page."
            )

    @staticmethod
    def relative(here, target):
        return posixpath.relpath(target, posixpath.dirname(here) or ".")

    def link(self, href, source, here, base):
        """Rewrite a link from `source` for output page `here`. None = keep the text only."""
        parts = urlsplit(unescape(href))
        if parts.scheme or parts.netloc or not parts.path:
            return unescape(href)
        target = posixpath.normpath(posixpath.join(base, unquote(parts.path)))
        fragment = "#" + parts.fragment if parts.fragment else ""
        if target in self.pages:
            return self.relative(here, self.pages[target]) + fragment
        if target in self.assets:
            return self.relative(here, self.assets[target])
        if target in CHEATSHEET_SOURCES and self.cheatsheet:  # the PDF, when built
            return self.relative(here, self.cheatsheet)
        if target.startswith("docs/diagrams/"):  # planned diagram, not drawn yet
            return self.relative(here, "diagrams/" + posixpath.basename(target))
        if target in self.planned:  # planned guide page, not written yet
            self.warnings.append(f"{source}: link to a guide page not written yet: {href}")
            return None
        if target.startswith("..") or not (ROOT / target).exists():
            self.errors.append(f"{source}: link to a missing file: {href}")
            return None
        if self.repo:  # a file outside the website, e.g. main.tex: link to GitHub
            kind = "tree" if (ROOT / target).is_dir() else "blob"
            return f"{self.repo}/{kind}/main/{quote(target)}{fragment}"
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
        return html

    @staticmethod
    def diagrams(html):
        """Each diagram from docs/diagrams/ becomes a figure with an "Open full size"
        link, so readers can zoom. If docs/diagrams/NAME-narrow.svg exists, phones
        get that taller drawing instead (the <picture> element picks it)."""
        def figure(match):
            tag, src, name = match[1], match[2], match[3]
            if (ROOT / f"docs/diagrams/{name}-narrow.svg").is_file():
                narrow = src[: -len(".svg")] + "-narrow.svg"
                tag = f'<picture><source media="(max-width: 600px)" srcset="{narrow}">{tag}</picture>'
            return (
                f'<figure class="diagram"><a class="diagram-zoom" href="{src}" tabindex="-1">{tag}</a>'
                f'<a class="diagram-open" href="{src}">Open full size</a></figure>'
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
            return (f'<figure class="shot"><img src="{src}" alt="{escape(alt)}" '
                    f'width="{size["width"]}" height="{size["height"]}" loading="lazy"></figure>')

        return re.sub(r"<!--\s*preview ([\w-]+):(.*?)-->", figure, html, flags=re.S)

    def anatomy(self, here):
        """Rows for "Anatomy of your thesis" on the landing page, with pictures
        of each page when previews.py made them."""
        def code(text):
            # A long path may break only after a slash, never at its hyphen
            def path(match):
                parts = match[1].split("/")
                return "<code>" + "/<wbr>".join(f'<span class="nowrap">{p}</span>' if p else ""
                                               for p in parts) + "</code>"

            return re.sub(r"`([^`]+)`", path, escape(text))

        def picture(name):
            size = self.previews[name]
            return {"src": self.relative(here, f"previews/{name}.png"),
                    "width": size["width"], "height": size["height"]}

        rows = []
        for name, label, edit, auto in ANATOMY:
            row = {"label": escape(label), "edit": code(edit), "auto": code(auto)}
            names = [f"anatomy-{name}", f"anatomy-{name}-lens", f"anatomy-{name}-full"]
            if all(n in self.previews for n in names):
                whole, lens, full = (picture(n) for n in names)
                details = self.previews[names[1]]
                whole["alt"] = escape(f"Whole page {details['printed']} of the sample thesis, "
                                      "with the close-up area outlined")
                lens["alt"] = escape(details["alt"])
                x, y, w, h = details["spot"]
                # On phones a close-up is shown larger, its right edge cut off,
                # except where the right edge matters (the contents' page numbers)
                row["img"] = {"page": whole, "lens": lens, "full": full["src"], "whole": name == "contents",
                              "spot": f"left: {x}%; top: {y}%; width: {w}%; height: {h}%"}
            rows.append(row)
        return rows

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
               f'<nav aria-label="On this page"><ol>{links}</ol></nav></details>')
        opening = re.search(r'</h1>\s*(?:<p class="page-tag">.*?</p>\s*)?(?:<p>.*?</p>)?', body, flags=re.S)
        if opening:
            body = body[: opening.end()] + "\n" + box + body[opening.end() :]
        return body, toc

    def timeline(self, here):
        """The "Your thesis, start to finish" drawing on the landing page, with
        the taller -narrow version for phones when it exists."""
        name = "docs/diagrams/thesis-timeline"
        entry = {"src": self.relative(here, "diagrams/thesis-timeline.svg")}
        size = svg_size(ROOT / f"{name}.svg")
        if size:
            entry.update(width=size[0], height=size[1])
        else:
            self.warnings.append(f"{name}.svg is not drawn yet; the landing page links to it anyway.")
        if (ROOT / f"{name}-narrow.svg").is_file():
            entry["narrow"] = self.relative(here, "diagrams/thesis-timeline-narrow.svg")
        return entry

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
            body = pandoc(["--from=gfm", "--to=html5", "--wrap=none", "--syntax-highlighting=none"], text)
            body = self.rewrite(body, source, here, posixpath.dirname(source))
            body = self.diagrams(body)
            body = self.pictures(body, source, here)
            # A scroll box lets wide tables scroll on phones without losing table semantics.
            body = re.sub(r"<table\b.*?</table>", r'<div class="table-wrap">\g<0></div>', body, flags=re.S)
            toc = []
            if kind == "guide":
                body, toc = self.page_top(body, Path(source).stem)

        def item(path, label, name=None):
            entry = {"href": self.relative(here, path), "label": escape(label)}
            if name in PAGE_TAGS:
                entry.update(tag=escape(PAGE_TAGS[name][0]), tagclass=PAGE_TAGS[name][1])
            return {**entry, "current": True} if path == here else entry

        def guide_item(name, label):
            source = f"docs/{name}.md"
            return item(self.pages[source], label, name) if source in self.pages else None

        chain = [(name, label, top) for name, label, top in GUIDE if f"docs/{name}.md" in self.pages]
        nav = [guide_item(name, label) for name, label, _ in chain]
        quick = guide_item(*QUICK[:2])
        groups, stages = [], {}
        for stage, pages in NAV:
            entries = [entry for entry in (guide_item(name, label) for name, label, _ in pages) if entry]
            groups.append({"label": escape(stage), "pages": entries})
            stages[re.sub(r"\W+", "_", stage.lower())] = entries  # Fix and finish -> fix_and_finish
        header = [entry for entry, (_, _, top) in zip(nav, chain) if top]
        if quick and QUICK[2]:
            header.append(quick)
        values = {
            "lang": "en",
            "kind": kind,
            "title": escape(title),
            "pagetitle": escape(HOME_TITLE if kind == "home" else f"{title} · {NAME}"),
            "description": escape(description),
            "root": self.relative(here, "x")[:-1],
            "nav": nav + ([quick] if quick else []),
            "navgroups": groups,
            "header": header,
            "project": [
                item(self.pages[path], label)
                for path, (_, label) in PROJECT.items()
                if label and path in self.pages
            ],
            "edition": escape(self.edition),
            "feedback_url": self.relative(here, self.feedback),
        }
        if quick:
            values["quick"] = quick
        if kind == "home":
            values["home"] = True
            values["stages"] = stages
            values["anatomy"] = self.anatomy(here)
            values["timeline"] = self.timeline(here)
            if all("img" in row for row in values["anatomy"]):
                values["pictures"] = True
        if kind == "guide":
            names = [name for name, _, _ in chain]
            if Path(source).stem in names:
                index = names.index(Path(source).stem)
                if index > 0:
                    values["prev"] = nav[index - 1]
                if index + 1 < len(nav):
                    values["next"] = nav[index + 1]
            elif nav:  # quick answers sit outside the chain: offer the start of the guide
                values.update(next=nav[0], next_label="Start the guide")
            values["pager"] = True
            values["updated"] = last_updated(source)
            if toc:
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
            values["suggest_url"] = f"{self.repo}/issues/new?template=suggestion.yml"
        if self.offline:
            values["offline"] = True
        if self.cheatsheet:
            values.update(cheatsheet_url=self.relative(here, self.cheatsheet), cheatsheet_pdf=True)
        elif self.repo:
            values["cheatsheet_url"] = f"{self.repo}/tree/main/cheatsheet"
        args = ["--from=markdown", "--to=html5", "--quiet"]
        args.append("--template=" + str(SITE / "guide-template.html"))
        args += [f"--variable-json={key}:{json.dumps(value)}" for key, value in values.items()]
        html = pandoc(args, f"{FENCE}{{=html}}\n{body}\n{FENCE}\n")
        if kind in ("home", "notfound"):  # these link guide pages by their Markdown file
            html = self.rewrite(html, source, here, "", markdown_only=True)
        if kind == "notfound":  # served at any depth, so every local link starts from the site root
            base = (self.url or "") + "/"
            html = re.sub(r'((?:href|src)=")(?![a-z]+:|/|#)', r"\g<1>" + base, html)
        return html


def make_previews(destination):
    """Pictures of the sample thesis (scripts/previews.py); {} without LaTeX."""
    from previews import make

    return make(destination / "previews")


def reuse_previews(destination):
    """The offline guide reuses the pictures of the last build_site.py --previews
    run (dist/site/previews), as package.py reuses its cheat sheet; {} if none."""
    from previews import read

    source = ROOT / "dist/site/previews"
    if not source.is_dir() or source.is_symlink() or destination.resolve() == source.parent.resolve():
        return {}
    (destination / "previews").mkdir()
    for path in source.glob("*.png"):
        if path.is_file() and not path.is_symlink():
            shutil.copyfile(path, destination / "previews" / path.name)
    return read(destination / "previews")


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


class PageLinks(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links, self.ids = [], set()
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        for name in ("id", "name") if tag == "a" else ("id",):
            if attributes.get(name):
                self.ids.add(attributes[name])
        for name in ("href", "src"):
            if attributes.get(name):
                self.links.append(attributes[name])
        for candidate in (attributes.get("srcset") or "").split(","):
            if candidate.strip():
                self.links.append(candidate.split()[0])


def validate(destination, beside=()):
    """Check links and anchors offline, and that nothing private or binary is staged.
    `beside` names files the caller puts next to the website folder (the offline
    cheat sheet); links to them are allowed. Returns (errors, warnings); missing
    diagrams/ files are only warnings."""
    errors, warnings, parsed = [], [], {}
    root = destination.resolve()

    def parse(path):
        if path not in parsed:
            parsed[path] = PageLinks(path)
        return parsed[path]

    pages = sorted(root.rglob("*.html"))
    for page in pages:
        name = page.relative_to(root).as_posix()
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
            elif not target.is_file():
                planned = target.relative_to(root).parts[0] == "diagrams"
                (warnings if planned else errors).append(f"{name}: missing file: {link}")
            elif address.fragment and target.suffix == ".html":
                if unquote(address.fragment) not in parse(target).ids:
                    errors.append(f"{name}: missing heading or anchor: {link}")
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        top, suffix = relative.parts[0], path.suffix.lower()
        if path.is_symlink():
            errors.append(f"Symlink not allowed in the website: {relative}")
        elif FORBIDDEN_FOLDERS.intersection(relative.parts):
            errors.append(f"Private or source folder in the website: {relative}")
        elif path.is_dir() or suffix in ALLOWED:
            pass
        elif relative.as_posix() in ("og-image.png", CHEATSHEET_PDF, "sitemap.xml", "robots.txt", "copy.js"):
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


def build_site(destination=None, offline=False, previews=False, cheatsheet=False):
    """Build the website, or with offline=True the guide for the starter ZIP.
    Offline, cheatsheet=True means the caller puts OFFLINE_CHEATSHEET beside
    the destination folder, so the guide links to it."""
    check_pandoc()
    destination = Path(destination or ROOT / "dist/site")
    site = Site(offline)
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for source, output in site.assets.items():
        if (ROOT / source).is_symlink():
            raise SystemExit(f"Website input must not be a symlink: {source}")
        (destination / output).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, destination / output)
    if previews:
        site.previews = make_previews(destination)
    elif offline:
        site.previews = reuse_previews(destination)
    if cheatsheet and offline:  # package.py adds the PDF beside guide/
        site.cheatsheet = "../" + OFFLINE_CHEATSHEET
    elif cheatsheet and build_cheatsheet(destination):
        site.cheatsheet = CHEATSHEET_PDF
    for source, output in site.pages.items():
        (destination / output).parent.mkdir(parents=True, exist_ok=True)
        (destination / output).write_text(site.render(source), encoding="utf-8")
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
    beside = {OFFLINE_CHEATSHEET} if site.cheatsheet.startswith("../") else set()
    errors, warnings, count = validate(destination, beside)
    for warning in site.warnings + warnings:
        print("WARNING: " + warning)
    if site.errors or errors:
        raise SystemExit("Website check failed:\n- " + "\n- ".join(site.errors + errors))
    print(f"PASS: {count} pages; local links and anchors work; no LaTeX sources, archives, "
          "RPI artwork, or PDFs other than the cheat sheet staged.")
    return destination


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
    args = parser.parse_args()
    destination = build_site(previews=args.previews, cheatsheet=args.cheatsheet or args.previews)
    print("Open in a browser: " + str(destination / "index.html"))


if __name__ == "__main__":
    main()
