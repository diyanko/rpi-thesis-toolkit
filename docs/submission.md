# Submitting your thesis or dissertation

For master's and doctoral students approaching their defense or final
submission with a draft that compiles. This page gives the usual path from
finished draft to approved PDF, and what to double-check along the way.

> [!IMPORTANT]
> This toolkit is unofficial and community-made, not affiliated with or
> endorsed by RPI or the Office of Graduate Education (OGE), and not reviewed
> by OGE. OGE's current rules win: use the
> [OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation)
> for the manual, checklist, forms, and dates. OGE recommends its Word template
> unless you are **proficient in LaTeX**, and its staff review **formatting**
> but cannot debug LaTeX code.

## The path to graduation

Dates change each term. **Check the current OGE calendar**, and keep your
advisor and committee informed of the current deadline policy.

1. **Finish a complete draft**, work through the
   [final PDF checklist](#final-pdf-checklist) below, and check every
   attribution, quotation, and citation: OGE's review starts with an
   academic-integrity check (manual §3.1).
2. **Doctoral students: confirm any committee changes were approved** before
   you defend.
3. **Request a preliminary formatting review** from OGE at least a week before
   your defense. Send a mostly complete draft and say which citation style you
   use. It is not available after you defend. Fix what it finds.
4. **Defend.**
5. **Finish the content revisions** your committee asks for.
6. **Complete signatures and paperwork** as in OGE's current checklist for your
   degree. If a chapter reuses a paper you wrote **with co-authors**, this
   includes the **Declaration of Co-Contribution**. A paper you wrote alone
   needs its chapter attribution (manual {{cite:attribution-reuse}}; see
   [chapters based on published papers](writing.md#chapters-based-on-published-papers)).
   <!-- TODO(verify): requirements.md records that the manual's treatment of a sole-authored paper that is submitted but not yet published is unresolved. -->
   **Unresolved case:** if your sole-authored paper is *submitted or in review
   but not yet published*, the manual's wording is unclear about whether it
   goes on the declaration. Check OGE's current checklist, or ask OGE, before
   you decide ([points that need OGE confirmation](project/requirements.md#needs-oge-confirmation)).
   The declaration describes your role in each paper; the
   [CRediT contributor roles](https://credit.niso.org/) help you name it.
7. **Upload your final PDF to ProQuest promptly.** Any embargo is chosen in ProQuest
   during upload. Upload each reuse permission (the whole document) as a copyright
   permission, not as a supplemental file.
8. **Expect several rounds of formatting revisions,** often with short
   turnaround times. Revision emails may come from the ProQuest submission
   system rather than from RPI, so check your spam folder.

## What OGE commonly flags

The toolkit follows the manual edition recorded in the
[requirements map](project/requirements.md). Check these areas yourself.

| Area | What the toolkit handles for you | What you still check |
| --- | --- | --- |
| Title page | Layout, capitalized title, degree wording, committee list, space for the seal, bracketed graduation date | Exact names, degree, department, month and year; the seal downloaded from RPI and saved as `assets/rpi-seal.jpg`, with no placeholder box left ([add the RPI seal](get-started.md#add-the-rpi-seal-one-minute)) |
| Margins and page numbers | {{rule:page-size}}. {{rule:front-roman}}. {{rule:body-arabic}}. {{rule:page-number-position}} ({{cite:page-size,front-roman,body-arabic,page-number-position}}) | Nothing extends into the margins (wide tables, images, long URLs, landscape pages) |
| Contents and lists | Automatic contents, list of tables, and list of figures using your full captions, with aligned page numbers and room for numbers like 12.10 | Chapter and appendix titles in capitals; consistent section and caption capitalization (OGE asks for one consistent case; the starter's capitals for chapter titles are only its convention); no short captions; each list switched on only if you have that kind of object |
| Captions | Bold, single-spaced captions, with examples that put table captions above and figure captions below | You place each `\caption` (table above, figure below); every figure and table has one, and it is mentioned in the text |
| Attributions and co-contribution | A `\chapterattribution{...}` command that prints an unnumbered note on the chapter's first page | Exact wording from the current OGE manual ({{cite:attribution}}); the citation in your reference style (`\fullcite{key}` does this); an attribution for every reused paper, including ones you wrote alone; every co-authored one listed on the Declaration of Co-Contribution |
| Reproduced figures and tables | A caption example and wording for material used with permission or under a Creative Commons license | Permission or license for each item; credit in the caption; permissions documents as OGE instructs |
| Equations | Numbered `equation` examples, including a multi-line one with a single centered number | {{rule:equations}}. {{rule:unnumbered-displays}}. Long equations broken ({{cite:equations,unnumbered-displays}}) |
| References | Consistent formatting from one style; references placed before appendices; printed access dates; [Check your references](check-references.md) lists URLs without one | Style agreed with advisor; an access date printed for every URL ({{cite:access-dates}}); non-journal sources checked against the style guide |

## Final PDF checklist

Check [what OGE commonly flags](#what-oge-commonly-flags), then complete this list. Two optional tools help: [Check your PDF](check-pdf.md) measures a few of these points, and [Check your references](check-references.md) looks through `references.bib`. The ticks are not saved: they reset when you leave the page, so copy the list somewhere if you want to keep your progress.

- [ ] Every sample paragraph, placeholder, and invented example is gone.
- [ ] Built with a [clean recompile](troubleshooting.md#clean-recompile), with any `\includeonly` line commented out again.
- [ ] On Overleaf, the compile mode is back to **Normal** (not **Fast draft**), and every figure and the seal show in the PDF.
- [ ] If you use the optional build helper, its pre-submission hints are resolved.
- [ ] No bold citation keys or **??** anywhere; no missing characters.
- [ ] Contents and lists include figures and tables in the appendices.
- [ ] Reviewed newer class changes and applied any formatting fixes your thesis
  needs: [Check your PDF](check-pdf.md) names the version that made your PDF;
  read the [changelog](../CHANGELOG.md) entries since then, starting with
  **Changes your PDF?** ([update safely](going-further.md#update-the-formatting-safely)).

A successful compile proves only that LaTeX made a PDF. Archive the final
source, the exact PDF you submitted, and your permission documents in two
places ([back up your work](going-further.md#back-up-your-work)).

## Official resources

Everything official starts from the
[OGE Submit Your Thesis / Dissertation page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation),
which links to:

- the current thesis and dissertation **manual** (formatting rules);
- the **master's** and **doctoral** checklists (process and paperwork);
- **forms**, including the Declaration of Co-Contribution;
- **Additional Resources**, including citation guidance for STEM and non-STEM fields;
- preparation **workshops**, where you can ask questions;
- OGE's own Word and LaTeX tips sheets;
- the current **deadlines and calendar**.

RPI's official LaTeX template and the RPI seal are on RPI ITS's
[Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation).
Document links change, so start from these pages rather than bookmarking
them.

For help with the writing itself, RPI's Student Success Center runs a Writing
Lab. For LaTeX problems, use this guide or [ask the community](troubleshooting.md#ask-for-help).
