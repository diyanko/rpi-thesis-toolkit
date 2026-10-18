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

**Changes your PDF?** No.

- **One set of fixes for every error message:** Fixing problems, Explain my
  error, and the optional build helper now give the same advice from one
  list. Explain my error and the build helper also recognize the starter's
  own messages (such as a missing setting, an unknown degree or month, or a
  missing seal), and each fix says what to do on your computer and on
  Overleaf where they differ.

## 0.9.0 (beta), 17 Oct 2026

Published as the pre-release `v0.9.0`.

**Changes your PDF?** No.

**Version:** minor

- **Five tools, one design:** every tool page has the same layout, a clear
  "Nothing is uploaded" line, and short results; the home page lists them all.
  On a laptop or desktop the tool pages use the full width, LaTeX in the
  guide and in tool output is colored for easier reading, and form fields,
  checkboxes, and yes/no switches match the site's hand-drawn style.

- **Settings builder:** fill in a form and copy a checked `\thesissetup` block
  for `metadata.tex`; it rejects the same values the class rejects.
- **Bring your work in:** a new tool in the guide's Tools group. Paste text
  from Word, Google Docs, or Markdown, or a table from Excel or Sheets, and
  get LaTeX ready for a chapter: headings, emphasis, lists, links, special
  characters, and tables with a caption. It runs in your browser; nothing is
  uploaded.
- **Check your references:** paste or drop `references.bib`; it reads your
  citation style and lists missing fields, access dates, duplicate keys, name
  and capitalization problems, each with the fix.
- **Explain my error:** paste an error or a whole log from your editor or
  Overleaf; it finds the first real error, says what it means, and shows the
  fix and the guide section. Same knowledge as the build helper.

## 0.8.1 (beta), 17 Oct 2026

Published as the pre-release `v0.8.1`.

**Changes your PDF?** No.

- **A shorter home page:** one line about what the toolkit does, buttons to
  download the starter or open it in Overleaf right under it, one drawing of
  what you get, and a "What's here" overview of every part of the toolkit.
- **A cleaner footer** on every page, grouped by Guide, Tools, Project, and
  Help; "Suggest a change" needs no account.
- **Share this guide** copies the link (or opens your phone's share sheet).
- Refined colors in light and dark; numbers in the text show a plain 0.
- **Get started** suggests an editor on your computer that compiles when you
  save (VS Code with LaTeX Workshop as the worked example; other editors with a
  LaTeX extension work too), with Overleaf as the no-install alternative.
  Terminal commands moved to Going further; no step needs them.
- The VS Code settings in the download build on save, open the PDF beside your
  text, and keep the Problems list to text that runs into the margin.

## 0.8.0 (beta), 17 Oct 2026

Published as the pre-release `v0.8.0`.

**Changes your PDF?** Yes, in two places: the space around displayed
equations, and the contents if your sections go four levels deep. Recompile
and look at pages with displayed equations and at the contents.

- **Displayed equations** no longer get double space around them: about
  20 pt above instead of 33, as RPI's template sets it.
- **Deep section numbers** such as 12.10.10.10 no longer touch their titles
  in the contents.
- **Clearer errors:** a misspelled setting names the setting and
  `metadata.tex`; a wrong degree, month, or chair value echoes what you wrote
  and notes that values are case-sensitive; a seal file name with `_` no longer
  stops the compile.
- **The build helper** shows the first real error and its line, and explains
  missing figures and undefined citations or references.
- **Website:**
  - the appearance menu works in Safari and on iPhone;
  - Check your PDF falls back to its written checklist on older browsers;
  - controls have clearer borders in light mode;
  - guide pages print more cleanly.

## 0.7.1 (beta), 16 Oct 2026

Published as the pre-release `v0.7.1`.

**Changes your PDF?** No.

- **Check your PDF** works without contacting any other site, says "Could
  not tell" instead of passing anything it could not measure, adds checks for
  page size, headings missing from the contents, embedded fonts, blank pages,
  and file size, and can print its result. In the offline guide it points to
  the website, because browsers block it on local files.
- **One wording per rule:** guide pages quote and cite OGE rules from the
  requirements map, so a rule and its manual page are written once.
- **Pictures:** the timeline shows Check your PDF and the reviewer
  checklist, diagrams use `\parencite` and "compile" throughout, sample-PDF
  close-ups have captions, and an unused diagram is gone.
- **Sidebar and layout:** optional pages have their own marker in the same
  column as the numbers; list numbers, focus rings, footer links, and search
  highlights are tidier.
- **Starter comments** name guide pages instead of files the download does
  not include; the appendix example uses `\parencite`.
- **Build helper:** a missing chapter whose name has accents or non-Latin
  letters is reported with its full name; local classes and packages in
  subfolders, and the files they load, are followed; missing characters and a
  missing STIX Two Math font are named.
- **Check your PDF** reads chapter headings with a "CHAPTER 1" line above the
  title, headings that wrap differently in the contents, contents pages that
  start mid-entry, superscripts in headings, and PDFs with an unusual page
  unit. Small differences from the manual's numbers (page-number distance,
  slight margin overruns, a heading a little low) get their own result,
  "Differs from the manual's wording", separate from "Look at this". A check
  can be cancelled, and choosing another PDF replaces the old result.

## 0.7.0 (beta), 16 Oct 2026

Published as the pre-release `v0.7.0`.

**Changes your PDF?** Only if you compile with LuaLaTeX or XeLaTeX and use
one of the 24 AMS symbols listed below: they printed as blank space before
and now appear. Recompile and check the pages that use them. pdfLaTeX does
not change.

- **AMS symbols no longer print blank on LuaLaTeX and XeLaTeX.** The math
  font lacks `\bigstar`, `\Finv`, `\Game`, `\digamma`, `\backepsilon`,
  `\pitchfork`, `\Join`, `\doublebarwedge`, `\blacktriangle`,
  `\vartriangle`, `\blacktriangledown`, `\triangledown`, `\diagup`,
  `\diagdown`, `\precneqq`, `\succneqq`, `\precapprox`, `\succapprox`,
  `\precnapprox`, `\succnapprox`, `\subseteqq`, `\supseteqq`,
  `\subsetneqq`, and `\supsetneqq`. The class now takes just these from
  STIX Two Math, a Times-style math font included in TeX Live and Overleaf.
- **Check your PDF:** a new optional guide page,
  [Check your PDF](docs/check-pdf.md), reads your PDF in your browser (it is
  never uploaded) and reports paper size, page numbering and its position,
  level-1 heading position, side margins, contents entries, and the toolkit
  version, each with the manual section it comes from. It is not an OGE
  review.
- **Reviewer checklist:** a two-page [checklist](docs/reviewer-checklist.md)
  for advisors, committee members, and OGE reviewers: what the class sets,
  what still needs a look, and where students record exceptions. Guide pages
  with long tables now print without a blank half page.
- **Search** understands more words (acronyms, landscape, glossary, Mendeley)
  and pasted LaTeX warnings, highlights what matched, and opens with `/`.
- **AI prompts to copy** for setting up, fixing an error, converting to
  LaTeX, and suggesting a change: [Going further](docs/going-further.md#prompts-to-copy).

## 0.6.0 (beta), 16 Oct 2026

Published as the pre-release `v0.6.0`.

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
