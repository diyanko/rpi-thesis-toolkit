# Submitting your thesis or dissertation

For master's and doctoral students approaching their defense or final
submission with a draft that compiles. Here is the usual path from finished
draft to approved PDF, and what to double-check along the way.

> [!IMPORTANT]
> The RPI Thesis Toolkit is **unofficial and community-made**. It is not
> affiliated with or endorsed by RPI or the Office of Graduate Education
> (OGE), and OGE has not reviewed it.
> OGE's current requirements always win: follow the
> [OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation)
> for the manual, your degree checklist, forms, and dates. The toolkit was
> built against the manual edition recorded in the
> [requirements map](project/requirements.md).

Good to know: OGE recommends its Word template unless you are **proficient in
LaTeX**, and OGE staff review your **formatting** but cannot debug LaTeX code.
For LaTeX help, use this guide and the project's issue tracker (see
[fixing problems](troubleshooting.md#ask-for-help)).

## The path to graduation

![Submission timeline. Step 1: finish a complete draft and check its attributions and citations. Step 2: request OGE's preliminary formatting review at least a week before your defense. Step 3: defend. Step 4: finish the content revisions. Step 5: complete signatures and paperwork. Step 6: upload your final PDF to ProQuest promptly. Step 7: expect several rounds of formatting revisions, until OGE approves.](diagrams/submission-timeline.svg)

Dates and deadlines change each term — **check the current OGE calendar**, and
keep your advisor and committee informed of the current deadline policy.

1. **Finish a complete draft**, work through the
   [final PDF checklist](#final-pdf-checklist) below, and check every
   attribution, quotation, and citation: OGE's review starts with an
   academic-integrity check (manual §3.1).
2. **Request a preliminary formatting review** from OGE well before your
   defense — allow at least a week. Send a mostly complete draft and say
   which citation style you use. It is not available after you defend.
   Fix what the review finds.
3. **Defend.**
4. **Finish the content revisions** your committee asks for.
5. **Complete signatures and paperwork** as described in OGE's current
   checklist for your degree, including the co-contribution form if any
   chapter includes published or co-authored work. The form describes your
   role in each paper; the [CRediT contributor roles](https://credit.niso.org/)
   help you name it. Doctoral students: confirm any committee changes were
   approved before you defend.
6. **Upload your final PDF to ProQuest promptly.** Embargo options, if you
   need one, are chosen in ProQuest during upload. Upload each reuse
   permission (the whole document) as a copyright permission, not as a
   supplemental file.
7. **Expect several rounds of formatting revisions**, often with short
   turnaround times. Revision emails may come from the ProQuest submission
   system rather than from RPI, so check your spam folder.

## What OGE commonly flags

| Area | What the toolkit handles for you | What you still check |
| --- | --- | --- |
| Title page | Layout, capitalized title, degree wording, committee list, space for the seal, bracketed graduation date | Exact names, degree, department, month and year; the seal downloaded from RPI and saved as `assets/rpi-seal.jpg`, with no placeholder box left ([how](../assets/README.md)) |
| Margins and page numbers | One-inch margins, letter paper, Roman numerals in front matter, Arabic from chapter 1; numbers 0.75 in from the edge, bottom center on front-matter and opening pages, top right elsewhere | Nothing extends into the margins (wide tables, images, long URLs, landscape pages) |
| Contents and lists | Automatic contents, list of tables, and list of figures using your full captions, with aligned page numbers and room for numbers like 12.10 | Chapter and appendix titles in capitals; consistent section and caption capitalization; no short captions; each list switched on only if you have that kind of object |
| Captions | Bold, single-spaced captions; table captions above, figure captions below | Every figure and table has one, and it is mentioned in the text |
| Attributions and co-contribution | A `\chapterattribution{...}` command that prints an unnumbered note on the chapter's first page | Exact wording from the current OGE manual; the citation in your reference style (`\fullcite{key}` does this); every attributed paper listed on the co-contribution form |
| Reproduced figures and tables | A caption example and wording for material used with permission or under a Creative Commons license | Permission or license for each item; credit in the caption; permissions documents as OGE instructs |
| Equations | Numbered `equation` examples, including a multi-line one with a single centered number | Every displayed equation numbered, number on the same line, long equations broken |
| References | Consistent formatting from one style; references placed before appendices; printed access dates; a build hint for URLs without one | Style agreed with advisor; an access date printed for every URL; non-journal sources checked against the style guide |

## Final PDF checklist

Alongside the table above:

- [ ] Every sample paragraph, placeholder, and invented example is gone.
- [ ] Built from scratch, with any `\includeonly` line commented out again.
- [ ] No pre-submission hints left from the build helper.
- [ ] No bold citation keys or **??** anywhere; no missing characters.
- [ ] Contents and lists include figures and tables in the appendices.
- [ ] Your `rpi-thesis.cls` is the latest version: compare the version at the
  top of the file (also printed in the compile log) with the newest entry in
  the toolkit's [changelog](../CHANGELOG.md), and read its **Changes your
  PDF?** notes ([update safely](workflows.md#update-the-formatting-safely)).

A successful compile proves only that LaTeX made a PDF. Archive the final
source, the exact PDF you submitted, and your permission documents in two
places ([back up your work](workflows.md#back-up-your-work)).

## Official resources

Everything official starts from the
[OGE Submit Your Thesis / Dissertation page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation).
From there you will find:

- the current thesis and dissertation **manual** (formatting rules);
- the **master's** and **doctoral** checklists (process and paperwork);
- **forms**, including the co-contribution form;
- **Additional Resources**, including citation guidance for STEM and non-STEM fields;
- preparation **workshops**, where you can ask questions;
- OGE's own Word and LaTeX tips sheets;
- the current **deadlines and calendar**.

RPI's official LaTeX template and the RPI seal are on a separate page, RPI
ITS's [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation).

Its document links change, so start there rather than bookmarking them.
For help with the writing itself, RPI's Student Success Center runs a
Writing Lab. OGE staff review formatting but don't debug LaTeX. For LaTeX
problems, [ask this community](troubleshooting.md#ask-for-help).
