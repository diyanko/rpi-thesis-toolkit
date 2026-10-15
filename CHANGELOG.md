# Change log

What changed for you in each version, newest first. Your version is in the
`\ProvidesClass` line near the top of `rpi-thesis.cls` (and under Creator in
your PDF's document properties). Technical details are in the
[project's pull requests](https://github.com/diyanko/rpi-thesis-toolkit/pulls?q=is%3Apr).

**Changes your PDF?** **Yes** means updating `rpi-thesis.cls` may change how
your thesis looks, including page breaks: recompile and compare every page.
**No** means only the guide, scripts, or examples changed. Before updating,
read [update the formatting safely](docs/workflows.md#update-the-formatting-safely).

## Unreleased

**Changes your PDF?** Yes, for LuaLaTeX and XeLaTeX documents using AMS math
commands that previously failed to compile, such as `\square` and
`\nleqslant`. The font settings are unchanged; recompile and compare your PDF.

- Restore conventional AMS math commands when using LuaLaTeX or XeLaTeX.
- The build helper detects missing chapters whose names contain spaces and
  reads compiler messages that wrap over several lines. It reads multiline
  imports, distinguishes inactive chapters from deleted sources on cached
  builds, and reports tools that cannot start. ZIP checks also detect missing
  filenames with spaces; packaging refuses linked source folders as well as
  linked files and checks the guide address before replacing either ZIP.
- Comparison PDFs keep corrected bibliography details while retaining
  deleted references. The slide-export recipe names the heading level that
  starts each slide, and the citation guide clarifies manual Overleaf uploads.
- Moving from Overleaf restores missing desktop helpers. Manual Markdown
  imports keep one chapter heading and preserve citation punctuation.
  Setup and troubleshooting direct old LaTeX installations to an update;
  the fresh-machine workflow uses supported distribution packages.
- Website caption help agrees with the writing guide, and the link checker
  checks home and directory links without crashing. Encoded asset filenames
  keep their meaning. Website builds refuse linked input folders and hold an
  operating-system lock that is released when the process exits.
- Search guide sections and individual common messages by question, topic,
  command, or pasted error, including common spelling mistakes. Search works
  in the website and the offline guide, with keyboard controls and one
  search button beside the appearance switch. The task links remain
  available without JavaScript. Pasted logs use their first error, brace and
  dollar-sign errors stay distinct, and results open matching optional examples.

## 0.2.0 (beta), 15 Oct 2026

Published as the pre-release `v0.2.0`.

**Changes your PDF?** No visible change.

**If you started with 0.1.0,** make one edit: in `main.tex`, replace the three
lines from `\begin{singlespace}` to `\end{singlespace}` with
`\thesisreferences`, and copy the new `latexmkrc` next to `main.tex`.

- **Easier starter files.** One line prints the reference list; `metadata.tex`
  groups its settings with short tips; the class is laid out in 13 labelled
  sections that cite the OGE manual.
- **The first compile works from a fresh download** in VS Code and other
  editors that run latexmk (a new `latexmkrc` creates the output folders);
  VS Code also offers XeLaTeX and LuaLaTeX recipes and remembers your choice.
- **Warnings that help.** LaTeX warns when your class file is older than your
  other files or a committee name is blank; the build helper flags malformed
  access dates, figures too tall for the page, and missing chapters.
- **Clearer citations.** Which command gives "(Lamport, 1994)", how to write
  several authors or an organization, and full credits tested in each listed
  style (MLA needs a one-line fix; see the citations page).
- **A shorter, friendlier guide** with a no-terminal clean recompile, a
  chapter skeleton, and commands checked for Windows, macOS, and Linux.
- **Website:** readable tables on phones, sharper pictures, smooth diagram
  lines, and a dark mode switch.

## 0.1.0 (beta), 14 Oct 2026

Published as the pre-release `v0.1.0`. **Changes your PDF?** Not
applicable: the first version.

- **The class** follows the OGE *Dissertation and Thesis Manual* and RPI's
  official LaTeX template (every rule and difference is in the
  [requirements map](docs/project/requirements.md)): title page from
  `metadata.tex` for master's, PhD, and DEng; one-inch margins, double
  spacing, page numbers 0.75 in from the edge; contents and lists from your
  full captions; single-spaced captions, footnotes, and references; chapter
  attributions; and errors that name the fix. The RPI seal is a separate
  download; a same-size placeholder holds its place.
- **The starter:** a doctoral dissertation by default, with sample front
  matter, three short chapters of copyable examples, an appendix, an
  access-dated web source, VS Code settings, an optional build helper, and
  tested recipes for theorems, algorithms, code, figure parts, and symbol
  lists.
- **The guide:** eleven pages in four stages, an offline copy in the ZIP, and
  a printable cheat sheet. The website works without JavaScript.
- **Tested:** fresh Windows, macOS, and Ubuntu machines (compiler only);
  Overleaf's free plan; all degree types and the LuaLaTeX and XeLaTeX engines;
  VS Code with LaTeX Workshop and TeXShop. **Not yet tested:** TeXstudio,
  TeXworks, and a full real thesis. OGE has not reviewed this version.
