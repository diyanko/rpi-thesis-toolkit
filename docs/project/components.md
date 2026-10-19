---
description: Maintainer page that shows every website component on one page, for design review in light and dark.
---

# Component gallery

A maintainer page for reviewing the website's design. It shows every piece
the guide uses, with placeholder text, so one pair of screenshots (light and
dark, from `python3 scripts/ui_check.py --shots`) covers the whole design.
Students never need this page; it is not linked from the guide.

When a new component appears in the guide, add one example of it here.

<p class="page-tag"><span class="tag tag-start">Start here</span> <span class="tag tag-now">Need now</span> <span class="tag tag-draft">If you have a draft</span> <span class="tag tag-stuck">When stuck</span> <span class="tag tag-later">Need later</span> <span class="tag tag-optional">Optional</span></p>

## Headings and text

Body text with a [link to another page](../writing.md), an
[external link](https://www.ctan.org/), **bold text**, *italic text*,
inline code such as `metadata.tex` or `chapters/01-introduction.tex`, a
longer phrase in code such as `\cite{lamport1994}`, a keyboard key
<kbd>Ctrl</kbd> + <kbd>S</kbd>, and <mark>highlighted text</mark>. A second
sentence makes the paragraph wrap, so line spacing and underline offsets are
visible across lines.

### A third-level heading

Text under a third-level heading.

#### A fourth-level heading

Text under a fourth-level heading.

## Lists

A bulleted list with a nested list:

- First item on one line.
- A second item long enough to wrap onto another line, so the bullet's
  alignment with the first line of text is visible.
  - A nested item.
  - Another nested item with `inline code`.
- Third item.

Numbered steps with a nested list and a code block:

1. Open `metadata.tex`.
2. Change the title, keeping the braces:

   ```tex
   \title{Your Thesis Title}
   ```

3. Compile again. If something looks wrong:
   1. Read the first error.
   2. Fix that line and compile again.

A list that starts at 9, to check two-digit numbers:

9. The ninth step.
10. The tenth step, long enough to wrap onto a second line so the wrapped
    text lines up under the first line.

A checklist (the boxes can be ticked; nothing is saved):

- [ ] An unticked item.
- [x] A ticked item.
- [ ] A longer item that wraps onto a second line, so the box stays on the
  first line and the wrapped text lines up with the text above it.

## Callouts

> [!NOTE]
> A note, with `inline code` and a [link](../citations.md).

> [!TIP]
> **A tip.** Compiling never changes your writing.

> [!IMPORTANT]
> Something to check before submitting.

> [!WARNING]
> A warning about a step that can lose work.

> [!CAUTION]
> A caution, styled like a warning.

A quotation:

> A quoted passage, indented and in softer italic text, with no rule at its edge.

## Table

| Setting | What it does | Example |
| --- | --- | --- |
| `degree` | Sets the degree on the title page | `doctoral` |
| `graduation-month` | The month you graduate | `May` |
| `\includegraphics[width=0.8\textwidth]{figures/my-plot}` | A long command that may break anywhere | Placeholder |

## Code

```tex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\textwidth]{figures/my-plot}
  \caption{A short caption.}
\end{figure}
```

```sh
python3 scripts/build.py
```

```prompt
An example prompt in ordinary sentences. Prompts wrap like text instead of scrolling sideways, because they are prose rather than code.
```

## Figure and diagram

![Placeholder diagram: your files stay the same while the class file is swapped, and recompiling updates the formatting.](../diagrams/class-swap.svg)

*In words:* a caption paragraph right after a picture reads as its caption.

A crop of the sample PDF (made by `build_site.py --previews`; absent otherwise). Its caption is the alt text's first clause, and on phones it scrolls sideways:

<!-- preview compile-pass-2-chapter: Chapter 1 after step 3: "a real citation example [1]", then "Chapter 2 contains small examples you can adapt, and Chapter 3 closes the document." -->

## Picture cards

Short cards that each show a drawing small; a card opens the drawing full
size (How it works, "Why LaTeX for a thesis").

<div class="benefit-cards">
<a class="benefit-card" href="../diagrams/class-swap.svg"><img class="benefit-thumb" src="../diagrams/class-swap.svg" alt="" width="720" height="430" loading="lazy"><strong>A card title</strong><span>One short line under it.</span></a>
<a class="benefit-card" href="../diagrams/move-a-chapter.svg"><img class="benefit-thumb" src="../diagrams/move-a-chapter.svg" alt="" width="720" height="456" loading="lazy"><strong>Another card</strong><span>Two short sentences. At most.</span></a>
</div>

## Disclosure

<details><summary>Optional: a closed section with a longer summary line that may wrap on phones</summary>

Text inside the disclosure, with a list:

- One item.
- Another item.

</details>

<details open><summary>Example: an open section</summary>

Text inside an open disclosure.

</details>

## Buttons and links

<p class="hero-actions"><a class="button" href="#buttons-and-links">Primary action</a> <a class="button button-secondary" href="#buttons-and-links">Secondary action</a> <a class="button" aria-disabled="true">Disabled</a></p>

Navigation links in the header, the sidebar and the footer share one set of
states: hover underlines the text, and the current page is the one sage pill.
No box anywhere carries a colored bar on one edge; status is said in words.

**Icons.** An action button opts into one hand-drawn icon with
`data-icon="..."` (copy, download, add, remove, clear, search, bulb, eye,
file, print, again, prev, next, check, undo; section 5 of `site/site.css`).
Use these for the same action everywhere; draw a new one only for a new kind
of action, in the same 24 px, 2 px stroke, slightly wobbly style.

<p class="tool-actions"><button type="button" class="button" data-icon="copy">Copy</button> <button type="button" class="button button-secondary" data-icon="download">Download .tex</button> <button type="button" class="button button-secondary button-small" data-icon="add">Add a member</button> <button type="button" class="button-quiet" data-icon="remove" aria-label="Remove"></button></p>

The quiet button (`.button-quiet`) is a 44 px icon with no edge until you
point at it, for a small action beside a field, such as removing a row.

**Action rows** (`.action-rows`, a list of `.card.help-card` items): one row
per way of doing something, its title and one line on the left and one
button on the right; stacked on phones. The Contribute page uses it.

**Header menus.** Guide and Tools in the header are native `<details>` menus
(they open without JavaScript; `site/theme.js` closes them on Esc or a click
elsewhere). The Tools menu takes each tool's doodle and one line from the
home page's list, so the two never disagree.

**Release answer.** On the website's change log, each version's
"Changes your PDF?" line becomes a stamp: No in sage, Yes in terra, Some in
plum (`changelog_page` in `scripts/build_site.py`).

A tertiary text link, used for a secondary route:

<p><a class="text-link" href="#buttons-and-links">A text link<span class="arrow" aria-hidden="true">→</span></a></p>

---

Text after a horizontal rule.


## Tool pages

Every tool (Settings builder, Convert to LaTeX, Check your references,
Explain my error, Check your PDF) follows one pattern, so a new tool reuses
it instead of adding styles. Tool pages (`PAGE_SCRIPTS` in
`scripts/build_site.py`) keep the same frame as every page, drop the
right-hand rail so the tool uses the whole main column, and show the tool's
doodle from the home page before the title. The classes live in section 12 of `site/site.css`.

1. **Purpose:** one or two short sentences under the title.
2. **Privacy:** `<p class="tool-privacy"><strong>Nothing is uploaded.</strong> ...</p>`,
   one sentence on what stays in the browser, drawn like a tip.
3. **Steps** (optional): three short numbered steps.
4. **Tool:** `<div class="tool NAME" data-NAME hidden>`; the script removes
   `hidden`. Inside: labels above fields; `.tool-drop` on the main paste area
   or drop zone; `.tool-file` for a file drop zone (a label around a
   `.tool-file-button`, with a visually hidden native input after it and a
   `.tool-file-names` line); `.tool-output` on read-only output (a `<pre>`
   with `data-empty` for its placeholder, colored by `site/tools-highlight.js`,
   labelled by a `.tool-label`); `.tool-actions` around
   the buttons (one `.button`, the rest `.button-secondary`); `.tool-status`
   for the one-line status; `.tool-results` (plus `.tool-card` for a single
   panel) for results.
5. **Preview** (optional): a live picture of the result beside the form on
   wide screens and under it otherwise, captioned as a sketch, never as the
   real output; the Settings builder's title page (`.settings-preview`) is
   the example. It uses the page's tokens, so it follows light and dark.
6. **No JavaScript:** `<p class="tool-nojs" data-NAME-nojs>`: "The X needs
   JavaScript, which is off or not available in this browser", then what to
   use instead (a table or checklist further down the page). The note waits
   a moment before showing, so a slow load does not flash it.

Wording: each result says what is wrong, why it matters in one clause, and
the fix, with a guide link. Every tool has a short message for empty input,
input that is too large, a wrong file type, nothing found, a clean result
("Looks fine"), and a failed copy or download. Rules and messages live in
data (the tool's `core.js` tables, `KNOWN_PROBLEMS` in `scripts/build.py`,
the settings schema), so a change is usually one row.

<p class="tool-privacy"><strong>Nothing is uploaded.</strong> The page reads your text in your browser and saves nothing.</p>

<div class="tool">
<label class="tool-drop tool-file" for="gallery-tool-file"><span class="tool-file-button">Choose files</span> <span class="tool-file-or">or drop them here</span></label><input class="visually-hidden" id="gallery-tool-file" type="file" multiple>
<p class="tool-file-names">Chosen: references.bib, preamble.tex</p>
<label for="gallery-tool-text">Your text</label>
<textarea id="gallery-tool-text" rows="3" spellcheck="false">@book{example, title = {An example}}</textarea>
<label><input type="checkbox"> An optional choice</label>
<p class="tool-actions"><button type="button" class="button">Check</button> <button type="button" class="button button-secondary">Clear</button></p>
<p class="tool-status">1 point to review. Nothing was uploaded.</p>
<div class="tool-results tool-card"><h3>Results</h3><h4>May print wrong (1)</h4><ul><li><strong>example — date or year:</strong> Check the source and add its publication date if available. <a href="../citations.md#check-the-output-yourself">Citations guide</a></li></ul></div>
<p class="tool-label" id="gallery-tool-output">Output to copy</p>
<pre class="tool-output" aria-labelledby="gallery-tool-output"><span class="tok-cmd">\thesissetup</span><span class="tok-brace">{</span>
  title = <span class="tok-brace">{</span>Your thesis title<span class="tok-brace">}</span>, <span class="tok-com">% a comment</span>
  committee = <span class="tok-brace">{</span><span class="tok-cmd">\member</span><span class="tok-opt">[</span><span class="tok-opt">Chair</span><span class="tok-opt">]</span><span class="tok-brace">{</span>Name<span class="tok-brace">}</span><span class="tok-brace">}</span>, <span class="tok-math">$x^2$</span>
<span class="tok-brace">}</span></pre>
</div>

<p class="tool-nojs">The tool needs JavaScript, which is off or not available in this browser. Use the checklist below instead.</p>

## Tool states

Every tool moves through the same four states, set by `ToolState.set` in
`site/tools-highlight.js` (each `ui.js` falls back to plain status text
without it). The status line is a `<div class="tool-status" role="status"
aria-live="polite">` under the actions; it keeps one line of room when empty,
so nothing jumps.

1. **Empty:** placeholders say what to paste in one short line ("Paste
   references.bib here."); output shows its `data-empty` line; buttons that
   need complete input are disabled (flat paper), and the others say what is
   missing when pressed.
2. **Working:** `data-state="working"` puts a small ring before the text
   (it turns only when motion is allowed); the tool gets `aria-busy="true"`,
   old results fade back, and the busy button gets `aria-disabled` and
   `data-busy`, so a second press does nothing.
3. **Error:** `data-state="error"` holds one `.tool-error` box: a short title,
   what happened and the fix, and a guide link. The live region announces it;
   focus stays where the student is, or moves to the field to fix.
4. **Done:** a one-line summary with counts in the status line, then the
   results; buttons that work on results move focus to the results heading.
   A clean result says what was checked, never that OGE will accept it.

Start over is always the last button in the tool's actions row: "Clear" on
the text tools, "Check another PDF" on Check your PDF. A drop zone turns blue
and dashed while a file is over it (`ToolState.dropZone`), on every tool.

<div class="tool">
<p class="tool-actions"><button type="button" class="button" data-busy aria-disabled="true">Check references</button> <button type="button" class="button button-secondary">Clear</button></p>
<div class="tool-status" data-state="working">Reading page 12 of 140…</div>
<div class="tool-status" data-state="error"><div class="tool-error"><p class="tool-error-title">That is not a PDF</p><p>draft.docx is not a PDF file. Choose the PDF your editor made, often main.pdf. <a href="../submission.md#final-pdf-checklist">Final PDF checklist</a>.</p></div></div>
<div class="tool-status" data-state="done">3 points to review in 42 entries. Nothing was uploaded.</div>
<p class="tool-actions"><button type="button" class="button" disabled>Copy settings</button> <button type="button" class="button button-secondary">Clear</button></p>
<label class="tool-drop tool-file is-over" for="gallery-over"><span class="tool-file-button">Choose files</span> <span class="tool-file-or">or drop them here (a file is over this zone)</span></label><input class="visually-hidden" id="gallery-over" type="file">
<label for="gallery-year">A field with a value to fix</label>
<input type="text" id="gallery-year" value="20255" aria-invalid="true">
</div>

## Form controls

Native controls drawn like the buttons: a sketchy edge, a small offset
shadow, the blue focus ring (press Tab to see it), and sage when chosen. They
live in section 12 of `site/site.css` and apply inside `.tool`. A yes/no
setting is a checkbox with `role="switch"` inside `<label class="tool-switch">`.
Tool output colors LaTeX with `site/tools-highlight.js`; guide code blocks
are colored when the site is built. Both use the `--code-*` tokens.

<div class="tool">
<fieldset><legend>A group of fields</legend>
<label for="gallery-text">A text field</label>
<input type="text" id="gallery-text" value="Department of Physics">
<label for="gallery-empty">An empty field</label>
<input type="text" id="gallery-empty" placeholder="A placeholder in muted text">
<label for="gallery-select">A menu</label>
<select id="gallery-select"><option>doctoral</option><option>masters</option></select>
<fieldset><legend>A nested group</legend>
<label for="gallery-nested">Full name</label>
<input type="text" id="gallery-nested">
</fieldset>
</fieldset>
<fieldset class="convert-options"><legend>Radio buttons</legend><label><input type="radio" name="gallery-radio" checked> <span>A chosen option</span></label><label><input type="radio" name="gallery-radio"> <span>Another option</span></label></fieldset>
<p><label><input type="checkbox" checked> A ticked checkbox</label></p>
<p><label><input type="checkbox"> An unticked checkbox with a longer label that wraps onto a second line on phones</label></p>
<p><label class="tool-switch"><input type="checkbox" role="switch" checked> <span>A switch that is on</span></label> <label class="tool-switch"><input type="checkbox" role="switch"> <span>A switch that is off</span></label></p>
<label for="gallery-area">A paste area</label>
<textarea class="tool-drop" id="gallery-area" rows="3" placeholder="Paste or drop text here."></textarea>
<label class="tool-drop tool-file" for="gallery-pdf"><span class="tool-file-button is-primary">Choose your PDF</span> <span class="tool-file-or">or drop it here</span></label><input class="visually-hidden" id="gallery-pdf" type="file">
<p class="tool-label" id="gallery-empty-output">Empty output</p>
<pre class="tool-output" data-empty="The LaTeX appears here." aria-labelledby="gallery-empty-output"></pre>
</div>
