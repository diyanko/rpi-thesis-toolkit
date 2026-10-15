# Workflows: moving, reviewing, and collaborating

For anyone whose thesis or dissertation already compiles and who wants to
move it, share drafts, collaborate, back up, or update the formatting. No
project yet? Start with [get started](get-started.md). For how these fit into
the wider research-writing process, see
[the suggested workflow](how-it-works.md#the-suggested-workflow-and-why).

## Common situations

| If you… | Do this |
| --- | --- |
| [Use Overleaf and want the files on your computer](#overleaf-to-your-computer) | Download the source ZIP |
| [Use your computer and want Overleaf](#your-computer-to-overleaf) | Upload a ZIP |
| [Want to use both](#use-your-computer-and-overleaf) | Keep one source of truth |
| [Get comments on paper or in a PDF](#an-advisor-reviews-a-pdf) | They annotate; you edit the source |
| [Have an advisor who wants Word](#an-advisor-wants-word-with-track-changes) | Send a review copy; apply edits by hand |
| [Need to show what changed](#show-what-changed-between-drafts) | Make a changes PDF with latexdiff |
| [Drafted in Markdown, Google Docs, or Word](bring-your-draft.md) | Bring the text in, one chapter at a time |
| [Write with co-authors or lab-mates](#co-authors-and-lab-mates) | Share one project |
| [Want a chapter as a journal or conference paper](#turn-a-chapter-into-a-paper) | Move the text into the venue's template |
| [Need slides or a poster](#make-slides) | Reuse your figures in any slide or poster tool |
| [Want a backup routine](#back-up-your-work) | Three copies, two kinds of storage |
| [Got a newer version of the toolkit](#update-the-formatting-safely) | Replace `rpi-thesis.cls`, then compare |
| [Want AI help with a LaTeX problem](#use-ai-for-technical-help) | Share the first error; try one change at a time |

### Overleaf to your computer

1. In Overleaf, download the project **source** as a ZIP, not just the PDF
   ([Overleaf: downloading a project](https://docs.overleaf.com/managing-projects-and-files/downloading-a-project)).
2. Extract it into a normal folder, keeping the folders together.
3. No LaTeX on your computer yet? Follow
   [the your-computer route](get-started.md#step-3a-your-computer-route).
4. Compile `main.tex` and compare the PDF with Overleaf's.

### Your computer to Overleaf

1. ZIP your whole project folder, including your downloaded seal in
   `assets/` (you can leave out `build/`).
2. Upload it as a new Overleaf project, then set the main document and
   compiler as in [the Overleaf route](get-started.md#step-3b-overleaf-route).
3. Recompile. Overleaf compiles with `latexmk`, so Biber runs automatically.

### Use your computer and Overleaf

The one rule: **only one copy is the source of truth at a time.** Edit there;
treat the other as a backup.

![Your thesis folder and an Overleaf project. Download source (ZIP) goes from Overleaf to your computer; Upload project (ZIP) goes back. One source of truth at a time: edit in one place, then move the whole project. On some Overleaf plans, Git or GitHub sync can keep them in step.](diagrams/overleaf-sync.svg)

*In words:* download the ZIP to move to your computer, upload a ZIP to move
to Overleaf, and edit in only one place at a time.

1. Before switching, save and compile where you are.
2. Move the whole project by ZIP ([to your computer](#overleaf-to-your-computer)
   or [to Overleaf](#your-computer-to-overleaf)).
3. Rename the old copy, e.g. `thesis-OLD-2027-02-10`, so you don't edit it by
   accident.

Overleaf's [Git integration and GitHub sync](https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization),
on some plans, can keep the copies in step without ZIPs.

### An advisor reviews a PDF

![Review loop. You compile the thesis and send a dated PDF to your advisor. Your advisor marks it up on paper or with a PDF reader's comment tools and sends it back. You make each change in your .tex files, recompile, and send the next dated PDF. The loop repeats until the draft is ready.](diagrams/review-loop.svg)

*In words:* send a PDF → your advisor marks it up → you edit the source →
recompile → repeat.

1. Send a PDF with the date in its name, e.g. `thesis-2027-02-10.pdf`, and keep a copy.
2. Your advisor comments on paper or with any PDF reader's comment tools.
3. Find each spot in your `.tex` files (search for a few words, or click in
   the PDF to jump there) and make the change.
4. Recompile and send the next dated PDF. After big revisions, add a
   [changes PDF](#show-what-changed-between-drafts).

### An advisor wants Word with track changes

A Word copy is for review only: it loses the title page, margins, numbering,
cross-references, and reference formatting.

1. Ask first whether a commented PDF would do; it shows the real layout.
2. If not, convert one chapter and check what was lost: on Overleaf, use the
   [Word export](https://docs.overleaf.com/managing-projects-and-files/importing-and-exporting-files);
   on your computer, use Pandoc (below).
3. Your advisor edits with track changes and comments.
4. Apply each accepted change to your `.tex` files by hand, then compile.

**Never convert the reviewed Word file back into LaTeX for your final
thesis.** Your `.tex` files stay the master copy.

<details>
<summary>For experienced users: make a Word copy with Pandoc</summary>

[Pandoc](https://pandoc.org/), a free conversion program, can turn a chapter
into `.docx`. It is optional and only needed for converting files; Overleaf
users don't need it (they can use the Word export above). Install it from the
[Pandoc installation page](https://pandoc.org/installing.html) (installers for
Windows and macOS, packages for Linux).

Pandoc does not run the thesis class and loses custom commands,
cross-references, and some equations and tables. In a terminal, from the
project folder, after creating `build/`:

```sh
pandoc chapters/01-introduction.tex --from=latex --to=docx --citeproc --bibliography=references.bib --resource-path=. --output=build/chapter-review.docx
```

This is untested beyond a simple chapter. Choose a CSL style if citation
formatting matters for the review.

</details>

### Show what changed between drafts

`latexdiff`, included in full TeX Live, makes a PDF with additions and
deletions marked, handy when your committee rereads a revised draft.

1. Keep the version your committee last saw (a dated backup ZIP). On Overleaf,
   [History](https://docs.overleaf.com/writing-and-editing/history-and-versioning)
   can download an earlier version as a ZIP.
2. Run latexdiff on your computer (terminal commands below, for experienced
   users), or follow
   [Overleaf's latexdiff article](https://www.overleaf.com/learn/latex/Articles/How_to_use_latexdiff_on_Overleaf).
3. Check the changes PDF before sending it: changed equations, tables, and
   figures can come out messy.

<details>
<summary>For experienced users: make a changes PDF with latexdiff</summary>

Extract the old version into a folder named `old` beside your project folder.
Then, from your project folder:

```sh
latexdiff --flatten ../old/main.tex main.tex > build/changes.tex
latexmk -norc -pdf -no-shell-escape -outdir=build build/changes.tex
```

`--flatten` pulls the included chapter files into one document; comment out
any `\includeonly` line in both versions first. The result is
`build/changes.pdf`. The Overleaf method in the linked article has not been
tested with this starter.

</details>

### Co-authors and lab-mates

1. Share **one** project: invite them to your Overleaf project (check
   [Overleaf's plans](https://docs.overleaf.com/getting-started/free-and-premium-plans)
   for collaborator limits) or use a
   [private GitHub repository](#keep-a-thesis-on-github-private).
2. Agree who edits which chapter, so two people don't rewrite the same paragraph.
3. Prefer comments for suggestions; it is your thesis. Word-using colleagues
   can still [share sources](citations.md#if-co-authors-use-word).

### Turn a chapter into a paper

1. Start from the venue's own template (for example `IEEEtran` or `acmart`,
   from Overleaf's gallery or the publisher's author page).
2. Copy in the chapter's text, equations, figures, and the `.bib` entries it
   cites. Drop thesis-only commands such as `\chapterattribution`.
3. Follow the venue's author instructions for style and length, and check its
   policy on material from a thesis.

**If the venue's template uses BibTeX.** Many venue templates use classic
BibTeX (`\bibliographystyle{...}` and `\bibliography{...}`) instead of
biblatex. Your `\cite` keys carry over, but
this starter's `.bib` entries use biblatex fields such as `date`,
`journaltitle`, and `urldate`, which BibTeX styles ignore, so years and
web-source details can silently disappear. Export a BibTeX-format file for the
paper instead: in Zotero, choose the **Better BibTeX** format (not Better
BibLaTeX), or Zotero's plain **BibTeX** export, keeping the same citation
keys. Replace `\printbibliography` and biblatex-only commands such as
`\textcite` or `\autocite`, then check the reference list.

### Make slides

Reuse the images in `figures/` in any slide or poster tool. To stay in
LaTeX, start from a **Beamer** template for slides, or a poster template
(Overleaf's gallery has many of both), and copy in your figures.

For experienced users writing slides in Markdown: Pandoc, an optional free
conversion program, turns them into a PowerPoint file, with a new slide at
each heading. Install it from the
[Pandoc installation page](https://pandoc.org/installing.html), then run
`pandoc talk.md --output=talk.pptx` in a terminal. Add `--reference-doc` with
a template `.pptx` to use your own design.

## Back up your work

Keep three copies on two kinds of storage, one of them off-site (the 3-2-1
rule): for example, your working folder, a cloud-synced copy, and an
automatic backup of your computer (Time Machine, File History, or an external
drive).

![The 3-2-1 rule: your thesis folder and an automatic backup (Time Machine, File History, or an external drive) are on your computer; a cloud-synced copy is off-site. Notes: sync is not backup, because deletions sync too, so use version history; on Overleaf, download the source ZIP regularly; for Zotero, use Zotero sync and keep its data folder out of cloud folders.](diagrams/backup-321.svg)

*In words:* three copies, two kinds of storage, one off-site.

- **Sync is not backup.** A deleted or damaged file syncs everywhere; learn
  where your service keeps version history.
- **Keep files on your computer.** Mark the thesis folder "Always keep on
  this device"; OneDrive and iCloud can leave files online only, and LaTeX
  then cannot find them.
- **Edit on one computer at a time,** and let sync finish before you switch,
  or you get conflict copies such as `main (1).tex`.
- **Overleaf:** download the **source ZIP** regularly and before big changes.
- **Zotero:** never put its data folder in a cloud-sync folder
  ([where Zotero keeps your library](citations.md#where-zotero-keeps-your-library)).
- **Keep what you send:** each dated PDF, and the scripts and data behind
  each figure. At submission, archive the final source, the submitted PDF,
  and your permission documents in two places.
- **Sensitive data** (such as interviews or surveys approved by an IRB, the
  board that reviews research with people; export-controlled data; or data
  under a data-use agreement) follows RPI's rules and your agreement, not
  personal cloud storage.

Now and then, extract a backup elsewhere and compile it to prove it works.
Git is a backup only once pushed somewhere else
([Git and GitHub](#git-and-github-are-different-things)).

LaTeX rewrites helper files such as `.aux` and `.log` on every compile. If
sync gets noisy, keep `build/` out of the synced folder. If a tool reports a
missing file and the folder path has spaces or unusual characters (such as a
long OneDrive folder name), try a simple path like `~/thesis` first.

## Git and GitHub are different things

- **Git** takes snapshots (*commits*) of your folder on your own computer, so
  you can compare versions and recover an old paragraph. It works offline.
- **GitHub** is a website that stores Git projects online. Committing does not
  upload anything; uploading is a *push*.

You need neither: to get the starter,
[download the ZIP](get-started.md#step-2-get-the-files). Git history on the
same disk is not a [backup](#back-up-your-work). See
[GitHub's introduction to Git](https://docs.github.com/en/get-started/using-git/about-git).

### Keep a thesis on GitHub private

This is optional. If you want your thesis on GitHub, keep it in a
**private** repository (a project space that only you and people you invite
can see): unpublished research doesn't belong in public.

> [!WARNING]
> **Don't fork the toolkit for your thesis.** A fork of a public repository
> is public, and GitHub doesn't let you make it private
> ([GitHub: visibility of forks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-permissions-and-visibility-of-forks)).

Use one of these private routes instead:

- **A new private repository:** create a repository and choose **Private**
  ([GitHub: creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)).
  Then add the files from your extracted starter with **Add file → Upload
  files** ([GitHub: adding a file](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)),
  or push your own Git copy (commands below).
- **Use this template:** if the toolkit's GitHub page shows a **Use this
  template** button, click it, select **Create a new repository**, and choose
  **Private** visibility
  ([GitHub: creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)).
  <!-- TODO(verify): checked 14 Oct 2026 against the GitHub docs linked here. On that date the toolkit repository was not marked as a template, so the button does not appear yet. Enable "Template repository" in its settings, or remove this route. -->

<details>
<summary>For experienced users: Git commands and remotes</summary>

In **your own writing copy**:

```sh
git init
git status    # review what will be added; no private data files
git add .
git commit -m "Start my thesis from the starter"
# after a writing change:
git diff
git add chapters/01-introduction.tex
git commit -m "Draft the introduction"
```

The `.gitignore` keeps generated files and PDFs next to `main.tex` out of
Git; PDF figures in `figures/` are kept.

If you **cloned** the toolkit's repository, it is your `origin` remote:
never push your thesis there. Check `git remote -v` and point `origin` at
your own private repository before pushing.

</details>

## Update the formatting safely

When OGE changes a rule or the toolkit fixes something, the fix lives in
`rpi-thesis.cls`, so your chapters never need replacing
([why this works](how-it-works.md#your-words-and-your-formatting-are-separate)).

1. **Find your version** in the `\ProvidesClass` line near the top of
   `rpi-thesis.cls`; your compile log (`main.log`) also prints it as
   `Document Class: rpi-thesis <date> <version>`.
2. **Read the [changelog](../CHANGELOG.md)** (the newest copy is in the
   latest release or on the project's GitHub page): every entry newer than
   your version starts with a **Changes your PDF?** line. If they all say
   *no*, you can skip the update.
3. **Back up** your whole project ([backups](#back-up-your-work)).
4. **Replace `rpi-thesis.cls`** — and only other files the change log names.
   Never overwrite your chapters, `metadata.tex`, or `references.bib`.
5. **Recompile from scratch and compare** with your last PDF, especially the
   title page, contents, and page numbers.

Close to a deadline, update only if a change fixes something that affects you.
To hear about updates, use **Watch → Custom → Releases** on the toolkit's
GitHub page (needs a GitHub account), or check the changelog before you submit.

## Use AI for technical help

AI is a practical tool that makes LaTeX easier to pick up and takes over
repetitive steps. It is optional, one route alongside web search, official
documentation, and [community help](troubleshooting.md#ask-for-help). An
ordinary **AI chat** (a tool that explains problems and suggests changes) is
often enough: use a tool you already have access to. This toolkit needs no
subscription, AI account, or special setup.

An AI chat is useful for:

- explaining an error message;
- finding a missing brace or an incorrect command;
- formatting a table from data you supply;
- turning a table screenshot, a handwritten equation, or a sketch into
  editable code ([prompts and helper tools](writing.md#helpers-for-common-tasks));
- inserting or resizing an image, and fixing captions or references;
- converting an existing equation into LaTeX without changing its meaning;
- fixing bibliography syntax or citation keys from your existing source
  records;
- spotting formatting problems or edge cases.

A quick routine:

1. Share the first error and a small example of the lines around it.
2. Try one suggested change.
3. Compile and look at the result in the PDF.
4. If it doesn't help, undo the change.

Prompts you can copy: for an error, in
[ask an AI chat to explain it](troubleshooting.md#ask-an-ai-chat-to-explain-it);
for tables, equations, and sketches, in
[ask an AI assistant](writing.md#ask-an-ai-assistant).

Don't paste confidential material, such as unpublished data or participant
details.

An **AI assistant that can edit files** or run a compile can apply a fix for
you. Work on a backup, keep the task small, review every change, compile,
and inspect the affected pages of the PDF.
