# Reviewer checklist

For an advisor, committee member, or Office of Graduate Education (OGE)
reviewer: what this unofficial, community-made toolkit sets in a thesis or
dissertation, and what still needs your eye.

This is not an OGE checklist: OGE's current manual and checklists on the
[OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation)
come first. Page numbers are the manual's printed pages, as recorded in the
[requirements map](project/requirements.md).

## What the class sets

The class file (`rpi-thesis.cls`) applies these by itself; each area links
to its row in the requirements map. Extra packages or class edits can
override them, so a quick look still helps.

| Area | What the class does | Manual |
| --- | --- | --- |
| [Page](project/requirements.md#page-layout-and-spacing) and [fonts](project/requirements.md#fonts) | US letter, 1 in margins; one black Times-like 12 pt font; body double spaced, captions, footnotes, block quotes, and references single spaced | §§2.1-2.2 p. 16 |
| [Page numbers](project/requirements.md#page-numbers) | Lowercase Roman front matter (title page is i, unnumbered; next ii); Arabic from Chapter 1; 0.75 in from the edge; bottom center on front matter and on the first page of each chapter, references, appendix; top right elsewhere | §1.1 p. 1; §2.2 pp. 16-17 |
| [Title and copyright](project/requirements.md#title-page-and-copyright) | Layout, degree wording, committee list, graduation month; optional copyright page ii | §1.1 pp. 1-2; §1.2 p. 3 |
| [Contents](project/requirements.md#contents-and-lists) and [appendices](project/requirements.md#appendices-and-permissions) | `\thesisfrontmatter` prints contents and lists; entries match headings and full captions; appendices lettered | §§1.3-1.5 pp. 4-10; App. A p. 38 |
| [Order (starter)](project/requirements.md#contents-and-lists) | Set by the starter's `main.tex`, not the class: front-matter order, references before appendices | Table 1.1 p. 15; App. A p. 38 |
| [Headings](project/requirements.md#headings), [captions](project/requirements.md#captions-tables-and-figures), [attributions](project/requirements.md#chapter-attributions) | Four distinct heading levels; bold captions with a colon, numbered by chapter; `\chapterattribution` sets an unmarked note at the foot of a chapter's first page | §§2.3-2.5 pp. 17-22; §2.8 pp. 27-29 |

## What still needs a human look

- [ ] **Figures:** centered, inside the margins, legible, caption below, no
  color in captions; lettered parts use one letter style (§§2.4-2.5
  pp. 18-23).
- [ ] **Tables, including long ones:** centered, caption above, nothing in
  the margin on any page (§2.4 pp. 18-19; §2.2 p. 16).
- [ ] **Landscape pages:** caption reads with the table; the class keeps the
  page number top right, a placement awaiting
  [OGE confirmation](project/requirements.md#needs-oge-confirmation)
  (§2.4 p. 19, Fig. 2.4).
  <!-- TODO(verify): landscape page-number placement awaits OGE confirmation; see requirements.md "Needs OGE confirmation". -->
- [ ] **Equations:** every display numbered at the right, one centered number
  for a multi-line equation; displays inside a lemma, theorem, proof, or
  algorithm may be unnumbered (§2.7 pp. 26-27).
- [ ] **Citation style:** one style suited to the field throughout;
  sequential numbered styles start at 1 in Chapter 1, captions included;
  every URL has an access date (§§3.2-3.4 pp. 32-34).
- [ ] **Copyright permissions:** each reproduced table or figure cites its
  source and gives permission or license wording in the caption (§2.6 pp. 24-25).
- [ ] **Attributions:** Table 2.1 wording for every reused paper, sole-authored
  too (§2.8 pp. 28-29).
- [ ] **Wording:** consistent heading and caption case, full department and
  committee names, no figures or references in the abstract (§1.1 p. 1; §1.8
  p. 14; §2.3 p. 17).

## Where students record exceptions

- **Permissions appendix:** one entry per uploaded permission file, listing
  the file's details, not the file (§A.1 pp. 38-39).
- **Chapter attributions** on each chapter's first page, and the Declaration
  of Co-Contribution for co-authored papers (§2.8.1 p. 28).
- **`preamble.tex`:** the citation style and extra packages, which can
  override the class. The PDF's **Creator** property names the class version
  ([changelog](../CHANGELOG.md)).
