# Workshop kit: your thesis in LaTeX, without the fear

A ready-to-run, hands-on session for people who are new to LaTeX or nervous
about it. Anyone can run it: the maintainer, a graduate student group, a
department, or the library. In about an hour, attendees compile the sample
thesis on Overleaf, put their own name on the title page, write a section, a
figure, a table, and a citation, fix an error on purpose, and learn where to
check their PDF before submitting.

The RPI Thesis Toolkit is unofficial and community-made, and the current rules
of RPI's Office of Graduate Education (OGE) come first. Say so when you
introduce it (the first and last slides do), and send people to the
[OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation)
for the current rules, forms, and dates.

## What is in this folder

| File | What it is |
| --- | --- |
| `slides.html` | The slide deck: 33 slides, 16:9, one HTML file that prints to PDF ([make the PDF](#make-the-pdf)). |
| `exercises.md` | A one-page attendee sheet: four exercises with the exact snippets and what attendees should see. Print it, or share the link. |
| `README.md` | This facilitator guide. |
| `../qr-site.svg`, `../qr-feedback.svg` | QR codes for the website and the help and feedback form, used on the slides. |

## Who it is for

- Master's and doctoral students at any stage, in any department, who have
  never used LaTeX or have tried it and got stuck.
- Students with a draft in Word, Google Docs, or Markdown who want to see
  what moving it would involve.
- No terminal, programming, Git, or AI is needed. Attendees need a laptop and
  a web browser.

It suits a group of about 5 to 30. With more than about 15, ask a second
person to walk the room during the live steps.

## Timing

Planned for 60 minutes. The minutes include the live steps.

| Part | Slides | Minutes |
| --- | --- | --- |
| Welcome, "you do not need to know LaTeX", the plan | 1-3 | 3 |
| What LaTeX does for a thesis | 4-8 | 4 |
| Three ways in | 9 | 2 |
| Live: open and compile the sample on Overleaf | 10-12 | 6 |
| Live: put your name on it with the Settings builder | 13 | 5 |
| Live: a section, a figure, a table | 14-18 | 8 |
| Live: cite a source; Zotero | 19-22 | 5 |
| When it breaks; exercise: break it on purpose | 23-26 | 7 |
| Before you submit: OGE first, Check your PDF | 27-29 | 3 |
| Bring your draft | 30 | 2 |
| Hands-on: your turn | 31 | 12 |
| Feedback and close | 32-33 | 3 |

**For 45 minutes:** skip slides 7 and 15, show slide 22 (Zotero) without the
steps, demonstrate slide 26 instead of timing it, and shorten the hands-on
time to 8 minutes. **For 90 minutes:** give the hands-on time 30 minutes and
add a demonstration of [Check your references](../../docs/check-references.md)
after slide 22.

## Prepare

### A week before

- **Room:** reliable Wi-Fi (Overleaf works only online), a projector, and
  power outlets or extension cords for laptops.
- **Tell attendees** to bring a laptop and to create a free
  [Overleaf](https://www.overleaf.com/) account beforehand; signing up in the
  room uses up time. Zotero is optional: those who want exercise C with their
  own sources can install [Zotero](https://www.zotero.org/) and its browser
  connector in advance.
- **Share the slides PDF and `exercises.md`** before the session, so anyone
  who prefers to follow on their own screen, or needs larger text, can.

### The day before

1. Run every live step yourself on a fresh Overleaf account: **Open in
   Overleaf** from the website, **Recompile**, the Settings builder, each
   snippet, and the broken `\parencit`. Steps and button names come from
   [Get started](../../docs/get-started.md) and the tool pages; if anything
   on screen differs from the slides, follow the website and note it for the
   [deck update](#keep-the-deck-current).
2. Keep a picture file (a PNG or JPG photo or plot) on your laptop for the
   figure demonstration.
3. Download the compiled sample PDF from your Overleaf project, for the
   Check your PDF demonstration.
4. Open these tabs in order: the website home page, the
   [Settings builder](../../docs/settings-builder.md),
   [Explain my error](../../docs/explain-my-error.md),
   [Convert to LaTeX](../../docs/convert-to-latex.md), and
   [Check your PDF](../../docs/check-pdf.md). Use the website, not the
   offline guide: Check your PDF does not run from the offline guide.
5. Print `exercises.md` (one per attendee, double-sided is fine) and the
   slides PDF if you want notes in hand.

## Make the PDF

The deck is `slides.html`. It uses the website's fonts and drawings by
relative path, so open or print it from inside the repository.

**Without a terminal:** open `outreach/workshop/slides.html` in Chrome or
Edge, choose **Print**, then **Save as PDF**, with margins set to **None**
and headers and footers turned off. Each slide prints as one 16:9 page.

**Optional, in a terminal:** from the repository folder, run
`python3 scripts/outreach.py`. It prints every outreach page, this deck
included, to `build/outreach/` (the deck is `build/outreach/workshop/slides.pdf`).
It needs Chromium or Google Chrome. Never commit the PDFs; `build/` is not
tracked.

## Run sheet

Each part lists what to say and what to do. Say it in your own words; the
quotes are a starting point, not a script.

### Welcome (slides 1-3)

- **Say:** "You do not need to know LaTeX. Today you type a few lines, press
  a button, and get a real thesis PDF with your name on it."
- **Say:** "This toolkit is unofficial and community-made. OGE's current
  manual and checklists come first, and its staff review formatting, not
  LaTeX code."
- **Do:** ask for a show of hands: who has used LaTeX before, who has a
  draft already, who is on Overleaf now. Adjust the pace to the room.

### What LaTeX does (slides 4-8)

- **Say:** "You write the words. The class file sets margins, spacing,
  headings, page numbers, and the contents, following the OGE manual."
- **Say** on slide 6: "Four files matter today: `metadata.tex` for the title
  page, `chapters/` for your words, `references.bib` for your sources, and
  `rpi-thesis.cls`, which you leave alone."
- **Say** on slide 8: "Word is a fine choice too. OGE recommends its own Word
  template unless you are proficient in LaTeX. Pick what helps you finish."
  Keep this honest; nobody should leave feeling they chose wrong.

### Three ways in (slide 9)

- **Say:** "Today is Overleaf: nothing to install. For a whole thesis, the
  guide suggests an editor on your computer: no compile time limit, and the
  files stay with you. You can switch later." Point people with a draft to
  slide 30, which comes later.

### Live: compile the sample (slides 10-12)

- **Do:** on the website home page, click **Open in Overleaf**; sign in if
  asked; check that `main.tex` is at the top of the file list; click
  **Recompile**.
- **Expected:** the PDF appears beside the editor: a title page reading
  "YOUR THESIS TITLE" with a seal placeholder, the contents, and three short
  chapters.
- **Do:** wait until most hands say it worked. Helpers check anyone stuck
  ([common snags](#common-snags-and-fixes)).
- **Say** on slide 12: "You can't break it. Compiling never changes your
  writing. An error means: fix this spot and compile again."

### Live: put your name on it (slide 13)

- **Do:** open the Settings builder. Type a title, a name, a degree
  (`masters` or `doctoral`), a department, a graduation month and year, and
  two committee members, one marked Chair. Show the sketch of the title page
  updating.
- **Do:** click **Copy settings**. In Overleaf, open `metadata.tex`, select
  from `\thesissetup{` down to the last `\committeemember` line, paste over
  it, and click **Recompile**.
- **Expected:** the title page shows the new title in capitals, the name,
  the degree wording, and the committee under "Approved by".
- **Say:** "The seal belongs to RPI, so the starter leaves a box. Download
  the seal from RPI ITS's Thesis Preparation page and save it as
  `assets/rpi-seal.jpg`." ([Add the RPI seal](../../docs/get-started.md#add-the-rpi-seal-one-minute))

### Live: a section, a figure, a table (slides 14-18)

- **Say** on slide 15: "A command starts with a backslash, braces hold its
  text, `%` starts a note, a blank line starts a paragraph. That is most of
  it." ([Writing basics](../../docs/writing.md))
- **Do:** paste each snippet from the slides at the end of
  `chapters/01-introduction.tex` and recompile after each one. For the
  figure, upload your picture into `figures/` as `my-plot.png` first, or
  write `example-image` in place of `figures/my-plot`.
- **Expected:** a new numbered section and contents line; Figure 1.1 with
  its caption below; Table 1.1 with its caption above; new lines in the List
  of Figures and the List of Tables.
- **Say:** "Never type a number. `\label` names it, `\ref` prints it." If a
  figure lands on the next page, say that this is normal.
- **Mention:** spreadsheet cells go into
  [Convert to LaTeX](../../docs/convert-to-latex.md), which writes the whole
  table.

### Live: cite a source (slides 19-22)

- **Do:** add the sample citation sentence to
  `chapters/01-introduction.tex` and recompile.
- **Expected:** another [1] pointing to Lamport's book, already listed under
  REFERENCES.
- **Say** on slide 22: "Agree on a citation style with your advisor first;
  the sample's numbered style is not a department's style. Zotero is free
  and optional: export your collection as BibLaTeX to `references.bib`, and
  on Overleaf upload it over the old file." ([Citations](../../docs/citations.md))

### When it breaks (slides 23-26)

- **Do** on slide 24: walk through the real error: the file, the line, the
  message, and where LaTeX stopped (the end of the `l.13` line).
  ([Read an error message](../../docs/troubleshooting.md#read-an-error-message))
- **Do** on slide 25: on Overleaf, click **Logs and output files**, copy the
  first error, paste it into Explain my error, and click **Explain the
  error**.
- **Exercise** on slide 26 (5 minutes): everyone changes `\parencite` to
  `\parencit` in `chapters/01-introduction.tex`, recompiles, finds the
  error, pastes it into Explain my error, then fixes it.
- **Expected:** "Undefined control sequence" in
  `chapters/01-introduction.tex` on the changed line; after the fix, the
  PDF is back to normal.
  <!-- TODO(verify): the guide marks Overleaf's "Logs and output files" button label as not rechecked in the current editor; check it during the dry run. -->

### Before you submit (slides 27-29)

- **Say:** "OGE's rules win. The manual, checklists, forms, and dates are on
  the OGE submission page; start there each term. Request OGE's preliminary
  formatting review before your defense; it is not available afterwards."
  ([Submitting](../../docs/submission.md))
- **Do** on slide 29: open Check your PDF, click **Choose your PDF**, and
  pick the sample PDF you downloaded. Show the four results: **Looks
  right**, **Differs from the manual's wording**, **Look at this**, and
  **Could not tell**.
- **Say:** "Nothing is uploaded. It is not an OGE review: use the final PDF
  checklist too."

### Bring your draft (slide 30)

- **Say:** "Keep your original untouched and move one small section first."
- **Do:** paste a short passage with a heading and a bulleted list into
  Convert to LaTeX (or click **Show an example**), choose **Part of a
  chapter**, click **Copy**, paste it below the `\chapter` and `\label`
  lines, and recompile. ([Bring your draft](../../docs/bring-your-draft.md))

### Hands-on (slide 31)

- **Do:** start a visible timer. Attendees pick exercises A to D from
  `exercises.md`. Walk the room. Ask "what did you expect to see?" before
  fixing anything for someone; let them type the fix.
- **Do:** note every place people get stuck, in a few words. This is the
  most useful feedback the project can get.

### Feedback and close (slides 32-33)

- **Do:** leave slide 32 up for two minutes so people can scan the QR code
  for the [help and feedback form](https://forms.gle/fjfiLfkmVhkcyRNCA).
- **Say:** "Tell me where you got stuck: a confusing step, a missing topic,
  or a tip for the next person."
- **Say** on slide 33: "Next: Get started, to set up your computer; Writing
  basics; and Fixing problems, for common messages." Repeat that the toolkit
  is unofficial and that OGE's current requirements come first.

## Hands-on exercises

The attendee sheet is [`exercises.md`](exercises.md). What each should
produce:

| Exercise | Expected result | Guide |
| --- | --- | --- |
| A. Your title page | The title in capitals, the name, the degree wording, the committee under "Approved by", the bracketed graduation date; a seal box until the seal is added | [Put your name on it](../../docs/get-started.md#put-your-name-on-it) |
| B. A figure and a table | Figure 1.1 with its caption below, Table 1.1 with its caption above, "As Figure 1.1 shows" in the text, new lines in both lists | [Figures and tables](../../docs/writing.md#figures-and-tables) |
| C. Cite a source | Another [1] for Lamport's book; with a pasted entry, a new number and a new entry under REFERENCES | [Citations](../../docs/citations.md#try-the-sample-citation) |
| D. One section of a draft | The text with headings, bold, italics, and lists in LaTeX; a list of what the page left to do by hand | [Convert to LaTeX](../../docs/convert-to-latex.md) |

The snippets in B and C, and the broken `\parencit` on slide 26, were
compiled with the unchanged starter and give the results above. The section
number in the section exercise depends on the sections already in chapter 1.

## Common snags and fixes

Most messages are also in [common messages](../../docs/troubleshooting.md#common-messages)
and in Explain my error, which give the same advice.

| Snag | What to do |
| --- | --- |
| Overleaf asks you to sign in and opens no project | Sign in, then go back to the website and click **Open in Overleaf** again. |
| ``File `rpi-thesis.cls' not found`` | `main.tex` and `rpi-thesis.cls` must be at the top of the file list, not inside a folder ([Overleaf route](../../docs/get-started.md#step-3b-overleaf-route)). |
| Odd errors on a fresh project | Open **Settings** (the gear icon): under **Compiler**, the main document is `main.tex`, the compiler is **pdfLaTeX**, and the TeX Live version is the newest. |
| A box where the seal should be | Expected: the seal is not included. Download it from RPI ITS's Thesis Preparation page and save it as `assets/rpi-seal.jpg` ([add the seal](../../docs/get-started.md#add-the-rpi-seal-one-minute)). |
| **Copy settings** stays greyed out | The form is not complete yet; read the list under the form. At least one committee member must be Chair or Co-Chair. |
| `Committee chair is missing` | Put `[Chair]` (or `[Co-Chair]`) on one `\committeemember` line, spelled exactly so. |
| `Undefined control sequence` | A typo after a backslash. Look at the end of the `l.` line ([read an error message](../../docs/troubleshooting.md#read-an-error-message)). |
| ``File `figures/my-plot' not found`` | Upload the picture into the `figures` folder, then compare its name with the one in `\includegraphics`. |
| `Misplaced alignment tab character &` | An `&` outside a table, often in a title. Write it as `\&`. |
| `Missing $ inserted` | An underscore in ordinary text. Write `\_`. |
| **??** or a citation key in bold | Recompile. If it stays, check that the key or label matches exactly ([bold keys and question marks](../../docs/how-it-works.md#bold-citation-keys-and-question-marks)). |
| The figure or table moved to the next page | Normal: LaTeX places it where it fits. Refer to it with `Figure~\ref{...}`, not "below". |
| A new Zotero source does not appear | Export again, upload the new `references.bib` to Overleaf, and check that the key matches ([Zotero](../../docs/citations.md#step-2-collect-and-cite-sources-with-zotero)). |
| The PDF does not update, or an error looks impossible | Open the **Recompile** menu (the small arrow beside the button) and choose **Recompile from scratch** ([clean recompile](../../docs/troubleshooting.md#clean-recompile)). |
| Overleaf says the compile timed out | Large images are the usual cause: shrink photos, or try **Fast [draft]** from the **Recompile** menu for now. |
| Check your PDF does not start | Open it on the website, not from the offline guide in the starter ZIP. |

Something else? Paste the first error into Explain my error, or use
[Ask for help](../../docs/troubleshooting.md#ask-for-help) after the
session. Never ask attendees to share unpublished research or personal
details to get help.

## Collect feedback

- Slide 32 shows a QR code for the
  [help and feedback form](https://forms.gle/fjfiLfkmVhkcyRNCA)
  (`forms.gle/fjfiLfkmVhkcyRNCA`). It needs no account and takes a couple of
  minutes. Leave the slide up while people fill it in.
- After the session, send your own notes through the same form: which steps
  people got stuck on, which questions came up, and anything on screen that
  differed from the slides. With a GitHub account, an issue works too
  ([ways to help](../../CONTRIBUTING.md#three-ways-to-help)).
- Do not collect names, e-mail addresses, or thesis material for the
  project; the form is enough.

## Keep the deck current

- **No versions or dates:** the deck names no tool versions, release
  numbers, deadlines, or staff, so it does not expire on its own. Keep it
  that way.
- **When the guide changes,** recheck the slides and `exercises.md` against
  it. The names to look for: **Open in Overleaf**, **Recompile**, **Logs and
  output files**, **Settings builder**, **Copy settings**, **Explain the
  error**, **Convert to LaTeX**, **Part of a chapter**, **Copy**, **Check
  your PDF**, **Choose your PDF** and its four results, and the files
  `metadata.tex`, `chapters/01-introduction.tex`, `references.bib`, and
  `assets/rpi-seal.jpg`. The snippets come from
  [Writing basics](../../docs/writing.md) and
  [Citations](../../docs/citations.md); copy any change exactly.
- **When the starter changes,** recompile the snippets in exercises B and C
  and the broken `\parencit` (the error must still point at line 13 of
  `chapters/01-introduction.tex`), and update the expected results.
- **Drawings and fonts** are linked from `docs/diagrams/`, `site/art/`, and
  `site/fonts/` by relative path, so they update with the website. If one is
  renamed, update its `src` in `slides.html`. The colors copy the light
  tokens in section 2 of `site/site.css`; change them together.
- **QR codes** point to the website and the feedback form. If either address
  changes, replace `../qr-site.svg` or `../qr-feedback.svg` and the short
  address printed under it.
- **Before each session,** do the dry run in [Prepare](#the-day-before);
  it is the quickest way to catch a renamed button.
