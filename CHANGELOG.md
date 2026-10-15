# Change log

What changed for you in each version, newest first. Your version is in the
`\ProvidesClass` line near the top of `rpi-thesis.cls` (and under Creator in
your PDF's document properties). Technical details are in the
[project's pull requests](https://github.com/diyanko/rpi-thesis-toolkit/pulls?q=is%3Apr).

**Changes your PDF?** **Yes** means updating `rpi-thesis.cls` may change how
your thesis looks, including page breaks: recompile and compare every page.
**No** means only the guide, scripts, or examples changed. Before updating,
read [update the formatting safely](docs/workflows.md#update-the-formatting-safely).

## 0.3.0 (beta), 15 Oct 2026

Published as the pre-release `v0.3.0`.

**Changes your PDF?** Only if you use LuaLaTeX or XeLaTeX with AMS math
commands such as `\square` or `\nleqslant`: they now compile. Recompile and
compare; nothing else in the layout changed.

**If you started with 0.2.0,** copy the new `rpi-thesis.cls` (and, if you use
it, `scripts/build.py`) into your project.

- **Search the guide:** one search button finds sections, tasks, and pasted
  error messages, even with typos. It works offline too.
- **AMS math works on every engine,** including LuaLaTeX and XeLaTeX.
- **A sharper build helper:** it spots missing chapters (even with spaces in
  their names), multi-line error messages, and tools that will not start.
- **Smoother moves:** from Overleaf to your computer, from Markdown drafts,
  and when comparing two versions of your thesis.
- **The offline guide** links to the project files of its own release.

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
