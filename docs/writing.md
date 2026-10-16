# Writing basics

For anyone writing the chapters of a thesis or dissertation, once the sample
compiles ([get started](get-started.md)). You write ordinary text plus a few
*commands*: short instructions that start with a backslash, `\`. The class
file (`rpi-thesis.cls`) handles the layout. Compile after each small change,
so you always know what broke. Prefer paper? Print the
[one-page cheat sheet](../cheatsheet/). Need a table, equation, figure, or
code listing? Jump to [helpers for common tasks](#helpers-for-common-tasks).

## The 10 commands you'll actually use

| Command | What it does | Example |
| --- | --- | --- |
| `\chapter{...}` | Starts a chapter; the number is added for you | `\chapter{INTRODUCTION}` |
| `\section{...}` | Starts a section (`\subsection` goes one level down) | `\section{Research question}` |
| A blank line | Starts a new paragraph | Leave one empty line between paragraphs |
| `\emph{...}` | *Emphasis*, in italics (`\textbf{...}` gives bold) | `\emph{not}` |
| `\parencite{...}` | Cites a source from `references.bib`, in parentheses or brackets (`\textcite` puts the author in the sentence) | `\parencite{lamport1994}` |
| `\label{...}` and `\ref{...}` | Names something, then prints its number | `Figure~\ref{fig:plot}` |
| `figure` | A figure with its caption | See [add a figure](#add-a-figure) |
| `table` | A table with its caption | See [edit a table](#edit-a-table) |
| `equation` | A numbered equation | See [equations](#equations) |
| `%` | Starts a note LaTeX ignores | `% check this number` |

To print a special character, put a backslash before it: `\&`, `\%`, `\_`,
`\$`, `\#`. Keep every `{` paired with a `}`, and use `~` to keep "Figure"
on the same line as its number. That's most of a thesis; the rest is your
writing.

![A few lines of a chapter file with six numbered pins: commands start with a backslash; braces hold what a command acts on; \begin and \end wrap an environment such as a figure, table, or equation; a line starting with % is a note LaTeX ignores; a blank line starts a new paragraph; \cite and \ref are filled in when you compile.](diagrams/read-a-tex-file.svg)

*In words:* commands start with `\`, braces hold their text, `\begin` and
`\end` wrap a block (an *environment*), `%` starts a note, and a blank line
starts a paragraph.

## Paragraphs and headings

Separate paragraphs with one blank line, not `\\` or extra blank lines.

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

**Capitalization.** OGE's rule (manual §2.3; see the heading rows in the
[requirements map](project/requirements.md)) is to use one consistent case
for each kind of heading. The starter's own convention is CAPITALS for
chapter and appendix titles, matching its built-in titles (CONTENTS,
REFERENCES), so type them that way unless you choose another consistent case
([redefine the names](going-further.md#not-yet-covered)). For sections and captions, pick sentence
case ("Results of the field study") or title case ("Results of the Field
Study") and never mix them. To change the reference-list title, add
`\renewcommand{\referencesname}{References}` to `preamble.tex`.

## Chapters

1. Create a new file, e.g. `chapters/04-discussion.tex`, containing only this:

   ```tex
   \chapter{TITLE}
   \label{chap:short-name}

   Your first paragraph.
   ```

   Do not copy a finished chapter: its figure, table, and equation labels
   would repeat, and every label must be unique.
2. Replace `TITLE` and `short-name`.
3. Add `\include{chapters/04-discussion}` to `main.tex` where it belongs.

To hide a chapter, put `%` at the start of its `\include` line.

## Cross-references

Give anything you point at a `\label{...}` and refer to it with `\ref{...}`;
never type a figure, table, chapter, or page number by hand. Put the label
after the heading, after `\caption` for a [figure](#add-a-figure) or
[table](#edit-a-table), or inside the [equation](#equations), and give each
label a unique name.

```tex
As Figure~\ref{fig:my-plot} shows, … (see Equation~\eqref{eq:line}).
```

Seeing **??** instead of a number, or a citation key in **bold**? Compile
again; if it stays, check that the names match exactly. More in
[bold keys and question marks](how-it-works.md#bold-citation-keys-and-question-marks)
and [fixing problems](troubleshooting.md#common-messages).

## Cite a source

1. Add the source to `references.bib`, by exporting from Zotero or pasting an
   entry ([citations and references](citations.md)).
2. Find its **key**, the word after `@book{` or `@article{` in that entry.
3. Cite it where you need it, then compile. Use `\parencite` for a citation
   in parentheses and `\textcite` when the author is part of the sentence:

   ```tex
   An earlier study describes this approach~\parencite{your-key}.
   \textcite{your-key} describe this approach in detail.
   ```

   Replace `your-key` with the key from your source's entry. Check how your
   style prints both ([the citation commands](citations.md#change-the-citation-style)).

Only sources you cite appear in the reference list. Agree on a citation style
with your advisor first ([agree on a style](citations.md#step-1-agree-on-a-style-with-your-advisor)),
because the style decides what each command prints.

## Quote a source

For a short quotation inside a sentence, use `\enquote{...}`; it prints
curly quotation marks that face the right way, and typed `"` marks do not. Set
a long quotation apart with `quote` (or `quotation` for several paragraphs);
the class single-spaces it (OGE manual §2.1). Your citation style says how long
a quotation must be to set apart.

```tex
As one participant said, \enquote{the forms took longer than the work}, and
others agreed.

\begin{quote}
  A long quotation goes here, on its own lines, followed by its
  citation~\parencite[23]{lamport1994}.
\end{quote}
```

The optional `[23]` is a page locator: it prints the page number inside the
citation, for example [1, p. 23] in the sample style. See
[the citation commands](citations.md#change-the-citation-style).

## Figures and tables

![A sketch of a thesis page. The table caption sits above the table and the figure caption below the figure, both in bold with a colon after the number. An equation has its number on the same line at the right margin, and a two-line equation has one centered number. The list of figures repeats the full caption word for word, so there is no short caption.](diagrams/caption-rules.svg)

*In words:* table captions **above**, figure captions **below**, equation
numbers on the same line; the lists repeat each full caption.

Mention every figure and table in your text. `[htbp]` lets LaTeX place each
one where it fits, so it may move to the next page. That is normal.

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

   The file extension (`.png`, `.jpg`, `.pdf`) is optional. This fits images
   that are wider than tall. For a **tall (portrait) image**, such as a
   scanned page, a phone photo, or a tall map, use this line instead so the
   image and its caption fit on one page:

   ```tex
   \includegraphics[width=\linewidth,height=0.7\textheight,keepaspectratio]{figures/my-scan}
   ```
3. Refer to it in your text: `Figure~\ref{fig:my-plot} shows …`
4. Compile, and check that the figure is legible.

A plot, photo, map, scanned artwork, or architectural drawing all use these
same examples. For a flowchart, see [draw a diagram](#draw-a-diagram); for a chart
from data or another image format, see
[export a chart or convert an image](#export-a-chart-or-convert-an-image).
Credit material that is not yours ([permissions](#reproduced-figures-and-permissions)).

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
  letter to add a column, and delete a letter and its cells to remove one.
- `&` moves to the next column, and `\\` ends the row.
- Tables can hold words too. For text that should wrap, use `p{5cm}` instead
  of `l`; for a heading over two columns, write `\multicolumn{2}{c}{Heading}`.
- In a cell, `&`, `%`, `_`, `#`, and `$` need a backslash: `R\&D`, `50\%`.
- Refer to it with `Table~\ref{tab:my-table}`.

Have the data in a spreadsheet? Try
[make a table from a spreadsheet](#make-a-table-from-a-spreadsheet).

<details>
<summary>Example: a table of words, with a wrapped column and a merged heading</summary>

Replace the `tabular` part of the sample with this.

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
them sideways; the height limit in [add a figure](#add-a-figure) keeps a tall
image on its page. For a wide table, wrap long text in `p{}` columns, shorten headings
(explain abbreviations in the caption), drop columns you don't need, or split
it into two tables. Keep the text the same size as in your other tables rather
than shrinking it. An `Overfull \hbox` message points to anything still too
wide ([common messages](troubleshooting.md#common-messages)).

As a last resort, add `\usepackage{rotating}` to `preamble.tex` and use
`sidewaystable` or `sidewaysfigure` for a landscape page. For a table longer
than a page, uncomment the `longtable` line in `preamble.tex` and put
`\caption` in its first row. Check the page numbers and captions afterwards.

### Use one full caption, not a short one

Write `\caption{Your full caption.}`, never `\caption[Short]{Long}`: OGE
expects the lists to match the captions word for word. A long caption is
fine. Sentence-case captions end with a period. The build helper flags short
captions.

### Reproduced figures and permissions

A figure or table from someone else's work (or your own published paper)
needs the **full citation** and a **permission or license statement** in its
caption (see `chapters/02-research.tex`):

- **With permission:** "Reproduced from [full citation], with permission from
  [publisher]." Add any notice your permission document requires.
- **Creative Commons or open access:** "Reproduced from [full citation] under
  the CC BY 4.0 license." Name the exact license.

`\fullcite{key}` prints the full citation in the styles listed in
[print a full reference](citations.md#print-a-full-reference-in-the-text);
MLA and Chicago author-date need a setup there, and ACS shortens long author
lists. Check the printed caption.
Keep permission
emails or license text, and follow OGE's current instructions for the
permissions appendix ([submitting](submission.md)). With a numbered citation
style, also check
[delayed figures and tables](citations.md#numbered-styles-check-delayed-figures-and-tables).

## Equations

Inline math goes between dollar signs: `$x = 2$`. For displayed equations, OGE
expects:

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

If the number drops below a long equation, use `split` to break it over
several lines with one centered number:

```tex
\begin{equation}
  \begin{split}
    (a + b)^2 &= (a + b)(a + b) \\
              &= a^2 + 2ab + b^2
  \end{split}
  \label{eq:square}
\end{equation}
```

`\\` ends a line, and `&` marks where the lines line up. `\eqref{...}` prints
the number in parentheses.

For a matrix, use `pmatrix` or `bmatrix`; for a definition by cases, use
`cases`. The class already loads `amsmath`, the *package* (add-on) that
provides them. Prefer clicking an equation together? See
[write an equation](#write-an-equation).

## Chapters based on published papers

If a chapter reuses your own published, accepted, or submitted article, OGE
expects an attribution statement on its first page, even if you wrote the
article alone.

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
   Co-Contribution**. A published article you wrote alone needs the
   attribution but not the declaration (OGE manual §2.8.1). Whether that also
   holds for a sole-authored paper that is submitted or under review but not
   yet published is not confirmed
   ([needs OGE confirmation](project/requirements.md#needs-oge-confirmation)).
   Check OGE's current checklist or ask OGE.
   <!-- TODO(verify): sole-authored paper submitted or under review but unpublished: attribution and declaration requirements not confirmed with OGE; do not choose either reading. -->

## Optional sections

- To drop the acknowledgments or appendices, follow the comments in `main.tex`.
- If you have no tables (or no figures) anywhere, including appendices, set
  `list-of-tables` (or `list-of-figures`) to `false` in `metadata.tex`.
- Keep the abstract and the contents.

## Helpers for common tasks

Free web tools and AI assistants can do the fiddly parts, such as turning a
table, an equation, or a sketch into code, so you spend your time on the
thesis, not the syntax. What you keep is plain, editable files. Every helper is
optional, everything here also works by hand, and they are independent
third-party services whose terms can change.

| I need to... | Start here |
| --- | --- |
| Turn spreadsheet cells into a table | [Tables Generator](#make-a-table-from-a-spreadsheet) |
| Build an equation by clicking | [Equation editor](#write-an-equation) |
| Find a symbol I can draw | [Detexify](#find-a-symbols-command) |
| Make a flowchart or schematic | [Diagram tools](#draw-a-diagram) |
| Add a chart from research data | [Export a plot](#export-a-chart-or-convert-an-image) |
| Include source code | [Code listing example](going-further.md#add-code-to-an-appendix) |
| Convert a document or image file | [Conversion help](going-further.md#ask-for-a-file-conversion) |
| Get unstuck on a tricky technical step | [An AI assistant](#ask-an-ai-assistant) |

### Make a table from a spreadsheet

Use [Tables Generator](https://www.tablesgenerator.com/latex_tables) to turn
spreadsheet cells into an editable LaTeX table.

![Spreadsheet cells with three rows become a LaTeX tabular snippet, which prints as a table with its caption above it.](diagrams/helper-table.svg)

1. Paste your cells into its grid, or use **File → Import CSV or Excel
   file**. Remove unused rows and columns there.
2. Optional: pick the booktabs style to match the sample, and give a
   long-text column a width so it wraps. Don't scale the table to fit.
3. Copy only the lines from `\begin{tabular}` to `\end{tabular}` and paste
   them over the `tabular` part of [the template's table](#edit-a-table),
   keeping its `\caption` above and its `\label`.
4. `booktabs` is already loaded; put any other `\usepackage` line it lists in
   `preamble.tex`.

Keep the output as `tabular` for this route; `tabularx` or multipage tables
need other code ([wide and multipage tables](#too-wide-for-the-page)). To put
LaTeX in a cell on purpose, such as `$x^2$`, untick **Escape special
characters**.

### Write an equation

Use [LaTeXEditor.app](https://latexeditor.app/) to build an equation by
clicking symbols, fractions, matrices, or a system of equations.

![A handwritten or clicked-together equation becomes LaTeX source, which prints as a numbered equation with its number at the right margin.](diagrams/helper-equation.svg)

- **In a sentence:** paste it between dollar signs, `$...$`.
- **On its own line:** paste it into the [numbered equation example](#equations),
  before `\label`, or inside `split` for several lines with one number.
  Leave out any `$`, `$$`, `\[`, or `\]` around the code, and keep
  `equation`, not `equation*`, so it stays numbered.
- **Undefined command?** The editor's preview knows commands your thesis may
  not have loaded. Chemistry such as `\ce{H2O}` needs
  `\usepackage[version=4]{mhchem}` in `preamble.tex`; compile to check.

### Find a symbol's command

Use [Detexify](https://detexify.kirelabs.org/) when you can draw a symbol but
do not know its LaTeX command.

![A hand-drawn nabla symbol is matched to the command \nabla, which prints as the symbol.](diagrams/helper-symbol.svg)

Draw one symbol, pick the match, and copy its command. If it names a package,
add `\usepackage{...}` to `preamble.tex`; `amssymb` and `amsfonts` are already
covered by the class. For a whole handwritten equation, rebuild it in the
equation editor instead.

### Draw a diagram

Use [draw.io](https://app.diagrams.net/) to arrange shapes and arrows into
flowcharts, concept maps, timelines, or schematics.

![A rough sketch of boxes and arrows is redrawn in draw.io and exported, becoming a clean diagram in the thesis, with its caption below it.](diagrams/helper-diagram.svg)

1. Save the editable file in `figures/`, such as `figures/my-diagram.drawio`.
2. Export a PDF next to it (**File → Export as → PDF**, with **Crop**
   ticked so no blank page surrounds the drawing). PNG works too.
3. Write `figures/my-diagram` in `\includegraphics` ([add a figure](#add-a-figure))
   and compile. Check that the labels are readable at the printed size.

Export as PDF uses
[draw.io's server](https://www.drawio.com/docs/manual/export/export-to-pdf/),
which draw.io says deletes the diagram once the PDF is returned. To keep it on
your computer, use the draw.io desktop app, or export a PNG or SVG, and check
the result. **File → Print** with **Crop** and **Save as PDF** also stays
local, but **Crop** there is not supported in Safari, and this route has not
been tested here; if the PDF has blank margins, use another route.
<!-- TODO(verify): draw.io desktop app export with Crop and Print-with-Crop were not hand-tested; confirm against the draw.io docs. -->
Want a mathematical drawing as TikZ code?
[Mathcha](https://www.mathcha.io/) can export it: add `\usepackage{tikz}` to
`preamble.tex` and check that it compiles.

### Export a chart or convert an image

For a chart, keep the spreadsheet or plotting code and the original data, and
export a PDF where possible, or a PNG, for the [figure example](#add-a-figure).
Check axes, units, and legends against the data, and use the data file rather
than reconstructing values from a screenshot.

Have an SVG or another image format? Export PDF or PNG from the app that made
it; renaming the file does not convert it. Keep photos and scans sharp enough
for print, and inspect labels and cropping afterwards. Need the steps?
[Describe the conversion you want](going-further.md#ask-for-a-file-conversion).

### Ask an AI assistant

For the tricky technical bits, an AI assistant that accepts images can turn a
table screenshot, a photo of a handwritten equation, or a rough sketch into
editable code, and can explain a compile error; follow up in plain words
("make the first column wider"). It is for technical help only, never for
writing your thesis. Prompts you can copy:

```prompt
Convert this table into LaTeX. Preserve every value and heading. Flag unclear cells instead of guessing.
```

```prompt
Transcribe this equation into LaTeX without simplifying it. Preserve signs, subscripts, superscripts, and grouping. Flag anything unclear.
```

```prompt
Turn this sketch into an editable diagram. Preserve the labels and arrow directions. List anything ambiguous.
```

```prompt
Fix this formatting problem with the smallest change. Preserve my content and the thesis template's formatting. Explain where to paste the correction.
```

Before you use the result, compare every table cell, equation symbol, and
diagram label with the original (a clean compile doesn't prove it is right),
paste only the table, equation, or figure into the template's examples (never
another document's preamble, and don't change `rpi-thesis.cls`), and share only
material you're comfortable sending to that service.

More: [AI for technical help](going-further.md#use-ai-for-technical-help). Stuck?
See [fixing problems](troubleshooting.md).
