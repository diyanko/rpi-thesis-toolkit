# Check your PDF

Choose a thesis or dissertation PDF, from any program; the page measures
paper size, page numbers, headings, side margins, the contents, and fonts
against the OGE *Dissertation and Thesis Manual*. It is not an OGE review:
use the [final PDF checklist](submission.md#final-pdf-checklist) as well.

<p class="tool-privacy"><strong>Nothing is uploaded.</strong> The page reads your PDF in your browser. Its PDF reader, Mozilla's free pdf.js, is part of this website, so nothing is downloaded from another website.</p>

<div class="tool pdf-check" data-pdf-check data-version="" hidden><label class="pdf-check-drop tool-drop tool-file" for="pdf-check-file"><span class="tool-file-button is-primary">Choose your PDF</span> <span class="tool-file-or">or drop it here</span></label><input class="visually-hidden" id="pdf-check-file" type="file" accept="application/pdf,.pdf"><p class="tool-file-names" data-file-names></p><p class="pdf-check-status tool-status" role="status" aria-live="polite"></p><button type="button" class="button button-secondary pdf-check-cancel" hidden>Cancel the check</button><div class="pdf-check-results tool-results"></div></div>

<p class="pdf-check-nojs tool-nojs" data-pdf-check-nojs>The checker needs JavaScript, which is off or not available in this browser. Everything it looks at is listed below; check those points by eye, then use the <a href="submission.md#final-pdf-checklist">final PDF checklist</a>.</p>

## Reading the results

The page compares your PDF with the wording of the OGE manual. Each point
gets one of these results:

- **Looks right:** the page measured this point and found nothing to look at.
- **Differs from the manual's wording:** a small difference from what the
  manual says, such as page numbers a little closer to the edge than 0.75 in.
  The result names the manual's value and the one measured. It has not
  passed: follow the manual where you can, and if you are unsure whether the
  difference is acceptable, confirm it with OGE.
- **Look at this:** something differs clearly from what the manual asks, or
  (for an information point) is worth a look. The details name the PDF page.
- **Could not tell:** the page could not measure this point in this PDF, for
  example because it found no contents page. It says why. Check the point by
  eye; it has not passed.
- **Information:** a fact about the file, not a rule.

To keep a record, or to send one with a question, use **Print or save the
result** below the results. The printout lists the file name, the date, the
toolkit version, every point with its result and source, and every page it
names. Your browser's print window can save it as a PDF.

A long PDF takes a while to read. **Cancel the check** stops it; choosing
another PDF also replaces a check that is still running.

## What it looks at

Each rule names the manual section and printed page it comes from; the
[requirements map](project/requirements.md) has the details. The
measurements are the same ones the toolkit's own tests use on the sample
thesis.

| Point | What the page measures | Manual |
| --- | --- | --- |
| Paper size | Every page is US letter, 8.5 × 11 in (upright or sideways). | §2.2 p. 16 |
| Same page size | Every page has the same size. | §2.2 p. 16 |
| Page numbering | The title page shows no number; the front matter, the contents included, is numbered ii, iii, … in lowercase Roman numerals; the first page of Chapter 1 is page 1, and numbers then run on without gaps. A last page without a number, such as a notice page a library adds, is noted in the details. | §1.1 p. 1; §2.2 p. 16 |
| Page-number position | Bottom center on front matter and on the first page of each chapter, the references, and each appendix; top right on other pages. | §2.2 pp. 16-17 |
| Page-number distance | Each number is 0.75 in from the edge. A distance between 0.3 in and 1.2 in is reported as differing from the manual's wording; one closer or farther, as a point to look at. | §2.2 pp. 16-17 |
| Level-1 headings | A page that starts a chapter, the references, an appendix, or a front-matter section starts its heading at the top margin, not lower. On a PDF made with this toolkit, the heading must sit exactly where the class puts it; on another PDF, a heading a little lower (down to 1.5 in from the top edge) is reported as differing from the manual's wording. | §2.2 |
| Side margins | No text reaches into the 1 in left or right margin. Text up to 0.125 in into it is reported as differing from the manual's wording. | §2.2 p. 16 |
| Contents entries | Each contents entry matches a heading on the page it names, line for line, not words inside a paragraph. A title may wrap at different words, and a "CHAPTER 1" line above the title on the page matches "1. TITLE" in the contents. | §1.3 p. 4 |
| Headings in the contents | Every level-1 heading after the contents has its own contents entry; an entry for its first section does not count. | §1.3 p. 4 |
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
