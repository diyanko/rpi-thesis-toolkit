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
# cards (site/index.html) follow the same four stages.
NAV = [
    ("Start", [
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
# label, what you edit, what is automatic). `code` becomes <code>. Without
# --previews the same rows show as a small table. The title page, which
# carries the RPI seal, is never pictured.
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
ALLOWED = {".html", ".css", ".svg", ".woff2"}  # plus fonts/*.txt, previews/*.png|webp, og-image.png
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


def last_updated(source):
    """'14 Oct 2026' from the last commit that changed `source`; '' without Git history."""
    try:
        day = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", source],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
        ).stdout.strip()
        if not day:
            return ""
        day = date.fromisoformat(day)
        return f"{day.day} {day:%b %Y}"
    except (OSError, ValueError, subprocess.SubprocessError):
        return ""


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
        guide = "" if offline else "guide/"
        self.pages = {"site/index.html": "index.html"}
        self.pages.update({f"docs/{name}.md": f"{guide}{name}.html" for name, _, _ in GUIDE})
        for source, (name, _) in PROJECT.items():
            if not (offline and source.startswith("docs/project/")):
                self.pages[source] = f"project/{name}.html"
        self.assets = {"site/site.css": "site.css", "site/logo.svg": "logo.svg"}
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
        """Rows for "Anatomy of your thesis" on the landing page, with a picture
        of each page when --previews made one."""
        def code(text):
            # A long path may break only after a slash, never at its hyphen
            def path(match):
                parts = match[1].split("/")
                return "<code>" + "/<wbr>".join(f'<span class="nowrap">{p}</span>' if p else ""
                                               for p in parts) + "</code>"

            return re.sub(r"`([^`]+)`", path, escape(text))

        rows = []
        for name, label, edit, auto in ANATOMY:
            row = {"label": escape(label), "edit": code(edit), "auto": code(auto)}
            size = self.previews.get(name)
            if size:
                row["img"] = {
                    "src": self.relative(here, f"previews/{name}.png"),
                    "alt": escape(f"Page {size['page']} of the sample thesis: {label.lower()}"),
                    "width": size["width"],
                    "height": size["height"],
                }
            rows.append(row)
        return rows

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

        def item(path, label):
            entry = {"href": self.relative(here, path), "label": escape(label)}
            return {**entry, "current": True} if path == here else entry

        nav = [item(self.pages[f"docs/{name}.md"], label) for name, label, _ in GUIDE]
        groups, start = [], 0
        for stage, pages in NAV:
            groups.append({"label": escape(stage), "pages": nav[start : start + len(pages)]})
            start += len(pages)
        values = {
            "lang": "en",
            "kind": kind,
            "title": escape(title),
            "pagetitle": escape(HOME_TITLE if kind == "home" else f"{title} · {NAME}"),
            "description": escape(description),
            "root": self.relative(here, "x")[:-1],
            "nav": nav,
            "navgroups": groups,
            "header": [entry for entry, (_, _, top) in zip(nav, GUIDE) if top],
            "project": [
                item(self.pages[path], label)
                for path, (_, label) in PROJECT.items()
                if label and path in self.pages
            ],
            "edition": escape(self.edition),
            "feedback_url": self.relative(here, self.feedback),
        }
        if kind == "home":
            values["home"] = True
            values["anatomy"] = self.anatomy(here)
            if self.previews:
                values["pictures"] = True
        if kind == "guide":
            index = [name for name, _, _ in GUIDE].index(Path(source).stem)
            if index > 0:
                values["prev"] = nav[index - 1]
            if index + 1 < len(nav):
                values["next"] = nav[index + 1]
            values["pager"] = True
            values["updated"] = last_updated(source)
        if kind == "notfound":
            values["notfound"] = True
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
        elif relative.as_posix() in ("og-image.png", CHEATSHEET_PDF):
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
    if cheatsheet and offline:  # package.py adds the PDF beside guide/
        site.cheatsheet = "../" + OFFLINE_CHEATSHEET
    elif cheatsheet and build_cheatsheet(destination):
        site.cheatsheet = CHEATSHEET_PDF
    for source, output in site.pages.items():
        (destination / output).parent.mkdir(parents=True, exist_ok=True)
        (destination / output).write_text(site.render(source), encoding="utf-8")
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
