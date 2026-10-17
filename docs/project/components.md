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

> A quoted passage, shown with a rule at its left edge and softer text.

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

A tertiary text link, used for a secondary route:

<p><a class="text-link" href="#buttons-and-links">A text link<span class="arrow" aria-hidden="true">→</span></a></p>

---

Text after a horizontal rule.
