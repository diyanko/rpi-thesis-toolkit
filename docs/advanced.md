# Advanced use

For anyone who wants more control. Nothing here is needed to write your
thesis or dissertation. If the sample doesn't compile yet, start with
[get started](get-started.md).

## Where customizations belong

| You want to change… | Edit | Notes |
| --- | --- | --- |
| Details shown on the title page | `metadata.tex` | Every setting is in the table below |
| Document order, chapters, optional sections | `main.tex` | References stay before appendices |
| Packages and citation style | `preamble.tex` | Loaded after the class |
| Formatting rules | `rpi-thesis.cls` | Avoid: [updating the class](workflows.md#update-the-formatting-safely) overwrites edits. Check [the requirements map](project/requirements.md) first |

Extra geometry, spacing, caption, or heading packages in `preamble.tex` can
silently break a requirement; prefer the documented settings. Also:

- **Class options are rejected.** `\documentclass[11pt]{rpi-thesis}` stops with
  "Unsupported class option". The class always uses 12pt, US letter, one-sided.
- **hyperref is already loaded** by the class (with `hidelinks,unicode`). Don't
  load it again; use `\hypersetup{...}` in `preamble.tex`. Packages that must
  load *before* hyperref need a class change.

## All thesis settings

Settings go inside `\thesissetup{...}` in `metadata.tex`.

| Key | Values | Notes |
| --- | --- | --- |
| `title` | text, required | Printed in capitals |
| `author` | text, required | |
| `degree` | `doctoral` (default), `masters`, `engineering-doctorate` | Doctor of Philosophy, Master of Science, Doctor of Engineering |
| `degree-name` | text (default: from `degree`) | Overrides the degree name shown; put it **after** `degree` |
| `department` | text, required | Full name, e.g. `Department of Physics, Applied Physics and Astronomy` |
| `graduation-month` | `May`, `August`, `December`; required | Graduation month, not submission month |
| `graduation-year` | four digits, required | |
| `seal-file` | file path (default: `assets/rpi-seal.jpg`) | Download the seal from RPI ([add the RPI seal](get-started.md#add-the-rpi-seal-one-minute)). If missing, `assets/rpi-seal.png` is tried, then a placeholder box with a warning |
| `copyright-page` | `true`, `false` (default) | Adds the copyright page (ii) |
| `list-of-tables` | `true` (default), `false` | `false` only if you have no tables |
| `list-of-figures` | `true` (default), `false` | `false` only if you have no figures |

List committee members outside `\thesissetup`, one per line, in order:

- `\committeemember[Chair]{Name}` or `\committeemember[Co-Chair]{Name}`: at
  least one is required.
- `\committeemember{Name}` for everyone else. Text in the optional brackets
  prints after the name, following a comma.

There is no fixed committee size. Check the title page with long titles,
department names, or large committees.

Other class commands:

- `\frontchapter{Title}`: an unnumbered front-matter section listed in the
  contents.
- `\thesisfrontmatter`: copyright page, contents, and lists.
- `\thesismainmatter`: switches to Arabic page 1.
- `\chapterattribution{...}`: an unnumbered note at the foot of the page; place
  it right after `\chapter` (see
  [writing basics](writing.md#chapters-based-on-published-papers)).

`degree-name` does not make the toolkit suitable for undergraduate theses or
other document types; those need their own requirements check.

## Build commands

Overleaf, VS Code (with the recipe in `.vscode/`), and the optional build
helper use `latexmk` to run the engine and Biber as often as needed. For
TeXShop, TeXworks, or TeXstudio, see the
[other-editor compile steps](get-started.md#other-editors-and-the-command-line).

These terminal commands are optional. Run them from the folder containing
`main.tex`: either `latexmk -norc -pdf main.tex` (PDF next to `main.tex`) or
the build helper below. An AI assistant can explain or adapt any command for
your system: give it your operating system and the command or its error
output, then check the result
([more on AI help](workflows.md#use-ai-for-technical-help)).

The helper needs Python 3.9 or newer (no extra packages) and TeX Live 2022 or
newer with `latexmk`, your engine, and Biber. On Windows, prefer TeX Live,
which includes the Perl that `latexmk` needs.

The commands below use `python3`, which works on macOS and Linux. On Windows,
type `py` instead of `python3`: `py scripts/build.py`.

Check the installed tools and see the next steps:

```sh
python3 scripts/build.py --doctor
```

Compile with pdfLaTeX; the PDF goes in `build/main.pdf`:

```sh
python3 scripts/build.py
```

Recompile everything from scratch:

```sh
python3 scripts/build.py --fresh
```

After a successful build, the helper prints non-fatal **pre-submission
hints**: `.bib` entries with a `url` but no `urldate`, and `\caption[...]`
short captions.

The helper ignores personal `latexmkrc` files, disables shell escape, and
creates the output subfolders (`build/chapters/`, …) a first pass needs. If you
type `latexmk -outdir=...` yourself, create those subfolders first, or let
`latexmk` retry after "I can't write on file".

### Choose a compile engine

pdfLaTeX uses New TX fonts; LuaLaTeX and XeLaTeX use TeX Gyre Termes via
`fontspec`/`unicode-math`. Switch for characters pdfLaTeX can't handle, then
check glyphs and pagination. Other scripts are untested.

With the build helper, run this from the folder containing `main.tex` (on
Windows, `py scripts/build.py --engine lualatex`):

```sh
python3 scripts/build.py --engine lualatex
```

For XeLaTeX, replace `lualatex` with `xelatex`.

### Compile selected chapters

After one full compile, uncomment the `\includeonly` line in `preamble.tex`.
Inside its braces, list the chapter files you want, without `.tex`; the
sample line selects `chapters/02-research`. Compile `main.tex` as usual.
Comment out `\includeonly` and compile the whole thesis before sharing or
submitting.

## Recipes for common extras

Each recipe was compiled with pdfLaTeX, LuaLaTeX, and XeLaTeX in a copy of the
sample. To use one, uncomment its lines under "Optional extras" in
`preamble.tex`, add the snippet, compile, and check the pages it changes. OGE
has not reviewed these recipes; where the OGE *Dissertation and Thesis Manual*
says nothing, the [requirements map](project/requirements.md#needs-oge-confirmation)
lists the point under "Needs OGE confirmation".

Pick a task: [parts (a), (b)](#show-a-figure-in-parts-a-b) ·
[theorems and proofs](#add-theorems-and-proofs) ·
[an algorithm](#add-an-algorithm) ·
[code in an appendix](#add-code-to-an-appendix) ·
[a list of symbols](#add-a-list-of-symbols-or-abbreviations)

### Show a figure in parts (a), (b)

For one figure with several panels. Uncomment the `subcaption` line in
`preamble.tex` and use your own image names. The manual asks for only the
letter under each part, all explanation in the main caption, and the same
letter style in every caption (§2.5). Put this in your chapter file:

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

*Caveat:* the manual does not specify theorem formatting; see the
[requirements map](project/requirements.md#needs-oge-confirmation).

Uncomment the three lines under "Theorems and proofs" in `preamble.tex`.
Theorems and lemmas then share one numbering by chapter (Theorem 2.1,
Lemma 2.2). Displayed equations inside a theorem, lemma, proof, or algorithm
may be unnumbered (§2.7); elsewhere, keep using `equation`. Put this in your chapter file:

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

*Caveat:* the manual does not mention algorithm format; see the
[requirements map](project/requirements.md#needs-oge-confirmation).

Uncomment the four lines under "Algorithms" in `preamble.tex`. They number
algorithms by chapter, format their captions like figure captions (bold, with
a colon), and single-space them. Algorithms have their own numbering and do
not appear in the lists of tables or figures.

Put this in your chapter file:

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

*Caveat:* the manual does not mention code listings and the typewriter font
is unconfirmed; see the
[requirements map](project/requirements.md#needs-oge-confirmation).

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
checklist asks for one font throughout. If OGE asks you to avoid the
typewriter font, change `\ttfamily` to `\rmfamily` in `preamble.tex` and add
`columns=fullflexible,keepspaces=true` to the second `\lstset` line.

### Add a list of symbols or abbreviations

The manual calls this optional section a nomenclature (§1.6). It goes after the
list of figures and before any preface or acknowledgment, appears in the
contents, and is formatted like the lists of tables and figures. Another title,
such as LIST OF ABBREVIATIONS, is a point to confirm with OGE.

1. Uncomment the `longtable` line in `preamble.tex`.
2. Create `frontmatter/nomenclature.tex` with the snippet below, one row per
   entry in the order you choose. `\\[10pt]` matches the spacing in the lists
   of tables and figures; the last row has none.
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

Packages that sort entries for you, such as `nomencl` or `glossaries`, need an
extra program run that the build helper does not do.

## Not yet covered

Publication-based theses need a dedicated, tested example and are on the
[roadmap](project/maintenance.md#roadmap-and-not-yet-covered). Until then,
try the usual LaTeX packages in `preamble.tex` and check the PDF against the
manual. Want to help add one? See [how to contribute](../CONTRIBUTING.md).

To use a capitalization other than capitals for level-1 titles, redefine the
built-in names in `preamble.tex` (`\renewcommand{\contentsname}{Contents}`,
likewise `\listtablename`, `\listfigurename`, and `\appendicesname`), add
`\renewcommand{\referencesname}{References}` (or your chosen capitalization),
and match every chapter, appendix, and
front-matter title (OGE manual §2.3).

The PDF is not validated as tagged or PDF/UA accessible. Use descriptive
captions, meaningful headings, and legible figures.
