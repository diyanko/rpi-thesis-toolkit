# Maintaining the toolkit

This page is for whoever looks after the project next — probably another
student. Keep things simple: fewer moving parts means fewer things to break.
The current version and its validation record are in
[CHANGELOG.md](../../CHANGELOG.md). Each new change-log entry starts with a
**Changes your PDF?** line so students know whether to update.

Much of this project is drafted and maintained with AI coding agents; every
change is reviewed by a human maintainer and must pass the automated checks.
Agents follow [AGENTS.md](../../AGENTS.md); the
[maintainer handbook](README.md) lists every maintainer page.

## RPI materials

Never commit RPI-owned material (seal, original template, manuals,
checklists, slides). Maintainers keep reference copies in `_local/` (ignored)
and link to RPI's pages. Compare against RPI's official template when
changing formatting, and record differences in
[requirements.md](requirements.md). RPI's official LaTeX template and the
seal are on RPI ITS's
[Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation);
keep your copy of the template in `_local/legacy/` and the seal in
`assets/rpi-seal.jpg` (both ignored by Git).

Maintainer decisions (14 Oct 2026), settled and not awaiting anyone's input:

- **No RPI materials are redistributed.** Nothing RPI-owned is in the
  repository, the starter ZIPs, or the website, so no redistribution
  permission is needed.
- **The seal:** the toolkit uses the current seal supplied on RPI ITS's
  Thesis Preparation page. Each student downloads it and saves it as
  `assets/rpi-seal.jpg` (or `.png`); until then the title page shows a
  placeholder. The seal stays out of the repository, the starter ZIPs, the
  website artwork, and this project's license. (The 2026 manual's sample title
  page shows an older design; the Thesis Preparation download is the one we
  point to.)

These are the maintainer's project decisions, not OGE approval and not
permission to redistribute RPI artwork. Present the project as unofficial and
community-made ([style guide](style-guide.md#talking-about-rpi)).

## Where things live

The full map of public, generated, and local-only files is in the
[maintainer handbook](README.md#where-things-live). Personal notes,
prototypes, and downloaded OGE documents go in `_local/`, which Git ignores.

The guide's stages and page order are defined once, in `NAV` at the top of
`scripts/build_site.py`: four stages (Start, Write, Fix and finish, Go
further), each with its pages. The grouped sidebar, header links, and
previous/next links are generated from it. The landing page's **Help at your
level** cards in `site/index.html` follow the same four stages by hand, and
so does the guide list in `README.md`; update them when `NAV` changes.

Help and feedback arrive through GitHub Issues (the issue forms in `.github/`)
and one "help and feedback" form that needs no sign-in. The form's URL lives
in exactly one place: the "Ask for help" section of `docs/troubleshooting.md`
(`#ask-for-help`). Paste or change it only there; `README.md`,
`CONTRIBUTING.md`, and the website footer's **Help & feedback** link all point
to that section. The repository lives on the owner's personal GitHub account;
do not hard-code an organization name in docs or scripts.

Turn support into documentation: when a question could come up again, add a
one-line row to the "Common messages" table in `docs/troubleshooting.md` (or
open a GitHub issue labeled `documentation` to do it later). Spend about 10
minutes a month triaging the form's response sheet.

## The website

Markdown is the **only** source. HTML is generated, never edited or committed.
Contributors do not need Pandoc; CI builds everything.

To preview locally (needs [Pandoc](https://pandoc.org/installing.html) 3.11 or newer):

```sh
python3 scripts/build_site.py              # website in dist/site/
python3 scripts/build_site.py --previews   # also pictures of sample pages
python3 scripts/package.py                 # student ZIP in dist/
```

Open `dist/site/index.html` in a browser. The build checks every local link and
heading anchor and fails with the page and link to fix. A missing diagram in
`docs/diagrams/` is only a warning while the diagrams are being drawn.

The build holds an operating-system file lock beside its output folder,
using [flock on Unix](https://docs.python.org/3/library/fcntl.html#fcntl.flock)
or [byte-range locking on Windows](https://docs.python.org/3/library/msvcrt.html#msvcrt.locking).
The lock file stays in place; the operating system releases the lock when
the process exits, including after a crash. Do not delete the file while a
build runs. Linked source files and linked source folders are refused before
their contents enter the website or starter ZIPs.

How the website is put together:

- `dist/site/index.html` is the landing page: `site/index.html` wrapped in
  `site/guide-template.html`. Guide pages are `guide/<name>.html`. `README`
  (About), `CREDITS`, `CONTRIBUTING`, `CHANGELOG`, `LICENSE`,
  `CODE_OF_CONDUCT`, and the requirements and attribution records are
  `project/<name>.html` (the list is `PROJECT` in `scripts/build_site.py`).
  Those with a label are in the footer; the code of conduct and the
  attribution record are linked from the credits and contributing pages
  instead. The handbook overview (`docs/project/README.md`) and the style
  guide stay on GitHub only.
- Links between Markdown files become links between pages. A link to any other
  repository file (for example `main.tex`) becomes a GitHub link once
  `repository_url` is set in `site/site.json`, and plain text until then. The
  same setting turns on the footer's **Edit this page** and **Suggest a
  change** links; `site_url` adds canonical links for search engines.
- Every footer shows the edition line, read from `docs/project/sources.json`
  (first document and `last_reviewed`) and the `\ProvidesClass` line of
  `rpi-thesis.cls`. Update those, never the template, when they change.
- Two more optional scripts: `site/copy.js` adds labelled Copy buttons to code
  blocks, and `site/viewer.js` opens "View larger" pictures as a dialog (and
  hides the link when a drawing is already shown near full size). Without
  JavaScript, code stays selectable and the same links open the picture
  through CSS (`:target`), with Close going back.
- Optional guide search uses `site/search.js` and a generated
  `search-index.js`. The build indexes the rendered guide headings and full
  section text, before navigation is added, and checks every result's page
  and anchor. Each troubleshooting table row gets a generated anchor and a
  separate result, using its message and the guide's suggested fix.
  Optional examples have separate results at their disclosure anchors, so
  selecting a hidden fix opens its containing example. Text from inside an
  example is not attributed to the heading above it. Task
  labels from **How do I…?** also describe their destination sections in the
  index. Project pages, PDFs, and local files are not indexed. The data
  loads as a classic script so the same search works from offline `file:`
  pages without a server. A compact search control beside the appearance
  switch opens the search dialog. On phones the header control uses a
  labeled magnifying-glass icon. This is the only search entry point;
  the sidebar and **How do I…?** keep their task links. Search stays hidden until
  ready; task links and navigation work without JavaScript. Ctrl+K or Cmd+K
  opens search; Tab visits result links, arrow keys move between them, Enter
  from the field opens the first result, and Escape closes the dialog.
  Ranking favors section headings and task labels over body text, weights
  distinctive terms more heavily, and tolerates missing words in a longer
  question. Normalization preserves meaningful symbols such as `??`, `$`,
  `&`, and braces; distinct “Missing … inserted” errors stay distinct.
  Pasted logs are reduced to their first diagnostic before the single-line
  field can discard line breaks. Log searches discard line-number noise.
  Known error signatures take priority. Synonyms, spelling tolerance,
  and task-intent rules live in `site/search.js`. Short searches such as
  `APA`, `TOC`, `MS degree`, or `Biber` lead with the main task rather than
  an obscure error mentioning that word. Related results are
  labeled; unrecognized logs point to reading errors and asking for help,
  without inventing a fix. No query is sent to a server or stored.
  When changing it, check real guide queries (including `bibliograpy`,
  `seel`, `my bibliography doesn't show up`, `my picture is on the wrong
  page`, `??`, and pasted errors with paths and line numbers), keyboard and screen-reader
  behavior, empty results, both themes, and the packaged offline guide.
- The optional `site/theme.js` restores a saved Light or Dark choice before
  the stylesheet loads; System leaves appearance to the device. The header
  button appears only after its handlers are ready. Its panel closes with
  Escape or a click outside, and the current choice is labeled for screen
  readers. Storage failures leave
  switching usable on the current page; saved choices across offline
  `file:` pages depend on the browser. Light tokens and the `--dark-*`
  palette live in section 2 of `site/site.css`. Both automatic and explicit
  dark modes map to that same palette. When changing themes, also check
  checkmarks, embedded SVG diagrams, native controls, and print with Dark
  selected. The site build makes fixed Light/Dark SVG copies under `themes/`
  and checks their links. The optional script selects those copies for manual
  choices, including responsive images and the favicon; System and no-script
  pages retain the original SVGs. This avoids relying on browsers to pass a
  manual theme into an SVG's media query. Keep actual PDF previews white. See
  [MDN on embedded SVG appearance](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-color-scheme)
  and [browser storage limits](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage).
- `--previews` compiles the sample thesis and saves the contents page, a
  chapter opening, a table/figure page, and the references as PNGs in
  `previews/` (needs TeX Live and poppler's `pdftoppm`/`pdftotext`; skipped with
  a note if missing). The title page is never used.
  It also compiles the marked `class-demo-source` code block in
  `docs/why-latex.md` twice, changing only `amsart` to `IEEEtran`, and saves
  each first page and its total page count. The optional layout switcher uses
  native radio buttons and CSS; plain builds without previews omit it, and
  the explanation and copyable source remain available. Missing article
  classes skip this comparison without affecting thesis previews. Keep the
  source free of class-specific adapters so the one-word claim stays true.
  With TeX present it also compiles `cheatsheet/cheatsheet.tex` to
  `downloads/rpi-thesis-cheatsheet.pdf`.
- The site may contain only HTML, CSS, SVG, the named optional JavaScript
  files and generated search index, WOFF2 fonts (with their license
  text), PNG/WebP files under `previews/`, and the cheat sheet PDF. Git
  history, `_local/`, research, other PDFs, LaTeX sources, `reference/`,
  `assets/` (where students put the RPI seal), and archives are refused.

`.github/workflows/build.yml` runs on pull requests and pushes to `main`, in a
TeX Live container: it compiles the thesis, runs `check.py` (without the
seal, so the title page shows the placeholder, and with the legacy hash check
skipped), builds the website with previews and the cheat sheet, fails if the
cheat sheet PDF is missing, and packages the ZIP. The ZIP and website are kept
as workflow artifacts (no thesis PDFs). Publishing to GitHub Pages is manual:
a maintainer runs the workflow from the **Actions** tab on `main` and ticks
**publish**, only after authorization and after the
[public-release checklist](#public-release-readiness) is complete. See
[GitHub's custom-workflow guide](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

The student ZIP (`rpi-thesis-starter-v<class version>.zip`) holds the thesis
files, `assets/README.md` (how to download the seal), `scripts/build.py`,
`.vscode/settings.json`, `.vscode/extensions.json`, a student `.gitignore`,
`README.md`, `LICENSE.md`, the offline guide in `guide/` (opened by
`START-HERE.html`), and `rpi-thesis-cheatsheet.pdf` when the cheat sheet has
been compiled. Maintainer pages, `AGENTS.md`, `CLAUDE.md`, site tooling,
`cheatsheet/` sources, and every RPI file (the seal, the original template)
stay out; `package.py` refuses any seal file and any other PDF.
Packaging also requires a nonempty `site_url` in `site/site.json` for the
Overleaf README's guide link; an unset address stops packaging before either
existing ZIP is replaced.

### Updating pinned tools

CI pins its tools so a build does not change by itself. Once a year (or when
something breaks):

- **Pandoc:** set `PANDOC_VERSION` in `build.yml` to the version you use
  locally, and `PANDOC_SHA256` to the checksum of `pandoc-<version>-1-amd64.deb`
  shown on the [Pandoc release page](https://github.com/jgm/pandoc/releases).
- **TeX Live:** replace the `sha256:` digest after `texlive/texlive:latest@`
  with the current one from [Docker Hub](https://hub.docker.com/r/texlive/texlive/tags),
  and update the date in the comment. Then run `check.py` and look at the PDFs.
- **pypdf:** set `PYPDF_VERSION` in `build.yml` to the new version, and
  `PYPDF_SHA256` to the sha256 of its `py3-none-any` wheel, shown under
  **Download files** on [pypdf's PyPI page](https://pypi.org/project/pypdf/#files).
  Then run `check.py`.
- **Actions:** check the latest major version of each `actions/...` step on
  its GitHub releases page.
- **Helper websites:** open each tool in the `helpers` list of
  `sources.json` (named in the "Helpers for common tasks" section of
  `docs/writing.md`), check that it loads without sign-in, that the menu
  names and the draw.io privacy note still match, and that the guide's
  snippets compile; update `last_reviewed`. Each entry records what was
  verified and why a tool was kept or omitted (Lagrida: evaluated, omitted as
  a second similar editor; Mathcha: TikZ export not verified with this class,
  so verify before expanding). Replace or remove a tool that has changed
  rather than adding alternatives.

Writing conventions for the guide, the website, and error messages are in
the [style guide](style-guide.md).

## Review a requirement change

When OGE publishes new guidance, or a student reports a concrete mismatch:

1. Read the latest document through the official submission page. Keep any
   working copy in `_local/`; do not commit or mirror it.
2. Record its title, edition/date, link, review date, hash where useful, and
   relevant sections in `sources.json` and the [requirements map](requirements.md).
3. Separate formatting changes from administrative ones. Change code only for
   formatting; link out for dates, contacts, and forms.
4. Make a small change with a before/after explanation and examples.
5. Build, check, and inspect affected PDF pages. Add a change-log entry with
   its **Changes your PDF?** line. Never overwrite students' writing files.
6. Ask OGE to clarify ambiguous requirements only when authorized. Record what
   was confirmed and by whom; silence is not approval.

Do not change typography from an automated scrape or search result.

## Local verification

```sh
python3 scripts/build.py --doctor
python3 scripts/build.py --fresh
python3 scripts/check.py        # needs pypdf
python3 scripts/build_site.py   # needs Pandoc
python3 scripts/package.py
```

`check.py` builds isolated variants (MS, PhD with copyright and a large
committee, DEng, minimal, LuaLaTeX, XeLaTeX) and checks PDF structure,
including that the seal placeholder appears exactly when `assets/` has no
seal. After a title-page change, run it twice: with `assets/rpi-seal.jpg`
and with the file moved aside (as in CI). If `_local/legacy/` exists, it also
confirms that your local copy of RPI's original template matches the hashes
in `upstream-files.json`; otherwise it prints SKIP. Parsed
PDF text cannot judge layout quality, so also look at the pages.

### Coordinating concurrent work

Use the same process for people and AI assistants:

1. Assign one editor to each file, or an explicit region of a shared file.
   Other reviewers send a reproduction and suggested correction to that
   editor. Keep independent test fixtures and reports in separate `_local/`
   folders. Have one person integrate the changes and write the final report.
2. Run focused checks while editing. Before final verification, stop edits
   and record a SHA-256 manifest of the inputs being reviewed, the commands,
   and the tool environment. A passing result applies to those inputs.
3. Have one build owner run the gates required by
   [AGENTS.md](../../AGENTS.md#verification-gates). When all are needed, run
   the thesis build and structural checks, then the website with
   `--previews`, packaging, and a smoke check of the extracted ZIP. Do not
   replace that preview build with a plain site build before packaging.
4. Reuse completed checks while their inputs remain unchanged. A later
   search correction needs query and browser checks; it does not invalidate
   an unchanged thesis's engine checks. Compare the input manifest after
   testing. If an input changed, rerun its affected gates before handoff.
5. Give the next reviewer one report listing the input manifest, changed
   files, results, evidence locations, and remaining limits. Distinguish
   native operating-system tests from simulations and browser event tests
   from real clipboard checks. Keep commit and publication approval separate.

The existing preview fingerprint checks whether its thesis inputs changed.
Use that freshness check; do not bypass it or add a second preview cache.
File locks prevent overlapping website promotions, but they do not freeze
source files while another editor works.

## Compatibility promise

**During the beta (versions 0.x), there is no compatibility promise.**
Settings, commands, and files may be renamed, simplified, or removed between
versions whenever that makes the starter cleaner. Each such change goes in
`CHANGELOG.md` with **Changes your PDF?** and the exact edit a student needs
to make, and the class reports old or unknown settings with an error that
names the fix.

From version 1.0.0, students copy a newer `rpi-thesis.cls` into an existing
thesis, so within one major version these stay backward compatible:

- every setting in `metadata.tex`, that is, the `\thesissetup` keys and their
  accepted values;
- the commands the starter files use (for example `\committeemember`,
  `\frontchapter`, `\chapterattribution`).

New keys and commands may be added, and formatting may be corrected to match
OGE requirements. Removing or renaming any of the above, or changing what an
existing value means, is a breaking change: bump the major version and
explain the change and the fix in `CHANGELOG.md`.

## Repository settings checklist (when first pushing)

- [ ] **Visibility:** public once the
      [public-release checklist](#public-release-readiness) is complete.
- [ ] **Description:** "Unofficial, community-made LaTeX thesis and
      dissertation starter and guide for RPI graduate students".
- [ ] **Topics:** latex, thesis, dissertation, rpi, rensselaer, latex-template,
      thesis-template, overleaf, zotero, biblatex.
- [ ] **Website:** the GitHub Pages URL. Put it in `site/site.json` as
      `site_url`, and the repository URL as `repository_url`. Add the same
      two addresses to `CITATION.cff` (see [make a release](#make-a-release)).
- [ ] **Social preview image** (Settings → General): a picture that does not
      show the RPI seal or other RPI artwork.
- [ ] **Pages:** Settings → Pages → Source: **GitHub Actions**.
- [ ] **Issues on; Discussions off.** Check that the issue forms and the OGE
      contact link appear under **New issue**, and that the default labels
      `question`, `enhancement`, `bug`, and `documentation` exist.
- [ ] **Actions:** allow GitHub Actions; keep the default read-only token.

## Public-release readiness

Two stages: the repository and website can be public before the first
downloadable release.

### Before the repository goes public

- [ ] **No RPI-owned files anywhere:** `git ls-files` lists no seal,
      original template, manual, checklist, or slides, and neither does the
      starter ZIP. The published Git history must not contain them either;
      local backup branches made before the cleanup are never pushed.
- [ ] Every public page presents the project as unofficial and community-made
      ([style guide](style-guide.md#talking-about-rpi)).
- [ ] CI passes on `main`.
- [ ] Maintainer authorization for publication.

### Before the first release (v0.1.0)

- [ ] Have a novice complete the first-PDF and first-edit workflows unaided.
- [ ] Test fresh installs and editors (VS Code with LaTeX Workshop, TeXShop,
      TeXstudio) on macOS, Windows, Linux.
- [ ] Upload the starter ZIP to Overleaf, add the seal as `assets/README.md`
      describes, and verify a clean build.
- [ ] Test citation presets with URL access dates and caption citations.
- [ ] Review long titles, large committees, long contents/captions, Unicode.
- [ ] Ask OGE for a preliminary formatting review of the sample PDF, as a
      student would, and record the date and outcome in `requirements.md`.

Until then, do not call a release compliant, approved, or fully tested.

## Versions

One version number, everywhere a student or maintainer might look:

- **The class is the version.** The `\ProvidesClass` line in `rpi-thesis.cls`
  holds a date and `vX.Y.Z`. The website footer, the ZIP names
  (`rpi-thesis-starter-vX.Y.Z.zip`), and `CITATION.cff` use the same number,
  and every PDF records it in its document properties (Creator).
- **`main.tex` asks for that date:** `\documentclass{rpi-thesis}[YYYY/MM/DD]`.
  If a student's `rpi-thesis.cls` is older than their starter files, LaTeX
  warns on every compile. `scripts/package.py` refuses to build a release
  when the two dates differ.
- **What changes the number** (see the [compatibility promise](#compatibility-promise)):
  - `Z` (patch): fixes that do not change any PDF, and guide-only changes;
  - `Y` (minor): new settings, or formatting corrected to match OGE; the
    change-log entry says **Changes your PDF? Yes**;
  - `X` (major): from 1.0.0, a breaking change to settings or commands.
    During the beta, breaking changes are allowed and bump `Y`.
- **Beta releases** use the same `vX.Y.Z` tag, marked as a pre-release on
  GitHub; the version itself never carries `-beta`. Versions below 1.0.0 are
  the beta: the website and change log say so in words.

## Make a release

Only with the maintainer's authorization. Everyday changes need none of this:
merge them to `main` and they ship with the next release.

1. **Bump:** `python3 scripts/bump.py X.Y.Z` sets the version everywhere (class
   line and date, `main.tex`, download links, `CITATION.cff`, and the change
   log's "Unreleased" heading). Check the change-log entry reads well.
2. **Verify:** `python3 scripts/verify.py release`. Before a minor or major
   release, also run **Fresh-machine test** in the Actions tab (about an hour)
   on the branch.
3. **Merge** the pull request to `main`.
4. **Publish** from an up-to-date `main`: `python3 scripts/package.py`, then
   `gh release create vX.Y.Z --prerelease --title vX.Y.Z --notes-file <entry>
   dist/rpi-thesis-starter-vX.Y.Z.zip dist/rpi-thesis-overleaf-vX.Y.Z.zip`
   (the ZIPs are reproducible, so they match what CI tested).
5. **Deploy the website:** Actions, **Build thesis, website, and starter ZIP**,
   run on `main` with "publish" ticked. Its strict build refuses to publish a
   site that links a different version than the class.
6. **Check** the live home page's download and "Open in Overleaf" links once.

Feedback that changes formatting (for example from OGE's preliminary review)
goes in the change-log entry and in [requirements.md](requirements.md).
Silence is not approval.


## Roadmap and not yet covered

Each item needs source evidence where formatting is involved, a short tested
example, a plain explanation, and focused validation before it reaches
students.

- **Publication-based theses**, landscape pages, long tables, reference
  styles across disciplines (including citations in captions), and
  first-install problems reported by students.
- **Overleaf template gallery** submission, once a release has been stable
  through a real-student test and an OGE preliminary review.
- **Accessible, tagged PDF**, once the LaTeX kernel's tagging support covers
  the packages the class relies on (including `titlesec` and `caption`). Do
  not claim tagged-PDF or PDF/UA compliance from visual checks.
- Word export stays a review copy only; treat any improvement there as
  separate, carefully tested work.

## Asking for feedback

The most useful feedback describes one task and the moment it became hard.
Ask someone to compile the example, change their name, and edit a paragraph
without coaching, then ask where they paused and what would have helped.
Record their editor, operating system, and toolkit version; keep private
research out. Send any invitation yourself through appropriate channels, and
offer opt-in credit in [CREDITS.md](../../CREDITS.md#people).

## OGE review packet

Offer the MS and doctoral sample PDFs, a link to the source, the
requirements map, source dates, and known gaps. Ask about title-page details
and seal, spacing, font, section order, and common rejection patterns. Keep
community maintenance independent unless a formal agreement is made, and record
any feedback with the version it applies to.
