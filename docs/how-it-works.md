# How it works

A friendly look behind the curtain, for anyone curious about how the files fit
together and what happens when you press Compile. You don't need this page to
write, but when something looks odd, it helps you find the next step.

## Your words and your formatting are separate

Each chapter is its own file, your sources live in `references.bib`, and your
images live in `figures/`. One more file, `rpi-thesis.cls`, is the **formatting
engine**: margins, spacing, page numbers, headings, captions, and the title
page. Your files hold content and settings, and never say how a page should
look.

![Swapping the class file. On the left, your files (metadata.tex, frontmatter, chapters, appendices, figures, references.bib, preamble.tex) stay exactly as they are. In the middle, an old rpi-thesis.cls is replaced with a new one, with a note that this is for compatible updates and to see the changelog. On the right, recompiling produces a PDF with the same words in the updated formatting.](diagrams/class-swap.svg)

*In words:* your files + `rpi-thesis.cls` give your PDF. Replace the class
file, recompile, and the same words come out with the updated formatting
(during beta, check the changelog for any other edit).

So when OGE changes a rule or the toolkit fixes something, you usually replace **one
file** and your chapters are untouched. While the toolkit is in beta, an
update may also need a small edit elsewhere; the changelog lists it
([update the formatting safely](workflows.md#update-the-formatting-safely)).
That is also why you normally leave the class file alone: edits there would be
lost in the next update. (If you know Word, formatting lives with your text
there; here it lives in one separate file.)

What the class takes care of on every page:

![Two thesis pages. Front matter (ABSTRACT): heading at the top margin, centered, bold; double-spaced text; 1 inch margins on all sides; roman page number (vi) bottom center, 0.75 inch from the edge. Body page: arabic page number top right, 0.75 inch from the edge; bold table caption above the table and bold figure caption below the figure; single-spaced footnotes. Chapter-opening pages put the number at the bottom center. Margins, page numbers, spacing, and caption style are set once in rpi-thesis.cls.](diagrams/page-anatomy.svg)

*In words:* 1-inch margins, page numbers in the right place (roman, then
arabic), double spacing, bold captions, and single-spaced footnotes. You still
type your headings and decide where each caption goes.

## What each file does

| File or folder | What it is | Do you edit it? |
| --- | --- | --- |
| `main.tex` | The file you compile; lists the pieces in order | To add or remove chapters |
| `metadata.tex` | Your title, name, degree, and committee | Yes, first |
| `frontmatter/` | Abstract and acknowledgments | Yes |
| `chapters/` | One file per chapter | Yes: you write here |
| `appendices/` | Supplementary material | If you need it |
| `figures/` | Your images | Add files here |
| `references.bib` | Your sources, one entry each | Through Zotero, or by hand |
| `preamble.tex` | Extra packages (add-ons) and the citation style | Rarely |
| `rpi-thesis.cls` | The formatting rules | Normally never |
| `assets/` | Where the RPI seal you download goes | Once, to [add the seal](get-started.md#add-the-rpi-seal-one-minute) |
| `build/` | Output from the build helper or VS Code | No, it is regenerated |

## What "compiling" does

**Compiling** turns your plain-text `.tex` files into a PDF. A full build runs
several programs in a row, repeated as needed:

![Build pipeline. Step 1: pdfLaTeX reads main.tex and writes notes about labels, headings, and the citations it needs. Step 2: Biber reads that citation list and references.bib and writes a formatted reference list. Step 3: pdfLaTeX runs again and places the references. Step 4: pdfLaTeX runs once more so page numbers in the contents and cross-references settle. One Compile runs these steps as often as needed. The result is main.pdf.](diagrams/build-pipeline.svg)

1. **pdfLaTeX** lays out the pages and writes notes to itself: which labels
   and headings exist, and which citations you used. At this point a citation
   shows its key in bold, like [**lamport1994**], cross-references show **??**,
   and the contents page is empty.
2. **Biber** reads those notes and `references.bib`, and writes the formatted
   reference list (`.bbl`). The PDF does not change yet.
3. **pdfLaTeX** reads the `.bbl`: the citation becomes [1], the **??** become
   chapter numbers, and the contents fill in.
4. **pdfLaTeX** once more settles page numbers in the contents and
   cross-references, which shifted when the references appeared.

<!-- Each "preview" comment below becomes a picture on the website, made by
scripts/previews.py. GitHub hides them. If the sample thesis changes, check
that their alt text still matches the pictures. -->

<!-- preview compile-pass-1-chapter: Chapter 1 after step 1. The sentence reads "a real citation example [lamport1994]" with the key in bold, then "Chapter ?? contains small examples you can adapt, and Chapter ?? closes the document." -->

<!-- preview compile-pass-2-chapter: Chapter 1 after step 3: "a real citation example [1]", then "Chapter 2 contains small examples you can adapt, and Chapter 3 closes the document." -->

Overleaf, VS Code, and the build helper run every step for you, repeating
passes until the output stops changing (via a tool called `latexmk`). The extra
files (`.aux`, `.bbl`, `.toc`, ...) are scratch notes you never edit; the
`.log` file holds the full error messages and is worth reading.

## Bold citation keys and question marks

These are LaTeX saying "I haven't finished filling this in yet". Start with
your editor's compile ([first compile](get-started.md#step-4-your-first-compile));
if it does not clear, try a [clean recompile](troubleshooting.md#clean-recompile);
if you run each program yourself, follow the
[other-editor compile steps](get-started.md#other-editors-and-the-command-line).

| You see | It means | Fix |
| --- | --- | --- |
| A citation key in **bold**, like **lamport1994** | Not in the reference list yet | Run a full compile. If it stays bold, check the key's spelling in `\cite{}` and `references.bib` |
| **??** where a number should be | The `\ref{}` label is not known yet | Compile again. If it stays, check `\label{}` and `\ref{}` |
| An empty or outdated contents page | Written on one pass, read on the next | Compile again |

## Where the PDF ends up

| How you compile | Your PDF |
| --- | --- |
| Overleaf | The preview pane; use its download button for a copy |
| TeXShop or TeXstudio | `main.pdf`, next to `main.tex` |
| VS Code (included recipe) | `build/main.pdf` |
| Optional build helper (`python3 scripts/build.py`, or `py scripts/build.py` on Windows, typed in a terminal) | `build/main.pdf` |
| `latexmk` in a terminal | `main.pdf`, next to `main.tex` |

Switched methods? Open the PDF from the method you just used, not an old copy.

## Your computer or Overleaf?

![Your computer compared with Overleaf. Both start from the same project files and run the same compile steps (pdfLaTeX, Biber, then pdfLaTeX twice, repeated as needed), so they produce matching PDFs when both use a current TeX setup. On your computer the files live in a folder you control, LaTeX is installed locally, and you work offline in an editor. On Overleaf the files and the LaTeX installation live on Overleaf's servers and you work in a browser.](diagrams/overleaf-vs-local.svg)

Same files, same programs; only *where* things live differs. The PDFs match when
both use the same TeX version (Overleaf lets you choose one in its settings).
To move or use both, see [workflows](workflows.md#use-your-computer-and-overleaf).

## The suggested workflow, and why

A thesis is not just a document you format at the end. This is one way to
connect drafting, advisor feedback, sources, and figures. It is a suggestion,
not a rule; you and your advisor decide how you work.

![Research-writing workflow. Drafting and advisor review, in a drafting app or directly in the thesis files, feed three kinds of thesis material: chapter files, figures with the files they were made from, and references collected in a citation manager and exported to references.bib. These come together when you compile, into one thesis PDF formatted by rpi-thesis.cls. Arrows loop back from the thesis to drafting and review for the next round of revision.](diagrams/research-workflow.svg)

*In words:* draft and discuss, then chapter files, figures, and references,
then compile into one thesis, then review and loop back.

**Required versus suggested.** OGE's manual and your degree checklist, on the
[OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation),
are what count, and they win over anything here ([submitting](submission.md)).
`rpi-thesis.cls` is the toolkit's reading of those rules, starting from RPI's
official LaTeX template on RPI ITS's
[Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation),
so you still check the PDF ([what OGE commonly flags](submission.md#what-oge-commonly-flags)).
Everything else here, from drafting apps and Zotero to
[optional helpers](writing.md#helpers-for-common-tasks), is a convenience you
can swap out.

**The short version** (the steps overlap and repeat):

1. **Talk about your research early.** Feedback on your argument is worth more
   before the layout matters. Already have a stable draft or published papers?
   [Bring them in](bring-your-draft.md) now.
2. **Draft where you and your advisor are comfortable** ([below](#draft-where-you-and-your-advisor-can-work-comfortably)).
   At ease in LaTeX? Drafting in the chapter files skips the move later.
3. **Keep references and figure sources organized.** Save real source records
   in a citation manager while you read, and keep each figure's data or
   editable drawing beside it in `figures/`. With only a few sources,
   [pasting entries by hand](citations.md#if-you-cant-use-zotero-paste-an-entry-by-hand)
   is fine.
4. **Move stable material in gradually,** one section or chapter at a time.
   Try one small section early, with a figure and a few citations, so any
   conversion problems show up long before a deadline.
5. **Compile and look through the whole PDF every so often,** not only at the
   end. Before you submit, use the [final PDF checklist](submission.md#final-pdf-checklist).

More recipes are in [workflows](workflows.md).

### Draft where you and your advisor can work comfortably

Use what lets you and your advisor read, comment, and revise without
friction; you don't need a new app to start. If you are choosing, this guide
suggests a Markdown tool: plain text with a few symbols for structure, such as
`#` before a heading. You never need to learn it to use this toolkit, but your
draft stays a readable file in any editor, and free tools such as Pandoc can
convert it to LaTeX, Word, or slides. Four apps, for different situations:

- **[Obsidian](https://obsidian.md/):** Markdown files on your own computer.
  You can share a vault (a folder of notes), but that is not simultaneous
  editing of one file
  ([Obsidian: collaborate on a shared vault](https://help.obsidian.md/sync/collaborate)).
- **[HackMD](https://hackmd.io/):** collaborative Markdown in your browser.
- **[Google Docs](https://workspace.google.com/products/docs/):** live
  co-writing and comments, familiar to many advisors.
- **[Notion](https://www.notion.com/):** if you already use it. It is
  block-based, not a folder of Markdown files, but it can
  [export your pages as Markdown](https://www.notion.com/help/export-your-content).

App-specific links, embeds, citations, and math syntax may need cleanup when
you export. **Word** works too, for an existing draft or an advisor who reviews
in Word ([from Word or Google Docs](bring-your-draft.md#from-word-or-google-docs),
[an advisor wants Word](workflows.md#an-advisor-wants-word-with-track-changes)).

### Reuse your material elsewhere

![One source, many destinations. Your content files (chapters, figures, and references.bib) sit in the middle. Arrows lead outward to: the thesis PDF, through rpi-thesis.cls; a journal or conference paper, through the venue's class such as IEEEtran or acmart; slides, through Beamer; a Word copy for reviewers, through Pandoc; and a web page. A caption reads "a world of possibilities, not a to-do list".](diagrams/one-source-many-outputs.svg)

*In words:* your chapters and sources sit in the middle; the thesis PDF is the
one destination you need, and the others are options.

Reuse is a head start, not a copy: each output needs its own template, some
cleanup, and a check against its own requirements, and this toolkit's
formatting is only for RPI graduate theses.
[Workflows](workflows.md#turn-a-chapter-into-a-paper) has recipes.

One habit pays off everywhere: a citation typed as text, such as "(Lamport,
1994)", is not a citation key such as `lamport1994`. Only the key, matched to
an entry in `references.bib`, lets LaTeX build the citation and reference list,
so [collect real records early](citations.md#step-2-collect-and-cite-sources-with-zotero)
and keep their keys stable. For a tool for a specific task, try the
[helper picker](writing.md#helpers-for-common-tasks) or the
[How do I...? task index](how-do-i.md).

## Want to learn more LaTeX?

[Overleaf Learn](https://www.overleaf.com/learn) has friendly tutorials on
almost every topic, whichever editor you use. [CTAN](https://ctan.org/) holds
every package and its manual, including [biblatex](https://ctan.org/pkg/biblatex).
