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
  `assets/rpi-seal.jpg`; until then a same-size placeholder shows where it goes.
- One-inch margins, double spacing, Roman then Arabic page numbers placed
  0.75 in from the edge, capitalized level-1 titles, and contents and lists
  that use your full captions.
- Single-spaced captions, footnotes, long and rotated tables, and references,
  with references placed before the appendices.
- A `\chapterattribution{...}` command for chapters based on published papers.
- Clear errors that name the file and the fix, for example for a missing
  chair or an unknown degree.
- `amsthm` (theorems and proofs) loads with one `\usepackage{amsthm}` line on
  every engine; the class handles the clash with the pdfLaTeX math font.

**The starter:** sample front matter, three short chapters with figure,
table, equation, citation, and reproduced-figure examples, an appendix, a
`references.bib` with an access-dated web source, VS Code settings with the
recipe **RPI Thesis Toolkit: pdfLaTeX + Biber**, and a build helper
(`scripts/build.py`) that also prints pre-submission hints. `preamble.tex`
holds commented-out package lines for the
[recipes for common extras](docs/advanced.md#recipes-for-common-extras):
figures in parts, theorems and proofs, algorithms, code listings, and a list
of symbols or abbreviations, each tested with pdfLaTeX, LuaLaTeX, and XeLaTeX.

**The guide:** nine pages in four stages (start, write, fix and finish, go
further), an offline copy in the starter ZIP, and a one-page printable cheat
sheet.

**Tested so far** on macOS with TeX Live: master's, PhD, and DEng title pages,
a large committee, a minimal document, and the LuaLaTeX and XeLaTeX engines;
PDF checks of page numbering, contents, captions, and reference order; TeXShop
and the build helper. **Not yet tested end to end:** Overleaf upload, VS Code
and TeXstudio, and fresh installs on Windows and Linux. OGE has not reviewed
this version.
