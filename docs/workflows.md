# Workflows: moving, reviewing, and collaborating

For anyone whose thesis or dissertation already compiles. No project yet?
Start with [get started](get-started.md). For the bigger picture, see
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
- [Back up your work](#back-up-your-work), or [use a private GitHub repository](#use-a-private-github-repository)
- [Update to a newer toolkit version](#update-the-formatting-safely)
- [Get help with a technical task](#use-ai-for-technical-help) or [convert a file](#ask-for-a-file-conversion)

### Overleaf to your computer

1. In Overleaf, download the project **source** as a ZIP, not just the PDF
   ([Overleaf: downloading a project](https://docs.overleaf.com/managing-projects-and-files/downloading-a-project)).
2. Extract it into a normal folder, keeping the folders together.
3. No LaTeX on your computer yet? Follow
   [the your-computer route](get-started.md#step-3a-your-computer-route).
4. Compile `main.tex` and compare the PDF with Overleaf's.

The Overleaf starter's ZIP has no VS Code settings, so your editor may put the
PDF beside `main.tex` instead of in `build/`.

### Your computer to Overleaf

1. ZIP your whole project folder, including your downloaded seal in
   `assets/` (you can leave out `build/`).
2. Upload it as a new Overleaf project, then set the main document and
   compiler as in [the Overleaf route](get-started.md#step-3b-overleaf-route).
3. Recompile. Overleaf compiles with `latexmk`, so Biber runs automatically.

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

1. Create `build/compare.bib` containing the text of `../old/references.bib`
   followed by the text of `references.bib`. In a text editor, paste one under
   the other; on macOS or Linux,
   `cat ../old/references.bib references.bib > build/compare.bib`.
2. Open `build/changes.tex` and change the line
   `\addbibresource{references.bib}` to `\addbibresource{build/compare.bib}`.
   (This is the generated file, not your thesis.)

Then compile it:

```sh
latexmk -norc -pdf -no-shell-escape -outdir=build build/changes.tex
```

Biber warns about duplicate keys and skips the second copy; that is expected.

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
- Swap `\thesisreferences` for the venue's bibliography lines (often `\printbibliography` or `\bibliography{...}`).
- Replace biblatex-only commands such as `\textcite`, then check the
  reference list.

### Make slides

Reuse the images in `figures/` in any slide or poster tool. To stay in LaTeX,
start from a **Beamer** template or a poster template (Overleaf's gallery has
many) and copy in your figures. To turn Markdown slides into PowerPoint, see
[Pandoc](#an-advisor-wants-word-with-track-changes): `pandoc talk.md --output=talk.pptx`
starts a new slide at each heading.

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
documents in two places. Now and then, extract a backup and compile it to prove
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

Formatting fixes live in `rpi-thesis.cls`, so your chapters never need
replacing ([why](how-it-works.md#your-words-and-your-formatting-are-separate)).

1. **Find your version:** the `\ProvidesClass` line near the top of
   `rpi-thesis.cls`, for example `2026/10/14 v0.1.0`. Your PDF shows it too,
   under **Creator** in its document properties. The online website's footer
   shows the newest version; an offline copy's footer is frozen.
2. **Read the changelog.** The [changelog](../CHANGELOG.md) bundled with
   your download is that version's copy and does not update itself. Read the
   newest one online: [all releases](https://github.com/diyanko/rpi-thesis-toolkit/releases)
   and the [online changelog](https://github.com/diyanko/rpi-thesis-toolkit/blob/main/CHANGELOG.md). Each entry newer than your version starts with a
   **Changes your PDF?** line. If they all say *no*, skip the update.
3. **Back up** your whole project ([backups](#back-up-your-work)).
4. **Download the newer starter** ([get started](get-started.md#step-2-get-the-files))
   into a separate folder. Copy its `rpi-thesis.cls` over the old one, plus
   only other files the changelog names. Never overwrite your chapters,
   `metadata.tex`, or `references.bib`.
5. **Recompile from scratch and compare** with your last PDF, especially the
   title page, contents, and page numbers.

While the toolkit is in beta (versions 0.x), an update may rename or simplify
a setting; its changelog entry gives the exact edit to make.
Close to a deadline, update only if a change fixes something that affects you.
To hear about updates, use **Watch → Custom → Releases** on the toolkit's
GitHub page (needs an account), or check the changelog before you submit.

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
