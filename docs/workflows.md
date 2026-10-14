# Workflows: moving, reviewing, and collaborating

For anyone whose thesis or dissertation already compiles and who wants to
move it, share drafts, collaborate, back up, or update the formatting. No
project yet? Start with [get started](get-started.md).

## Common situations

| If you… | Do this |
| --- | --- |
| [Use Overleaf and want the files on your computer](#overleaf-to-your-computer) | Download the source ZIP |
| [Use your computer and want Overleaf](#your-computer-to-overleaf) | Upload a ZIP |
| [Want to use both](#use-your-computer-and-overleaf) | Keep one source of truth |
| [Get comments on paper or in a PDF](#an-advisor-reviews-a-pdf) | They annotate; you edit the source |
| [Have an advisor who wants Word](#an-advisor-wants-word-with-track-changes) | Send a review copy; apply edits by hand |
| [Need to show what changed](#show-what-changed-between-drafts) | Make a changes PDF with latexdiff |
| [Drafted in Word, Google Docs, or Markdown](bring-your-draft.md) | Bring the text in, one chapter at a time |
| [Write with co-authors or lab-mates](#co-authors-and-lab-mates) | Share one project |
| [Want a chapter as a journal or conference paper](#turn-a-chapter-into-a-paper) | Move the text into the venue's template |
| [Need slides](#make-slides) | Reuse your figures in any slide tool |
| [Want a backup routine](#back-up-your-work) | Three copies, two kinds of storage |
| [Got a newer version of the toolkit](#update-the-formatting-safely) | Replace `rpi-thesis.cls`, then compare |
| [Want to use an AI assistant](#optional-ai-help) | Small examples only; check everything |

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
<summary>For experienced users: a Word copy with Pandoc</summary>

[Pandoc](https://pandoc.org/) can turn a chapter into `.docx`. It does not run
the thesis class and loses custom commands, cross-references, and some
equations and tables. From the project folder, after creating `build/`:

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
2. Run latexdiff on your computer (below), or follow
   [Overleaf's latexdiff article](https://www.overleaf.com/learn/latex/Articles/How_to_use_latexdiff_on_Overleaf).
3. Check the changes PDF before sending it: changed equations, tables, and
   figures can come out messy.

<details>
<summary>For experienced users: latexdiff commands</summary>

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
   for collaborator limits) or use a **private** GitHub repository.
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

<details>
<summary>For experienced users: citations in venue templates</summary>

Many venue templates use classic BibTeX (`\bibliographystyle{...}` and
`\bibliography{...}`) instead of biblatex. Your `\cite` keys carry over, but
this starter's `.bib` entries use biblatex fields such as `date`,
`journaltitle`, and `urldate`, which BibTeX styles ignore, so years and
web-source details can silently disappear. Export a BibTeX-format file for the
paper instead: in Zotero, choose the **Better BibTeX** format (not Better
BibLaTeX), or Zotero's plain **BibTeX** export, keeping the same citation
keys. Replace `\printbibliography` and biblatex-only commands such as
`\textcite` or `\autocite`, then check the reference list.

</details>

### Make slides

Reuse the images in `figures/` in any slide tool. To stay in LaTeX, start
from a **Beamer** template (Overleaf's gallery has many) and copy in your
figures and equations.

<details>
<summary>For experienced users: PowerPoint from Markdown</summary>

Pandoc writes `.pptx` from Markdown, starting a new slide at each heading:
`pandoc talk.md --output=build/talk.pptx`. Add `--reference-doc` with a
template `.pptx` to use your own design.

</details>

## Back up your work

Keep three copies on two kinds of storage, one of them off-site (the 3-2-1
rule): for example, your working folder, a cloud-synced copy, and an
automatic backup of your computer (Time Machine, File History, or an external
drive).

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
- **Sensitive data** (IRB, export-controlled, or under a data-use agreement)
  follows RPI's rules and your agreement, not personal cloud storage.

Now and then, extract a backup elsewhere and compile it to prove it works.
Git is a backup only once pushed somewhere else
([Git and GitHub](#git-and-github-are-different-things)).

<details>
<summary>For experienced users: sync noise and file paths</summary>

LaTeX rewrites helper files such as `.aux` and `.log` on every compile. If
sync gets noisy, keep `build/` out of the synced folder. If a tool reports a
missing file and the folder path has spaces or unusual characters (such as a
long OneDrive folder name), try a simple path like `~/thesis` first.

</details>

## Git and GitHub are different things

- **Git** takes snapshots (*commits*) of your folder on your own computer, so
  you can compare versions and recover an old paragraph. It works offline.
- **GitHub** is a website that stores Git projects online. Committing does not
  upload anything; uploading is a *push*.

You need neither. Git history on the same disk is not a
[backup](#back-up-your-work). See
[GitHub's introduction to Git](https://docs.github.com/en/get-started/using-git/about-git).

> [!WARNING]
> If you put your thesis on GitHub (including with **Use this template** or a
> fork), make the repository **private**. Copies are public by default, and
> unpublished research doesn't belong there.

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

## Optional AI help

AI assistants are optional, but they can help explain an error, convert a
table, or find a command. Follow your advisor's, RPI's, and publishers'
current rules, and:

- **Share only small examples:** many services send what you paste to outside
  servers, so keep out unpublished drafts, data, and participant details.
- **Check everything:** apply one change at a time, compile, and verify quotes,
  numbers, and citations; AI can invent convincing references.
- **Keep the formatting intact:** never accept changed margins or class files
  just because an error went away.

<details>
<summary>For experienced users: assistants that edit files or run commands</summary>

Work on a copy or commit first. Give a narrow task and clear limits, for
example: "Fix only the first compilation error in this chapter. Preserve my
prose and citations. Show each changed line. Do not delete files, install
software, upload, or push." Review the diff and compile before accepting.
Check which folder and permissions the tool actually has.

</details>
