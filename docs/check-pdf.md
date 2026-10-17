# Check your PDF

Optional. This page reads your thesis or dissertation PDF and measures a few
formatting points: paper size, page numbers, heading position, side margins,
and the contents. Each result names the part of the OGE *Dissertation and
Thesis Manual* it comes from. It is not an OGE review, and a clean result does
not mean OGE will accept the PDF; use the
[final PDF checklist](submission.md#final-pdf-checklist) as well.

Your PDF stays on your computer: the page reads it in your browser and never
uploads it. It does need an internet connection, to download Mozilla's free
PDF reader, pdf.js, from cdnjs.cloudflare.com; your PDF is not sent there.

<div class="pdf-check" data-pdf-check data-version="" hidden><label class="pdf-check-drop" for="pdf-check-file"><span class="pdf-check-button">Choose your PDF</span> <span class="pdf-check-or">or drop it here</span></label><input class="visually-hidden" id="pdf-check-file" type="file" accept="application/pdf,.pdf"><p class="pdf-check-status" role="status" aria-live="polite"></p><div class="pdf-check-results"></div></div>

<p class="pdf-check-nojs" data-pdf-check-nojs>The checker needs JavaScript, which is off or not available in this browser. Everything it looks at is listed below; check those points by eye, then use the <a href="submission.md#final-pdf-checklist">final PDF checklist</a>.</p>

## What it looks at

Each point names the manual section and printed page it comes from; the
[requirements map](project/requirements.md) has the details. The
measurements are the same ones the toolkit's own tests use on the sample
thesis.

| Point | What the page measures | Manual |
| --- | --- | --- |
| Paper size | Every page is US letter, 8.5 × 11 in. | §2.2 p. 16 |
| Page numbering | The title page shows no number; the front matter is numbered ii, iii, … in lowercase Roman numerals; the first page of Chapter 1 is page 1, and numbers then run on without gaps. | §1.1 p. 1; §2.2 p. 16 |
| Page-number position | Bottom center on front matter and on the first page of each chapter, the references, and each appendix; top right on other pages; 0.75 in from the edge. | §2.2 pp. 16-17 |
| Level-1 headings | A page that starts a chapter, the references, an appendix, or a front-matter section starts its heading at the top margin, not lower. | §2.2 |
| Side margins | No text reaches into the 1 in left or right margin. | §2.2 p. 16 |
| Contents | Each contents entry matches the heading on the page it names. | §1.3 p. 4 |
| Toolkit version | If the PDF was made with this toolkit, which version made it, so you can [update the formatting](going-further.md#update-the-formatting-safely) before you submit. Not an OGE rule. | none |

## What it cannot tell you

- **Anything a person must judge:** capitalization, wording, captions,
  equations, references, permissions, and chapter attributions. See
  [what OGE commonly flags](submission.md#what-oge-commonly-flags).
- **Pictures and figures:** only text is measured, so a figure that runs into
  a margin is not found. Look at each figure page.
- **Headings it cannot recognize:** it finds level-1 headings written in
  capitals, as the starter writes them (for example `1. INTRODUCTION`). If
  your headings use other capitalization, some page-number and heading
  results may be missing or wrong.
- **PDFs from other tools:** it works best on a PDF compiled from this
  toolkit. A PDF from Word or another template can be checked, but expect
  more "Look at this" results to check by eye.
  <!-- TODO(verify): the checker has been tried on PDFs from this class only; results for Word and other templates are untested. -->

If a result looks wrong for your PDF, [ask for help](troubleshooting.md#ask-for-help)
and say which point and page; never send your thesis file unless you choose to.
