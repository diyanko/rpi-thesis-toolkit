# Writing basics

For anyone writing the chapters of a thesis or dissertation, once the sample
compiles ([get started](get-started.md)). You write ordinary text plus a few
*commands*: short instructions that start with a backslash, `\`. The class
file (`rpi-thesis.cls`, which holds the formatting rules) handles the layout.
Compile (make the PDF) after each small change, so you always know what
broke. Prefer paper? Print the [one-page cheat sheet](../cheatsheet/).

## The 10 commands you'll actually use

| Command | What it does | Example |
| --- | --- | --- |
| `\chapter{...}` | Starts a chapter; the number is added for you | `\chapter{INTRODUCTION}` |
| `\section{...}` | Starts a section (`\subsection` goes one level down) | `\section{Research question}` |
| A blank line | Starts a new paragraph | Leave one empty line between paragraphs |
| `\emph{...}` | *Emphasis*, printed in italics (`\textbf{...}` gives bold) | `\emph{not}` |
| `\cite{...}` | Cites a source from `references.bib` | `\cite{lamport1994}` |
| `\label{...}` and `\ref{...}` | Names something, then prints its number | `Figure~\ref{fig:my-plot}` |
| `figure` with `\includegraphics` | A figure with its caption | `\includegraphics[width=\linewidth]{figures/my-plot}` |
| `table` | A table with its caption | See [edit a table](#edit-a-table) |
| `equation` | A numbered equation | `\begin{equation} E = mc^2 \end{equation}` |
| `%` | Starts a note LaTeX ignores | `% check this number` |

To print a special character, put a backslash before it: `\&`, `\%`, `\_`,
`\$`, `\#`. Keep every `{` paired with a `}`, and use `~` to keep a word
such as "Figure" on the same line as its number.

That's most of a thesis. Everything else is your writing.

![A few lines of a chapter file with six numbered pins. 1: commands start with a backslash, as in \section. 2: braces hold what a command acts on, as in the section title inside { }. 3: \begin{figure} and \end{figure} wrap an environment, a block such as a figure, table, or equation. 4: a line starting with % is a note LaTeX ignores. 5: a blank line starts a new paragraph. 6: \cite and \ref are filled in for you when you compile, with the citation and the figure number.](diagrams/read-a-tex-file.svg)

*In words:* commands start with `\`, braces hold their text, `\begin` and
`\end` wrap a block (an *environment*), `%` starts a note, a blank line
starts a paragraph, and `\cite` and `\ref` are filled in when you compile.

## Paragraphs and headings

Separate paragraphs with one blank line; don't add space with `\\` or
extra blank lines.

```tex
\chapter{INTRODUCTION}
\label{chap:introduction}

This is my first paragraph, with a \textbf{bold} word and an \emph{italic} one.

This is another paragraph.

\section{Research question}
\subsection{Context}
```

LaTeX numbers headings and builds the contents, so never type the numbers.
Use at most four levels (`\chapter` to `\subsubsection`).

**Capitalization** (OGE manual §2.3): type chapter and appendix titles in
CAPITALS, like the built-in titles (CONTENTS, REFERENCES). For sections and
captions, pick sentence case ("Results of the field study") or title case
("Results of the Field Study") and never mix them.

## Chapters

1. Copy an existing chapter file, e.g. to `chapters/04-discussion.tex`.
2. Change its `\chapter{...}` title and `\label{...}`.
3. Add `\include{chapters/04-discussion}` to `main.tex` where it belongs.

To hide a chapter, put `%` at the start of its `\include` line.

## Cross-references

Give anything you point at a `\label{...}` and refer to it with `\ref{...}`;
never type a figure, table, chapter, or page number by hand.

```tex
As Figure~\ref{fig:my-plot} shows, … (see Equation~\eqref{eq:line}).
```

Something not filled in?

- **??** instead of a number: compile again. If it stays, check that the
  names in `\label{...}` and `\ref{...}` match exactly.
- A citation key in **bold**: check that the key in `\cite{...}` matches
  `references.bib` exactly, then run Biber and compile again.

More in [bold keys and question marks](how-it-works.md#bold-citation-keys-and-question-marks)
and [fixing problems](troubleshooting.md#common-messages).

## Cite a source

1. Add the source to `references.bib`, by exporting from Zotero or pasting an
   entry ([citations and references](citations.md)).
2. Find its **key**, the word after `@book{` or `@article{` in that entry.
3. Cite it where you need it, then compile:

   ```tex
   LaTeX keeps the content separate from the layout~\cite{lamport1994}.
   ```

Only sources you cite appear in the reference list. Choose the citation style
with your advisor ([agree on a style](citations.md#step-1-agree-on-a-style-with-your-advisor)).

## Quote a source

For a short quotation inside a sentence, use `\enquote{...}`. It prints
curly quotation marks that face the right way; typed `"` marks do not. Set a
long quotation apart with `quote` (or `quotation` for several paragraphs).
The class single-spaces it (OGE manual §2.1). Your citation style says how
long a quotation must be to set apart.

```tex
As one participant said, \enquote{the forms took longer than the work}, and
others agreed.

\begin{quote}
  A long quotation goes here, on its own lines, followed by its
  citation~\cite{lamport1994}.
\end{quote}
```

## Figures and tables

![A sketch of a thesis page. 1: the table caption sits above the table, all in bold, with a colon after the number: "Table 2.1: Values for three groups." 2: the figure caption sits below the figure in the same style: "Figure 2.1: A sample image." 3: equation y = mx + b has its number (2.1) on the same line at the right margin. 4: a two-line equation has one number, (2.2), centered vertically. 5: the list of figures entry "2.1 A sample image." repeats the full caption word for word, so don't use \caption[short]{…}.](diagrams/caption-rules.svg)

*In words:* table captions **above**, figure captions **below**, equation
numbers on the same line; the lists repeat each full caption.

Mention every figure and table in your text. `[htbp]` lets LaTeX place each
one where it fits, so it may move to the next page; that is normal.

### Add a figure

1. Put the image (PNG, JPG, or PDF) in the `figures/` folder, for example
   `figures/my-plot.png`.
2. Paste this after the paragraph that first mentions the figure. The caption
   goes **below** the image, and `\label` comes after `\caption`:

   ```tex
   \begin{figure}[htbp]
     \centering
     \includegraphics[width=\linewidth]{figures/my-plot}
     \caption{Your full caption, ending with a period.}
     \label{fig:my-plot}
   \end{figure}
   ```

   The file extension (`.png`, `.jpg`, `.pdf`) is optional.
3. Refer to it in your text: `Figure~\ref{fig:my-plot} shows …`
4. Compile, and check that the figure is legible.

A figure can be a plot, a photo, a map, a scanned artwork, or an
architectural drawing; each works the same way. Export a plot from your
analysis software (as PDF where it can), and keep the data behind it. Use
photos and scans large enough to stay sharp in print, and credit any that
aren't yours ([permissions](#reproduced-figures-and-permissions)). For a
flowchart or concept map, see [draw a diagram](#draw-a-diagram).

### Edit a table

Start from the sample table in `chapters/02-research.tex`. The caption goes
**above** the table, and `\label` comes after `\caption`:

```tex
\begin{table}[htbp]
  \centering
  \caption{Your full caption, ending with a period.}
  \label{tab:my-table}
  \begin{tabular}{lr}
    \toprule
    Group & Value \\
    \midrule
    A & 12 \\
    B & 18 \\
    \bottomrule
  \end{tabular}
\end{table}
```

- `{lr}` has one letter per column: `l` left, `c` centered, `r` right. Add a
  letter to add a column.
- `&` moves to the next column, and `\\` ends the row.
- To remove a column, delete its letter and its cell in every row; to remove
  a row, delete its line.
- Tables can hold words, such as interview themes or survey answers. For
  text that should wrap, use a paragraph column: `p{5cm}` instead of `l`.
- For a heading over two columns, write `\multicolumn{2}{c}{Heading}`.
- In a cell, `&`, `%`, `_`, `#`, and `$` need a backslash: `R\&D`, `50\%`.
- Refer to it with `Table~\ref{tab:my-table}`.

Have the data in a spreadsheet? See
[make a table from a spreadsheet](#make-a-table-from-a-spreadsheet).

<details>
<summary>Example: a table of words, with a wrapped column and a merged heading</summary>

Replace the `tabular` part of the sample with this. `\cmidrule{2-3}` draws a
short line under columns 2 and 3.

```tex
\begin{tabular}{lp{5cm}r}
  \toprule
  & \multicolumn{2}{c}{From 30 interviews} \\
  \cmidrule{2-3}
  Theme & Typical comment & People \\
  \midrule
  Cost & This longer comment wraps onto a second line inside its column. & 12 \\
  Access & R\&D staff, 50\% of site \#3 & 18 \\
  \bottomrule
\end{tabular}
```

</details>

### Too wide for the page?

Nothing may run into the margins. `width=\linewidth` keeps an image inside
them. For a wide table, wrap long text in `p{}` columns, shorten headings or
abbreviations (explain them in the caption), drop columns you don't need, or
split it into two tables. Keep the text the same size as in your other
tables rather than shrinking it. An `Overfull \hbox` message points to
anything still too wide ([common messages](troubleshooting.md#common-messages)).

As a last resort for a very wide table, add `\usepackage{rotating}` to
`preamble.tex` and use `sidewaystable` or
`sidewaysfigure` for a landscape page. For a table longer than a page,
uncomment the `longtable` line in `preamble.tex` and put `\caption` in its
first row. Check the page numbers and captions on those pages.

### Use one full caption, not a short one

Write `\caption{Your full caption.}`, never `\caption[Short]{Long}`: OGE
expects the lists to match the captions word for word. A long caption is
fine; keep it whole. Sentence-case captions end with a period. The build
helper flags short captions.

### Reproduced figures and permissions

A figure or table from someone else's work (or your own published paper)
needs the **full citation** and a **permission or license statement** in its
caption (example in `chapters/02-research.tex`):

- **With permission:** "Reproduced from [full citation], with permission from
  [publisher]." Add any notice your permission document requires.
- **Creative Commons or open access:** "Reproduced from [full citation] under
  the CC BY 4.0 license." Name the exact license.

`\fullcite{key}` prints the full citation in your style. Keep permission
emails or license text, and follow OGE's current instructions for the
permissions appendix and uploads ([submitting](submission.md)). With a
numbered citation style, also check
[delayed figures and tables](citations.md#numbered-styles-check-delayed-figures-and-tables).

## Equations

Inline math goes between dollar signs: `the value $x = 2$ is`. For displayed
equations, OGE expects:

- **Every displayed equation numbered** (except within lemmas, theorems,
  proofs, and algorithms). Use `equation`, not `equation*` or `\[ … \]`.
- **The number on the same line** (see the picture in
  [figures and tables](#figures-and-tables)).

A numbered equation, referred to as `Equation~\eqref{eq:line}`:

```tex
\begin{equation}
  y = mx + b
  \label{eq:line}
\end{equation}
```

If the number drops below a long equation, break it over several lines with
`split`. It keeps one number, centered:

```tex
\begin{equation}
  \begin{split}
    (a + b)^2 &= (a + b)(a + b) \\
              &= a^2 + 2ab + b^2
  \end{split}
  \label{eq:square}
\end{equation}
```

`\\` ends a line, and `&` marks the point where the lines line up, such as
the equals sign. `\eqref{...}` prints the number in parentheses.

For a matrix, use `pmatrix` (parentheses) or `bmatrix` (square brackets); for
a definition by cases, use `cases`. The class already loads `amsmath`, the
*package* (add-on) that provides them. Want to click an equation together instead? See
[write an equation](#write-an-equation).

<details>
<summary>Example: a matrix and cases</summary>

```tex
\begin{equation}
  A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}
  \label{eq:matrix}
\end{equation}

\begin{equation}
  f(x) =
  \begin{cases}
    0 & \text{if } x < 0, \\
    x & \text{otherwise.}
  \end{cases}
  \label{eq:cases}
\end{equation}
```

</details>

## Chapters based on published papers

If a chapter reuses your own published, accepted, or submitted article, OGE
expects an attribution statement on that chapter's first page, even if you
wrote the article alone.

1. Put `\chapterattribution{...}` directly below the chapter's `\chapter` and
   `\label` lines. It prints as an unnumbered note at the foot of the page.
2. **Start with the wording for your article's status** (OGE manual §2.8,
   Table 2.1; every variant is in the comment at the top of
   `chapters/02-research.tex`), then add the full citation with `\fullcite{key}`:

   ```tex
   \chapterattribution{Portions of this chapter have previously appeared as:
     \fullcite{my-article}.}
   ```

3. **Co-authored article?** Also list it on the **Declaration of
   Co-Contribution**. An article you wrote alone needs the attribution but
   not the declaration (OGE manual §2.8.1).

## Optional sections

- To drop the acknowledgments or appendices, follow the comments in `main.tex`.
- If you have no tables (or no figures) anywhere, including appendices, set
  `list-of-tables` (or `list-of-figures`) to `false` in `metadata.tex`.
- Keep the abstract and the contents.

## Helpers for common tasks

AI assistants and free web tools can do the fiddly parts, turning a table,
an equation, or a sketch into code, so you spend your time on the thesis,
not the syntax. What you keep is plain, editable files (`.tex`, `.drawio`)
that are yours. Every helper is optional; everything here also works by
hand. They are independent third-party services whose terms can change.

### Make a table from a spreadsheet

![Spreadsheet cells with three rows become a LaTeX tabular snippet, which prints as a table with its caption above it.](diagrams/helper-table.svg)

*In words:* paste your cells into
[Tables Generator](https://www.tablesgenerator.com/latex_tables), then copy
its `tabular` code into the template's table.

1. Paste your cells into its grid, or use **File → Import CSV or Excel
   file**. Remove unused rows and columns there.
2. Optional: pick the booktabs style to match the sample, and give a
   long-text column a width so it wraps. Don't scale the table to fit; that
   shrinks the text.
3. Copy only the lines from `\begin{tabular}` to `\end{tabular}` and paste
   them over the `tabular` part of [the template's table](#edit-a-table),
   keeping its `\caption` above and its `\label`.
4. Skip the `\usepackage` lines it lists (`booktabs` is already loaded)
   unless the compile reports an undefined command.

It escapes `&`, `%`, `_`, and similar characters so they print as typed. For
LaTeX in a cell on purpose, such as `$x^2$` or `\cite{key}`, untick
**Escape special characters**, or fix that cell after pasting.

### Write an equation

![A handwritten or clicked-together equation becomes LaTeX source, which prints as a numbered equation with its number at the right margin.](diagrams/helper-equation.svg)

*In words:* build the equation in [LaTeXEditor.app](https://latexeditor.app/)
by clicking symbols, fractions, matrices, or a system of equations, then copy
the code from its text box.

- **In a sentence:** paste it between dollar signs, `$...$`.
- **On its own line:** paste it into the [numbered equation example](#equations),
  before `\label`, or inside `split` for several lines with one number.
  Leave out any `$`, `$$`, `\[`, or `\]` around the code, and keep
  `equation`, not `equation*`, so it stays numbered.
- **Undefined command?** The editor's preview knows commands your thesis may
  not have loaded. Chemistry such as `\ce{H2O}` needs
  `\usepackage[version=4]{mhchem}` in `preamble.tex`, the file where extra
  packages are loaded; compile to check.

### Find a symbol's command

![A hand-drawn nabla symbol is matched to the command \nabla, which prints as the symbol.](diagrams/helper-symbol.svg)

*In words:* draw one symbol in [Detexify](https://detexify.kirelabs.org/),
pick the match, and copy its command, such as `\nabla`.

If it names a package, add `\usepackage{...}` to `preamble.tex`. You don't
need `amssymb` or `amsfonts`: the class already provides their symbols, so
those lines are harmless but unnecessary. Detexify recognizes one symbol at a time; for a whole
handwritten equation, use the equation editor or
[an AI assistant](#ask-an-ai-assistant).

### Draw a diagram

![A rough sketch of boxes and arrows becomes a clean diagram in the thesis, with its caption below it.](diagrams/helper-diagram.svg)

*In words:* draw flowcharts, concept maps, timelines, or schematics in
[draw.io](https://app.diagrams.net/), and use the exported file with
[the figure example](#add-a-figure).

1. Save the editable file in `figures/`, such as `figures/my-diagram.drawio`.
2. Export a PDF next to it (**File → Export as → PDF**, with **Crop**
   ticked so no blank page surrounds the drawing). PNG works too.
3. Write `figures/my-diagram` in `\includegraphics` and compile. Check that
   the labels are readable at the printed size; if not, change the `width`
   or the font size in draw.io.

Export as PDF uses draw.io's server to make the file
([draw.io's PDF export page](https://www.drawio.com/docs/manual/export/export-to-pdf/)).
To keep it on your computer, use **File → Print**, tick **Crop**, and choose
**Save as PDF** in your browser's print dialog.

Want a mathematical drawing as TikZ code? [Mathcha](https://www.mathcha.io/)
can export it: add `\usepackage{tikz}` to `preamble.tex`, and check that the
code compiles in your thesis, since some content doesn't export.

### Ask an AI assistant

An AI assistant that accepts images can turn a table screenshot, a photo of
a handwritten equation, or a rough sketch into editable code, including TikZ
for diagrams. It can also wrap a table, align equations, clarify labels, or
explain a compile error; follow up in plain words ("make the first column
wider"). Prompts you can copy:

```text
Convert this table into LaTeX. Preserve every value and heading. Flag unclear cells instead of guessing.
```

```text
Transcribe this equation into LaTeX without simplifying it. Preserve signs, subscripts, superscripts, and grouping. Flag anything unclear.
```

```text
Turn this sketch into an editable diagram. Preserve the labels and arrow directions. List anything ambiguous.
```

```text
Fix this formatting problem with the smallest change. Preserve my content and the thesis template's formatting. Explain where to paste the correction.
```

Before you use the result:

- Compare every table cell, equation symbol, and diagram label and arrow
  with the original. A clean compile doesn't prove the transcription is right.
- Paste only the table, equation, or figure into the template's examples.
  Add a needed `\usepackage` line (such as `tikz`) to `preamble.tex`, but
  don't paste in another document's preamble or change `rpi-thesis.cls`.
- Have the data in a spreadsheet? Start from that, not a screenshot. For
  plots, keep the real data; an assistant can help with the plotting code.
- Share only material you're comfortable sending to that service.

More: [AI for technical help](workflows.md#use-ai-for-technical-help).

Stuck? See [fixing problems](troubleshooting.md).
