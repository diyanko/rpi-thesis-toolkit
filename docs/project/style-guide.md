# Writing style guide

How to write anything a student or contributor reads: the guide in `docs/`,
the front-door pages, the website, LaTeX comments, issue forms, and error
messages. When in doubt, choose the plainer sentence.

## Voice

- Plain, warm, and direct. Speak to the reader as "you".
- Help the student finish their thesis; do not sell LaTeX. Mention trade-offs
  honestly, including when Word or another route is reasonable.
- Beginner steps first, as numbered steps with one action each. Put detail for
  experienced users in a collapsed block:

  ```html
  <details><summary>For experienced users: what latexmk does</summary>

  Text in Markdown here.

  </details>
  ```

  Leave a blank line after `</summary>` and before `</details>`.
- No filler or overclaiming: avoid "simply", "just", "perfect", "guaranteed",
  "compliant", or "approved". Say what was checked and what was not.

## Terminology

| Use | Not | Notes |
| --- | --- | --- |
| thesis or dissertation | thesis (when scope matters) | Page titles and first mentions name both. Afterwards "thesis" may stand for both. |
| master's thesis | masters thesis, MS thesis | |
| doctoral dissertation | PhD thesis | Covers both PhD and DEng |
| master's, PhD, DEng | Masters, Ph.D., D.Eng. | Class options: `masters`, `doctoral`, `engineering-doctorate` |
| Office of Graduate Education (OGE) | Graduate School, grad office | Spell out once per page, then OGE |
| the manual | the OGE manual 2026 | First mention: the OGE *Dissertation and Thesis Manual*; no edition year in student pages |
| RPI Thesis Toolkit | the template, the repo | The whole project. "The starter" means the downloadable files; "the class" means `rpi-thesis.cls`. |
| Overleaf | overleaf, OverLeaf | |
| your computer | locally, local machine | |
| compile | build, typeset, render | Making the PDF. `build.py` is only the script's name. |
| Biber | biber, BibTeX | Biber is the program this starter uses; BibTeX is a different one |
| `.bib` file, `references.bib` | bib, bibtex file | |
| LaTeX, pdfLaTeX, LuaLaTeX, TeX Live, MiKTeX | Latex, latex | Product names in their official spelling |

## Talking about RPI

The toolkit is unofficial and community-made. It works alongside RPI's
official resources and links to them, but it is never RPI's or OGE's own work.

| Say | Never say (about this project) |
| --- | --- |
| "works with RPI's requirements", "follows the OGE manual" | "official", "approved", "endorsed", "compliant" |
| "RPI's official LaTeX template (available from RPI ITS)" | "RPI's template" or "the RPI template" for this starter |
| "for RPI students", "RPI Thesis Toolkit" (with the **Unofficial** tag) | "the RPI thesis template", "OGE's toolkit" |
| "Download the seal from RPI's Thesis Preparation page" | anything suggesting the seal is included or ours |

Using RPI's name descriptively is fine. Never suggest that OGE reviewed,
recommended, or approved anything, and never quote or paraphrase private
advice from RPI staff as an endorsement. Link to RPI's pages instead of
copying their documents or images.

## Degree scope

Every page serves master's and doctoral students alike. Never write a step,
example, or heading that implies the toolkit is only for one of them. When a
step differs by degree, say so explicitly ("Doctoral students: ...").

## Formatting

- No emojis or decorative symbols (such as check marks, crosses, or stars).
  The arrow → is allowed only in menu paths (**File → Download**) and step
  sequences, not as decoration.
- Callouts use GitHub syntax (`> [!TIP]`, `> [!NOTE]`, `> [!WARNING]`,
  `> [!IMPORTANT]`), at most one or two per page. Use WARNING only for a
  real risk of losing work or a rejected thesis.
- Headings in sentence case, one H1 per page. Prefer task headings ("Add a
  citation") over topic headings ("Citations").
- Link text makes sense out of context: "the OGE submission page", not
  "here" or "this link".
- Dates in prose: `14 Oct 2026`. Dates in data, file names, and BibLaTeX
  fields: ISO, `2026-10-14`.
- Student pages contain no deadlines, staff names, office hours, or tool
  version numbers. Link to the stable OGE submission page instead; deep links
  and versions live in `docs/project/sources.json` and the maintainer docs.
- State the "unofficial; not affiliated with or endorsed by RPI or OGE"
  disclaimer once each in `README.md` and `docs/submission.md`, not on every
  page. The website header carries a short **Unofficial** tag.
- Link to official documentation for third-party tools instead of describing
  menus that will change.
- Refer to code by name (macro, key, or section comment), not line number.

## Diagrams

- One standalone SVG per diagram in `docs/diagrams/`, with `<title>` and
  `<desc>` inside the file and no scripts or external fonts.
- In Markdown, give the image meaningful alt text, then a short text fallback
  directly below it, starting with *In words:*.
- The page must still make sense if the picture does not load.

## Page or section

Add a new page only for a new student task with its own goal; add it to one
of the four stages in `NAV` in `scripts/build_site.py` (Start, Write, Fix and
finish, Go further), and to the matching card in `site/index.html` and list
in `README.md`. Otherwise add a section to an existing page. Each topic has
one canonical page; elsewhere, link to it instead of repeating it.

Open every page with one sentence saying who it is for and what they need
first. End it so the next step is obvious: the previous/next links follow
`NAV`, so add a closing link only when a different page is the better next step.
Every page stands alone: a student may arrive from a search engine, so link to
the exact section instead of writing "as described above" or "on the previous
page".

## Error messages and LaTeX comments

Name the file, say what went wrong in plain words, and give the smallest
correction: "Graduation year must have four digits. In `metadata.tex`, write
the year like 2027."
