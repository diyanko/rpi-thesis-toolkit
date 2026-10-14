# Advanced use

For experienced users and the curious; nothing here is needed to write your
thesis or dissertation. If the sample doesn't compile yet, start with [get started](get-started.md).

## Where customizations belong

| You want to change… | Edit | Notes |
| --- | --- | --- |
| Details shown on the title page | `metadata.tex` | Every setting is in the table below |
| Document order, chapters, optional sections | `main.tex` | References stay before appendices |
| Packages and citation style | `preamble.tex` | Loaded after the class |
| Formatting rules | `rpi-thesis.cls` | Avoid: edits are lost when you [update the class](workflows.md#update-the-formatting-safely); check [the requirements map](project/requirements.md) first |

Another geometry, spacing, caption, or heading package in `preamble.tex` can
silently break a requirement; prefer the documented settings. Also note:

- **Class options are rejected.** `\documentclass[11pt]{rpi-thesis}` stops with
  "Unsupported class option". The class always uses 12pt, US letter, one-sided.
- **hyperref is already loaded** (by the class, with `hidelinks,unicode`)
  before `preamble.tex` runs. Do not load it again; change its options with
  `\hypersetup{...}` in `preamble.tex`. Packages that must load *before*
  hyperref need a class change.

## All thesis settings

Settings go inside `\thesissetup{...}` in `metadata.tex`.

| Key | Values | Default | Notes |
| --- | --- | --- | --- |
| `title` | text | — (required) | Printed in capitals on the title page |
| `author` | text | — (required) | |
| `degree` | `masters`, `doctoral`, `engineering-doctorate` | `masters` | Master of Science, Doctor of Philosophy, Doctor of Engineering |
| `degree-name` | text | from `degree` | Overrides the displayed degree name; put it **after** `degree` |
| `department` | text | — (required) | Full name, e.g. `Department of Physics, Applied Physics and Astronomy` |
| `graduation-month` | `May`, `August`, `December` | — (required) | Graduation, not submission, month |
| `graduation-year` | four digits | — (required) | |
| `seal-file` | file path | `assets/rpi-seal.jpg` | You download the seal from RPI ([how](../assets/README.md)). If missing, `assets/rpi-seal.png` is tried; then a same-size placeholder box, a warning, and a build hint |
| `copyright-page` | `true`, `false` | `false` | Adds the copyright notice page (ii) |
| `list-of-tables` | `true`, `false` | `true` | Set `false` only if there are no tables anywhere |
| `list-of-figures` | `true`, `false` | `true` | Set `false` only if there are no figures anywhere |

Committee members are listed outside `\thesissetup`, one per line, in order:

- `\committeemember[Chair]{Name}` or `\committeemember[Co-Chair]{Name}` — at
  least one is required.
- `\committeemember{Name}` for everyone else. Text in the optional brackets is
  printed after the name, following a comma.

There is no fixed committee size; check the title page with long titles,
department names, or large committees.

Other commands from the class: `\frontchapter{Title}` (unnumbered front-matter
section that appears in the contents), `\thesisfrontmatter` (copyright page,
contents, and lists), `\thesismainmatter` (switches to Arabic page 1), and
`\chapterattribution{...}` (an unnumbered, single-spaced note at the foot of
the current page; place it right after `\chapter` — see
[writing basics](writing.md#chapters-based-on-published-papers)).

`degree-name` does not make the toolkit suitable for undergraduate theses or
other document types; those need their own requirements check.

## Build commands

The helper needs Python 3 (no extra packages) and a LaTeX distribution with
`latexmk`, the chosen engine, and Biber; on Windows, prefer TeX Live, which
includes the Perl that `latexmk` needs. The VS Code recipe in `.vscode/` runs
the same steps ([setup](get-started.md#step-3a-your-computer-route)).

```sh
python3 scripts/build.py --doctor            # check tools, build nothing
python3 scripts/build.py                     # pdfLaTeX → build/main.pdf
python3 scripts/build.py --fresh             # rebuild everything from scratch
python3 scripts/build.py --engine lualatex   # or --engine xelatex
```

After a successful build, the helper also prints non-fatal **pre-submission
hints**: `.bib` entries with a `url` but no `urldate`, and `\caption[...]`
short captions.

The helper ignores personal `latexmkrc` files, disables shell escape, and
creates the output subfolders (`build/chapters/`, …) a first pass needs;
create them yourself if you run `latexmk` with an output directory.

**Engines.** pdfLaTeX uses New TX fonts; LuaLaTeX and XeLaTeX use TeX Gyre
Termes via `fontspec`/`unicode-math`. Switch for characters pdfLaTeX can't
handle, then check glyphs and pagination. Other scripts are untested.

**Partial builds.** After one full build, uncomment the `\includeonly` line in
`preamble.tex` to compile only selected chapters. Comment it out and do a full
build before sharing or submitting.

## Recipes for common extras

Each recipe was compiled with pdfLaTeX, LuaLaTeX, and XeLaTeX in a copy of
the sample. To use one, uncomment its group of lines under "Optional extras"
in `preamble.tex`, add the snippet, compile, and check the pages it changes.
OGE has not reviewed these recipes; where the OGE *Dissertation and Thesis
Manual* says nothing, the [requirements map](project/requirements.md#needs-oge-confirmation)
lists the point under "Needs OGE confirmation".

### Show a figure in parts (a), (b)

Use this when one figure has several panels. Uncomment the `subcaption`
line in `preamble.tex` and replace the file names with your images. The
manual asks for only the letter under each part, all explanation in the main
caption, and the same letter style in every caption (§2.5).

```latex
\begin{figure}[htbp]
  \centering
  \begin{subfigure}{0.45\linewidth}
    \includegraphics[width=\linewidth]{figures/front.png}
    \caption{}\label{fig:sample-front}
  \end{subfigure}\hfill
  \begin{subfigure}{0.45\linewidth}
    \includegraphics[width=\linewidth]{figures/side.png}
    \caption{}\label{fig:sample-side}
  \end{subfigure}
  \caption{Two views of the sample: (a) from the front; (b) from the side.}
  \label{fig:sample}
\end{figure}
```

Each empty `\caption{}` prints only its letter, and `\ref{fig:sample-side}`
prints a number such as "2.1b". Only the main caption appears in the list of
figures.

### Add theorems and proofs

Uncomment the three lines under "Theorems and proofs" in `preamble.tex`.
Theorems and lemmas then share one numbering by chapter (Theorem 2.1,
Lemma 2.2). Displayed equations inside a theorem,
lemma, proof, or algorithm may be unnumbered (§2.7); everywhere else, keep
using `equation`.

```latex
\begin{theorem}\label{thm:sum}
For every integer $n \ge 1$,
\[
  \sum_{k=1}^{n} k = \frac{n(n+1)}{2}.
\]
\end{theorem}
\begin{proof}
Use induction on $n$. \ldots
\end{proof}
```

### Add an algorithm

Uncomment the four lines under "Algorithms" in `preamble.tex`. They number
algorithms by chapter, format
their captions like figure captions (bold, with a colon), and single-space
them. Algorithms are numbered on their own and do not appear in the lists of
tables or figures.

```latex
\begin{algorithm}[htbp]
  \caption{Euclid's algorithm for the greatest common divisor.}
  \label{alg:euclid}
  \begin{algorithmic}[1]
    \Function{Gcd}{$a, b$}
      \While{$b \neq 0$}
        \State $(a, b) \gets (b, a \bmod b)$
      \EndWhile
      \State \Return $a$
    \EndFunction
  \end{algorithmic}
\end{algorithm}
```

### Add code to an appendix

Uncomment the four lines under "Code listings" in `preamble.tex`, then put
the snippet in an appendix file, such as `appendices/additional-material.tex`.
Code is single spaced, in a typewriter font, with the caption above and long
lines wrapped inside the margins. Keep code black: do not add colored syntax
styles (§2.1).

```latex
\begin{lstlisting}[language=Python,
    caption={A Python function that computes the mean of a list of numbers.},
    label={lst:mean}]
def mean(values):
    return sum(values) / len(values)
\end{lstlisting}
```

For a whole file, save it in a `code/` folder and use
`\lstinputlisting[language=Python,caption={...}]{code/analysis.py}`. The
checklist asks for one font throughout; if OGE asks you to avoid the
typewriter font, change `\ttfamily` to `\rmfamily` in `preamble.tex` and add
`columns=fullflexible,keepspaces=true` to the second `\lstset` line.

### Add a list of symbols or abbreviations

The manual calls this optional section a nomenclature (§1.6): it goes after
the list of figures and before any preface or acknowledgment, appears in the
contents, and is formatted like the lists of tables and figures. Another
title, such as LIST OF ABBREVIATIONS, is a point to confirm with OGE.

1. Uncomment the `longtable` line in `preamble.tex`.
2. Create `frontmatter/nomenclature.tex` with the snippet below, one row per
   entry in the order you choose. `\\[10pt]` leaves the same space between
   entries as in the lists of tables and figures; the last row has none.
3. In `main.tex`, add `\input{frontmatter/nomenclature}` below the comment
   about optional sections, before the acknowledgments.

```latex
\frontchapter{NOMENCLATURE}
\begin{longtable}{@{}p{1in}p{5.3in}@{}}
$c$   & Speed of light in vacuum \\[10pt]
$k_B$ & Boltzmann constant \\[10pt]
FEM   & Finite element method \\
\end{longtable}
```

Packages that sort entries for you, such as `nomencl` or `glossaries`, need
an extra program run that the build helper does not do.

## Not yet covered

Publication-based theses need a dedicated, tested example and are on the
[roadmap](project/maintenance.md#roadmap-and-not-yet-covered). Until then,
you can try the usual LaTeX packages in `preamble.tex`, then check the PDF
against the manual. Want to help add one? See [how to contribute](../CONTRIBUTING.md).

To use a capitalization other than capitals for level-1 titles, redefine the
built-in names in `preamble.tex` (`\renewcommand{\contentsname}{Contents}`,
likewise `\listtablename`, `\listfigurename`, and `\appendicesname`), change
`title={REFERENCES}` in `main.tex`, and match every chapter, appendix, and
front-matter title (OGE manual §2.3).

The PDF is not validated as tagged or PDF/UA accessible. Use descriptive
captions, meaningful headings, and legible figures.
