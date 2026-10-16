# Change log

What changed for you in each version, newest first. Your version is in the
`\ProvidesClass` line near the top of `rpi-thesis.cls` (and under Creator in
your PDF's document properties). Technical details are in the
[project's pull requests](https://github.com/diyanko/rpi-thesis-toolkit/pulls?q=is%3Apr).

**Changes your PDF?** **Yes** means updating `rpi-thesis.cls` may change how
your thesis looks, including page breaks: recompile and compare every page.
**No** means only the guide, scripts, or examples changed. Before updating,
read [update the formatting safely](docs/going-further.md#update-the-formatting-safely).

## Unreleased

**Changes your PDF?** Only if you use Chicago (`biblatex-chicago`): the
reference list now has one blank line between entries instead of about half
a line, and long web addresses break like in the other styles. Recompile and
compare your reference pages. Other styles do not change.

- **Chicago reference lists get the right spacing.** The class now applies
  its reference-list spacing after `biblatex-chicago` has set its own. A
  spacing line of your own below the biblatex line still wins.
- **Correction to 0.4.0:** it said "Changes your PDF? No". That held if you
  kept your older `preamble.tex`, but with Chicago and a `preamble.tex` from
  0.4.0 or later, the reference list had about half a blank line between
  entries, not the one blank line OGE asks for. This version fixes it.
- **Use just the class** recipe numbers references in the order you cite
  them, like the starter; it listed them alphabetically before.
- `\yen` works with pdfLaTeX, like every other `amssymb` symbol.
- `LICENSE.md` in both downloads linked a credits file the download does not
  include; such links now point to the project's online copy.

## 0.5.0 (beta), 16 Oct 2026

Published as the pre-release `v0.5.0`.

**Changes your PDF?** No.

- **A shorter guide:** eight pages instead of eleven. "Why LaTeX" is now part
  of [How it works](docs/how-it-works.md); the workflows and advanced pages
  are one page, [Going further](docs/going-further.md). Old guide addresses
  no longer work.
- **Before 1.0, anything may move.** Updating is still usually just the class
  file, but a version may rename a setting or need another file changed; this
  log says so when it does. The one-file promise starts at 1.0.

## 0.4.0 (beta), 16 Oct 2026

Published as the pre-release `v0.4.0`.

**Changes your PDF?** No.

- **Updating is one file:** download the newest `rpi-thesis.cls` from its
  permanent link, replace yours (on Overleaf: Upload), and recompile.
- **Know your version:** every compile log starts with the class version and
  where the newest one lives.
- **Use just the class** in a LaTeX project you already have: a short recipe
  on the Bring your draft page.
- Reference-list spacing moved from `preamble.tex` into the class; an older
  `preamble.tex` that still sets it keeps working.

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
