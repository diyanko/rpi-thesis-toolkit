# Going further

For a thesis or dissertation that already compiles: share drafts, back up,
update the formatting file, get technical help, or change a setting. Pick
the task you need; Git, AI, and the extra packages are optional. Still setting
up? [Get started](get-started.md). For the bigger picture, see
[the suggested workflow](how-it-works.md#the-suggested-workflow-and-why).

## Common situations

- [Move from Overleaf to your computer](#overleaf-to-your-computer), or [the other way](#your-computer-to-overleaf)
- [Use both](#use-your-computer-and-overleaf) (keep one source of truth)
- [Get comments on paper or in a PDF](#an-advisor-reviews-a-pdf)
- [Have an advisor who wants Word](#an-advisor-wants-word-with-track-changes)
- [Show what changed](#show-what-changed-between-drafts) with a changes PDF
- [Bring in a draft written elsewhere](bring-your-draft.md)
- [Write with co-authors or lab-mates](#co-authors-and-lab-mates)
- [Turn a chapter into a paper](#turn-a-chapter-into-a-paper) or [make slides](#make-slides)
- [Write a proposal or qualifying exam](#write-a-proposal-or-qualifying-exam) in the same format

### Overleaf to your computer

1. In Overleaf, download the project **source** as a ZIP, not just the PDF
   ([Overleaf: downloading a project](https://docs.overleaf.com/managing-projects-and-files/downloading-a-project)).
2. Extract it into a normal folder, keeping the folders together.
3. **Add any missing desktop build files.** The small Overleaf starter leaves
   out the build helper (`scripts/build.py`) and editor settings. Find your version in the
   `\ProvidesClass` line near the top of `rpi-thesis.cls`, then download that
   version's **starter ZIP** from [all releases](https://github.com/diyanko/rpi-thesis-toolkit/releases)
   into a separate folder. Copy only missing `scripts/build.py`, `latexmkrc`,
   and the `.vscode` folder into your thesis folder. Show hidden files in
   your file manager if `.vscode` is not visible. Keep your thesis files,
   settings, bibliography, and images.
4. No LaTeX on your computer yet? Follow
   [the your-computer route](get-started.md#step-3a-your-computer-route).
5. Compile `main.tex` and compare the PDF with Overleaf's.

With the copied settings, VS Code writes `build/main.pdf`. Other editors may
put `main.pdf` beside `main.tex`.

### Your computer to Overleaf

1. ZIP your whole project folder, including your downloaded seal in
   `assets/` (you can leave out `build/`).
2. Upload it as a new Overleaf project, then set the main document and
   compiler as in [the Overleaf route](get-started.md#step-3b-overleaf-route).
3. Recompile. Overleaf runs the bibliography step for you.

### Use your computer and Overleaf

The one rule: **only one copy is the source of truth at a time.** Edit there;
treat the other as a backup.

![Your thesis folder and an Overleaf project. Download source (ZIP) goes from Overleaf to your computer; Upload project (ZIP) goes back. Edit in one place at a time. On some Overleaf plans, Git or GitHub sync can keep them in step.](diagrams/overleaf-sync.svg)

*In words:* download a ZIP to move to your computer, upload a ZIP to move to
Overleaf, and edit in only one place.

1. Save and compile where you are.
2. Move the whole project by ZIP ([to your computer](#overleaf-to-your-computer)
   or [to Overleaf](#your-computer-to-overleaf)).
3. Rename the old copy, e.g. `thesis-OLD-2027-02-10`, so you don't edit it by
   accident.

On some plans, Overleaf's [Git and GitHub sync](https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization)
can skip the ZIPs.

### An advisor reviews a PDF

![Review loop. You send a dated PDF to your advisor, who marks it up and sends it back. You make each change in your .tex files, recompile, and send the next dated PDF, until the draft is ready.](diagrams/review-loop.svg)

*In words:* send a PDF → your advisor marks it up → you edit the source →
recompile → repeat.

1. Send a PDF with the date in its name, e.g. `thesis-2027-02-10.pdf`, and keep a copy.
2. Your advisor comments on paper or in a PDF reader.
3. Find each spot in your `.tex` files (search a few words, or click in the PDF
   to jump there) and make the change.
4. Recompile and send the next dated PDF. After big revisions, add a
   [changes PDF](#show-what-changed-between-drafts).

### An advisor wants Word with track changes

A Word copy is for review only: it loses the title page, margins, numbering,
cross-references, and reference formatting.

1. Ask first whether a commented PDF would do; it shows the real layout.
2. If not, convert one chapter and check what was lost. On Overleaf, use the
   [Word export](https://docs.overleaf.com/managing-projects-and-files/importing-and-exporting-files);
   on your computer, use Pandoc (below).
3. Your advisor edits with track changes and comments.
4. Apply each accepted change to your `.tex` files by hand, then compile.

**Never convert the reviewed Word file back into LaTeX for your final
thesis.** Your `.tex` files stay the master copy.

<details>
<summary>Optional: make a Word copy with Pandoc</summary>

[Pandoc](https://pandoc.org/) is a free program that converts documents between
formats ([install it](https://pandoc.org/installing.html)). It does not run the
thesis class, so it loses custom commands, cross-references, and some equations
and tables. In a terminal in your project folder (the one containing
`main.tex`), create the folder once (any terminal):

```sh
mkdir build
```

Then run:

```sh
pandoc chapters/01-introduction.tex --from=latex --to=docx --citeproc --bibliography=references.bib --resource-path=. --output=build/chapter-review.docx
```

This is untested beyond a simple chapter. Choose a CSL style if citation
formatting matters for the review.

Not comfortable in a terminal? Tell an AI assistant your operating system and
goal, for example: "give me the exact commands to make a Word copy of
chapters/01-introduction.tex with Pandoc, and tell me what to check."
([More on AI help](#use-ai-for-technical-help).)

</details>

### Show what changed between drafts

`latexdiff`, included in full TeX Live, makes a PDF with additions and
deletions marked, handy when your committee rereads a revision.

1. Keep the version your committee last saw (a dated backup ZIP). On Overleaf,
   [History](https://docs.overleaf.com/writing-and-editing/history-and-versioning)
   can download an earlier version.
2. Run latexdiff on your computer (below), or follow
   [Overleaf's latexdiff article](https://www.overleaf.com/learn/latex/Articles/How_to_use_latexdiff_on_Overleaf).
3. Check the changes PDF before sending it: changed equations, tables, and
   figures can come out messy.

<details>
<summary>Optional: make a changes PDF with latexdiff</summary>

Extract the old version into a folder named `old` beside your project folder,
and create a `build` folder in your project folder. Open a terminal there:
**Command Prompt** on Windows (PowerShell's output encoding can differ),
**Terminal** on macOS or Linux.

Create the comparison file. On Windows, run this in Command Prompt: in
PowerShell 5.1, `>` writes a different encoding.

```sh
latexdiff --flatten ../old/main.tex main.tex > build/changes.tex
```

The changes PDF would lose any citation whose entry you deleted from
`references.bib`. So give it a comparison bibliography that holds the entries
from both versions, and leave your real `references.bib` alone:

1. Create `build/compare.bib` containing the text of `references.bib`
   followed by the text of `../old/references.bib`. In a text editor, paste one under
   the other; on macOS or Linux,
   `cat references.bib ../old/references.bib > build/compare.bib`.
2. Open `build/changes.tex` and change the line
   `\addbibresource{references.bib}` to `\addbibresource{build/compare.bib}`.
   (This is the generated file, not your thesis.)

Then compile it:

```sh
latexmk -norc -pdf -no-shell-escape -outdir=build build/changes.tex
```

Biber warns about duplicate keys and skips the second copy; that is expected.
Putting the current entries first keeps any corrected source details, while
the old file supplies entries you deleted.

`--flatten` pulls the chapter files into one document, so comment out any
`\includeonly` line in both versions first. The result is `build/changes.pdf`.
The Overleaf method in the linked article has not been tested with this
starter, and it may not handle deleted references either.

Not comfortable in a terminal? Tell an AI assistant your operating system, your
folder names, and the goal, and ask for the exact commands and what to check.

</details>

### Co-authors and lab-mates

1. Share **one** project: invite them to your Overleaf project (check
   [Overleaf's plans](https://docs.overleaf.com/getting-started/free-and-premium-plans)
   for collaborator limits) or use a
   [private GitHub repository](#use-a-private-github-repository).
2. Agree who edits which chapter, so two people don't rewrite the same paragraph.
3. Prefer comments for suggestions; it is your thesis. Word-using colleagues
   can still [share sources](citations.md#if-co-authors-use-word).

### Turn a chapter into a paper

1. Start from the venue's own template (for example `IEEEtran` or `acmart`,
   from Overleaf's gallery or the publisher's author page).
2. Copy in the chapter's text, equations, figures, and the `.bib` entries it
   cites. Drop thesis-only commands such as `\chapterattribution`.
3. Follow the venue's author instructions and its policy on material from a
   thesis.

**If the venue's template uses BibTeX** (many do, instead of biblatex), your
`\cite` keys carry over, but this starter's `.bib` entries use biblatex-only
fields such as `urldate`, which BibTeX styles ignore. Years and web details can
silently disappear. To fix this:

- Export a BibTeX-format file for the paper, keeping the same citation keys.
  In Zotero, choose **Better BibTeX** (not Better BibLaTeX) or plain **BibTeX**.
- Swap `\thesisreferences` for the venue's bibliography lines (with BibTeX,
  usually `\bibliographystyle{...}` and `\bibliography{...}`).
- Replace biblatex-only commands such as `\textcite` (with `natbib`, `\citet`;
  see [the citation commands](citations.md#change-the-citation-style)), then
  check the reference list.

### Make slides

Reuse the images in `figures/` in any slide or poster tool. To stay in LaTeX,
start from a **Beamer** template or a poster template (Overleaf's gallery has
many) and copy in your figures.

Optional: to turn Markdown slides into PowerPoint, run
`pandoc talk.md --slide-level=1 --output=talk.pptx` in a terminal
([Pandoc](https://pandoc.org/) is a free converter). It starts a new slide at
each top-level heading (`# Slide title`); lower-level headings stay on that
slide.

### Write a proposal or qualifying exam

Other long documents, such as a thesis or candidacy proposal or a research or
doctoral qualifying exam report, can use the starter as a model: the same
chapters, citations, figures, and page layout. OGE does not review them, so
follow what your department or committee asks for.

Copy the starter into a new folder. Keep `metadata.tex` filled in (the class
still checks it), and in `main.tex` replace `\maketitle` with a simple title
page of your own, whose lines you can change freely:

```latex
\pagenumbering{roman}
\begin{titlepage}
  \centering
  \MakeUppercase{Your proposal title}\par
  \vspace{2\baselineskip}
  Your Full Name\par
  \vspace{2\baselineskip}
  Doctoral Candidacy Proposal\par
  Department of Your Department\par
  Rensselaer Polytechnic Institute\par
  \vspace{2\baselineskip}
  May 2027\par
\end{titlepage}
\setcounter{page}{2}
```

Delete the front-matter lines you do not need, such as the acknowledgment.

## Back up your work

Keep your thesis in two places, one off your computer, so a lost laptop costs
you an afternoon, not a thesis. Pick what suits you:

- **A cloud-synced folder** (OneDrive, Google Drive, Dropbox, or iCloud): keep
  your thesis folder inside it.
- **A private GitHub repository** ([set one up](#use-a-private-github-repository)).
  Never public.
- **Overleaf:** use its **History**, and download the **source ZIP** regularly
  and before big changes. On some plans, Git or GitHub sync also works.
- **Your computer's own backup** (Time Machine, File History, an external
  drive) is a good extra layer.

Watch for these:

- **Sync is not backup.** A deleted or damaged file syncs everywhere, so learn
  where your service keeps version history.
- **Keep files on your computer.** Mark the thesis folder "Always keep on this
  device"; OneDrive and iCloud can leave files online only, and LaTeX then
  cannot find them.
- **Edit on one computer at a time,** and let sync finish before switching, or
  you get conflict copies such as `main (1).tex`.
- **Zotero:** keep its data folder out of cloud-sync folders
  ([details](citations.md#where-zotero-keeps-your-library)).
- **Sensitive data** (IRB-approved interviews, export-controlled data, data
  under a data-use agreement) follows RPI's rules and your agreement, not
  personal cloud storage.

Also keep each dated PDF you send and the scripts and data behind your figures.
At submission, archive the final source, the submitted PDF, and your permission
documents in two places. Git's ignore rules leave out compiled PDFs and the
downloaded seal: keep a separate final archive that includes them. Now and
then, extract a backup and compile it to prove
it works. If a tool reports a missing file and your folder path has spaces or
unusual characters, try a simple path like `~/thesis`.

## Use a private GitHub repository

Optional: you need neither Git nor GitHub to finish your thesis. **Git** saves
snapshots (*commits*) of your folder on your computer. **GitHub** stores Git
projects online; uploading is a *push*, and Git history on the same disk is not
a backup until you push it. Keep a thesis in a **private** repository (only
you and people you invite can see it): unpublished research doesn't belong in
public.

> [!WARNING]
> **Don't fork the toolkit for your thesis.** A fork of a public repository
> is public, and GitHub doesn't let you make it private
> ([GitHub: visibility of forks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-permissions-and-visibility-of-forks)).

Use one of these private routes instead:

- **A new private repository:** create one and choose **Private**
  ([GitHub: creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)).
  Then add your starter's files with **Add file → Upload files**.
- **Use this template:** if the toolkit's GitHub page shows a **Use this
  template** button, click it, choose **Create a new repository**, and set
  **Private**
  ([GitHub: creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)).
  <!-- TODO(verify): checked 14 Oct 2026 against the GitHub docs linked here. On that date the toolkit repository was not marked as a template, so the button does not appear yet. Enable "Template repository" in its settings, or remove this route. -->

**Without a terminal:** to save later work, open the repository's page.
GitHub's uploader puts each file in the folder you are viewing, so an
uploaded chapter lands at the top level unless you first open the matching
folder.

1. Open the folder that matches where the file lives on your computer (for
   `chapters/02-research.tex`, open `chapters` on GitHub first). Choose
   **Add file → Upload files**, drag in the changed file, and commit.
2. Check the path shown above the file (for example `chapters/02-research.tex`,
   not `02-research.tex` at the top) and open the file to confirm the content
   is your latest.
3. Renamed or deleted files are not updated by an upload. Open the old file on
   GitHub, delete it there (the pencil or **…** menu), and upload the new one.
4. Check that your commit appears in the **commit list** (the **Commits**
   link on the repository page).

The first upload of the whole project can be large: GitHub's browser upload
is limited to 100 files at a time, so upload folders in batches, or use
[GitHub Desktop](https://desktop.github.com/) or a
[cloud-synced folder](#back-up-your-work) instead
([GitHub: adding a file](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)).
<!-- TODO(verify): the 100-file browser-upload limit and the folder-upload behavior were not re-checked against GitHub's current documentation. -->

To get back an older chapter, open that file on GitHub, choose **History**,
open the older version, and download it. Do not work in your real folder:
copy your whole project, put the old chapter in the *copy*, compile, and
compare the PDF with your current one. Only then replace the file in your
real project. For ongoing backups, the simpler
[cloud-synced folder](#back-up-your-work) is easier to keep up.

<details>
<summary>Optional: Git commands for local snapshots</summary>

These commands save **local snapshots**; they upload nothing. First
[install Git](https://git-scm.com/downloads) and follow
[Git's first-time setup](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup).
Open a terminal in the folder containing `main.tex`.

Start a history:

```sh
git init
```

Save a snapshot (`git add .` stages every unignored file; run `git status`
first to see the list):

```sh
git add .
```

```sh
git commit -m "Start my thesis from the starter"
```

Later, run `git diff` to review a change, then add and commit it the same way.
If `git diff` or `git log` fills the screen, press `q` to return.
The `.gitignore` keeps generated files and PDFs next to `main.tex` out of Git;
PDF figures in `figures/` are kept.

If you **cloned** the toolkit's repository, it is your `origin` remote: never
push your thesis there. Run `git remote -v` and point `origin` at your own
private repository before pushing. An AI assistant can walk you through this
for your system ([AI help](#use-ai-for-technical-help)).

</details>

## Update the formatting safely

Formatting fixes arrive in one file, `rpi-thesis.cls`. Updating usually means
replacing that file; your chapters, `metadata.tex`, and `references.bib` stay
as they are ([why](how-it-works.md#your-words-and-your-formatting-are-separate)).
Before version 1.0, anything may change, and the changelog says what to do.

1. **Read the changelog** entries newer than your version (below), and note
   any edit they ask for besides the class.
2. **Download the newest class:**
   [rpi-thesis.cls](https://diyanko.github.io/rpi-thesis-toolkit/downloads/rpi-thesis.cls)
   (it is also inside every new starter ZIP).
3. **Replace yours.** On your computer, save it over the `rpi-thesis.cls` next
   to `main.tex`. On Overleaf, click **Upload**, choose the file, and confirm
   that it replaces the old one. Make any other edit the changelog named.
4. **Recompile and look** at your PDF, especially the title page, contents,
   and page numbers.

Which version do you have? The quickest way: drop your PDF into
[Check your PDF](check-pdf.md); it names the version that made it and says
whether a newer one exists. Your compile log also has a line of the form
`rpi-thesis YYYY/MM/DD vX.Y.Z`, and the website's footer shows the newest. The
[changelog](../CHANGELOG.md) lists what each version changed, starting with
**Changes your PDF?**

Close to a deadline, update only if a change fixes something that affects
you. To hear about updates, use **Watch → Custom → Releases** on the toolkit's
GitHub page (needs an account).

## Use AI for technical help

An AI chat (a tool that explains problems and suggests changes) can make LaTeX
and terminal steps much easier. It is optional, one route beside web search,
official documentation, and [community help](troubleshooting.md#ask-for-help).
Use a tool you already have; nothing here needs a subscription or an AI
account. It is for technical parts, not for writing your thesis.

Four good uses:

- **Explain an error,** or find a missing brace or wrong command
  ([a prompt to copy](troubleshooting.md#ask-an-ai-chat-to-explain-it)).
- **Edit a table, equation, or figure:** turn a screenshot or sketch into
  editable code, resize an image, or fix a caption
  ([prompts to copy](writing.md#ask-an-ai-assistant)).
- **Convert a file** ([below](#ask-for-a-file-conversion)).
- **Run terminal steps** such as Pandoc, latexdiff, or build commands. Give it
  your operating system and goal, and ask for the exact commands and what to
  check. Ask it to explain each one if you want to learn.

To stay in control:

1. Share your goal, your operating system, and one small example or the first
   error. Never paste confidential material, such as unpublished data or
   participant details.
2. Try one suggested change, and keep the original.
3. Compare the result: compile and look at the affected pages.
4. If it doesn't help, undo it.

An **AI assistant that can edit files** can apply fixes for you: work on a
backup, keep the task small, and review every change.

### Prompts to copy

Use the setup, error, and conversion prompts in an AI chat or an assistant
that can edit files. The contribution prompt needs an assistant with file
and GitHub access. Replace the parts in [brackets], and leave out unpublished
data, participant details, and anything else confidential.

**Set up:**

```prompt
I am setting up the RPI Thesis Toolkit, an unofficial, community-made LaTeX starter for RPI theses and dissertations. Its guide is https://diyanko.github.io/rpi-thesis-toolkit/guide/get-started.html. I use [Overleaf / my computer with Windows, macOS, or Linux]. Walk me through [installing LaTeX / opening the starter] one step at a time, following that guide. Do not change rpi-thesis.cls, and do not invent OGE rules: say when I should check OGE's own pages.
```

**Fix an error:**

```prompt
I am using the RPI Thesis Toolkit, an unofficial LaTeX starter for RPI theses. Here is the first error from my compile, with its file and line: [paste the error and the few lines around it]. I use [Overleaf / my computer with Windows, macOS, or Linux]. Explain the cause and suggest the smallest fix. Keep my text, data, and citations unchanged, do not change rpi-thesis.cls or any formatting setting, and do not invent OGE rules.
```

**Convert to LaTeX:**

```prompt
I am using the RPI Thesis Toolkit, an unofficial LaTeX starter for RPI theses. Convert this [Word section / Markdown text / table / equation] into LaTeX for a chapter file of that starter: [paste it or attach the file]. Preserve every word, value, and symbol, and flag anything unclear instead of guessing. Use plain LaTeX commands, add no formatting packages, leave rpi-thesis.cls untouched, and do not invent OGE rules.
```

**Suggest a change to the toolkit** (for an AI assistant that can edit files;
see [CONTRIBUTING.md](../CONTRIBUTING.md)):

```prompt
Read AGENTS.md in https://github.com/diyanko/rpi-thesis-toolkit and follow its "Contributing as an agent" steps. If you cannot fork or push, stop and show me the diff. Do not push or open the pull request until I approve. What I'd like changed: [describe it].
```

### Ask for a file conversion

Describe the result in ordinary words: a LaTeX chapter as a Word review copy, a
Word draft as Markdown, or an image in a format LaTeX accepts. A conversion
program (such as [Pandoc](#an-advisor-wants-word-with-track-changes)) or the
original app's export does the work; AI helps you choose and run it. Give the
input, the output you want, your operating system, and a small example of the
target layout. One prompt to adapt:

```prompt
I have [input file] and need [output format] for [purpose]. I use [Windows/macOS/Linux] and prefer [steps without a terminal / help running the conversion]. Keep the original unchanged. Preserve the content and flag anything that cannot transfer exactly. Return a converted file if your tool supports it, or explain the shortest steps. Tell me what to compare before I use the result.
```

Try one section or image first. Compare wording, values, equations, citation
keys, and image quality with the original; not everything transfers. For an
image, ask it to convert the supplied file without redrawing it.

Routes without AI: [bring a draft into LaTeX](bring-your-draft.md),
[make a Word review copy](#an-advisor-wants-word-with-track-changes), or
[export a chart or image](writing.md#export-a-chart-or-convert-an-image). Keep
one working source; a Word review copy does not update your LaTeX chapter.

## Where customizations belong

| You want to change… | Edit | Notes |
| --- | --- | --- |
| Details shown on the title page | `metadata.tex` | Every setting is in the table below |
| Document order, chapters, optional sections | `main.tex` | References stay before appendices |
| Packages and citation style | `preamble.tex` | Loaded after the class |
| Formatting rules | `rpi-thesis.cls` | Avoid: [updating the class](#update-the-formatting-safely) overwrites edits. Check [the requirements map](project/requirements.md) first |

Extra geometry, spacing, caption, or heading packages in `preamble.tex` can
silently break a requirement; prefer the documented settings. Also:

- **Class options are rejected.** `\documentclass[11pt]{rpi-thesis}` stops with
  "Unsupported class option". The class always uses 12pt, US letter, one-sided.
- **hyperref is already loaded** by the class (with `hidelinks,unicode`). Don't
  load it again; use `\hypersetup{...}` in `preamble.tex`. Packages that must
  load *before* hyperref need a class change.

## All thesis settings

Settings go inside `\thesissetup{...}` in `metadata.tex`. Names and
values are case-sensitive: `degree = doctoral` and `graduation-month = May`
work, `Doctoral` and `may` stop the compile with a message naming them, as
does a setting name the class does not know.

| Key | Values | Notes |
| --- | --- | --- |
| `title` | text, required | Printed in capitals. Math needs one extra step, below the table |
| `author` | text, required | |
| `degree` | `doctoral` (default), `masters`, `engineering-doctorate` | Doctor of Philosophy, Master of Science, Doctor of Engineering |
| `degree-name` | text (default: from `degree`) | Overrides the degree name shown; put it **after** `degree` |
| `department` | text, required | Full name, e.g. `Department of Physics, Applied Physics and Astronomy` |
| `graduation-month` | `May`, `August`, `December`; required | Graduation month, not submission month |
| `graduation-year` | four digits, required | |
| `seal-file` | file path (default: `assets/rpi-seal.jpg`) | Download the seal from RPI ([add the RPI seal](get-started.md#add-the-rpi-seal-one-minute)). If missing, `assets/rpi-seal.png` is tried, then a placeholder box with a warning |
| `copyright-page` | `true`, `false` (default) | Adds the copyright page (ii) |
| `list-of-tables` | `true` (default), `false` | `false` only if you have no tables |
| `list-of-figures` | `true` (default), `false` | `false` only if you have no figures |

**Math in the title:** write it as `\texorpdfstring{$\alpha$}{alpha}`. The
first part is printed; the second is the plain text the PDF's title property
shows (PDF readers and library catalogs read that).

List committee members outside `\thesissetup`, one per line, in order:

- `\committeemember[Chair]{Name}` or `\committeemember[Co-Chair]{Name}`: at
  least one is required.
- `\committeemember{Name}` for everyone else. Text in the optional brackets
  prints after the name, following a comma.

There is no fixed committee size. Check the title page with long titles,
department names, or large committees.

Other class commands:

- `\frontchapter{Title}`: an unnumbered front-matter section listed in the
  contents.
- `\thesisfrontmatter`: copyright page, contents, and lists.
- `\thesismainmatter`: switches to Arabic page 1.
- `\chapterattribution{...}`: an unnumbered note at the foot of the page; place
  it right after `\chapter` (see
  [writing basics](writing.md#chapters-based-on-published-papers)).
- `\thesisreferences`: the reference list, single-spaced, titled REFERENCES,
  and listed in the contents (needs biblatex, which `preamble.tex` loads).
- `\referencesname`: the reference list's title; change it with
  `\renewcommand{\referencesname}{...}` in `preamble.tex`.
- `\appendicesname`: the APPENDICES line the contents shows before the first
  appendix.

`degree-name` does not make the toolkit suitable for undergraduate theses or
other document types; those need their own requirements check. For a proposal
or qualifying exam, see [write a proposal or qualifying exam](#write-a-proposal-or-qualifying-exam).

## Build commands

Optional: no step in this guide needs a terminal (a text window for
commands). Your editor or Overleaf compiles when you save or click
**Recompile**. These commands are for anyone who prefers typing them, or who
wants the build helper's setup check and pre-submission hints.

Overleaf, VS Code (with the recipe in `.vscode/`), and the build helper use
`latexmk`, a tool that runs the engine and the bibliography step (Biber) as
often as needed. For TeXShop, TeXworks, or TeXstudio, see
[other editors](get-started.md#other-editors).

Run these from the folder containing `main.tex`. The plainest is

```sh
latexmk -norc -pdf main.tex
```

which puts `main.pdf` next to `main.tex`. Or use the build helper below. An AI assistant can explain or adapt any command for
your system: give it your operating system and the command or its error
output, then check the result
([more on AI help](#use-ai-for-technical-help)).

The helper needs Python 3.9 or newer (no extra packages) and TeX Live 2022 or
newer with `latexmk`, your engine, and Biber. On Windows, prefer TeX Live,
which includes the Perl that `latexmk` needs; with MiKTeX, install Perl too.

The commands below use `python3`, which works on macOS and Linux. On Windows,
type `py` instead of `python3`: `py scripts/build.py`. If `python3` is not
recognized or opens the Microsoft Store, close the Store and use `py`. On
macOS, the first `python3` may offer to install developer tools; accept, or
use `latexmk` instead.

Check the installed tools and see the next steps:

```sh
python3 scripts/build.py --doctor
```

Compile with pdfLaTeX; the PDF goes in `build/main.pdf`:

```sh
python3 scripts/build.py
```

Recompile everything from scratch:

```sh
python3 scripts/build.py --fresh
```

After a successful build, the helper prints non-fatal **pre-submission
hints**, such as `.bib` entries with a `url` but no `urldate`, `\caption[...]`
short captions, a missing seal, and figures or tables too large for a page.

The helper ignores personal `latexmkrc` files, disables shell escape, and
creates the output subfolders (`build/chapters/`, …) a first pass needs. If you
type `latexmk -outdir=...` yourself, create those subfolders first, or let
`latexmk` retry after "I can't write on file".

### Choose a compile engine

pdfLaTeX uses New TX fonts; LuaLaTeX and XeLaTeX use TeX Gyre Termes via
`fontspec`/`unicode-math`. Switch for characters pdfLaTeX can't handle, then
check glyphs and pagination. Other writing systems are untested.

- **Overleaf:** **Settings** (the gear icon), then under **Compiler**, pick
  LuaLaTeX or XeLaTeX.
- **VS Code:** open the Command Palette (Ctrl+Shift+P, or Cmd+Shift+P on
  macOS), run **LaTeX Workshop: Build with recipe**, and pick
  **RPI Thesis Toolkit: LuaLaTeX + Biber** or **XeLaTeX + Biber**. Pick it
  again after you reopen VS Code.

Optional, with the build helper, from the folder containing `main.tex` (on
Windows, `py scripts/build.py --engine lualatex`):

```sh
python3 scripts/build.py --engine lualatex
```

For XeLaTeX, replace `lualatex` with `xelatex`.

### Compile selected chapters

After one full compile, uncomment the `\includeonly` line in `preamble.tex`.
Inside its braces, list the chapter files you want, without `.tex`; the
sample line selects `chapters/02-research`. Compile `main.tex` as usual.
Comment out `\includeonly` and compile the whole thesis before sharing or
submitting.

## Recipes for common extras

Each recipe was compiled with pdfLaTeX, LuaLaTeX, and XeLaTeX in a copy of the
sample. To use one, uncomment its lines under "Optional extras" in
`preamble.tex`, add the snippet, compile, and check the pages it changes. OGE
has not reviewed these recipes; where the OGE *Dissertation and Thesis Manual*
says nothing, the [requirements map](project/requirements.md#needs-oge-confirmation)
lists the point under "Needs OGE confirmation".

Pick a task: [parts (a), (b)](#show-a-figure-in-parts-a-b) ·
[theorems and proofs](#add-theorems-and-proofs) ·
[an algorithm](#add-an-algorithm) ·
[code in an appendix](#add-code-to-an-appendix) ·
[a list of symbols](#add-a-list-of-symbols-or-abbreviations)

### Show a figure in parts (a), (b)

For one figure with several panels. Uncomment the `subcaption` line in
`preamble.tex` and use your own image names. The manual asks for only the
letter under each part, all explanation in the main caption, and the same
letter style in every caption (§2.5). Put this in your chapter file:

```latex
\begin{figure}[htbp]
  \centering
  \begin{subfigure}{0.45\linewidth}
    \includegraphics[width=\linewidth]{figures/front.png}
    \caption{}\label{fig:sample-front}
  \end{subfigure}\hfill
  \begin{subfigure}{0.45\linewidth}
    \includegraphics[width=\linewidth]{figures/side.png}
    \caption{}\label{fig:sample-side}
  \end{subfigure}
  \caption{Two views of the sample: (a) from the front; (b) from the side.}
  \label{fig:sample}
\end{figure}
```

Each empty `\caption{}` prints only its letter, and `\ref{fig:sample-side}`
prints a number such as "2.1b". Only the main caption appears in the list of
figures.

### Add theorems and proofs

*Caveat:* the manual does not specify theorem formatting; see the
[requirements map](project/requirements.md#needs-oge-confirmation).

Uncomment the three lines under "Theorems and proofs" in `preamble.tex`.
Theorems and lemmas then share one numbering by chapter (Theorem 2.1,
Lemma 2.2). Displayed equations inside a theorem, lemma, proof, or algorithm
may be unnumbered (§2.7); elsewhere, keep using `equation`. Put this in your chapter file:

```latex
\begin{theorem}\label{thm:sum}
For every integer $n \ge 1$,
\[
  \sum_{k=1}^{n} k = \frac{n(n+1)}{2}.
\]
\end{theorem}
\begin{proof}
Use induction on $n$. \ldots
\end{proof}
```

### Add an algorithm

*Caveat:* the manual does not mention algorithm format; see the
[requirements map](project/requirements.md#needs-oge-confirmation).

Uncomment the four lines under "Algorithms" in `preamble.tex`. They number
algorithms by chapter, format their captions like figure captions (bold, with
a colon), and single-space them. Algorithms have their own numbering and do
not appear in the lists of tables or figures.

Put this in your chapter file:

```latex
\begin{algorithm}[htbp]
  \caption{Euclid's algorithm for the greatest common divisor.}
  \label{alg:euclid}
  \begin{algorithmic}[1]
    \Function{Gcd}{$a, b$}
      \While{$b \neq 0$}
        \State $(a, b) \gets (b, a \bmod b)$
      \EndWhile
      \State \Return $a$
    \EndFunction
  \end{algorithmic}
\end{algorithm}
```

### Add code to an appendix

*Caveat:* the manual does not mention code listings and the typewriter font
is unconfirmed; see the
[requirements map](project/requirements.md#needs-oge-confirmation).

Uncomment the four lines under "Code listings" in `preamble.tex`, then put
the snippet in an appendix file, such as `appendices/additional-material.tex`.
Code is single spaced, in a typewriter font, with the caption above and long
lines wrapped inside the margins. Keep code black: do not add colored syntax
styles (§2.1).

```latex
\begin{lstlisting}[language=Python,
    caption={A Python function that computes the mean of a list of numbers.},
    label={lst:mean}]
def mean(values):
    return sum(values) / len(values)
\end{lstlisting}
```

For a whole file, save it in a `code/` folder and use
`\lstinputlisting[language=Python,caption={...}]{code/analysis.py}`. The
checklist asks for one font throughout. If OGE asks you to avoid the
typewriter font, change `\ttfamily` to `\rmfamily` in `preamble.tex` and add
`columns=fullflexible,keepspaces=true` to the second `\lstset` line.

### Add a list of symbols or abbreviations

The manual calls this optional section a nomenclature (§1.6). It goes after the
list of figures and before any preface or acknowledgment, appears in the
contents, and is formatted like the lists of tables and figures. Another title,
such as LIST OF ABBREVIATIONS, is a point to confirm with OGE.

1. Uncomment the `longtable` line in `preamble.tex`.
2. Create `frontmatter/nomenclature.tex` with the snippet below, one row per
   entry in the order you choose. `\\[10pt]` matches the spacing in the lists
   of tables and figures; the last row has none.
3. In `main.tex`, add `\input{frontmatter/nomenclature}` below the comment
   about optional sections, before the acknowledgments.

```latex
\frontchapter{NOMENCLATURE}
\begin{longtable}{@{}p{1in}p{5.3in}@{}}
$c$   & Speed of light in vacuum \\[10pt]
$k_B$ & Boltzmann constant \\[10pt]
FEM   & Finite element method \\
\end{longtable}
```

Packages that sort entries for you, such as `nomencl` or `glossaries`, need an
extra program run that the build helper does not do.

## Use another case for chapter titles

The starter writes chapter, appendix, and built-in titles (CONTENTS,
REFERENCES) in capitals. To use another consistent case (OGE manual §2.3),
redefine the built-in names in `preamble.tex`
(`\renewcommand{\contentsname}{Contents}`, likewise `\listtablename`,
`\listfigurename`, `\appendicesname`, and `\referencesname`), then match
every chapter, appendix, and front-matter title.

## Not yet covered

Publication-based theses need a dedicated, tested example and are on the
[roadmap](project/maintenance.md#roadmap-and-not-yet-covered). Until then,
try the usual LaTeX packages in `preamble.tex` and check the PDF against the
manual. Want to help add one? See [how to contribute](../CONTRIBUTING.md).

The PDF is not validated as tagged or PDF/UA accessible. Use descriptive
captions, meaningful headings, and legible figures.
