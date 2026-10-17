# Bring your work in

Paste a section of your draft from Word, Google Docs, a spreadsheet, or a
Markdown or text file; the page writes it as LaTeX for the starter. It is a
first pass: read it next to your original, and move one section at a time.

<p class="tool-privacy"><strong>Nothing is uploaded.</strong> The page converts your text in your browser. Nothing in what you paste is loaded or run, not even pictures, and nothing is saved when you leave the page.</p>

<div class="tool convert" data-convert hidden><fieldset class="convert-options"><legend>Start the LaTeX with</legend><label><input type="radio" name="convert-start" value="body" checked> <span>Part of a chapter: headings become <code>\section</code></span></label><label><input type="radio" name="convert-start" value="chapter"> <span>A new chapter: the first heading becomes <code>\chapter</code></span></label></fieldset><div class="convert-panes"><div class="convert-pane"><label class="convert-label" for="convert-input">Your text</label><textarea class="convert-input tool-drop" id="convert-input" spellcheck="false" autocomplete="off" aria-describedby="convert-hint" placeholder="Paste or drop text from Word, Google Docs, Excel, Google Sheets, or a Markdown or text file."></textarea><p class="visually-hidden" id="convert-hint">From Word, Google Docs, Excel, Google Sheets, or a Markdown or text file.</p><p class="convert-actions tool-actions"><button type="button" class="button button-secondary convert-example">Show an example</button> <button type="button" class="button button-secondary convert-clear">Clear</button></p></div><div class="convert-pane"><p class="convert-label tool-label" id="convert-output-label">LaTeX <span class="convert-source"></span></p><pre class="convert-output tool-output" data-empty="The LaTeX appears here." aria-labelledby="convert-output-label"></pre><p class="convert-actions tool-actions"><button type="button" class="button convert-copy" disabled>Copy</button> <button type="button" class="button button-secondary convert-download" disabled>Download .tex</button></p></div></div><p class="convert-status tool-status" role="status" aria-live="polite"></p><div class="convert-results tool-results"></div></div>

<p class="convert-nojs tool-nojs" data-convert-nojs>The converter needs JavaScript, which is off or not available in this browser. The same steps by hand are under <a href="#without-the-converter">without the converter</a>.</p>

<!-- TODO(verify): the readers follow the clipboard shapes Word, Google Docs, Excel, and Google Sheets are known to write, tested on synthetic samples; check them with text copied from current Word (Windows and macOS) and Google Docs. -->

## What it converts

| In your draft | In the LaTeX |
| --- | --- |
| Heading 1, 2, 3 (or `#`, `##`, `###` in Markdown) | `\section`, `\subsection`, `\subsubsection`. With **A new chapter**, the first level becomes `\chapter`, in CAPITALS, with a `\label` |
| Paragraphs | Paragraphs, with a blank line between them |
| **Bold** and *italics* | `\textbf{...}` and `\emph{...}` |
| Bulleted and numbered lists | `itemize` and `enumerate`, one `\item` each |
| Links to web and e-mail addresses | `\url{...}` or `\href{...}{...}` |
| A table, or cells copied from Excel or Google Sheets | The starter's [table](writing.md#edit-a-table): caption above, a `\label`, and rules from `booktabs` |
| `%` `&` `_` `#` `$` `{` `}` `~` `^` `\` | `\%` `\&` `\_` `\#` `\$` and so on, so they print as typed |
| Greek letters and math signs, such as α and ± | `\ensuremath{\alpha}`, `\ensuremath{\pm}` |
| In Markdown: `$x$` and `$$ ... $$` | `$x$` unchanged; a numbered `equation` with a `\label` |

Choose **Part of a chapter** for a section that goes into an existing
chapter file, and **A new chapter** for a whole chapter in a file of its own.

## What it leaves for you

Under the LaTeX, the page lists what it did not convert, with a link to the
guide section that shows how.

- **Pictures:** a `%` line marks where each one was. Save the picture in
  `figures/` and [add a figure](writing.md#add-a-figure).
- **Footnotes:** each marker stays as text, such as `[1]`. Move the footnote
  text into `\footnote{...}` at its marker.
- **Equations from Word:** each is marked `[equation]`. Write it again in
  LaTeX ([equations](writing.md#equations)).
- **Comments** from Word or Google Docs are left out.
- **Citations:** typed citations and citation-manager fields stay as text.
  Change each one to `\parencite{key}` with the key from `references.bib`
  ([cite a source](writing.md#cite-a-source)).
- **Cross-references:** "see Figure 3" stays as typed; change it to
  `Figure~\ref{fig:...}` ([cross-references](writing.md#cross-references)).
- **Merged table cells** are split into separate cells; check them.
- **Files:** Word, Excel, and PowerPoint files are not read yet. Open the
  file, select the text, copy it, and paste it here. A long `.docx` can go
  through [Pandoc](bring-your-draft.md#convert-a-draft-with-pandoc-optional)
  instead.

## Put it in your thesis

1. **Part of a chapter:** open the chapter file in `chapters/` where the text
   belongs, and paste it below the `\chapter{...}` and `\label{...}` lines.
2. **A new chapter:** **Download .tex**, save it in `chapters/` with a name
   that keeps the order, such as `04-methods.tex`, and add
   `\include{chapters/04-methods}` to `main.tex` after the other `\include`
   lines ([add a chapter](writing.md#chapters)).
3. **Compile.** If an error appears, it is almost always in the part you just
   pasted ([fixing problems](troubleshooting.md)). Then compare every
   heading, table, and number with your original.

## Without the converter

The same steps by hand, which also work without JavaScript:

1. Copy the text into a chapter file ([add a chapter](writing.md#chapters)).
2. Mark the headings with `\section{...}` or `\subsection{...}`, bold with
   `\textbf{...}`, and italics with `\emph{...}`.
3. Put a backslash before special characters in ordinary text: `%` → `\%`,
   `&` → `\&`, `_` → `\_`, `$` → `\$`, `#` → `\#`.
4. Rebuild tables from the [table example](writing.md#edit-a-table), or with
   [a spreadsheet helper](writing.md#make-a-table-from-a-spreadsheet).
5. Compile, and fix the first error before moving the next section.

[Bring your draft](bring-your-draft.md) has the full route for Word, Google
Docs, Markdown, and LaTeX papers, including Pandoc for long documents.
