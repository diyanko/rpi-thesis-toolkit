# How it works

For anyone who wants to understand the RPI Thesis Toolkit, whatever your
LaTeX experience. You don't *need* this page to write, but when something
looks odd, knowing what happens behind the scenes turns a mystery into a
two-minute fix.

## The big idea

**Draft anywhere, format once.** Write early drafts wherever you like — Word,
Google Docs, Markdown, a notes app — and [bring the text in](bring-your-draft.md)
when you're ready. From then on, headings, numbering, captions, contents, and
references are formatted in one central place, the same way every time, so
you can stop formatting as you go.

Drafting elsewhere first? [Bring your draft](bring-your-draft.md#still-drafting-make-the-move-easy)
has tips that make the move a paste.

The same files can later feed a paper, slides, or a Word copy for a reviewer
([common situations](workflows.md#common-situations)) — a world of
possibilities, not a to-do list. Use only what you need.

![One source, many destinations. Your content files (chapters, figures, and references.bib) sit in the middle. Arrows lead outward to: the thesis PDF, through rpi-thesis.cls; a journal or conference paper, through the venue's class such as IEEEtran or acmart; slides, through Beamer; a Word copy for reviewers, through Pandoc; and a web page. A caption reads "a world of possibilities, not a to-do list".](diagrams/one-source-many-outputs.svg)

*In words:* your chapters and sources sit in the middle; the thesis PDF is the
one destination you need.

## Your words and your formatting are separate

`rpi-thesis.cls` is the **formatting engine**: margins, spacing, page numbers,
headings, captions, and the title page. Your files — `metadata.tex`, your
chapters, `references.bib` — hold the **content and settings**, and never say
how a page should look.

![Swapping the class file. On the left, your files (metadata.tex, frontmatter, chapters, appendices, figures, references.bib, preamble.tex) stay exactly as they are. In the middle, an old rpi-thesis.cls is replaced with a new one. On the right, recompiling produces a PDF with the same words in the updated formatting.](diagrams/class-swap.svg)

*In words:* your files + `rpi-thesis.cls` → your PDF. Replace the class file,
recompile, and the same words come out with the updated formatting.

So when OGE changes a rule, or the toolkit fixes something, you replace
**one file** and recompile; your chapters are untouched
([update the formatting safely](workflows.md#update-the-formatting-safely)). It is
also why you normally leave the class file alone: edits there would be lost in
the next update.

If you know Word, the difference is where formatting lives: Word keeps it
with your text, in each paragraph's style, so you see the final look as you
type. Here it lives in one separate file.

## What each file does

![File map of the project. main.tex is the starting point; it loads the class, then preamble.tex (packages, citation style, and the link to references.bib), metadata.tex (your name, degree, committee), then the front matter, the chapters, the reference list, and the appendices. rpi-thesis.cls supplies the formatting rules. Images live in figures/.](diagrams/file-map.svg)

| File or folder | What it is | Do you edit it? |
| --- | --- | --- |
| `main.tex` | The file you compile; lists which pieces go in, in order | To add or remove chapters or optional sections |
| `metadata.tex` | Your title, name, degree, department, date, and committee | Yes, first |
| `frontmatter/` | Abstract and acknowledgments | Yes |
| `chapters/` | One file per chapter | Yes — this is where you write |
| `appendices/` | Supplementary material, after the references | If you need it |
| `figures/` | Your images | Add files here |
| `references.bib` | Your list of sources, one entry each: exported from Zotero, or pasted by hand | Through Zotero, or by hand |
| `preamble.tex` | Extra packages and the citation style | Only to change style or add a package |
| `rpi-thesis.cls` | The formatting rules: margins, spacing, page numbers, headings, title page | Normally never |
| `assets/` | Where you put the RPI seal you download for the title page | Once, to [add the seal](get-started.md#add-the-rpi-seal-one-minute) |
| `build/` | Output from the build helper or VS Code | No — it is regenerated |

## What "compiling" does

**Compiling** turns your plain-text `.tex` files into a PDF. A full build runs
several programs in a row, usually pdfLaTeX → Biber → pdfLaTeX → pdfLaTeX,
repeated as needed:

![Build pipeline. Step 1: pdfLaTeX reads main.tex and writes notes about labels, headings, and the citations it needs. Step 2: Biber reads that citation list and references.bib and writes a formatted reference list. Step 3: pdfLaTeX runs again and places the references. Step 4: pdfLaTeX runs once more so page numbers in the contents and cross-references settle. One Compile runs these steps as often as needed. The result is main.pdf.](diagrams/build-pipeline.svg)

1. **pdfLaTeX** (first pass) lays out the pages and writes notes to itself:
   which labels and headings exist (`.aux`, `.toc`, `.lof`, `.lot`) and which
   citations you used (`.bcf`).
2. **Biber** reads that citation list and `references.bib`, and writes the
   formatted reference list (`.bbl`).
3. **pdfLaTeX** (second pass) reads the `.bbl` and puts in the references.
4. **pdfLaTeX** (third pass) settles page numbers in the contents and
   cross-references, which may have shifted when the references appeared.

Overleaf, VS Code, and the build helper run every step for you, repeating
passes until the output stops changing (via a tool called `latexmk`); in
TeXShop or TeXstudio you may run them yourself. After a
simple wording change, one pdfLaTeX pass is usually enough.

The extra files (`.aux`, `.bcf`, `.bbl`, `.toc`, …) are scratch notes you never
edit. The `.log` file is worth reading: it holds the full error messages.

### What the PDF looks like after each step

If you run the four steps one at a time, the sample thesis changes like this.

<!-- Each "preview" comment below becomes a picture on the website, made by
scripts/previews.py. GitHub hides them. If the sample thesis changes, check
that their alt text still matches the pictures. -->

**After step 1, pdfLaTeX.** Every page is laid out, but the citation shows its
key in bold, like [**lamport1994**], chapter numbers in cross-references show
as **??**, and the contents page is empty. So far pdfLaTeX has only written
its notes.

<!-- preview compile-pass-1-chapter: Chapter 1 after step 1. The sentence reads "a real citation example [lamport1994]" with the key in bold, then "Chapter ?? contains small examples you can adapt, and Chapter ?? closes the document." -->

<!-- preview compile-pass-1-contents: The contents page after step 1: the heading CONTENTS with nothing under it. -->

**After step 2, Biber.** Nothing in the PDF changes. Biber only writes the
formatted reference list (`main.bbl`) for the next pass.

**After step 3, pdfLaTeX.** The citation becomes a number, [1], the **??**
become chapter numbers, and the contents fill in. The References line may
still be missing, and the pages after it may show the wrong number, because
the reference list only arrived in this pass.

<!-- preview compile-pass-2-chapter: Chapter 1 after step 3: "a real citation example [1]", then "Chapter 2 contains small examples you can adapt, and Chapter 3 closes the document." -->

<!-- preview compile-pass-2-contents: The end of the contents after step 3: 3. Conclusion, page 4; 3.1 Future work, page 4; Appendices, page 5; A. Additional material, page 5. There is no References line. -->

**After step 4, pdfLaTeX.** The References line appears and the appendix
moves to its final page number. Nothing is left to settle.

<!-- preview compile-pass-3-contents: The end of the contents after step 4: 3. Conclusion, page 4; 3.1 Future work, page 4; References, page 5; Appendices, page 6; A. Additional material, page 6. -->

If a bold key or **??** is still there after all four steps, see
[bold citation keys and question marks](#bold-citation-keys-and-question-marks).

## Bold citation keys and question marks

These are LaTeX saying "I haven't finished filling this in yet".

| You see | It means | Fix |
| --- | --- | --- |
| A citation key in **bold**, like **lamport1994** | That citation is not in the formatted reference list yet | Run Biber, then compile twice. If it stays bold, check the key's spelling in both `\cite{}` and `references.bib` |
| **??** where a chapter, figure, or equation number should be | The `\ref{}` label is not known yet | Compile again. If it stays, check the `\label{}` and `\ref{}` spelling |
| An empty or outdated contents page | The contents are written on one pass and read on the next | Compile again |

## Where the PDF ends up

| How you compile | Your PDF |
| --- | --- |
| Overleaf | The preview pane; use Overleaf's download button for a copy |
| TeXShop or TeXstudio | `main.pdf`, next to `main.tex` |
| VS Code (with the included recipe) | `build/main.pdf` |
| Build helper (`python3 scripts/build.py`) | `build/main.pdf` |
| `latexmk` typed directly | `main.pdf`, next to `main.tex` |

Switched methods? Open the PDF from the method you just used, not an old copy.

## Your computer or Overleaf?

![Your computer compared with Overleaf. Both start from the same project files and run the same compile steps (pdfLaTeX, Biber, then pdfLaTeX twice, repeated as needed) to produce the same PDF. On your computer the files live in a folder you control, LaTeX is installed locally, and you work offline in an editor. On Overleaf the files and the LaTeX installation live on Overleaf's servers and you work in a browser.](diagrams/overleaf-vs-local.svg)

Same files, same programs, same PDF — only *where* things live differs. To
move or use both, see [workflows](workflows.md#use-your-computer-and-overleaf).

## Want to learn more LaTeX?

[Overleaf Learn](https://www.overleaf.com/learn) has friendly tutorials on
almost every topic, whichever editor you use. [CTAN](https://ctan.org/) holds
every package and its manual, including [biblatex](https://ctan.org/pkg/biblatex).
