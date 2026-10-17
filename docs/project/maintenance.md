# Maintaining the toolkit

Reference for the person who looks after the RPI Thesis Toolkit (an
unofficial, community-made project) and the AI agents that draft most changes.
Students never need this page and it is not in the student ZIP. Every step to
follow (the development cycle, releases, recipes) is in
[AGENTS.md](../../AGENTS.md), the only process document; this page explains
how things work and never repeats a step. `CLAUDE.md` only points to
`AGENTS.md`. The current version and its validation record are in
[CHANGELOG.md](../../CHANGELOG.md).

Other pages in this folder: [style-guide.md](style-guide.md) (any text a
student reads), [requirements.md](requirements.md) (each OGE rule, how the
class meets it, differences from RPI's official LaTeX template, open
questions for OGE), [attribution.md](attribution.md) (what is ours and what is
not), [components.md](components.md) (every website component on one page),
`sources.json` (OGE documents and helper websites reviewed, with dates), and
`upstream-files.json` (hashes of RPI's original template, compared by
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

**How the class is organized.** `rpi-thesis.cls` has numbered sections, one
per group of rules. Each opens with a banner naming its rule ids
(`% Rules: ...`) from `docs/project/requirements.md`, whose "cls §N" column
points back, so a rule can be traced in both directions. Every fixed size says
whether it comes from RPI's template or is this project's choice. Student
input enters only through `\thesissetup` and `\committeemember` (section 10)
and is checked before anything prints. `check.py` covers page structure;
`regressions.py` covers bibliography styles, AMS symbols, the class-only
recipe, the contents stress test, and the build helper's messages.

**Generated (never tracked):** every `.html` page, all PDFs, `build/`,
`dist/site/`, and `dist/*.zip`. Delete stray `.html` files next to Markdown,
and PDFs or LaTeX working files outside `build/`.

**Local only (ignored, never published):**

| What | Where |
| --- | --- |
| Notes, prototypes, agent scratch files, worktrees | `_local/` |
| Downloaded OGE manuals and checklists | `_local/oge/` (read them from the official page; never commit or mirror) |
| RPI's original LaTeX template, for comparison | `_local/legacy/` (from RPI ITS's [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation)) |
| The RPI seal, to compile the sample | `assets/rpi-seal.jpg` (each student downloads it) |
| Agent and editor settings | `.claude/`, `.codex/`, `.idea/`, `.venv/`, `__pycache__/` |

Guide stages and page order are defined once, in `NAV` at the top of
`scripts/build_site.py`. The guide list in `README.md` follows the same stages
by hand. The home page (`site/index.html`) links pages from its three cards
(Start, Tools, Help) by hand; its "What's new" line comes from `CHANGELOG.md`.

Help arrives through GitHub Issues (the forms in `.github/ISSUE_TEMPLATE/`)
and one no-sign-in help and feedback form. The form's URL lives only in the
"Ask for help" section of `docs/troubleshooting.md`; every other page links to
that section. The repository is on the owner's personal GitHub account; do not
hard-code an organization name.

## RPI materials

Maintainer decisions (14 Oct 2026), settled:

- **No RPI materials are redistributed.** Nothing RPI-owned is in the
  repository, the ZIPs, or the website, so no redistribution permission is
  needed.
- **The seal:** the toolkit points to the current seal on RPI ITS's Thesis
  Preparation page. Each student downloads it and saves it as
  `assets/rpi-seal.jpg` (or `.png`); until then the title page shows a
  placeholder. (The 2026 manual's sample title page shows an older design.)

These are project decisions, not OGE approval and not permission to
redistribute RPI artwork.

## Verification internals

What to run is in [AGENTS.md](../../AGENTS.md#development-cycle). How it works:

- **Auto mode** runs full whenever Git cannot tell what changed, on a clean
  tree, or when any staged, unstaged, or untracked file is outside guide and
  website text.
- **Full** compiles the thesis and runs `check.py` (isolated MS, PhD with
  copyright and a large committee, minimal DEng, LuaLaTeX, and XeLaTeX
  variants) and `regressions.py` in parallel, then `scripts/tests/test_*.py`, the
  website, and the ZIPs. Browser tests run after the TeX checks so they do not
  compete with the compilers.
- **Missing tools:** a step whose tool (TeX Live, Pandoc 3.11 or newer,
  `pypdf`, Chrome) is missing is skipped and named in the summary, with
  skip counts for tests; CI and release mode fail instead, since they have
  every tool. **Release** mode adds a strict publish build, a browser layout
  sweep, and reproducible ZIPs, and fails when the sweep cannot run. CI's
  container has no browser and sets `VERIFY_ALLOW_NO_BROWSER=1`: only the
  sweep and the unit tests that need a browser may then skip, and the summary
  labels them ("no browser, allowed in CI"). Run release mode locally before
  tagging.
- **Screenshots:** `ui_check.py --baseline save` keeps them in
  `_local/shots/baseline/`; `--baseline compare` lists which pages, widths,
  and themes changed (informational, exit status unaffected). The component
  gallery is shot full length, so its light and dark pair reviews the whole
  design at once. `ui_check.py --pdf-result [PDF]` screenshots Check your PDF
  showing a result. Shared helpers live in `scripts/common.py` (paths, site
  settings, class version) and `scripts/chrome.py` (the headless browser).
- **`tidy.py`** removes local branches and worktrees already merged into
  `origin/main`, including rebase merges when every unique commit's patch is
  in `main` and all changed paths still match it. A branch that changed again,
  moved after the check, or cannot be proven merged stays. It never touches
  `main`, the current worktree, locked worktrees, or uncommitted changes. It
  also deletes entries of `_local/design/` and `_local/shots/` untouched for
  14 days, never the screenshot baseline or the rest of `_local/`.
- **`task.py`** runs the cycle. Worktrees live in the main checkout's
  `_local/wt/`, and every worktree writes screenshots to the main checkout's
  `_local/shots/`, so one baseline serves them all. The branch has no
  upstream until `finish` pushes it, so a plain push never targets `main`.
  The Codex review prompt lives only in `REVIEW_PROMPT` in `task.py`; its
  output is saved to `build/review.md`.

## Pull requests from forks

`main` requires the **build** check to pass (admins may still push small guide
fixes directly). A first-time contributor's workflows wait for **Approve and
run workflows** on the pull request. Auto-merge is not available for pull
requests from forks: wait for the required **build** check, then rebase-merge
by hand and thank the contributor (offer a credit in
[CREDITS.md](../../CREDITS.md#people)).

## Versions and compatibility

One version number everywhere. **The class is the version:** the
`\ProvidesClass` line in `rpi-thesis.cls` holds a date and `vX.Y.Z`; the
website footer, ZIP names, `CITATION.cff`, and every PDF's Creator property
use the same number. `main.tex` asks for that date
(`\documentclass{rpi-thesis}[YYYY/MM/DD]`), so an older class warns on every
compile. LaTeX compares only dates, so two releases on the same day look the
same to it; the change log says which versions work together.
`scripts/package.py` refuses a release when the dates differ.

- `Z` (patch): fixes that change no PDF, and guide-only changes.
- `Y` (minor): new settings, or formatting corrected to match OGE
  (**Changes your PDF? Yes**). Before 1.0.0, breaking changes also bump `Y`.
- `X` (major): from 1.0.0, a breaking change to settings or commands.
- Versions below 1.0.0 are the beta: plain `vX.Y.Z` tags, marked as
  pre-releases on GitHub; the version never carries `-beta`.

### Compatibility

Before 1.0, anything may change (settings, files, pages, addresses), with no
aliases and no redirects, and the change log says what to do. The guide's
"Update the formatting safely" section and the README that
`scripts/package.py` writes into both ZIPs say the same.

From 1.0, students update by replacing `rpi-thesis.cls` alone, often in the
middle of a thesis: an update never needs another file changed and never
breaks a thesis that compiled before. Formatting lives only in the class;
every `\thesissetup` key and starter command keeps working (a rename keeps the
old name as an alias that warns); and if an update truly needs a change
elsewhere, the change-log entry gives the exact edit.

## Review a requirement change

The steps are the "Review a requirement change" recipe in
[AGENTS.md](../../AGENTS.md#recipes). Reviewed OGE documents are recorded in
`sources.json` and the [requirements map](requirements.md); the health check
(below) does not notice a manual replaced at the same address, so the yearly
review re-reads the documents.

## The website

Markdown is the only source; HTML is generated and never edited or committed.
Contributors do not need Pandoc; CI builds everything.
`python3 scripts/build_site.py` writes `dist/site/` (`--previews` adds pictures
of sample pages and needs TeX Live and poppler); `python3 scripts/package.py`
writes the ZIPs to `dist/`.

- **Links:** the build checks every local link and heading anchor and refuses
  linked source files and folders. Links between Markdown files become links
  between pages; a link to another repository file becomes a GitHub link. Page
  lists (`NAV`, `PROJECT`) are in `scripts/build_site.py`. A guide heading
  that another page links to carries a fixed id (`## Heading {#heading}`), so
  rewording it keeps the links; keep the id when you edit the text.
- **Build stamp:** every online page carries
  `<meta name="rpi-thesis-build" content="SHA">`, and the site root has
  `build.txt` (`commit=<SHA>` and `release=v<RELEASE_VERSION>`), so a live
  check can tell which build is served. The SHA is `GITHUB_SHA` in CI, else
  `git rev-parse HEAD`; `--publish` fails without one. The offline guide
  carries neither.
- **JavaScript is optional.** The scripts in `site/` (`copy.js`, `viewer.js`,
  `theme.js`, `search.js` and its index, `site/pdf-check/`) are enhancements;
  search sends nothing anywhere.
- **Check your PDF** (`site/pdf-check/`) reads a PDF in the browser with
  pdf.js, vendored unchanged in `site/pdf-check/pdfjs/` with its license (to
  update it, follow the comment at the top of `core.js`). Its checks name
  rules and measurements by id from the requirements map, listed in
  `RULE_IDS` and `MEASURE_IDS` in `core.js`; `build_site.py` stops on an
  unknown id. `check.py` reads the same Measurements table, so change a number
  only there. The offline guide leaves the checker out.
- **Colors:** light and dark tokens live in section 2 of `site/site.css`.
- **Allowed files:** HTML, CSS, SVG, the named scripts, WOFF2 fonts, PNG or
  WebP under `previews/`, and the cheat sheet PDF.

The student ZIP (`rpi-thesis-starter-v<version>.zip`) holds the thesis files,
`assets/README.md`, `scripts/build.py`, the `.vscode` settings, a student
`.gitignore`, `README.md`, `LICENSE.md`, the offline guide (`START-HERE.html`),
and the cheat sheet PDF. Maintainer pages, `AGENTS.md`, `CLAUDE.md`, site
tooling, and every RPI file stay out; `package.py` refuses any seal file and
any other PDF, and requires `site_url` and `repository_url` in
`site/site.json`. A relative link in a shipped Markdown file to a file the ZIP
leaves out becomes a link to that file at the release tag; only those link
destinations are rewritten, and a broken or unfindable link stops the build.

### Workflows

- **`build.yml`** verifies every pull request and push. A push to `main`
  deploys the website when `scripts/release.py gate` allows it: the commit is
  still the tip of `main`, its version is the newest release, and the starter
  ZIP built in this run equals the released one except for the offline guide
  and cheat sheet. So guide fixes go live at once and starter changes wait for
  a release. Every deploy also reads the live `build.txt` and refuses when the
  live commit is newer or on another line of history, unless **rollback** is
  set; a missing `build.txt` counts as the first deploy, an unreadable one
  fails. The gate runs again inside the Pages lock just before publishing. A
  pushed `vX.Y.Z` tag releases.
- **`fresh-machines.yml`** installs TeX on new Windows, macOS, and Ubuntu
  machines the way the guide says and compiles the starter: on each release
  tag, monthly, and on demand. It never blocks a release.
- **`health.yml`** runs monthly: external links and RPI's thesis pages
  (`scripts/health.py` against `scripts/oge-watch.json`), and a full verify on
  the newest, unpinned TeX Live. Problems open one issue labelled `health`.
  The watch compares the links and text in each page's `<main>`; `--update`
  records every page or nothing. Not covered: a manual or checklist replaced
  at the same Box address (only its links are compared).

### Updating pinned tools

CI pins its tools so a build does not change by itself.

- **Pandoc:** `PANDOC_VERSION` and `PANDOC_SHA256` in `build.yml` (checksum of
  `pandoc-<version>-1-amd64.deb` on the
  [Pandoc release page](https://github.com/jgm/pandoc/releases)).
- **TeX Live:** the `sha256:` digest after `texlive/texlive:latest@`, from
  [Docker Hub](https://hub.docker.com/r/texlive/texlive/tags), with the date in
  the comment. Look at the PDFs after a change.
- **pypdf:** `PYPDF_VERSION` and `PYPDF_SHA256` (the `py3-none-any` wheel on
  [PyPI](https://pypi.org/project/pypdf/#files)).
- **Actions:** the latest major version of each `actions/...` step.
- **Helper websites:** the `helpers` list in `sources.json` (named in
  "Helpers for common tasks" in `docs/writing.md`). Each must load without
  sign-in, match the guide's menu names and the draw.io privacy note, and
  compile the guide's snippets; update `last_reviewed`. Replace a tool that
  changed rather than adding alternatives. Mathcha's TikZ export is not
  verified with this class; Lagrida was omitted as a second similar editor.

## Release internals

The steps are the Release row of the
[development cycle](../../AGENTS.md#development-cycle).

- **`bump.py`** sets the version everywhere (class line and date, `main.tex`,
  download links, `CITATION.cff`, the change-log heading). Without a version
  it picks minor when the Unreleased "Changes your PDF?" line says anything
  but No or the section names a new setting, else patch. The version must
  increase, and it checks every source before writing, so a missing heading
  or link changes no files.
- **On the tag**, `build.yml` verifies in release mode, creates or resumes the
  GitHub pre-release with both ZIPs and `rpi-thesis.cls`
  (`scripts/release.py publish`: existing assets must match by sha256), deploys
  the website, and checks that the live site serves this build and every
  download matches (`scripts/release.py live`).
- **A failed tag run** can be re-run: each step checks what is already done.
  If it needs a code fix and the release does not exist yet, fix on `main`
  and move the tag (`git tag -f vX.Y.Z && git push -f origin vX.Y.Z`); once
  assets are published, make a new patch release instead. A tag older than
  the newest release never deploys.
- **Rollback:** Actions, **Build thesis, website, and starter ZIP**, Run
  workflow on the older tag with **rollback** ticked; the next deploy from
  `main` replaces it. A tag run uses that tag's own `build.yml`, so never
  dispatch a tag whose `build.yml` lacks the **rollback** input or the
  live-site check; revert on `main` and release a patch instead. The
  `github-pages` environment allows `main` and `v*` tags to deploy.

## Public release readiness

**Keep true at all times:**

- [ ] `git ls-files`, the starter ZIP, and the published Git history contain
      no seal, original template, manual, checklist, or slides. Local backup
      branches made before a cleanup are never pushed.
- [ ] Every public page presents the project as unofficial and community-made.
- [ ] CI passes on `main`, and the maintainer authorizes each publication.
- [ ] GitHub settings: description ("Unofficial, community-made LaTeX thesis
      and dissertation starter and guide for RPI graduate students"); topics
      (latex, thesis, dissertation, rpi, rensselaer, latex-template,
      thesis-template, overleaf, zotero, biblatex); Pages source **GitHub
      Actions**; Issues on, Discussions off; `main` requires the **build**
      check; labels `question`, `enhancement`, `bug`, `documentation`,
      `good first issue`, `help wanted`, and the areas `class`, `guide`,
      `site`, `checker`, `tooling`, `health`; default read-only Actions
      token; a social preview image without RPI artwork; `site_url` and
      `repository_url` in `site/site.json` and `CITATION.cff`.

**Before 1.0.0** (open; releases until then are pre-releases):

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

The most useful feedback describes one task and the moment it became hard:
someone compiles the example, changes their name, and edits a paragraph
without coaching, then says where they paused. Record their editor, operating
system, and toolkit version; keep private research out; offer opt-in credit in
[CREDITS.md](../../CREDITS.md#people).

For OGE: the MS and doctoral sample PDFs, a link to the source, the
requirements map, source dates, and known gaps. Useful questions: title-page
details and seal, spacing, font, section order, and common rejection patterns.
Keep community maintenance independent unless a formal agreement is made, and
record any feedback with the version it applies to.

## Handing over the project

- Transfer the repository or add the new maintainer with admin rights; update
  `site/site.json` if the addresses change (`build_site.py`, `package.py`, and
  `health.py` read them from there; guide pages and `README.md` link them by
  hand, and `CITATION.cff` has its own copy).
- Hand over the help and feedback form and its response sheet.
- Confirm no RPI-owned files are tracked and the new maintainer knows
  [the principles](../../AGENTS.md#principles).
- Run `verify.py` once on their computer; review open issues and every
  `TODO(verify)` marker.
- Add the outgoing maintainer to [CREDITS.md](../../CREDITS.md#people), with
  their consent. Share notes by adding them here, not by handing over `_local/`.
