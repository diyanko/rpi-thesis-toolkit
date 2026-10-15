# Change log

What changed in each version of the RPI Thesis Toolkit, newest first. Your
version is in the `\ProvidesClass` line near the top of `rpi-thesis.cls`.

Every entry starts with **Changes your PDF?**

- **Yes:** updating `rpi-thesis.cls` may change how an existing thesis looks,
  including page breaks and page numbers. Recompile and compare every page.
- **No:** only the guide, scripts, or examples changed. Your PDF stays the same.

Before an update, read [update the formatting safely](docs/workflows.md#update-the-formatting-safely).

## 0.1.0, unreleased

**Changes your PDF?** Not applicable: this is the first version.

The first public version of an unofficial, community-made starter for RPI
master's theses and doctoral dissertations (PhD and DEng). It is not
affiliated with or endorsed by RPI or its Office of Graduate Education (OGE),
and it includes no RPI-owned files.

**The class (`rpi-thesis.cls`)** follows the OGE *Dissertation and Thesis
Manual* and RPI's official LaTeX template; each rule and each difference is
recorded in the [requirements map](docs/project/requirements.md).

- Title page from the settings in `metadata.tex`: degree wording for master's,
  PhD, and DEng; committee with chair or co-chair; bracketed graduation date;
  optional copyright page. It uses the seal you download from RPI and save as
  `assets/rpi-seal.jpg` (or `.png`); until then a same-size placeholder shows
  where it goes, and adding the seal later triggers an ordinary rebuild.
- One-inch margins, double spacing, Roman then Arabic page numbers placed
  0.75 in from the edge, capitalized level-1 titles, and contents and lists
  that use your full captions.
- Single-spaced captions, footnotes, long and rotated tables, and references,
  with references placed before the appendices.
- A `\chapterattribution{...}` command for chapters based on published papers.
- Clear errors that name the file and the fix, for example for a missing
  chair or an unknown degree.
- `amsthm` (theorems and proofs) loads with one `\usepackage{amsthm}` line on
  every engine; the class handles the clash with the pdfLaTeX math font. A
  pasted `\usepackage{amssymb}` or `amsfonts` is harmless: the class's math
  fonts already provide those symbols.

**The starter:** set up as a doctoral dissertation by default (change one setting for a master's thesis or DEng), with sample front matter, three short chapters with copyable
examples (a real figure with `\includegraphics`, a table, inline and numbered
equations, citations, special characters, and a reproduced-figure caption), an appendix, a
`references.bib` with an access-dated web source, VS Code settings with the
recipe **RPI Thesis Toolkit: pdfLaTeX + Biber**, and a build helper
(`scripts/build.py`) that follows only the files `main.tex` uses, reports
missing files with their line, and prints pre-submission hints. `preamble.tex`
holds commented-out package lines for the
[recipes for common extras](docs/advanced.md#recipes-for-common-extras):
figures in parts, theorems and proofs, algorithms, code listings, and a list
of symbols or abbreviations, each tested with pdfLaTeX, LuaLaTeX, and XeLaTeX.

**The guide:** eleven pages in four stages (start, write, fix and finish, go
further), an offline copy in the starter ZIP, and a one-page printable cheat
sheet. *Why LaTeX for your thesis?* explains what LaTeX does for you and what
it costs; *How do I…?* links common tasks to the sections that answer them;
*Writing basics* opens with the ten commands most theses use; and new
diagrams show what updates automatically, a moved chapter renumbering
itself, how to read a `.tex` file, and what to do when a compile stops.
*Writing basics* walks through adding a figure, editing a table, citing a
source, and numbered equations; the citations page explains how floating
figures can affect numbered citation order; the guide recommends a private
repository (never a public fork) for a thesis on GitHub, notes that a paper
you wrote alone needs a chapter attribution but no Declaration of
Co-Contribution, and describes optional AI help for technical LaTeX problems.

**Tested so far:** on fresh Windows 11, macOS, and Ubuntu 22.04 and 24.04
machines, installing TeX as the guide describes and compiling the starter;
on Overleaf's free plan, opening and compiling the starter; on macOS, the
master's, PhD, and DEng title pages, a large committee, a minimal document,
the LuaLaTeX and XeLaTeX engines, PDF checks of page numbering, contents,
captions, and reference order, VS Code with LaTeX Workshop, TeXShop, and the
build helper. **Not yet tested:** TeXstudio and TeXworks, and a full real
thesis by a student. OGE has not reviewed this version.
