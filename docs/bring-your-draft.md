# Bring your existing draft

For anyone with a thesis or dissertation draft in Word, Google Docs,
Markdown, a LaTeX paper, or RPI's official LaTeX template: you do not have to
start over. First get the sample compiling ([get started](get-started.md))
and keep your original draft unchanged. Try moving **one small section**
first, so you meet any surprises early, then move one chapter at a time,
compiling after each.

## What goes where

![Where each part of a Word or Google Docs draft goes, matched by numbered pins. 1: title, your name, degree and committee go in metadata.tex. 2: abstract to frontmatter/abstract.tex. 3: acknowledgments to frontmatter/acknowledgments.tex. 4: each chapter goes in its own file in chapters/, such as 01-introduction.tex, listed in main.tex; its tables and equations are marked "rebuild in LaTeX". 5: figures go in figures/ as image files. 6: references go into Zotero, then references.bib, and each citation becomes \cite{key}. 7: appendices go in appendices/. Note: text pastes in; equations, tables and citations are rebuilt.](diagrams/draft-to-files.svg)

*In words:* title-page details go in `metadata.tex`; your writing in
`frontmatter/`, `chapters/`, and `appendices/`; images in `figures/`; sources
in `references.bib`. The title page, contents, lists, and page numbers are
built for you.

## From Word or Google Docs

From Google Docs, copy the text directly, or download a `.docx`
(**File → Download → Microsoft Word**) and follow the same steps.

1. **Copy the text** (paragraphs, headings, footnotes) into a chapter file
   ([add a chapter](writing.md#chapters)).
2. **Mark it up:** make each heading a `\chapter{...}`, `\section{...}`, or
   `\subsection{...}`; turn footnotes into `\footnote{...}` and italics into
   `\emph{...}`; put a backslash before special characters: `%` → `\%`,
   `&` → `\&`, `_` → `\_`, `$` → `\$`, `#` → `\#`.
3. **Rebuild what doesn't paste,** using the examples in
   [writing basics](writing.md) and `chapters/02-research.tex`: block
   quotations (`quote`), equations (`equation`), tables, figures (images
   saved in `figures/`), cross-references (`\label` and `\ref` instead of
   "see Figure 3"), and citations (`\cite{key}`).
4. **References:** if you used Zotero or another citation manager,
   [export your library](citations.md#step-2-collect-and-cite-sources-with-zotero).
   If you typed your list by hand, add each source to Zotero, or
   [paste entries](citations.md#if-you-cant-use-zotero-paste-an-entry-by-hand)
   into `references.bib`.

<details><summary>For experienced users: a rough first pass from Word with Pandoc</summary>

[Pandoc](https://pandoc.org/), a free conversion program, can turn a `.docx`
into LaTeX. It is optional and only needed for converting files; Overleaf
users don't need it. Install it from the
[Pandoc installation page](https://pandoc.org/installing.html) (installers for
Windows and macOS, packages for Linux), then run this in a terminal (a text
window for typing commands) in your draft's folder:

```sh
pandoc my-draft.docx --to=latex --extract-media=figures --output=my-draft.tex
```

Treat the result as a **rough first pass that needs cleanup**: copy only the
body text into chapter files, remove extra formatting commands, rebuild
tables and captions from the examples, and replace citations with
`\cite`. Check every equation against the original.

</details>

## From Markdown

Markdown marks text with symbols, such as `**bold**` and `## Heading`; LaTeX
uses commands, such as `\textbf{bold}` and `\section{Heading}`. Most of a
Markdown draft carries over once each symbol becomes its command.

![Three panels, left to right: Markdown, the LaTeX it becomes, and the printed page. The Markdown has a heading after two hash signs, Field results; a sentence with three sites between double asterisks, two seasons between single asterisks, and the citation key lamport1994 in square brackets after an at sign; and the equation y = mx + b between double dollar signs. The LaTeX has the section command with Field results, the sentence with the bold command around three sites, the emph command around two seasons, and an autocite command with lamport1994, then the equation inside an equation environment with a label. A note says Pandoc writes the equation between backslash-brackets, without a number, so it was moved into the equation environment by hand. The printed page shows a numbered section heading, Field results; the sentence with three sites in bold, two seasons in italics, and the citation as [1]; and the equation with its number at the right margin.](diagrams/markdown-to-latex.svg)

*In words:* a heading becomes `\section`, bold and italics become
`\textbf` and `\emph`, a citation becomes a citation command, and a display
equation goes in an `equation` environment so that it gets a number.

### Move a section by hand

No extra programs needed. Start with one short section, not a whole
chapter.

1. **Copy the text** of the section into a chapter file, below its
   `\chapter{...}` and `\label{...}` lines
   ([add a chapter](writing.md#chapters)).
2. **Change the Markdown symbols** to commands, using the table below and
   the examples in [writing basics](writing.md).
3. **Put a backslash before special characters** in ordinary text:
   `%` → `\%`, `&` → `\&`, `_` → `\_`, `#` → `\#`, and `$` → `\$` unless it
   starts or ends math.
4. **Compile.** Fix the first error before moving the next section.

| In Markdown | In your chapter file | Example to copy |
| --- | --- | --- |
| `# Title` | The chapter's `\chapter{...}`, in CAPITALS; one chapter per file | [Paragraphs and headings](writing.md#paragraphs-and-headings) |
| `## Heading`, `### Heading` | `\section{...}`, `\subsection{...}` | [Paragraphs and headings](writing.md#paragraphs-and-headings) |
| `**bold**`, `*italics*` | `\textbf{bold}`, `\emph{italics}` | [Paragraphs and headings](writing.md#paragraphs-and-headings) |
| `[@key]` or a typed citation | `\cite{key}`, with the key from `references.bib` | [Cite a source](writing.md#cite-a-source) |
| `$x$` in a sentence | `$x$`, unchanged | [Equations](writing.md#equations) |
| `$$ ... $$` on its own line | An `equation` with a `\label`, so it gets a number | [Equations](writing.md#equations) |
| A table with vertical bars between cells | The template's `table`, caption above | [Edit a table](writing.md#edit-a-table) |
| `![caption](picture.png)` | The template's `figure`, image in `figures/`, caption below | [Add a figure](writing.md#add-a-figure) |
| "see Figure 3" | `Figure~\ref{fig:my-plot}` | [Cross-references](writing.md#cross-references) |
| `- item` lines | `\begin{itemize}`, one `\item` per line, then `\end{itemize}` | |

For a long chapter, a conversion program can do the first pass instead.
Moving sections by hand works equally well; the program only saves typing.

<details><summary>For experienced users: convert a long Markdown draft with Pandoc</summary>

[Pandoc](https://pandoc.org/) is a free conversion program. It is optional
and only needed for converting files; Overleaf users don't need it. Install
it from the [Pandoc installation page](https://pandoc.org/installing.html)
(installers for Windows and macOS, packages for Linux), then run this in a
terminal (a text window for typing commands) in your Markdown file's folder:

```sh
pandoc my-chapter.md --to=latex --biblatex --top-level-division=chapter --output=my-chapter.tex
```

- `--biblatex` turns Pandoc citations
  ([Pandoc's citation syntax](https://pandoc.org/MANUAL.html#citations))
  into commands this starter understands: `[@lamport1994]` becomes
  `\autocite{lamport1994}`, and `@lamport1994` becomes
  `\textcite{lamport1994}`. Without it, citations stay as plain text.
- `--top-level-division=chapter` makes `#` a `\chapter` and `##` a
  `\section`. Without it, `#` becomes a `\section`.

Leave out `--standalone`: without it, Pandoc writes chapter content only,
with no `\documentclass` or preamble, which is what you want. The output is a
first draft of a chapter, not a finished one. Open it, then fix these before
you compile:

1. **Headings.** Keep one `\chapter` per file and type its title in
   CAPITALS. Pandoc adds labels such as `\label{field-results}`; keep them or
   rename them.
2. **Equations.** Pandoc writes `\[ ... \]`, which prints *without* a number.
   Change each one to the template's `equation` and add a `\label`
   ([equations](writing.md#equations)).
3. **Tables.** Pandoc writes a `longtable`, which this starter does not load,
   so the compile stops at `Environment longtable undefined`. Rebuild each
   table from [the template's table](writing.md#edit-a-table): copy the cells,
   and drop the `\noalign{}`, `\endhead`, and `\endlastfoot` lines. Pandoc
   adds a caption only if the Markdown had a `: Caption` line under the
   table; add one if not.
4. **Figures.** Pandoc wraps each image in `\pandocbounded{...}`, which this
   starter does not define. Replace that line with
   `\includegraphics[width=\linewidth]{figures/my-plot}`, put the image in
   `figures/`, and add `[htbp]` after `\begin{figure}`
   ([add a figure](writing.md#add-a-figure)). Writing `{#fig:my-plot}` after
   the image in Markdown gives the figure that `\label`.
5. **Cross-references.** Markdown has none built in, but `\ref{fig:my-plot}`
   typed in the Markdown passes through unchanged. Write a space before it
   (Pandoc changes `~` into a printed tilde), then change the space to `~`.
6. **Lists.** Delete each `\tightlist` line; this starter does not define it.
   Lists with a blank line between items convert without it.
7. **Citations.** Every key must exist in `references.bib`
   ([citations](citations.md)). `\autocite` works like `\cite` here; keep it
   or change it to `\cite`.
8. **Other commands.** Pandoc already escapes special characters such as
   `%`, `&`, and `_`. If the compile reports another undefined command,
   rewrite that part with the template's examples rather than copying in
   another document's preamble or packages.

Copy the cleaned text into your chapter file, compile, and compare every
equation, table, figure, and citation with your Markdown original. Keep that
original: once a chapter is in LaTeX, edit the `.tex` file, because changes
do not flow back to the Markdown. For other options, see the
[Pandoc manual](https://pandoc.org/MANUAL.html).

</details>

## From a LaTeX paper (IEEE, ACM, Elsevier, …)

Text, equations, figures, `\label`/`\ref`, and `\cite` keys usually carry over.

1. Start a new chapter file with `\chapter{...}` and copy the paper's body
   text below it.
2. Delete the venue's front matter and formatting commands: `\maketitle`,
   author and affiliation blocks, keywords, and commands such as
   `\IEEEPARstart`, `\ccsdesc`, or Elsevier's `frontmatter` environment.
   Change two-column `figure*` and `table*` to `figure` and `table`.
3. Paste the paper's `.bib` entries into `references.bib` (keys must be
   unique), and delete `\bibliographystyle` and `\bibliography`.
4. Copy the images into `figures/`, fix the `\includegraphics` paths, and add
   any extra packages the paper needed to `preamble.tex`.
5. Compile, then add the [chapter attribution](writing.md#chapters-based-on-published-papers)
   and any [permission statements](writing.md#reproduced-figures-and-permissions)
   your publisher's terms require.

If the paper used `\citep` or `\citet`, add `natbib=true` to the biblatex
options in `preamble.tex`, or switch to `\parencite` and `\textcite`. If two
papers reuse a label such as `fig:results`, prefix each chapter's labels
(`ch3:fig:results`).

## From RPI's official LaTeX template

If you started with RPI's official LaTeX template (`thesis.cls`, from RPI
ITS), your chapters, figures, tables, equations, labels, and citations mostly
carry over. Copy each old chapter into a new file in `chapters/`, include it
from `main.tex`, then update:

| RPI's official template | RPI Thesis Toolkit |
| --- | --- |
| `\documentclass[chap]{thesis}` | `\documentclass{rpi-thesis}`, no options (already in `main.tex`); chapters print as "1. TITLE" |
| `\thesistitle{...}`, `\author{...}` | `title = {...}`, `author = {...}` in `metadata.tex`; drop `\bf` and manual `\\` breaks |
| `\degree{Doctor of Philosophy}` | `degree = doctoral` (or `masters`, `engineering-doctorate`) |
| `\department{...}` | `department = {...}` with your full department name |
| `\thadviser{...}` / `\cothadviser{...}` | `\committeemember[Chair]{...}` / `\committeemember[Co-Chair]{...}` |
| `\memberone{...}` … `\membersix{...}` | One `\committeemember{...}` line each |
| `\signaturelines{...}` | Delete; not needed |
| `\submitdate{[May 2027]\\ Submitted ...}` | `graduation-month = May`, `graduation-year = {2027}`; no submission date |
| `\copyrightpage`, `\copyrightyear{...}` | `copyright-page = true` (uses the graduation year) |
| `\titlepage`, `\tableofcontents`, `\listoftables`, `\listoffigures` | Delete; `main.tex` already makes them |
| `\specialhead{ABSTRACT}` | `\frontchapter{ABSTRACT}` (already in `frontmatter/abstract.tex`) |
| `thebibliography` with `\bibitem{key}` | One entry per source in `references.bib`, with the same keys |
| `\caption[short]{long}` | `\caption{long}` only (see [why](writing.md#use-one-full-caption-not-a-short-one)) |
| ALL-CAPS chapter titles | Keep them; the built-in titles are capitals too |
| `rpi_seal.png` | Copy it to `assets/rpi-seal.png`, or [download the current seal](get-started.md#add-the-rpi-seal-one-minute) |

Already have a `.bib` file? Copy it in as `references.bib` and
[choose your style](citations.md#change-the-citation-style).

## Still drafting? Make the move easy

Many people draft in Markdown, Google Docs, Notion, or Word and bring each
chapter into LaTeX once it is stable (see
[where to draft](how-it-works.md#draft-where-you-and-your-advisor-can-work-comfortably)).
That works well if you:

- **move one small section early,** long before a deadline, so you find
  out what needs rebuilding while there is time;
- **write citation keys, not formatted citations:** type `\cite{lamport1994}`
  (or `[@lamport1994]` in Markdown) with the key from Zotero or Better BibTeX
  ([citations](citations.md#step-2-collect-and-cite-sources-with-zotero));
- **keep equations, tables, and cross-references simple,** or mark them
  `[EQ]`, `[TABLE]`, `[FIG]`, since they are rebuilt in LaTeX anyway.

Drafting directly in LaTeX is equally fine and skips the conversion.

## Then keep going

Compile after each chapter. When something breaks, it is almost always the
last thing you pasted; see [fixing problems](troubleshooting.md). Next,
[writing basics](writing.md) covers figures, tables, equations, and
cross-references.
