# Formatting requirements and implementation

Baseline checked: **14 Oct 2026**. Sources (versions and fingerprints in
[sources.json](sources.json)): *Dissertation and Thesis Manual 2026* (PDF and
Word version; same text), the September 2025 *Thesis/Dissertation Formatting
Checklist* (**FC**), master's and doctoral checklists, *LaTeX Formatting Tips
& Tricks* (**LT**, Sep 2025), and the Fall 2026 preparation workshop. The
[OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation)
is the primary entry point.

This is a requirements map for an unofficial, community-made class; it is
not a claim of OGE approval. Page numbers are **printed manual pages**
(printed p. 1 = PDF p. 10). RPI's official LaTeX template (available from
RPI ITS's [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation))
is the baseline: this independent class follows its formatting except where
a difference below is justified by the manual or fixes a clear bug in RPI's
template. No RPI files are included in this project; maintainers compare
against a local copy in `_local/legacy/`.

Implementation names a macro, key, package, or section comment in
`rpi-thesis.cls` unless another file is given; search the class for it.

Verification: **check** = assertion in `scripts/check.py`; **visual** =
rendered page compared with the manual's sample and the output of RPI's
official template;
**student** = cannot be automated.

## Requirements map

| Requirement | Source | Implementation | Verification |
| --- | --- | --- | --- |
| US letter, 1 in margins on every page | §2.2 p. 16; FC | `geometry` options | check (paper size); visual |
| Level-1 headings start at the top margin, not lower | §2.2; LT ("known glitch") | `\titleformat{\chapter}` | check (heading baseline 84 pt on every opening page) |
| Front matter lowercase Roman; title is i, unnumbered; next page ii | §1.1 p. 1; FC | `\maketitle` (`\pagenumbering{roman}`) | check |
| Body Arabic from 1 on the first page of Chapter 1 | §2.2 p. 16 | `\thesismainmatter` | check |
| Page numbers 0.75 in from the edge; bottom center on front matter and on the first page of each chapter, references, appendix; top right elsewhere | §2.2 pp. 16-17; FC | `geometry` options; `\ps@rpibody`; `\pagestyle{plain}` | check (position on every page) |
| Same font for text and page numbers; text ≥ 10 pt (12 pt Times-like) | §2.1 p. 16; FC | `newtxtext` (pdfLaTeX), `\setmainfont` (LuaLaTeX, XeLaTeX); `\ps@rpibody` | visual; fonts embedded (pdfTeX default) |
| All text black, including URLs and links | §2.1 p. 16; §1.3 p. 4; FC | `hyperref` option `hidelinks` | visual |
| URLs in the text font | FC ("same font throughout") | `\urlstyle{same}` | visual |
| Body double spaced (≤ 4 lines/in) | §2.1 p. 16; FC | `\doublespacing` | visual |
| Single spaced: captions, footnotes, block quotes, chapter attributions; references single with a blank line between | §2.1 p. 16 | `\AtBeginEnvironment` (`\singlespacing`), `\chapterattribution`; `main.tex` `singlespace`; `preamble.tex` `\bibitemsep` | visual (stress test incl. longtable and rotated table) |
| Title page: title caps bold; name bold; degree caps italic; "Approved by:"; names single spaced with ", Chair"; department italic; RPI, Troy, New York; [Month Year]; seal | §1.1 pp. 1-2; FC | `\maketitle`, seal box `\rpi_seal:` and `\rpi_seal_placeholder:`; `metadata.tex`; seal downloaded by the student (`assets/README.md`) | check (degree, date, placeholder exactly when the seal is absent); visual |
| Degree wording: Master of Science / Doctor of Philosophy / Doctor of Engineering | §1.1 p. 1 | `\thesissetup` key `degree` | check (three degree cases) |
| Graduation month only May, August, December; four-digit year; chair present | §1.1 p. 1 | `\thesissetup` key `graduation-month`; `\rpi_validate:` | check (rejections) |
| Full department name | §1.1 p. 1 | `metadata.tex` comment | student |
| Copyright page optional; page ii; "© year / By / Name / All rights reserved" | §1.2 p. 3; FC | `\thesisfrontmatter` (key `copyright-page`) | check (page ii, text) |
| Front-matter order: title, copyright, contents, tables, figures, (nomenclature), preface/acknowledgment, abstract | Table 1.1 p. 15; FC | `\thesisfrontmatter`; `main.tex` | check (order) |
| Contents lists all front matter except title, copyright, itself; all chapters, sections, references, appendices; plain weight; numbers right aligned; text clear of number column | §1.3 p. 4; FC | section comment "Contents and lists (tocloft)"; `\frontchapter` | check (entries); stress test to 12.10.10.10 |
| Contents entries identical to body headings | §1.3 p. 4 | `\cftchapaftersnum` ("1." and "A.") | check |
| Lists of tables/figures when present; full caption; entries separated by a space; appendix objects included | §§1.4-1.5 pp. 7-10; FC | section comment "Contents and lists (tocloft)"; `\thesisfrontmatter` (`\listoftables`, `\listoffigures`); `build.py` short-caption hint | check (full captions); visual |
| Nomenclature/list of equations optional, after lists, in contents, formatted like the lists | §1.6 p. 13; FC | `main.tex` comment; `\frontchapter`; recipe in `docs/advanced.md` (`longtable`, single spaced by the class, 10 pt between entries like the lists) | visual (recipe, three engines); student |
| Abstract required; no length limit; no figures, references, attributions | §1.8 p. 14 | `frontmatter/abstract.tex` | student |
| Level-1 titles formatted alike in body and contents; levels 2-4 one case; every level distinct; none smaller than text | §2.3 pp. 17-18; FC | section comment "Headings follow RPI's original thesis.cls"; level 4 italic `\titleformat{\subsubsection}` | visual; student (case) |
| Tables/figures centered; table captions above, figure captions below; bold; one alignment; colon delimiter; chapter numbering with periods; no color | §§2.4-2.5 pp. 18-22; FC | `\captionsetup`; sample floats | visual |
| Landscape table: caption "above" (left); page number placement | §2.4 p. 19, Fig. 2.4 | `rotating` `sidewaystable`; top-right number stays in place | visual (stress test); see confirmation list |
| Reproduced tables/figures: full citation and permission or license wording in caption | §2.6 pp. 24-25 | `chapters/02-research.tex` example | student |
| Equations centered, numbered right in parentheses, multi-line number centered, every display numbered | §2.7 pp. 26-27; FC | amsmath defaults; sample `split` | visual; student |
| Displays inside a lemma, algorithm, theorem, or proof may be unnumbered | §2.7 p. 27 | theorem and algorithm recipes in `docs/advanced.md` (`amsthm`, `algorithm`, `algpseudocode`; lines commented out in `preamble.tex`); `package/amsthm/before` hook lets `amsthm` load after `newtxmath` (pdfLaTeX) | visual (recipe, three engines) |
| Lettered figure parts: only the letter in the figure, explanation in the caption, one letter style throughout | §2.5 pp. 22-23 | subfigure recipe in `docs/advanced.md` (`subcaption`, empty sub-captions print "(a)"); only the main caption enters the list of figures | visual (recipe, three engines); student (letter style) |
| Chapter attribution at the bottom of the chapter's first page, no mark, single spaced, citation style; wording per Table 2.1 | §2.8 pp. 27-29; FC | `\chapterattribution`; wording in `chapters/02-research.tex` comment | check (unmarked, first page) |
| Reused work needs a chapter attribution even when the student is the sole author; the Declaration of Co-Contribution lists every attributed article except sole-authored ones | §2.8.1 p. 28 | `docs/writing.md` ("Chapters based on published papers"), `docs/submission.md`; `chapters/02-research.tex` comment | student |
| Citation style suited to the field, checked against the official guide | §3.2 pp. 32-34 | style isolated in `preamble.tex` | student |
| In-text citations follow the chosen style; sequential numbers for styles such as IEEE, non-sequential numbers for SIAM (alphabetical list), author-year for APA | §3.3 p. 34 | style isolated in `preamble.tex`; `docs/citations.md` ("Numbered styles: check delayed figures and tables") | student |
| Sequential numbered styles: reference 1 is the first citation in Chapter 1; a caption's citation numbered where its table or figure appears in the body, not in the front matter | FC (does not apply to non-sequential styles such as SIAM, §3.3 p. 34) | Sample uses `sorting=none`: numbers follow source order, so a float placed on a later page can carry a lower number than nearby text (tested); list-of-figures citations do not affect numbering (tested); `docs/citations.md` explains the fixes (move the float's source or cite earlier) | student (delayed floats) |
| Access date for every URL (not DOIs), in the style's format | §3.4 p. 34; FC | `references.bib` example; `build.py` hint | build hint; tested: numeric, IEEE, APA, Chicago author-date, chem-acs print it |
| References before appendices; appendices lettered with titles; in contents | App. A p. 38 | `main.tex`; section comment "Appendices: lettered like chapters" (`\appendicesname`) | check |
| Permissions appendix lists file information, not the files | §A.1 pp. 38-39 | skeleton in `appendices/additional-material.tex` | student |

Chapter attribution wording (manual Table 2.1, p. 29), followed by the full
citation in the chosen style:

| Status | Wording |
| --- | --- |
| Published in a journal, presented at a conference, or a preprint | Portions of this chapter (or This chapter) have (has) previously appeared as: |
| Accepted, not yet published | Portions of this chapter (or This chapter) are (is) to appear as: |
| Submitted or under review | Portions of this chapter (or This chapter) are (is) under review as: — or — have (has) been submitted as: (with the journal or conference name) |

## Differences from RPI's official LaTeX template

"RPI's template" in this table means RPI's official LaTeX template (available
from RPI ITS; files dated 2018); it is not part of this project.

| Item | RPI's official template | This class | Justification |
| --- | --- | --- | --- |
| Line spacing | 1.4 stretch | Double | Manual §2.1 p. 16 and FC: "double-spaced" |
| Font and size options | Computer Modern; 10/11/12 pt options | Times-like, 12 pt only | §2.1 p. 16 lists Times New Roman 12 pt |
| Level-1 heading position | Baseline ~1.5 in from top | At the top margin | LT lists the wider top margin as a known glitch |
| Page-number distance | 0.58 in (bottom), 0.65 in (top) | 0.75 in | §2.2 p. 17; FC |
| Title-page phrase | "Partial Fullfillment" | "Partial Fulfillment" | Spelling error; §1.1 p. 2 |
| Submission date on title page | "Submitted [month year]" line | None | Manual p. 40 (Fig. A.2): no longer required |
| Committee size | At most 7 lines | Unlimited | Bug: §1.1 p. 1 requires all members |
| Department line | Prints "Department of" + field | Prints the full name entered | Same output; §1.1 p. 1 asks for the full name |
| Copyright text | "© Copyright year / by / Name / All Rights Reserved" | "© year / By / Name / All rights reserved" | §1.2 p. 3 and FC: match the manual's example |
| Chapter label | Samples use `[chap]`: "CHAPTER 1" above the title | "1. TITLE" (that template's class default) | Contents entry then matches the body exactly (§1.3 p. 4); manual Fig. 2.1 p. 18 |
| Appendix heading | "APPENDIX A" above the title | "A. TITLE" | Appendices formatted like chapters (App. A p. 38); matches contents entry |
| APPENDICES contents line | No page number | With page number | §1.3 p. 4: sections listed with page numbers; Fig. 1.4 p. 6 |
| Level-4 heading | Bold, same as level 3 | Italic | §2.3 p. 17: each level distinguished |
| Contents/list number columns | 1.4 em / 2.3 em / 3.2 em | 1.6 / 2.8 / 3.8 / 5 em | Bug: 12.10 touches and 12.10.10 overlaps the entry text (§1.3 p. 4) |
| Contents page-number column | 1.55 em | 3 em | Bug: roman numbers such as xviii overflow |
| Block quotes, longtable, rotated floats | Not single spaced | Single spaced | §2.1 p. 16 |
| References spacing | Small item gap | One blank line | §2.1 p. 16 |
| Chapter attributions | Not provided | `\chapterattribution` | §2.8 pp. 27-29 |
| Separate abstract title page | Provided (`abstitle-*.tex`) | Not provided | Not in the 2026 manual's front-matter list (Table 1.1 p. 15) |
| Bibliography | Manual `thebibliography` | BibLaTeX/Biber | Same placement and spacing; style chosen per §3.2 |
| `amsthm` with the math font | Loads without conflict (Computer Modern) | Clears `newtxmath`'s `\openbox` just before `amsthm` loads (pdfLaTeX); no effect unless `amsthm` is loaded | Compatibility only, no formatting rule: keeps the Times-like font (§2.1 p. 16) working with the theorem recipe; amsthm then supplies the proof box, as on LuaLaTeX and XeLaTeX |

## Project decisions

- **Seal**: the maintainer has decided that the toolkit uses the current
  seal supplied on RPI ITS's
  [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation),
  which students download themselves. This is a project decision, not OGE
  approval and not permission to redistribute the seal: it is never in the
  repository, the starter ZIP, the website artwork, or this project's license.
  The class reserves the seal's space and prints a framed placeholder box
  until the student saves `assets/rpi-seal.jpg` (or `.png`; see
  `assets/README.md`). Source note: the 2026
  manual's sample title page (§1.1 p. 2) shows an older design.

## Needs OGE confirmation

- **"CONTENTS" title**: wording from RPI's official template; the manual and
  FC call the page "Table of Contents". Kept (manual not explicit).
- **Landscape pages with bottom-center numbering**: §2.4 p. 19 says to place
  the number "in the left margin". With this class's top-right numbering the
  number stays where Fig. 2.4 shows it; confirm this is acceptable.
- **Co-chairs** printed as "Name, Co-Chair" (as in RPI's official template); the manual shows only
  "Chair".
- **APPENDICES** contents line for a single appendix.
- **Copyright year**: the class prints the graduation year.
- **Monospaced code** in appendices (FC: same font throughout). The code
  listing recipe in `docs/advanced.md` uses a typewriter font and documents
  a text-font alternative.
- **Algorithms and code listings**: the manual does not mention their
  format. The recipes in `docs/advanced.md` single-space them (§2.1 p. 16
  lists only captions, footnotes, block quotes, attributions, and
  references), number them by chapter like figures, and give them bold
  captions with a colon, placed above. They appear in neither the list of
  tables nor the list of figures, and the recipes add no separate list.
- **Theorem formatting**: the manual is silent; the recipe uses `amsthm`'s
  default style (bold label, italic statement), numbered by chapter.
- **Nomenclature title and page numbers**: the manual names the section
  "Nomenclature" (§1.6 p. 13) and asks for it to be formatted like the
  lists; the recipe's entries have no page numbers, and other titles
  (LIST OF SYMBOLS, LIST OF ABBREVIATIONS) are unconfirmed.

- **Sole-authored papers not yet published**: §2.8.1 p. 28 exempts sole
  authors from the Declaration of Co-Contribution, then says submitted,
  in-review, or to-be-submitted articles still go on it "since you are not
  the sole author". The guide applies the sole-author exemption whatever the
  paper's status; confirm this for a sole-authored submitted paper.

## Students must still check

Capitalization consistency, full department and committee names, caption
wording and case, centering and legibility, every equation numbered,
attribution wording (also for sole-authored work) and the Declaration of
Co-Contribution (co-authored work), permissions,
every reference against the official style guide (including access dates
and number format, e.g. ACS), and citation order in sequential numbered
styles, especially captions of floats that moved to a later page.

## How this stays current

Do not replace working requirements from a search result or an automatically
scraped excerpt. Read the current primary document, compare with this map,
record its version and source, change the class/examples where needed, then
compile and inspect representative PDFs. See [the update process](maintenance.md).
Keep changing administrative information, contacts, deadlines, plan limits,
and download URLs linked to official pages instead of freezing them in code.
