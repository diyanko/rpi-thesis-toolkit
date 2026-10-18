---
description: Check references.bib for citation keys, missing fields, names, dates, and style advice in your browser. Nothing is uploaded.
---

# Check your references

Paste or drop your `references.bib`; the page lists common problems
(repeated keys, missing fields, names, dates) and the fix for each.

<p class="tool-privacy"><strong>Nothing is uploaded.</strong> The page reads your files in your browser and saves nothing.</p>

<!-- bibcheck-interactive-start -->

1. Paste `references.bib`, or choose or drop the file.
2. Optional: add `preamble.tex` (your citation style) and chapter `.tex`
   files to check the keys you cite.
3. Choose **Check references**, fix what it lists, then compile and look at
   the reference list in your PDF.

<div class="tool bibcheck" data-bibcheck hidden>
<label class="tool-drop tool-file" for="bibcheck-files" data-drop><span class="tool-file-button" data-icon="file">Choose files</span> <span class="tool-file-or">or drop references.bib and .tex files here</span></label><input class="visually-hidden" id="bibcheck-files" type="file" accept=".bib,.tex" multiple>
<p class="tool-file-names" data-file-names></p>
<label for="bibcheck-bib">Contents of references.bib</label>
<textarea id="bibcheck-bib" data-bib rows="10" spellcheck="false" placeholder="Paste references.bib here."></textarea>
<details><summary>Optional: add your style and citations</summary>
<p>Choose these files above or paste them here. File names other than preamble.tex are treated as chapters. A new chapter file selection replaces the previous chapter selection; pasted chapter text is checked as well.</p>
<label for="bibcheck-preamble">Contents of preamble.tex</label>
<textarea id="bibcheck-preamble" data-preamble rows="4" spellcheck="false" placeholder="Paste preamble.tex here."></textarea>
<label for="bibcheck-tex">Chapter .tex text (optional)</label>
<textarea id="bibcheck-tex" data-tex rows="5" spellcheck="false" placeholder="Paste chapter text here."></textarea>
<label><input type="checkbox" data-unused> Also list entries not cited in the supplied .tex files</label>
</details>
<p class="tool-actions"><button type="button" class="button" data-run data-icon="search">Check references</button> <button type="button" class="button button-secondary" data-clear data-icon="clear">Clear</button></p>
<div class="tool-status" role="status" aria-live="polite"></div>
<div class="tool-results tool-card" data-results></div>
</div>

<p class="tool-nojs" data-bibcheck-nojs>The check needs JavaScript, which is off or not available in this browser. Use the checklist below with your .bib file and PDF.</p>

<!-- bibcheck-interactive-end -->

## Read the results

Results are grouped by how they may affect your references:

- **May stop citations:** repeated keys, missing cited entries, or broken
  entry syntax. These can cause errors or unresolved citations in the PDF.
- **May print wrong:** missing usual fields, access dates, or a name that may
  be parsed incorrectly. Check the source before adding information.
- **Style advice:** fields worth adding, possible capitalization problems,
  and settings that may hide fields. Advice can be wrong for a particular
  source or a customized style.
- **Tidy-ups:** possible duplicate records, repeated DOI links, or entries
  not cited in the supplied chapters, if you requested that check.

Every point gives the key (the label after `@book{`, for example), the
field, and its line in the box (with the file name when you added several
`.bib` files). Choose the line to select that entry or field in the box.
Each point also suggests a fix and links to the guide section that explains
it. **By entry** lists the same points under each entry instead.

### Safe fixes

A few points have a fix the page can make for you. Each one shows the field
now and after the fix; nothing changes until you choose the button, one fix
at a time or all at once. The page offers a fix only when the change is
certain and keeps the meaning:

- escaping a literal `&`, `%`, `_`, or `#` in a text field (not in names,
  links, or math);
- keeping only the DOI when `doi` holds a full `https://doi.org/` address
  or starts with `doi:`;
- writing an English month name, such as `January`, as its number;
- moving a full date such as `2020-05-01` from `year` to `date`;
- adding a missing comma between two fields.

Fixes never add information, such as dates, DOIs, or pages, and never change
keys; everything else stays advice for you to check against the source. The
fixes change only the text in the box. Choose **Download** to save the
corrected file, and use it in place of your old one. **Undo the fixes**
restores the text from before them. If Zotero exported the file, correct the
record in Zotero as well and export again, or the next export replaces your
changes; see [auto-export cautions](citations.md#set-it-and-forget-it).

## Checklist without JavaScript

- [ ] <span id="checklist-keys"></span>Each key is unique, including capitalization; every cited key exists
  in a `.bib` file your document loads.
- [ ] <span id="checklist-fields"></span>Each entry has its usual fields: an article's author, title, journal,
  and date; a book's author or editor, title, date, and publisher; a chapter's
  book title and pages; a thesis or report's institution and type. Compare
  with the source and [your style guide](citations.md#step-1-agree-on-a-style-with-your-advisor).
- [ ] Each URL has `urldate = {YYYY-MM-DD}`, the date you read it, and that
  access date appears in the PDF. This follows the OGE manual §3.4 p. 34
  ([access dates](citations.md#web-sources-need-an-access-date)). DOIs alone
  do not need access dates.
- [ ] <span id="checklist-dates"></span>Publication dates use `date = {YYYY-MM-DD}` (or a year or year-month
  when that is all the source gives). A separate `year` is four digits;
  `month` is a number or a month macro such as `jan`.
- [ ] <span id="checklist-links"></span>`doi` contains the identifier, such as `10.1234/example`, rather than
  a full web address. Check DOI and ISBN digits against the source. Prefer
  HTTPS when the source supports it; remove a URL that only repeats the DOI
  if your style does not need both.
- [ ] People are separated with `and`; organizations have an extra pair of
  braces, such as `author = {{Example Institute}}`. Check particles, suffixes,
  and differing initials against the sources
  ([name examples](citations.md#if-you-cant-use-zotero-paste-an-entry-by-hand)).
- [ ] <span id="checklist-capitals"></span>Capitals that must survive sentence case have protection, such as
  `{NASA}` and `{Python}`. Protect proper names, rather than every word.
- [ ] <span id="checklist-special-characters"></span>Literal `&`, `%`, `_`, and `#` in text fields are escaped as `\&`,
  `\%`, `\_`, and `\#`. URL and DOI fields handle these characters
  separately. Mathematical expressions such as `$L_p$` keep their mathematical
  syntax. Braces balance, and accented names remain readable in UTF-8.
- [ ] The chosen style prints the information you need. A library's abstract,
  keywords, or attachment path normally does not appear in the reference
  list. `doi=false` or `url=false` in the style options can hide fields.

## Styles and limits

Without `preamble.tex`, the page uses the starter's `numeric` style for field
advice. It recognizes numeric, author–year, IEEE, APA, MLA, Chicago (including
`biblatex-chicago`), and ACS setups from the [style examples](citations.md#change-the-citation-style).
Unknown styles receive general checks with a notice. Field expectations are
starting points from the [biblatex manual](https://ctan.org/pkg/biblatex),
not a claim that every source must have every field. APA adds DOI or URL
advice. APA and IEEE add a review of unprotected capitals in English titles
(IEEE keeps book titles in title case); MLA, Chicago, and ACS add field
suggestions. See the [APA package manual](https://ctan.org/pkg/biblatex-apa)
and [IEEE style source](https://github.com/josephwright/biblatex-ieee/blob/main/ieee.bbx)
for their sentence-case behavior. Custom styles and field options can change
what prints.

This is a partial check, not Biber (the bibliography processor) or a style
review. It does not visit links, verify published facts, infer which chapter
files your document includes, or decide whether two similar names are the
same person. Citation commands hidden in custom commands may be missed.
It reads common braced and quoted entries, string macros defined before use,
and concatenated values. When an entry is missing a closing brace, the page
reports it and checks the following entries on their own. It skips citations
inside `\verb`, `\lstinline`, and verbatim or listing environments. Inherited fields (`crossref` or `xdata`) are reported
for review rather than treated as missing. Advanced date notation, custom
name formats, and custom data models may need manual review. Files are
limited to 5 MB per selection; split larger libraries before checking.

A clean result means these checks found nothing to flag. Follow
[Check the output yourself](citations.md#check-the-output-yourself) for the
references in your PDF.
