# Writing basics

For anyone writing the chapters of a thesis or dissertation, once the sample
compiles ([get started](get-started.md)). You write ordinary text plus a few
commands; the class (`rpi-thesis.cls`) handles the layout. Compile after each
small change so you always know what broke. Prefer paper? Print the
[one-page cheat sheet](../cheatsheet/).

## Paragraphs and headings

A blank line starts a new paragraph. Don't add space with `\\` or extra blank lines.

```tex
\chapter{INTRODUCTION}
\label{chap:introduction}

This is my first paragraph.

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

## Handy commands

| To get… | Type… |
| --- | --- |
| *Italic emphasis* | `\emph{a word}` |
| **Bold** | `\textbf{a word}` |
| 25% | `25\%` |
| Research & development | `Research \& development` |
| A literal `_`, `$`, or `#` | `\_`, `\$`, `\#` |
| A note only you can see | `% This is a comment` |
| A citation | `\cite{lamport1994}` |
| A cross-reference | `Chapter~\ref{chap:introduction}` |

Keep braces `{ }` paired. The `~` keeps "Chapter" and its number together.

## Chapters

1. Copy an existing chapter file, e.g. to `chapters/04-discussion.tex`.
2. Change its `\chapter{...}` title and `\label{...}`.
3. Add `\include{chapters/04-discussion}` to `main.tex` where it belongs.

To hide a chapter, put `%` at the start of its `\include` line.

## Cross-references

Give anything you point at a `\label{...}` and refer to it with `\ref{...}`;
never type a figure, table, chapter, or page number by hand.

```tex
As Figure~\ref{fig:example} shows, … (see Equation~\eqref{eq:example}).
```

Seeing **??** instead of a number? See
[bold keys and question marks](how-it-works.md#bold-citation-keys-and-question-marks).

## Figures and tables

Copy the examples in `chapters/02-research.tex`, and put images in `figures/`.

![A sketch of a thesis page. 1: the table caption sits above the table, all in bold, with a colon after the number: "Table 2.1: Values for three groups." 2: the figure caption sits below the figure in the same style: "Figure 2.1: A sample image." 3: equation y = mx + b has its number (2.1) on the same line at the right margin. 4: a two-line equation has one number, (2.2), centered vertically. 5: the list of figures entry "2.1 A sample image." repeats the full caption word for word, so don't use \caption[short]{…}.](diagrams/caption-rules.svg)

*In words:* table captions **above**, figure captions **below**, equation
numbers on the same line; the lists repeat each full caption.

- Use `[htbp]` so LaTeX can place each object where it fits, and mention
  every figure and table in your text.
- Check that nothing runs into the margins and figure text is readable.
- Too wide? Add `\usepackage{rotating}` to `preamble.tex` and use
  `sidewaystable` or `sidewaysfigure`. Longer than a page? Use `longtable`
  (`\usepackage{longtable}`) with `\caption` in its first row.
- Sentence-case captions end with a period.

### Use one full caption, not a short one

Write `\caption{Your full caption.}`, never `\caption[Short]{Long}`: OGE
expects the lists to match the captions word for word. The build helper flags
short captions.

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
permissions appendix and uploads ([submitting](submission.md)).

## Equations

Inline math uses dollar signs: `$x = 2$`. For displayed equations, OGE expects:

- **Every displayed equation numbered** (except within lemmas, theorems,
  proofs, and algorithms). Use `equation`, not `equation*` or `\[ … \]`.
- **The number on the same line** (see the picture in
  [figures and tables](#figures-and-tables)). If it drops below, break the
  equation over several lines:

```tex
\begin{equation}
  \begin{split}
    (a + b)^2 &= (a + b)(a + b) \\
              &= a^2 + 2ab + b^2.
  \end{split}
  \label{eq:multiline}
\end{equation}
```

`\\` ends a line and `&` aligns the rows (use `align` for a number on
every line).

## Chapters based on published papers

If a chapter reuses your own published, accepted, or submitted article, OGE
expects an attribution statement on that chapter's first page.

1. Put `\chapterattribution{...}` directly below the chapter's `\chapter` and
   `\label` lines. It prints as an unnumbered note at the foot of the page.
2. **Start with the wording for your article's status** (OGE manual §2.8,
   Table 2.1; every variant is in the comment at the top of
   `chapters/02-research.tex`), then add the full citation with `\fullcite{key}`:

   ```tex
   \chapterattribution{Portions of this chapter have previously appeared as:
     \fullcite{my-article}.}
   ```

3. List every attributed article on the **Declaration of Co-Contribution**
   (not needed if you are the sole author).

## Optional sections

- To drop the acknowledgments or appendices, follow the comments in `main.tex`.
- If you have no tables (or no figures) anywhere, including appendices, set
  `list-of-tables` (or `list-of-figures`) to `false` in `metadata.tex`.
- Keep the abstract and the contents.

Stuck? See [fixing problems](troubleshooting.md).
