# Reviewer checklist

For an advisor, committee member, or Office of Graduate Education (OGE)
reviewer: what this unofficial, community-made toolkit sets in a thesis or
dissertation, and what still needs your eye.

This is not an OGE checklist: OGE's current manual and checklists on the
[OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation)
come first. Each rule below is quoted from the
[requirements map](project/requirements.md), which ties it to the manual;
page numbers are the manual's printed pages, **FC** is OGE's Formatting
Checklist, and **LT** its *LaTeX Formatting Tips & Tricks*.

## What the class sets

The class file (`rpi-thesis.cls`) supplies the layout defaults below; each
area links to its rows in the requirements map. Content choices, optional
short titles or captions, extra packages, and class edits can change the
result. Check the finished PDF as well.

| Area | What the class does | Manual |
| --- | --- | --- |
| [Page](project/requirements.md#page-layout-and-spacing) and [fonts](project/requirements.md#fonts) | {{rule:page-size}}. {{rule:font}}. {{rule:black-text}}. {{rule:double-spacing}}. {{rule:single-spacing}}. | {{cite:page-size,font,black-text,double-spacing,single-spacing}} |
| [Page numbers](project/requirements.md#page-numbers) | {{rule:front-roman}}. {{rule:body-arabic}}. {{rule:page-number-position}}. | {{cite:front-roman,body-arabic,page-number-position}} |
| [Title and copyright](project/requirements.md#title-page-and-copyright) | Layout, degree wording, committee list, graduation month; optional copyright page ii | {{cite:title-page,degree-wording,copyright-page}} |
| [Contents](project/requirements.md#contents-and-lists) and [appendices](project/requirements.md#appendices-and-permissions) | Automatic contents and object lists; aligned numbers; lettered appendices. Short title or caption arguments can make entries differ from the document. | {{cite:contents-entries,contents-match,lists,appendices}} |
| [Order (starter)](project/requirements.md#contents-and-lists) | Set by the starter's `main.tex`, not the class: front-matter order, references before appendices | {{cite:front-matter-order,appendices}} |
| [Headings](project/requirements.md#headings), [captions](project/requirements.md#captions-tables-and-figures), [attributions](project/requirements.md#chapter-attributions) | Four distinct heading levels; bold captions with a colon, numbered by chapter; `\chapterattribution` sets an unmarked note at the foot of a chapter's first page | {{cite:headings,captions,attribution}} |

## What still needs a human look

- [ ] **Contents and lists:** {{rule:contents-match}}; the lists of tables
  and figures use the full captions, appendix objects included. Optional
  short arguments such as `\section[Short]{Long}` and `\caption[Short]{Long}`
  break this ({{cite:contents-match,lists}}).
- [ ] **Figures and tables:** {{rule:captions}}. Each is legible and stays
  inside the margins on every page, long tables included. {{rule:lettered-parts}}
  ({{cite:captions,lettered-parts,page-size}}).
- [ ] **Landscape pages:** caption reads with the table; the class keeps the
  page number top right, a placement awaiting
  [OGE confirmation](project/requirements.md#needs-oge-confirmation)
  ({{cite:landscape}}).
  <!-- TODO(verify): landscape page-number placement awaits OGE confirmation; see requirements.md "Needs OGE confirmation". -->
- [ ] **Equations:** {{rule:equations}}. {{rule:unnumbered-displays}}
  ({{cite:equations,unnumbered-displays}}).
- [ ] **Citation style:** {{rule:citation-style}}. {{rule:sequential-numbering}}.
  {{rule:access-dates}} ({{cite:citation-style,sequential-numbering,access-dates}}).
- [ ] **Copyright permissions:** {{rule:reproduced}} ({{cite:reproduced}}).
- [ ] **Attributions:** {{rule:attribution}}. Every reused paper needs one,
  sole-authored too ({{cite:attribution,attribution-reuse}}).
- [ ] **Wording:** consistent heading and caption case, full department and
  committee names, no figures or references in the abstract
  ({{cite:headings,department-name,abstract}}).

## Where students record exceptions

- **Permissions appendix:** one entry per uploaded permission file, listing
  the file's details, not the file ({{cite:permissions-appendix}}).
- **Chapter attributions** on each chapter's first page, and the Declaration
  of Co-Contribution for co-authored papers ({{cite:attribution-reuse}}).
- **`preamble.tex`:** the citation style and extra packages, which can
  override the class. The PDF's **Creator** property names the class version
  ([changelog](../CHANGELOG.md)).
