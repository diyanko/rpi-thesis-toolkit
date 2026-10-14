# Bring your existing draft

For anyone with a thesis or dissertation draft in Word, Google Docs,
Markdown, a LaTeX paper, or RPI's official LaTeX template: you do not have to
start over. First get the sample compiling ([get started](get-started.md))
and keep your original draft unchanged. Then move **one chapter**, compile,
and repeat.

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
   `\emph{...}`; escape special characters: `%` → `\%`, `&` → `\&`,
   `_` → `\_`, `$` → `\$`, `#` → `\#`.
3. **Rebuild what doesn't paste,** using the examples in
   [writing basics](writing.md) and `chapters/02-research.tex`: equations (in
   `equation` environments), tables, figures (images saved in `figures/`),
   cross-references (`\label` and `\ref` instead of "see Figure 3"), and
   citations (`\cite{key}`).
4. **References:** if you used Zotero or another citation manager,
   [export your library](citations.md#step-2-collect-and-cite-sources-with-zotero).
   If you typed your list by hand, add each source to Zotero, or
   [paste entries](citations.md#if-you-cant-use-zotero-paste-an-entry-by-hand)
   into `references.bib`.

<details><summary>For experienced users: a rough first pass with Pandoc</summary>

[Pandoc](https://pandoc.org/) can convert a `.docx` into LaTeX:

```sh
pandoc my-draft.docx --to=latex --extract-media=figures --output=build/my-draft.tex
```

Treat the result as a **rough first pass that needs cleanup**: copy only the
body text into chapter files, remove extra formatting commands, rebuild
tables and captions from the examples, and replace citations with
`\cite`. Check every equation against the original.

</details>

## From Markdown

Copy the text in as for Word, or convert each chapter with Pandoc.

<details><summary>For experienced users: Markdown to LaTeX with Pandoc</summary>

```sh
pandoc my-chapter.md --to=latex --biblatex --top-level-division=chapter --output=build/my-chapter.tex
```

Headings become `\chapter`/`\section`, and Pandoc citations such as
`[@lamport1994]` become `\autocite{lamport1994}`, which this starter's
biblatex setup understands. Copy the result into a chapter file, then check
every equation, table, and figure path.

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

<details><summary>For experienced users: natbib commands and label clashes</summary>

For `\citep`/`\citet`, add `natbib=true` to the biblatex options in
`preamble.tex`, or switch to `\parencite`/`\textcite`. If two papers reuse a
label such as `fig:results`, prefix each chapter's labels (`ch3:fig:results`).

</details>

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
| `rpi_seal.png` | Copy it to `assets/rpi-seal.png`, or [download the current seal](../assets/README.md) |

Already have a `.bib` file? Copy it in as `references.bib` and
[choose your style](citations.md#change-the-citation-style).

## Still drafting? Make the move easy

Many people draft in Word, Google Docs, Notion, or Markdown and bring each
chapter into LaTeX once it is stable. That works well if you:

- **write citation keys, not formatted citations:** type `\cite{lamport1994}`
  with the key from Zotero or Better BibTeX
  ([citations](citations.md#step-2-collect-and-cite-sources-with-zotero));
- **keep equations, tables, and cross-references simple,** or mark them
  `[EQ]`, `[TABLE]`, `[FIG]`, since they are rebuilt in LaTeX anyway.

Drafting directly in LaTeX is equally fine and skips the conversion.

## Then keep going

Compile after each chapter. When something breaks, it is almost always the
last thing you pasted; see [fixing problems](troubleshooting.md). Next,
[writing basics](writing.md) covers figures, tables, equations, and
cross-references.
