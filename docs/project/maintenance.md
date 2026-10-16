# Maintaining the toolkit

For the person who looks after the RPI Thesis Toolkit (an unofficial,
community-made project) and the AI coding agents that draft most changes.
Students never need this page and it is not in the student ZIP. A human
maintainer reviews every change; the rules agents follow are in
[AGENTS.md](../../AGENTS.md), and `CLAUDE.md` only points to it. The current
version and its validation record are in [CHANGELOG.md](../../CHANGELOG.md);
each entry starts with a **Changes your PDF?** line.

Other pages in this folder: [style-guide.md](style-guide.md) (any text a
student reads), [requirements.md](requirements.md) (each OGE rule, how the
class meets it, differences from RPI's official LaTeX template, open
questions for OGE), [attribution.md](attribution.md) (what is ours and what is
not), `sources.json` (OGE documents reviewed, with dates and fingerprints),
and `upstream-files.json` (hashes of RPI's original template, compared by
`scripts/check.py` when `_local/legacy/` exists).

## Where things live

Everything is in one of three places. If a file fits none of them, ask before
adding it.

**Public source (tracked):**

| What | Where |
| --- | --- |
| Starter thesis files | `main.tex`, `metadata.tex`, `preamble.tex`, `references.bib`, `frontmatter/`, `chapters/`, `appendices/`, `figures/` |
| Formatting | `rpi-thesis.cls`; `assets/README.md` (how students get the seal; the seal is never committed) |
| Student guide | `docs/*.md`, `docs/diagrams/`, `cheatsheet/` |
| Front-door pages | `README.md`, `CONTRIBUTING.md`, `CREDITS.md`, `CHANGELOG.md`, `LICENSE.md`, `CODE_OF_CONDUCT.md`, `CITATION.cff` |
| Maintainer docs | `docs/project/`, `AGENTS.md`, `CLAUDE.md`, `.github/` templates |
| Website | `site/` (templates, CSS, fonts, `site.json` settings) |
| Scripts and CI | `scripts/`, `.github/workflows/` |
| Student editor settings | `.vscode/settings.json`, `.vscode/extensions.json` (shipped in the ZIP) |

**Generated (never tracked):** every `.html` page, all PDFs, `build/`,
`dist/site/`, and `dist/*.zip`.

**Local only (ignored, never published):**

| What | Where |
| --- | --- |
| Notes, prototypes, agent scratch files | `_local/` |
| Downloaded OGE manuals and checklists | `_local/oge/` (read them from the official page; never commit or mirror) |
| RPI's original LaTeX template, for comparison | `_local/legacy/` (from RPI ITS's [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation)) |
| The RPI seal, to compile the sample | `assets/rpi-seal.jpg` (each student downloads it) |
| Agent and editor settings | `.claude/`, `.codex/`, `.idea/`, `.venv/`, `__pycache__/` |

Delete stray `.html` files next to Markdown and PDFs or LaTeX working files
outside `build/`. `git status` should show only intended changes.

Guide stages and page order are defined once, in `NAV` at the top of
`scripts/build_site.py`. The landing page cards in `site/index.html` and the
guide list in `README.md` follow the same stages by hand; update them when
`NAV` changes.

Help arrives through GitHub Issues (the forms in `.github/`) and one
no-sign-in "help and feedback" form. The form's URL lives only in the "Ask for
help" section of `docs/troubleshooting.md`; every other page links to that
section. The repository is on the owner's personal GitHub account; do not
hard-code an organization name. When a question could come up again, add a row
to the "Common messages" table in `docs/troubleshooting.md`.

## RPI materials

Never commit RPI-owned material (seal, original template, manuals, checklists,
slides). Keep reference copies in `_local/` and link to RPI's pages.

Maintainer decisions (14 Oct 2026), settled:

- **No RPI materials are redistributed.** Nothing RPI-owned is in the
  repository, the ZIPs, or the website, so no redistribution permission is
  needed.
- **The seal:** the toolkit uses the current seal on RPI ITS's Thesis
  Preparation page. Each student downloads it and saves it as
  `assets/rpi-seal.jpg` (or `.png`); until then the title page shows a
  placeholder. The seal stays out of the repository, the ZIPs, the website
  artwork, and this project's license. (The 2026 manual's sample title page
  shows an older design; the Thesis Preparation download is the one we point
  to.)

These are project decisions, not OGE approval and not permission to
redistribute RPI artwork. Present the project as unofficial and
community-made ([style guide](style-guide.md#talking-about-rpi)).

## Verification

One command; CI runs the same (full logs in `build/verify/`):

```sh
python3 scripts/verify.py           # picks quick or full from the files changed since main
python3 scripts/verify.py quick     # guide or website text: hygiene and site, seconds
python3 scripts/verify.py full      # thesis, PDF checks and regressions (in parallel), website, ZIPs
python3 scripts/verify.py release   # full + strict publish build, layout sweep, reproducible ZIPs
```

Auto mode runs full whenever Git cannot tell what changed, on a clean tree,
or when any staged, unstaged, or untracked file is outside guide and website
text. Full also runs `scripts/test_*.py` (unit tests for the release and
health scripts). Release mode fails when the browser layout sweep cannot run;
CI's container has no browser and sets `VERIFY_ALLOW_NO_BROWSER=1`, so run
`verify.py release` locally before tagging.

It needs Python 3, TeX Live, Pandoc 3.11 or newer, and `pypdf`.
`python3 scripts/build.py --doctor` checks a computer's setup.

`check.py` builds isolated variants (MS, PhD with copyright and a large
committee, minimal DEng, LuaLaTeX, XeLaTeX) in parallel and checks PDF structure. After a
title-page change, run it with `assets/rpi-seal.jpg` and with the file moved
aside (as in CI). Parsed PDF text cannot judge layout, so also look at the
pages. For visible website changes, run `python3 scripts/ui_check.py --shots`.

One writer per checkout. A second agent or person works in its own git
worktree and branch, or owns separate files.

## Versions and compatibility

One version number everywhere. **The class is the version:** the
`\ProvidesClass` line in `rpi-thesis.cls` holds a date and `vX.Y.Z`; the
website footer, ZIP names, `CITATION.cff`, and every PDF's Creator property
use the same number. `main.tex` asks for that date
(`\documentclass{rpi-thesis}[YYYY/MM/DD]`), so a class with an earlier date
warns on every compile. LaTeX compares only dates: two releases on the same
day look the same to it, and the date says nothing about which versions work
together (the change log does). `scripts/package.py` refuses a release when
the dates differ.

- `Z` (patch): fixes that change no PDF, and guide-only changes.
- `Y` (minor): new settings, or formatting corrected to match OGE
  (**Changes your PDF? Yes**). Before 1.0.0, breaking changes also bump `Y`.
- `X` (major): from 1.0.0, a breaking change to settings or commands.
- Versions below 1.0.0 are the beta. Releases use the plain `vX.Y.Z` tag,
  marked as a pre-release on GitHub; the version never carries `-beta`.

### Compatibility

Before 1.0, anything may change (settings, files, pages, addresses), with no
aliases and no redirects, and the change log says what to do. The guide's
"Update the formatting safely" section and the README that
`scripts/package.py` writes into both ZIPs say the same.

The one-file-update promise starts at 1.0: students update by replacing
`rpi-thesis.cls` alone, often in the middle of a thesis, and an update never
needs another file changed and never breaks a thesis that compiled before.
Formatting lives only in the class; every `\thesissetup` key and starter
command keeps working (a rename keeps the old name as an alias that warns);
and if an update ever truly needs a change elsewhere, the change-log entry
gives the exact edit. New keys and commands may be added, and formatting may
be corrected to match OGE requirements.

## Review a requirement change

Once a year, and whenever OGE publishes new guidance or a student reports a
concrete mismatch:

1. Read the latest document through the OGE submission page linked in
   [requirements.md](requirements.md). Keep any working copy in `_local/oge/`.
2. Record its title, edition or date, link, review date, and relevant
   sections in `sources.json` and the requirements map.
3. Separate formatting changes from administrative ones. Change code only for
   formatting; link out for dates, contacts, and forms. Do not change
   typography from an automated scrape or search result.
4. Make a small change, run `verify.py`, and look at every affected PDF page.
5. Add the `CHANGELOG.md` entry with its **Changes your PDF?** line, and bump
   the version as above.
6. Ask OGE to clarify an ambiguous requirement only when authorized. Record
   what was confirmed and by whom; silence is not approval.

## The website

Markdown is the only source; HTML is generated and never edited or committed.
Contributors do not need Pandoc; CI builds everything.

```sh
python3 scripts/build_site.py              # website in dist/site/
python3 scripts/build_site.py --previews   # also pictures of sample pages
python3 scripts/package.py                 # student ZIP in dist/
```

Open `dist/site/index.html`. The build checks every local link and heading
anchor, and refuses linked source files and folders. Every online page carries
`<meta name="rpi-thesis-build" content="SHA">`, and the site root has
`build.txt` (`commit=<SHA>` and `release=v<RELEASE_VERSION>`, one per
line), so a live check can tell exactly which build is served. The SHA is `GITHUB_SHA` in CI, else
`git rev-parse HEAD`; uncommitted edits do not change it, and `--publish`
fails without one. The offline guide carries neither. Page lists (`NAV`,
`PROJECT`) are in `scripts/build_site.py`. Links between Markdown files become
links between pages; a link to another repository file becomes a GitHub link
once `repository_url` is set in `site/site.json`. The footer edition line is
read from `docs/project/sources.json` and the `\ProvidesClass` line.

The website works without JavaScript. The optional scripts in `site/`
(`copy.js`, `viewer.js`, `theme.js`, `search.js` and its generated index) are
enhancements; search runs in the browser and sends nothing anywhere. Light and
dark colors live in section 2 of `site/site.css`; check both themes when
changing them. `--previews` compiles the sample thesis and saves PNG pages
(never the title page) and needs TeX Live and poppler. The site may contain
only HTML, CSS, SVG, the named scripts, WOFF2 fonts, PNG/WebP under
`previews/`, and the cheat sheet PDF.

The student ZIP (`rpi-thesis-starter-v<version>.zip`) holds the thesis files,
`assets/README.md`, `scripts/build.py`, the `.vscode` settings, a student
`.gitignore`, `README.md`, `LICENSE.md`, the offline guide (`START-HERE.html`),
and the cheat sheet PDF. Maintainer pages, `AGENTS.md`, `CLAUDE.md`, site
tooling, and every RPI file stay out; `package.py` refuses any seal file and
any other PDF, and requires `site_url` and `repository_url` in
`site/site.json`. A relative link in a shipped Markdown file to a file the ZIP
leaves out (such as `CREDITS.md` from `LICENSE.md`) becomes a link to that
file in the repository at the release tag, and both ZIPs fail to build if any
relative link in their Markdown or top-level HTML is broken.

Three workflows in `.github/workflows/`:

- `build.yml` verifies every pull request and push. A push to `main` deploys
  the website when `scripts/release.py gate` allows it: the commit is still
  the tip of `main`, its version is the newest published release, and the
  starter's interface files (`rpi-thesis.cls`, `main.tex`, `metadata.tex`,
  `preamble.tex`, `latexmkrc`, `scripts/build.py`) equal the released starter
  ZIP's. So guide fixes go live at once, starter changes wait for a release,
  and a delayed or older run never replaces a newer site. The gate runs again
  just before publishing. A pushed `vX.Y.Z` tag releases (below).
- `fresh-machines.yml` installs TeX on new Windows, macOS, and Ubuntu machines
  the way the guide says and compiles the starter: on each release tag, once a
  month, and on demand. It never blocks a release.
- `health.yml` runs monthly: external links and RPI's thesis pages
  (`scripts/health.py`, compared with `scripts/oge-watch.json`; tested by
  `scripts/test_health.py` against a local server), and a full verify on the
  newest, unpinned TeX Live. Problems open one issue labelled `health`. The
  watch compares the links (relative ones resolved) and text in each watched
  page's `<main>`. A missing or unreadable baseline fails the check.
  `--update` records every page or nothing: if any page times out, answers
  with an error, or has no `<main>`, `oge-watch.json` stays as it was and the
  command exits 1. **Not covered:** a manual or checklist replaced at the same
  Box address. Box answers with a script-driven page rather than the file, so
  only the links are compared; the yearly requirement review re-reads the
  documents.

### Updating pinned tools

CI pins its tools so a build does not change by itself. Once a year, or when
something breaks:

- **Pandoc:** set `PANDOC_VERSION` in `build.yml` to your local version and
  `PANDOC_SHA256` to the checksum of `pandoc-<version>-1-amd64.deb` on the
  [Pandoc release page](https://github.com/jgm/pandoc/releases).
- **TeX Live:** replace the `sha256:` digest after `texlive/texlive:latest@`
  with the current one from [Docker Hub](https://hub.docker.com/r/texlive/texlive/tags)
  and update the date in the comment. Then run `verify.py` and look at the PDFs.
- **pypdf:** set `PYPDF_VERSION` and `PYPDF_SHA256` (the `py3-none-any` wheel
  under **Download files** on [PyPI](https://pypi.org/project/pypdf/#files)).
- **Actions:** check the latest major version of each `actions/...` step.
- **Helper websites:** open each tool in the `helpers` list of `sources.json`
  (named in the "Helpers for common tasks" section of `docs/writing.md`);
  check that it loads without sign-in, the menu names and the draw.io privacy
  note still match, and the guide's snippets compile; update `last_reviewed`.
  Replace or remove a tool that has changed rather than adding alternatives.
  Mathcha's TikZ export is not verified with this class; verify before
  expanding. Lagrida was evaluated and omitted as a second similar editor.

## Public-release readiness

The repository and website can be public before the first downloadable
release.

**Before the repository goes public:**

- [ ] `git ls-files` lists no seal, original template, manual, checklist, or
      slides, and neither does the starter ZIP. The published Git history must
      not contain them either; local backup branches made before a cleanup
      are never pushed.
- [ ] Every public page presents the project as unofficial and community-made.
- [ ] CI passes on `main`, and the maintainer has authorized publication.
- [ ] GitHub settings: description ("Unofficial, community-made LaTeX thesis
      and dissertation starter and guide for RPI graduate students"); topics
      (latex, thesis, dissertation, rpi, rensselaer, latex-template,
      thesis-template, overleaf, zotero, biblatex); Pages source **GitHub
      Actions**; Issues on, Discussions off; labels `question`,
      `enhancement`, `bug`, `documentation`; default read-only Actions token;
      a social preview image without RPI artwork; `site_url` and
      `repository_url` in `site/site.json` and `CITATION.cff`.

**Before the first release (v0.1.0):**

- [ ] A novice completes the first-PDF and first-edit workflows unaided.
- [ ] Fresh installs and editors (VS Code with LaTeX Workshop, TeXShop,
      TeXstudio) tested on macOS, Windows, Linux.
- [ ] The starter ZIP uploaded to Overleaf, with the seal added as
      `assets/README.md` describes, builds cleanly.
- [ ] Citation presets (URL access dates, caption citations), long titles,
      large committees, long contents or captions, and Unicode reviewed.
- [ ] OGE asked for a preliminary formatting review of the sample PDF, as a
      student would; date and outcome recorded in `requirements.md`.

Until then, do not call a release compliant, approved, or fully tested.

## Make a release

Only with the maintainer's authorization.

1. **Bump:** with the entry under `## Unreleased` in `CHANGELOG.md`, run
   `python3 scripts/bump.py X.Y.Z`. It sets the version everywhere (class line
   and date, `main.tex`, download links, `CITATION.cff`, the change-log
   heading). Patch for fixes; minor for anything that changes a PDF or a
   setting.
2. **Verify:** `python3 scripts/verify.py release`.
3. **Commit and tag:** commit `build: release vX.Y.Z` on `main`, `git tag
   vX.Y.Z`, then `git push --atomic origin main vX.Y.Z`.
4. **CI does the rest** (`build.yml` on the tag): verifies in release mode,
   creates or resumes the GitHub pre-release with both ZIPs and
   `rpi-thesis.cls` (`scripts/release.py publish`: existing assets must match
   by sha256, missing ones are uploaded, any conflict fails), deploys the
   website, and checks that the live site serves this exact build
   (`build.txt`) and that every download matches (`scripts/release.py live`).
   The fresh-machine test starts on the same tag.

**If a tag run fails**, re-run it: each step checks what is already done and
continues. If the failure needs a code fix and the release does not exist
yet, fix on `main`, move the tag (`git tag -f vX.Y.Z && git push -f origin
vX.Y.Z`), and it runs again; once assets are published, make a new patch
release instead. A tag older than the newest release never deploys.
**Rollback:** Actions, **Build thesis, website, and starter ZIP**, Run
workflow on the older tag with **rollback** ticked; the next deploy from
`main` replaces it. Never re-run workflow runs from before 17 Oct 2026: they
use the old deploy rule. The `github-pages` environment allows `main` and
`v*` tags to deploy.

## Roadmap and not yet covered

Each item needs source evidence where formatting is involved, a short tested
example, and focused validation before it reaches students.

- **Publication-based theses**, landscape pages, long tables, reference styles
  across disciplines (including citations in captions), and first-install
  problems reported by students.
- **Overleaf template gallery** submission, once a release has been stable
  through a real-student test and an OGE preliminary review.
- **Accessible, tagged PDF**, once the LaTeX kernel's tagging support covers
  the packages the class relies on (including `titlesec` and `caption`). Do
  not claim tagged-PDF or PDF/UA compliance from visual checks.
- Word export stays a review copy only.

## Feedback and the OGE review packet

The most useful feedback describes one task and the moment it became hard: ask
someone to compile the example, change their name, and edit a paragraph without
coaching, then ask where they paused. Record their editor, operating system,
and toolkit version; keep private research out. Send invitations yourself, and
offer opt-in credit in [CREDITS.md](../../CREDITS.md#people).

For OGE, offer the MS and doctoral sample PDFs, a link to the source, the
requirements map, source dates, and known gaps. Ask about title-page details
and seal, spacing, font, section order, and common rejection patterns. Keep
community maintenance independent unless a formal agreement is made, and
record any feedback with the version it applies to.

## Handing over the project

- Transfer the repository or add the new maintainer with admin rights; update
  `site/site.json` if the addresses change (`build_site.py`, `package.py`, and
  `health.py` read them from there; guide pages and `README.md` link them by
  hand, and `CITATION.cff` has its own copy).
- Hand over the help and feedback form and its response sheet.
- Confirm no RPI-owned files are tracked and the new maintainer knows the
  rule in [AGENTS.md](../../AGENTS.md#principles).
- Run `verify.py` once on their computer; review open issues and every
  `TODO(verify)` marker.
- Add the outgoing maintainer to [CREDITS.md](../../CREDITS.md#people), with
  their consent. Share notes by adding them here, not by handing over `_local/`.
