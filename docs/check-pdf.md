# Check your PDF

Optional. This page reads a thesis or dissertation PDF and measures a few
formatting points: paper size, page numbers, heading position, side margins,
the contents, and fonts. It works on a PDF from any program, not only this
toolkit, so you can also use it on a PDF someone sent you. Each result names
the part of the OGE *Dissertation and Thesis Manual* it comes from. It is not
an OGE review, and a clean result does not mean OGE will accept the PDF; use
the [final PDF checklist](submission.md#final-pdf-checklist) as well.

The PDF stays on your computer: the page reads it in your browser and never
uploads it. The PDF reader it uses, Mozilla's free pdf.js, is part of the
toolkit's website, so nothing is downloaded from another website.

<div class="pdf-check" data-pdf-check data-version="" hidden><label class="pdf-check-drop" for="pdf-check-file"><span class="pdf-check-button">Choose your PDF</span> <span class="pdf-check-or">or drop it here</span></label><input class="visually-hidden" id="pdf-check-file" type="file" accept="application/pdf,.pdf"><p class="pdf-check-status" role="status" aria-live="polite"></p><div class="pdf-check-results"></div></div>

<p class="pdf-check-nojs" data-pdf-check-nojs>The checker needs JavaScript, which is off or not available in this browser. Everything it looks at is listed below; check those points by eye, then use the <a href="submission.md#final-pdf-checklist">final PDF checklist</a>.</p>

## Reading the results

Each point gets one of four results:

- **Looks right:** the page measured this point and found nothing to look at.
- **Look at this:** something differs from what the manual asks, or (for an
  information point) is worth a look. The details name the PDF page.
- **Could not tell:** the page could not measure this point in this PDF, for
  example because it found no contents page. It says why. Check the point by
  eye; it has not passed.
- **Information:** a fact about the file, not a rule.

To keep a record, or to send one with a question, use **Print or save the
result** below the results. The printout lists the file name, the date, the
toolkit version, every point with its result and source, and every page it
names. Your browser's print window can save it as a PDF.

## What it looks at

Each rule names the manual section and printed page it comes from; the
[requirements map](project/requirements.md) has the details. The
measurements are the same ones the toolkit's own tests use on the sample
thesis.

| Point | What the page measures | Manual |
| --- | --- | --- |
| Paper size | Every page is US letter, 8.5 × 11 in (upright or sideways). | §2.2 p. 16 |
| Same page size | Every page has the same size. | §2.2 p. 16 |
| Page numbering | The title page shows no number; the front matter, the contents included, is numbered ii, iii, … in lowercase Roman numerals; the first page of Chapter 1 is page 1, and numbers then run on without gaps. | §1.1 p. 1; §2.2 p. 16 |
| Page-number position | Bottom center on front matter and on the first page of each chapter, the references, and each appendix; top right on other pages; 0.75 in from the edge. | §2.2 pp. 16-17 |
| Level-1 headings | A page that starts a chapter, the references, an appendix, or a front-matter section starts its heading at the top margin, not lower. | §2.2 |
| Side margins | No text reaches into the 1 in left or right margin. | §2.2 p. 16 |
| Contents entries | Each contents entry matches the heading on the page it names. | §1.3 p. 4 |
| Headings in the contents | Every level-1 heading after the contents has a contents entry. | §1.3 p. 4 |
| Fonts | Information: every font is embedded in the PDF, so it looks the same on any computer. | none |
| Blank pages | Information: pages with no text and nothing drawn on them. | none |
| File size | Information: the size of the file. The requirements map lists no size limit. | none |
| Toolkit version | Information: if the PDF was made with this toolkit, which version made it, so you can [update the formatting](going-further.md#update-the-formatting-safely) before you submit. | none |

<!-- TODO(verify): no row of the requirements map makes embedded fonts or a file-size limit an OGE rule; both stay information only until the manual or OGE's submission page says otherwise. -->

## What it cannot tell you

- **Anything a person must judge:** capitalization, wording, captions,
  equations, references, permissions, and chapter attributions. See
  [what OGE commonly flags](submission.md#what-oge-commonly-flags).
- **Pictures and figures:** only text is measured, so a figure that runs into
  a margin is not found. Look at each figure page.
- **Scanned pages:** a page that is a picture of text has no text to measure,
  so most points say "Could not tell".
- **Headings it cannot recognize:** it finds level-1 headings written in
  capitals (for example `1. INTRODUCTION`), headings that a PDF bookmark
  points to, and headings in capitals in the contents. If none of these
  applies, the heading points say "Could not tell" and some page-number
  results may be wrong.
- **PDFs from other programs:** every point is measured on the page, so a PDF
  from Word, Google Docs, or another LaTeX template can be checked too. It has
  been tried on PDFs from LaTeX only; expect more "Look at this" results to
  check by eye.
  <!-- TODO(verify): the checker has been tried on PDFs from this class and other LaTeX classes only; Word and Google Docs PDFs are untested. -->

The offline guide in the starter ZIP does not include the checker, because
some browsers, such as Chrome, do not let a page opened from a file start the
PDF reader. Open this page on the toolkit's website instead; your PDF still
stays on your computer.

If a result looks wrong for your PDF, [ask for help](troubleshooting.md#ask-for-help)
and say which point and page; never send your thesis file unless you choose to.
