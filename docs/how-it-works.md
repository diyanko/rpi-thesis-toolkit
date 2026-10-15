# How it works

For anyone who wants to understand the RPI Thesis Toolkit, whatever your
LaTeX experience: how the files fit together, what compiling does, and the
workflow this guide suggests. You don't *need* this page to write, but when something
looks odd, knowing what happens behind the scenes turns a mystery into a
two-minute fix.

## The big idea

**Your thesis is assembled from parts, and the formatting is shared.** Each
chapter is its own file, your sources live in `references.bib`, and your
images in `figures/`. One set of formatting rules, `rpi-thesis.cls`, lays out
headings, numbering, captions, the contents, and the reference list the same
way every time you compile. You still write, revise, and check the pages;
what you stop doing is applying the same formatting by hand in every chapter.

Still drafting somewhere else? That works: bring each chapter in when it is
ready. [The suggested workflow](#the-suggested-workflow-and-why), near the end
of this page, explains how the parts fit together and why.

## Your words and your formatting are separate

`rpi-thesis.cls` is the **formatting engine**: margins, spacing, page numbers,
headings, captions, and the title page. Your files — `metadata.tex`, your
chapters, `references.bib` — hold the **content and settings**, and never say
how a page should look.

![Swapping the class file. On the left, your files (metadata.tex, frontmatter, chapters, appendices, figures, references.bib, preamble.tex) stay exactly as they are. In the middle, an old rpi-thesis.cls is replaced with a new one. On the right, recompiling produces a PDF with the same words in the updated formatting.](diagrams/class-swap.svg)

*In words:* your files + `rpi-thesis.cls` → your PDF. Replace the class file,
recompile, and the same words come out with the updated formatting.

So when OGE changes a rule, or the toolkit fixes something, you replace
**one file** and recompile; your chapters are untouched
([update the formatting safely](workflows.md#update-the-formatting-safely)). It is
also why you normally leave the class file alone: edits there would be lost in
the next update.

If you know Word, the difference is where formatting lives: Word keeps it
with your text, in each paragraph's style, so you see the final look as you
type. Here it lives in one separate file.

What the class takes care of on every page:

![Two thesis pages. Front matter (ABSTRACT): heading at the top margin, centered, bold; double-spaced text; 1 inch margins on all sides; roman page number (vi) bottom center, 0.75 inch from the edge. Body page: arabic page number top right, 0.75 inch from the edge; bold table caption above the table and bold figure caption below the figure; single-spaced footnotes. Chapter-opening pages put the number at the bottom center. Margins, page numbers, spacing, and caption style are set once in rpi-thesis.cls.](diagrams/page-anatomy.svg)

*In words:* 1-inch margins, page numbers in the right place (roman, then
arabic), double spacing, bold captions, and single-spaced footnotes all come
from `rpi-thesis.cls`. You still type your headings and decide where each
caption goes.

## What each file does

![File map of the project. main.tex is the starting point; it loads the class, then preamble.tex (packages, citation style, and the link to references.bib), metadata.tex (your name, degree, committee), then the front matter, the chapters, the reference list, and the appendices. rpi-thesis.cls supplies the formatting rules. Images live in figures/.](diagrams/file-map.svg)

| File or folder | What it is | Do you edit it? |
| --- | --- | --- |
| `main.tex` | The file you compile; lists which pieces go in, in order | To add or remove chapters or optional sections |
| `metadata.tex` | Your title, name, degree, department, date, and committee | Yes, first |
| `frontmatter/` | Abstract and acknowledgments | Yes |
| `chapters/` | One file per chapter | Yes — this is where you write |
| `appendices/` | Supplementary material, after the references | If you need it |
| `figures/` | Your images | Add files here |
| `references.bib` | Your list of sources, one entry each: exported from Zotero, or pasted by hand | Through Zotero, or by hand |
| `preamble.tex` | Extra packages (add-ons for LaTeX) and the citation style | Only to change style or add a package |
| `rpi-thesis.cls` | The formatting rules: margins, spacing, page numbers, headings, title page | Normally never |
| `assets/` | Where you put the RPI seal you download for the title page | Once, to [add the seal](get-started.md#add-the-rpi-seal-one-minute) |
| `build/` | Output from the build helper or VS Code | No — it is regenerated |

## What "compiling" does

**Compiling** turns your plain-text `.tex` files into a PDF. A full build runs
several programs in a row, usually pdfLaTeX → Biber → pdfLaTeX → pdfLaTeX,
repeated as needed:

![Build pipeline. Step 1: pdfLaTeX reads main.tex and writes notes about labels, headings, and the citations it needs. Step 2: Biber reads that citation list and references.bib and writes a formatted reference list. Step 3: pdfLaTeX runs again and places the references. Step 4: pdfLaTeX runs once more so page numbers in the contents and cross-references settle. One Compile runs these steps as often as needed. The result is main.pdf.](diagrams/build-pipeline.svg)

1. **pdfLaTeX** (first pass) lays out the pages and writes notes to itself:
   which labels and headings exist (`.aux`, `.toc`, `.lof`, `.lot`) and which
   citations you used (`.bcf`).
2. **Biber** reads that citation list and `references.bib`, and writes the
   formatted reference list (`.bbl`).
3. **pdfLaTeX** (second pass) reads the `.bbl` and puts in the references.
4. **pdfLaTeX** (third pass) settles page numbers in the contents and
   cross-references, which may have shifted when the references appeared.

Overleaf, VS Code, and the build helper run every step for you, repeating
passes until the output stops changing (via a tool called `latexmk`); in
TeXShop or TeXstudio you may run them yourself. After a
simple wording change, one pdfLaTeX pass is usually enough.

The extra files (`.aux`, `.bcf`, `.bbl`, `.toc`, …) are scratch notes you never
edit. The `.log` file is worth reading: it holds the full error messages.

### What the PDF looks like after each step

If you run the four steps one at a time, the sample thesis changes like this.

<!-- Each "preview" comment below becomes a picture on the website, made by
scripts/previews.py. GitHub hides them. If the sample thesis changes, check
that their alt text still matches the pictures. -->

**After step 1, pdfLaTeX.** Every page is laid out, but the citation shows its
key in bold, like [**lamport1994**], chapter numbers in cross-references show
as **??**, and the contents page is empty. So far pdfLaTeX has only written
its notes.

<!-- preview compile-pass-1-chapter: Chapter 1 after step 1. The sentence reads "a real citation example [lamport1994]" with the key in bold, then "Chapter ?? contains small examples you can adapt, and Chapter ?? closes the document." -->

<!-- preview compile-pass-1-contents: The contents page after step 1: the heading CONTENTS with nothing under it. -->

**After step 2, Biber.** Nothing in the PDF changes. Biber only writes the
formatted reference list (`main.bbl`) for the next pass.

**After step 3, pdfLaTeX.** The citation becomes a number, [1], the **??**
become chapter numbers, and the contents fill in. The References line may
still be missing, and the pages after it may show the wrong number, because
the reference list only arrived in this pass.

<!-- preview compile-pass-2-chapter: Chapter 1 after step 3: "a real citation example [1]", then "Chapter 2 contains small examples you can adapt, and Chapter 3 closes the document." -->

<!-- preview compile-pass-2-contents: The end of the contents after step 3: 3. Conclusion, page 4; 3.1 Future work, page 4; Appendices, page 5; A. Additional material, page 5. There is no References line. -->

**After step 4, pdfLaTeX.** The References line appears and the appendix
moves to its final page number. Nothing is left to settle.

<!-- preview compile-pass-3-contents: The end of the contents after step 4: 3. Conclusion, page 4; 3.1 Future work, page 4; References, page 5; Appendices, page 6; A. Additional material, page 6. -->

If a bold key or **??** is still there after all four steps, see
[bold citation keys and question marks](#bold-citation-keys-and-question-marks).

## Bold citation keys and question marks

These are LaTeX saying "I haven't finished filling this in yet".

| You see | It means | Fix |
| --- | --- | --- |
| A citation key in **bold**, like **lamport1994** | That citation is not in the formatted reference list yet | Run Biber, then compile twice. If it stays bold, check the key's spelling in both `\cite{}` and `references.bib` |
| **??** where a chapter, figure, or equation number should be | The `\ref{}` label is not known yet | Compile again. If it stays, check the `\label{}` and `\ref{}` spelling |
| An empty or outdated contents page | The contents are written on one pass and read on the next | Compile again |

## Where the PDF ends up

| How you compile | Your PDF |
| --- | --- |
| Overleaf | The preview pane; use Overleaf's download button for a copy |
| TeXShop or TeXstudio | `main.pdf`, next to `main.tex` |
| VS Code (with the included recipe) | `build/main.pdf` |
| Optional build helper (`python3 scripts/build.py`, typed in a terminal) | `build/main.pdf` |
| `latexmk` typed in a terminal | `main.pdf`, next to `main.tex` |

Switched methods? Open the PDF from the method you just used, not an old copy.

## Your computer or Overleaf?

![Your computer compared with Overleaf. Both start from the same project files and run the same compile steps (pdfLaTeX, Biber, then pdfLaTeX twice, repeated as needed), so they produce matching PDFs when both use a current TeX setup. On your computer the files live in a folder you control, LaTeX is installed locally, and you work offline in an editor. On Overleaf the files and the LaTeX installation live on Overleaf's servers and you work in a browser.](diagrams/overleaf-vs-local.svg)

Same files, same programs: mostly, only *where* things live differs. The PDFs
match when both use the same TeX version (Overleaf lets you choose one in its
settings). To move or use both, see
[workflows](workflows.md#use-your-computer-and-overleaf).

## The suggested workflow, and why

A thesis is more than a document you format at the end. You draft, discuss
with your advisor, collect sources, make figures, revise chapters, and
finally assemble everything into one PDF. This section describes one way to
connect those parts. It is a suggestion, not a rule: you and your advisor
decide how you work.

![Research-writing workflow. Drafting and advisor review, in a drafting app or directly in the thesis files, feed three kinds of thesis material: chapter files, figures with the files they were made from, and references collected in a citation manager and exported to references.bib. These come together when you compile, into one thesis PDF formatted by rpi-thesis.cls. Arrows loop back from the thesis to drafting and review for the next round of revision.](diagrams/research-workflow.svg)

*In words:* draft and discuss → chapter files, figures, and references →
compile into one thesis → review, and loop back to revise. Any part can go
round again.

### What is required, and what is only suggested

- **What OGE requires:** the formatting and submission rules in the Office of
  Graduate Education (OGE) manual and your degree checklist, on the
  [OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation).
  They win over anything in this guide. OGE's own guidance recommends its
  Word template unless you are proficient in LaTeX
  ([submitting](submission.md)).
- **How this toolkit formats your thesis:** `rpi-thesis.cls` applies the
  toolkit's reading of those rules, starting from RPI's official LaTeX
  template, which is on RPI ITS's
  [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation)
  together with the seal. The toolkit is unofficial, so you still check the
  PDF ([what OGE commonly flags](submission.md#what-oge-commonly-flags)).
- **What this guide suggests:** the workflow below, the drafting apps, Zotero, and the
  editors this guide walks through. They are conveniences, not OGE
  requirements; swap any of them for what works for you.
- **Optional helpers:** independent websites and AI tools for fiddly tasks
  ([helpers](writing.md#helpers-for-common-tasks)). Everything also works
  without them.

### The workflow, step by step

The steps overlap and repeat: a chapter can go back to drafting after
committee feedback, and a figure can be remade when new results arrive.

1. **Write and talk about your research early.** Your argument and results
   benefit from your advisor's feedback long before the layout matters, and
   problems found early are cheaper to fix. *Another option may suit you if*
   you already have a stable draft or published papers: set up and
   [bring them in](bring-your-draft.md) now.
2. **Draft where you and your advisor can work comfortably.** Your effort
   goes into content, and review fits how your advisor already works
   ([drafting tools](#draft-where-you-and-your-advisor-can-work-comfortably)).
   *Another option may suit you if* you are at ease in LaTeX: drafting
   directly in the chapter files skips the move later.
3. **Keep references and figure sources organized as you go.** Save real
   source records in a citation manager while you read, and keep each
   figure's data, script, or editable drawing beside it in `figures/`. You
   can then cite by a stable key and remake a figure when the data changes.
   *Another option may suit you if* your thesis has only a few sources:
   [pasting entries by hand](citations.md#if-you-cant-use-zotero-paste-an-entry-by-hand)
   is fine.
4. **Move stable material into the thesis gradually.** Bring in one section
   or chapter at a time, as it settles. Try one small section early, ideally
   with a figure and a few citations, so you discover conversion problems
   long before a deadline. *Another option may suit you if* your advisor
   prefers to read the compiled PDF from the start: work in the chapter files
   from day one.
5. **Let the shared formatting do the repeated work.** Numbering,
   cross-references, captions, the contents, and the reference list come from
   one place instead of being redone in every chapter
   ([why this works](#your-words-and-your-formatting-are-separate)). Moving a
   draft in still takes some work: headings need marking up, and tables,
   equations, and citations are usually rebuilt. *Another option may suit you
   if* your thesis is short, with few figures, equations, or references, and
   you prefer Word
   ([when Word might make sense](why-latex.md#when-word-might-still-make-sense)).
6. **Check the assembled document throughout.** Compile and look through the
   whole PDF every so often, not only at the end: wide tables, missing
   citations, and odd page breaks are easier to fix one at a time. Before you
   submit, use the [final PDF checklist](submission.md#final-pdf-checklist).
   *Another option may suit you if* you are still drafting elsewhere: a look
   after each chapter you move in may be enough until then.

### Draft where you and your advisor can work comfortably

There is no single right drafting tool. Use what lets you and your advisor
read, comment, and revise without friction. You don't need a new app,
plugins, or a note-taking system to start; if what you use now works, keep
going.

If you are choosing, this guide suggests a tool that works with Markdown. Markdown is
plain text with a few symbols for structure, such as `#` before a heading and
`*stars*` around emphasis. You never need to learn it to use this toolkit,
but it helps with drafting:

- your draft is a readable text file that opens in any editor, now and years
  from now;
- headings, emphasis, lists, and links take a symbol or two;
- you can change editors without converting anything;
- free tools such as Pandoc can convert it to LaTeX, Word, or slides, so the
  same text can be reused;
- there is no page layout to adjust, so attention stays on the content.

Four apps, each suited to a different situation:

- **[Obsidian](https://obsidian.md/):** Markdown files on your own computer,
  for research notes and drafts. You can share a vault (a folder of notes)
  with others, but that is not simultaneous editing of the same file
  ([Obsidian: collaborate on a shared vault](https://help.obsidian.md/sync/collaborate)).
- **[HackMD](https://hackmd.io/):** collaborative Markdown in your browser.
- **[Google Docs](https://workspace.google.com/products/docs/):** live
  co-writing and comments, familiar to many advisors.
- **[Notion](https://www.notion.com/):** if you already use it. It is a
  block-based workspace, not a folder of ordinary Markdown files, but it can
  [export your pages as Markdown](https://www.notion.com/help/export-your-content).

Markdown apps don't all support the same features, and app-specific links,
embeds, databases, citation features, and math syntax may need cleanup when
you export.

**Word** works too, for an existing draft or when your advisor prefers to
review in Word. See [bring your draft](bring-your-draft.md#from-word-or-google-docs)
to move a chapter in, and
[an advisor wants Word](workflows.md#an-advisor-wants-word-with-track-changes)
for review copies later on.

### Reuse your material elsewhere

![One source, many destinations. Your content files (chapters, figures, and references.bib) sit in the middle. Arrows lead outward to: the thesis PDF, through rpi-thesis.cls; a journal or conference paper, through the venue's class such as IEEEtran or acmart; slides, through Beamer; a Word copy for reviewers, through Pandoc; and a web page. A caption reads "a world of possibilities, not a to-do list".](diagrams/one-source-many-outputs.svg)

*In words:* your chapters and sources sit in the middle; the thesis PDF is the
one destination you need, and the others are options.

The same habits (sources in one library, figures with their source files,
chapters as separate files) help with later papers, presentations, reports,
and documentation. Reuse is a head start, not a copy: each output needs its
own template, some cleanup, and a check against its own requirements, and
this toolkit's formatting is only for RPI graduate theses.
[Workflows](workflows.md#turn-a-chapter-into-a-paper) has recipes for papers,
slides, and Word copies.

A citation typed as text, such as "(Lamport, 1994)", a field inside your
citation manager, and a citation key such as `lamport1994` are different
things. Only the key, matched to an entry in `references.bib`, lets LaTeX
build the citation and the reference list. So collect real records early and
keep their keys stable
([citations](citations.md#step-2-collect-and-cite-sources-with-zotero)).

<details><summary>Optional: a table of tools for each part of the work</summary>

Each link goes to the part of this guide that explains the tool. A tool can
help with more than one part.

| Part of the work | Tools, and where this guide covers them |
| --- | --- |
| Draft and organize ideas | [Obsidian, HackMD, Google Docs, Notion, or Word](#draft-where-you-and-your-advisor-can-work-comfortably); or the [chapter files](writing.md#chapters) themselves |
| Collaborate and review | [Google Docs or HackMD](#draft-where-you-and-your-advisor-can-work-comfortably) while drafting; [a shared Overleaf project](workflows.md#co-authors-and-lab-mates); [a commented PDF](workflows.md#an-advisor-reviews-a-pdf); [a Word review copy](workflows.md#an-advisor-wants-word-with-track-changes); [latexdiff](workflows.md#show-what-changed-between-drafts) |
| Collect references and cite sources | [Zotero and Better BibTeX](citations.md#step-2-collect-and-cite-sources-with-zotero); [entries pasted by hand](citations.md#if-you-cant-use-zotero-paste-an-entry-by-hand); [`\cite{key}`](writing.md#cite-a-source) |
| Create tables, equations, figures, and diagrams | [Tables Generator](writing.md#make-a-table-from-a-spreadsheet); [LaTeXEditor.app](writing.md#write-an-equation); [Detexify](writing.md#find-a-symbols-command); [draw.io](writing.md#draw-a-diagram); the [figure and table examples](writing.md#figures-and-tables) |
| Assemble and check the thesis | [VS Code with LaTeX Workshop](get-started.md#step-3a-your-computer-route); [Overleaf](get-started.md#step-3b-overleaf-route); the [build helper](advanced.md#build-commands); the [final PDF checklist](submission.md#final-pdf-checklist) |
| Reuse material elsewhere | [A venue's paper template](workflows.md#turn-a-chapter-into-a-paper); [slides and posters](workflows.md#make-slides); [a Word copy](workflows.md#an-advisor-wants-word-with-track-changes) |

</details>

## Want to learn more LaTeX?

[Overleaf Learn](https://www.overleaf.com/learn) has friendly tutorials on
almost every topic, whichever editor you use. [CTAN](https://ctan.org/) holds
every package and its manual, including [biblatex](https://ctan.org/pkg/biblatex).
