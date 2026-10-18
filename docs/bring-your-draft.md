# Bring your draft

For anyone with a draft in Word, Google Docs, Markdown, or LaTeX: you do not
have to start over. Get the sample compiling first
([get started](get-started.md)) and keep your original untouched. Move **one
small section** first, to meet any surprises early. Then go one chapter at a
time, compiling after each. Moving a section or a table? Paste it into
[Bring your work in](bring-your-work-in.md) for a first pass in LaTeX.

Where do you start?

- **Word or Google Docs:** [From Word or Google Docs](#from-word-or-google-docs)
- **Markdown:** [From Markdown](#from-markdown)
- **A LaTeX paper (IEEE, ACM, Elsevier):** [From a LaTeX paper](#from-a-latex-paper-ieee-acm-elsevier)
- **RPI's official LaTeX template:** [From RPI's official LaTeX template](#from-rpis-official-latex-template)
- **Your own LaTeX thesis project:** [Use just the class](#already-have-a-latex-thesis-use-just-the-class)

## What goes where

![Where each part of a Word or Google Docs draft goes: title and committee to metadata.tex, abstract and acknowledgments to frontmatter/, each chapter to its own file in chapters/ (tables and equations rebuilt in LaTeX), figures to figures/, references through Zotero to references.bib, appendices to appendices/.](diagrams/draft-to-files.svg)

*In words:* from Word or Google Docs, text pastes in while equations,
tables, and citations are rebuilt. Markdown needs them checked and mostly
converted; a LaTeX paper keeps most of them. The title page, contents, lists,
and page numbers are built for you.

## From Word or Google Docs

In Google Docs, copy the text, or choose **File → Download → Microsoft
Word**.

1. **Convert one section:** paste it into
   [Bring your work in](bring-your-work-in.md). It turns headings, bold and
   italics, lists, links, special characters, and tables into LaTeX, and
   lists what it left for you. By hand instead: headings become
   `\chapter{...}`, `\section{...}`, or `\subsection{...}`; footnotes become
   `\footnote{...}`; italics become `\emph{...}`; and special characters get
   a backslash: `%` → `\%`, `&` → `\&`, `_` → `\_`, `$` → `\$`, `#` → `\#`.
2. **Paste the LaTeX** into a chapter file ([add a chapter](writing.md#chapters)).
3. **Rebuild what doesn't paste** (quotations, equations, tables, figures,
   cross-references, citations) from [writing basics](writing.md) and
   `chapters/02-research.tex`. Use `\label` and `\ref`, not "see Figure 3".
4. **References:** [export your Zotero library](citations.md#step-2-collect-and-cite-sources-with-zotero),
   or [paste entries](citations.md#if-you-cant-use-zotero-paste-an-entry-by-hand)
   into `references.bib`.

A long `.docx`? [Pandoc](#convert-a-draft-with-pandoc-optional) can make a
rough first pass.

## From Markdown

Markdown marks text with symbols, such as `**bold**` and `## Heading`; LaTeX
uses commands, such as `\textbf{bold}` and `\section{Heading}`. Most of a
Markdown draft carries over once each symbol becomes its command. Neither
route below changes your original file.

- **In your browser, nothing to install:** paste a section into
  [Bring your work in](bring-your-work-in.md), which reads Markdown too.
- **One short section by hand:** [move it by hand](#move-a-section-by-hand).
- **A longer draft:** [use Pandoc](#convert-a-draft-with-pandoc-optional), then
  clean up its output.

### Move a section by hand

1. **Copy the text** into a chapter file, below its `\chapter{...}` and
   `\label{...}` lines ([add a chapter](writing.md#chapters)). If your draft
   starts with `# Title`, use that title in the existing `\chapter{...}` and
   leave out the `# Title` line when pasting the text.
2. **Change the Markdown symbols** to commands, using the table below.
3. **Put a backslash before special characters** in ordinary text:
   `%` → `\%`, `&` → `\&`, `_` → `\_`, `#` → `\#`, and `$` → `\$` unless it
   starts or ends math.
4. **Compile.** Fix the first error before moving the next section.

| In Markdown | In your chapter file | Example |
| --- | --- | --- |
| `# Title` | Replace the title in the existing `\chapter{...}`, in CAPITALS; keep one chapter heading per file | [Headings](writing.md#paragraphs-and-headings) |
| `## Heading`, `### Heading` | `\section{...}`, `\subsection{...}` | [Headings](writing.md#paragraphs-and-headings) |
| `**bold**`, `*italics*` | `\textbf{bold}`, `\emph{italics}` | [Commands](writing.md#the-10-commands-youll-actually-use) |
| `[@key]` | `\parencite{key}` (key from `references.bib`) | [Cite a source](writing.md#cite-a-source) |
| `@key` as part of a sentence | `\textcite{key}` | [Cite a source](writing.md#cite-a-source) |
| `$x$` in a sentence | `$x$`, unchanged | [Equations](writing.md#equations) |
| `$$ ... $$` | An `equation` with a `\label` | [Equations](writing.md#equations) |
| A table with bars | The template's `table`, caption above | [Edit a table](writing.md#edit-a-table) |
| `![caption](picture.png)` | The template's `figure`, image in `figures/` | [Add a figure](writing.md#add-a-figure) |
| "see Figure 3" | `Figure~\ref{fig:my-plot}` | [Cross-references](writing.md#cross-references) |
| `- item` lines | `itemize` with one `\item` per line | |

<details id="convert-a-draft-with-pandoc-optional"><summary>Optional: convert a long draft with Pandoc</summary>

[Pandoc](https://pandoc.org/) is a free program that converts Markdown or
Word (`.docx`) files. It saves typing but does not make a finished chapter.
It runs in a terminal (a text window for commands). Prefer not to use one?
For Markdown, use the [by-hand route](#move-a-section-by-hand); for Word or
Google Docs, use [From Word or Google Docs](#from-word-or-google-docs).

**Tip:** installing Pandoc and running terminal commands is where an AI chat
helps most. Never paste confidential or unpublished material, and keep your
original to compare ([more](going-further.md#ask-for-a-file-conversion)). Try:

```prompt
I use [Windows/macOS/Linux]. Walk me through installing Pandoc and converting my-chapter.md into LaTeX chapter content for this thesis template. Tell me what to check afterwards.
```

1. **Install Pandoc** from its
   [installation page](https://pandoc.org/installing.html). You can convert on
   your computer even if you compile on Overleaf.
2. **Open a terminal in your file's folder:** Terminal on macOS or Linux;
   PowerShell or Command Prompt on Windows
   ([how](https://pandoc.org/getting-started.html)).
3. **Run one command,** replacing the input and output names and keeping the
   quotes. It writes a new `.tex` file beside your original; pick another
   output name if that file exists.

For Markdown:

```sh
pandoc "my-chapter.md" --to=latex --biblatex --top-level-division=chapter -o "my-chapter.tex"
```

For Word:

```sh
pandoc "my-draft.docx" --to=latex --extract-media=figures -o "my-draft.tex"
```

The `--extract-media=figures` part saves the images in `figures/media/`, next
to where you run the command. Move that folder into the thesis `figures/`
folder, or run the command from the thesis folder with the draft path in
quotes.

The result is a rough first pass: body text, no document setup or title
page. From Word, headings usually arrive as `\section`, so add the
`\chapter` yourself. **Open the new `.tex` file before copying anything,**
and check:

- **Headings:** one `\chapter{...}` per file, in CAPITALS. For a single
  section, keep the existing chapter heading.
- **Equations:** change `\[ ... \]` to the numbered
  [`equation` example](writing.md#equations), with a unique `\label`.
- **Tables and figures:** rebuild from the
  [table](writing.md#edit-a-table) and [figure](writing.md#add-a-figure)
  examples. Images go in `figures/`.
- **Citations and cross-references:** every key must be in `references.bib`;
  use `\ref`, not typed numbers.

Copy the cleaned content into your [chapter file](writing.md#chapters), with
no second chapter heading. Compile, fix the first error, then compare every
equation, table, figure, and citation with the original. Once a chapter is in
LaTeX, edit the `.tex`; changes do not flow back.

<details><summary>If the converted file does not compile: common Pandoc fixes</summary>

Paste the first error and the lines around it into an AI chat or a web
search, plus what you were converting.

- **`\tightlist` undefined:** delete that line. The list around it stays.
- **`longtable` undefined:** copy the cells into the template's
  [table example](writing.md#edit-a-table) and remove the generated
  `\noalign{}`, `\endhead`, and `\endlastfoot` lines.
- **`\pandocbounded` undefined:** use the template's
  [`\includegraphics` example](writing.md#add-a-figure) with your image's path.
- **Citations:** `--biblatex` turns `[@key]` into `\autocite{key}` and `@key`
  into `\textcite{key}`; both work here
  ([Pandoc's citation syntax](https://pandoc.org/MANUAL.html#citations)).
- **A printed tilde before a reference:** Pandoc writes a literal `~` as
  `\textasciitilde`. Change it back to `~`, as in `Figure~\ref{fig:my-plot}`.
- **Other undefined commands:** use the starter's example for that part, not
  another document's packages.

`--top-level-division=chapter` makes `#` a `\chapter` and `##` a `\section`.
Leave out `--standalone`: you need chapter content, not a second complete
document. More options: the [Pandoc manual](https://pandoc.org/MANUAL.html).

</details>

<details><summary>Example: Markdown, converted LaTeX, and the finished page</summary>

![Three panels, left to right: Markdown, the LaTeX it becomes, and the printed page. The Markdown has a heading after two hash signs, Field results; a sentence with three sites between double asterisks, two seasons between single asterisks, and the citation key lamport1994 in square brackets after an at sign; and the equation y = mx + b between double dollar signs. The LaTeX has the section command with Field results, the sentence with the bold command around three sites, the emph command around two seasons, and an autocite command with lamport1994, then the equation inside an equation environment with a label. A note says Pandoc writes the equation between backslash-brackets, without a number, so it was moved into the equation environment by hand. The printed page shows a numbered section heading, Field results; the sentence with three sites in bold, two seasons in italics, and the citation as [1]; and the equation with its number at the right margin.](diagrams/markdown-to-latex.svg)

*In words:* headings, bold, italics, and citations become LaTeX commands;
a display equation goes in an `equation` environment so it gets a number.

</details>

</details>

## From a LaTeX paper (IEEE, ACM, Elsevier)

Text, equations, figures, labels, and `\cite` keys usually carry over.

1. Start a chapter file with `\chapter{...}` and copy the paper's body below it.
2. Delete the venue's front matter and formatting: `\maketitle`, author
   blocks, keywords, and commands such as `\IEEEPARstart`, `\ccsdesc`, or
   Elsevier's `frontmatter`. Change `figure*` and `table*` to `figure` and
   `table`.
3. Paste the paper's `.bib` entries into `references.bib` (keys must be
   unique), and delete `\bibliographystyle` and `\bibliography`.
4. Copy the images into `figures/`, fix the `\includegraphics` paths, and add
   any extra packages to `preamble.tex`.
5. Add `\include{chapters/your-chapter-file}` to `main.tex` where the chapter
   belongs, as in the [chapter recipe](writing.md#chapters).
6. Compile, then add the [chapter attribution](writing.md#chapters-based-on-published-papers)
   and any [permission statements](writing.md#reproduced-figures-and-permissions)
   your publisher's terms require.

Paper used `\citep` or `\citet`? Add `natbib=true` to the biblatex options in
`preamble.tex`, or switch to `\parencite` and `\textcite`. Two papers reuse
a label such as `fig:results`? Prefix each chapter's labels (`ch3:fig:results`).

## From RPI's official LaTeX template

Your chapters, figures, tables, equations, labels, and citations mostly carry
over. Copy each old chapter into a new file in `chapters/`, include it from
`main.tex`, then update:

| RPI's official template | RPI Thesis Toolkit |
| --- | --- |
| `\documentclass[chap]{thesis}` | `\documentclass{rpi-thesis}`, no options (already in `main.tex`) |
| `\thesistitle{...}`, `\author{...}` | `title`, `author` in `metadata.tex`; drop `\bf` and manual `\\` |
| `\degree{Doctor of Philosophy}` | `degree = doctoral` (or `masters`, `engineering-doctorate`) |
| `\department{...}` | `department = {...}`, full name |
| `\thadviser{...}` / `\cothadviser{...}` | `\committeemember[Chair]{...}` / `[Co-Chair]` |
| `\memberone{...}` … `\membersix{...}` | One `\committeemember{...}` each |
| `\signaturelines{...}` | Delete |
| `\submitdate{[May 2027]\\ Submitted ...}` | `graduation-month`, `graduation-year`; no submission date |
| `\copyrightpage`, `\copyrightyear{...}` | `copyright-page = true` |
| `\titlepage`, `\tableofcontents`, `\listoftables`, `\listoffigures` | Delete; `main.tex` makes them |
| `\specialhead{ABSTRACT}` | `\frontchapter{ABSTRACT}` (already in `frontmatter/abstract.tex`) |
| `thebibliography` with `\bibitem{key}` | One entry per source in `references.bib`, same keys |
| `\caption[short]{long}` | `\caption{long}` only ([why](writing.md#use-one-full-caption-not-a-short-one)) |
| ALL-CAPS chapter titles | Keep them |
| `rpi_seal.png` | Copy it to `assets/rpi-seal.png`, or [download the current seal](get-started.md#add-the-rpi-seal-one-minute) |

Already have a `.bib` file? Copy it in as `references.bib` and
[choose your style](citations.md#change-the-citation-style).

## Already have a LaTeX thesis? Use just the class

Keep your own project and take only the formatting. Put
[`rpi-thesis.cls`](https://diyanko.github.io/rpi-thesis-toolkit/downloads/rpi-thesis.cls)
next to your main file, then make the top of that file follow this shape
(your packages go after the `\documentclass` line; drop any margin, spacing,
or title-page code of your own, since the class handles it):

```latex
\documentclass{rpi-thesis}
\usepackage{csquotes}  % \enquote and quotation support, as in the starter
\usepackage[backend=biber,style=numeric,sorting=none]{biblatex}  % your style
\addbibresource{references.bib}
\thesissetup{
  title = {Your thesis title},
  author = {Your full name},
  degree = doctoral,   % or masters, engineering-doctorate
  department = {Department of Your Full Department Name},
  graduation-month = May,
  graduation-year = {2027},
}
\committeemember[Chair]{Your committee chair}
\committeemember{Committee member two}

\begin{document}
\maketitle
\thesisfrontmatter
\frontchapter{ABSTRACT}
Your abstract.
\thesismainmatter
\chapter{INTRODUCTION}
Your chapters, or \include lines for them.
\thesisreferences
\end{document}
```

The biblatex line is the starter's: references numbered in the order you
first cite them. Already use a citation style? Keep your own biblatex line
instead. The class still puts one blank line between references (tested with
numeric, APA, MLA, and Chicago author-date); check your PDF with any other
style ([citations](citations.md#change-the-citation-style)).

Compile it (save in your editor, or click **Recompile** on Overleaf; both run
the bibliography step for you), and compare with the
[settings list](going-further.md#all-thesis-settings) if something is missing.
From RPI's official template, [the section above](#from-rpis-official-latex-template)
maps its settings one by one.

## Still drafting? Make the move easy

Many people draft elsewhere and bring each chapter into LaTeX once it is
stable ([where to draft](how-it-works.md#draft-where-you-and-your-advisor-can-work-comfortably)).
It goes smoothly if you:

- **move one small section early,** long before a deadline;
- **write citation keys,** such as `\parencite{lamport1994}` (or `[@lamport1994]`
  in Markdown), with the key from Zotero
  ([citations](citations.md#step-2-collect-and-cite-sources-with-zotero));
- **keep equations, tables, and cross-references simple,** or mark them
  `[EQ]`, `[TABLE]`, `[FIG]`, since they are rebuilt anyway.

Drafting directly in LaTeX is equally fine.

## Then keep going

Compile after each chapter. When something breaks, it is almost always the
last thing you pasted; see [fixing problems](troubleshooting.md). Next,
[writing basics](writing.md) covers figures, tables, equations, and
cross-references.
