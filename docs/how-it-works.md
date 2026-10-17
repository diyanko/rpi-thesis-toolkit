# How it works

Why LaTeX can suit a thesis, what happens when you press Compile, and how the
files fit together. You don't need this page to write, but it helps you decide
whether LaTeX suits you and, when something looks odd, find the next step.

**Learn a few commands, then let the shared formatting handle the repetition.**
You type or paste your text, and one file of formatting rules (the *class
file*, `rpi-thesis.cls`) keeps headings, numbering, and spacing consistent.
You still check the PDF.

## Why LaTeX for a thesis

Keep your attention on the chapter you are writing. Let shared rules handle
the repetition.

<div class="benefit-cards">
<a class="benefit-card" id="benefit-chapter" href="diagrams/one-chapter-at-a-time.svg" data-viewer="view-benefit-chapter"><strong>One chapter at a time</strong><span>Small files. One connected thesis.</span></a>
<a class="benefit-card" id="benefit-numbers" href="diagrams/move-a-chapter.svg" data-viewer="view-benefit-numbers"><strong>Let the numbers follow</strong><span>Move chapters. Keep references linked.</span></a>
<a class="benefit-card" id="benefit-formatting" href="diagrams/class-swap.svg" data-viewer="view-benefit-formatting"><strong>Shared formatting</strong><span>One class sets the shared rules.</span></a>
<a class="benefit-card" id="benefit-reuse" href="diagrams/one-source-many-outputs.svg" data-viewer="view-benefit-reuse"><strong>Reuse your source</strong><span>Adapt text and figures for another format.</span></a>
<a class="benefit-card" id="benefit-paste" href="diagrams/plain-text-shared-style.svg" data-viewer="view-benefit-paste"><strong>Leave stray styles behind</strong><span>Keep the words, without imported fonts.</span></a>
<a class="benefit-card" id="benefit-citations" href="diagrams/citation-flow.svg" data-viewer="view-benefit-citations"><strong>Keep citations connected</strong><span>Cite by key. Let the reference list follow.</span></a>
</div>

<dialog class="viewer benefit-preview" id="view-benefit-chapter" aria-label="One chapter at a time"><a class="viewer-close" href="#benefit-chapter">Close<span class="visually-hidden"> the picture</span></a><div class="viewer-pan" role="region" aria-label="Concept picture, scroll if needed"><picture><source media="(max-width: 600px)" srcset="diagrams/one-chapter-at-a-time-narrow.svg"><img src="diagrams/one-chapter-at-a-time.svg" alt="One chapter at a time: Small files. One connected thesis." width="640" height="400" loading="lazy"></picture></div></dialog>
<dialog class="viewer benefit-preview" id="view-benefit-numbers" aria-label="Let the numbers follow"><a class="viewer-close" href="#benefit-numbers">Close<span class="visually-hidden"> the picture</span></a><div class="viewer-pan" role="region" aria-label="Concept picture, scroll if needed"><picture><source media="(max-width: 600px)" srcset="diagrams/move-a-chapter-narrow.svg"><img src="diagrams/move-a-chapter.svg" alt="Let the numbers follow: Move chapters. Keep references linked." width="720" height="456" loading="lazy"></picture></div></dialog>
<dialog class="viewer benefit-preview" id="view-benefit-formatting" aria-label="Shared formatting"><a class="viewer-close" href="#benefit-formatting">Close<span class="visually-hidden"> the picture</span></a><div class="viewer-pan" role="region" aria-label="Concept picture, scroll if needed"><picture><source media="(max-width: 600px)" srcset="diagrams/class-swap-narrow.svg"><img src="diagrams/class-swap.svg" alt="Shared formatting: One class sets the shared rules." width="720" height="430" loading="lazy"></picture></div></dialog>
<dialog class="viewer benefit-preview benefit-caption" id="view-benefit-reuse" aria-label="Reuse your source"><a class="viewer-close" href="#benefit-reuse">Close<span class="visually-hidden"> the picture</span></a><p class="viewer-hint">Other formats need adaptation, conversion and review.</p><div class="viewer-pan" role="region" aria-label="Concept picture, scroll if needed"><picture><source media="(max-width: 600px)" srcset="diagrams/one-source-many-outputs-narrow.svg"><img src="diagrams/one-source-many-outputs.svg" alt="Reuse your source: Adapt text and figures for another format." width="720" height="600" loading="lazy"></picture></div></dialog>
<dialog class="viewer benefit-preview" id="view-benefit-paste" aria-label="Leave stray styles behind"><a class="viewer-close" href="#benefit-paste">Close<span class="visually-hidden"> the picture</span></a><div class="viewer-pan" role="region" aria-label="Concept picture, scroll if needed"><picture><source media="(max-width: 600px)" srcset="diagrams/plain-text-shared-style-narrow.svg"><img src="diagrams/plain-text-shared-style.svg" alt="Copied text with mixed styles becomes plain chapter text, then takes the shared document formatting." width="720" height="400" loading="lazy"></picture></div></dialog>
<dialog class="viewer benefit-preview benefit-caption" id="view-benefit-citations" aria-label="Keep citations connected"><a class="viewer-close" href="#benefit-citations">Close<span class="visually-hidden"> the picture</span></a><p class="viewer-hint">Choose your citation style and the matching commands. Zotero is optional.</p><div class="viewer-pan" role="region" aria-label="Concept picture, scroll if needed"><picture><source media="(max-width: 600px)" srcset="diagrams/citation-flow-narrow.svg"><img src="diagrams/citation-flow.svg" alt="Bibliography records and citation keys feed the formatted citations and reference list when you compile." width="720" height="612" loading="lazy"></picture></div></dialog>

Word can automate too. Its
[styles and fields need to be kept in step](https://support.microsoft.com/en-au/word/update-fields),
and [pasted text can bring its own formatting](https://support.microsoft.com/en-us/word/control-the-formatting-when-you-paste-text).
LaTeX was built for mathematics, so displayed equations are laid out and
numbered for you. It is free, and your files are plain text that
[back up like any folder](going-further.md#back-up-your-work).

**You only need about 10 commands.** A *command* is a short instruction that
starts with a backslash, such as `\section{Methods}`. Headings, citations,
cross-references, figures, tables, and equations cover most of a thesis, and
they fit in one table at the top of
[writing basics](writing.md#the-10-commands-youll-actually-use). For references,
[choose the citation style and matching commands](citations.md#change-the-citation-style).

<span id="see-it-in-action"></span>

## Change one word, watch the layout

The same words can look very different under another set of formatting
rules. This teaching example uses the American Mathematical Society's
[`amsart` class](https://ctan.org/pkg/amsart) for one column. Change
`amsart` to [`IEEEtran`](https://ctan.org/pkg/ieeetran) in
`\documentclass{amsart}`, compile again, and the headings, captions,
spacing, and columns follow the new class.

<!-- class-demo -->

*In words:* one example, two academic layouts. Only the class name changes.

*Note:* this article example does not use the RPI thesis starter. A real
[chapter-to-paper move](going-further.md#turn-a-chapter-into-a-paper) also means
adapting thesis-only commands, then checking the PDF.

<details><summary>Optional: try the one-word change yourself</summary>

In a separate, empty LaTeX project on your computer or Overleaf, paste this
example into the main file and compile. Replace `amsart` with `IEEEtran` on
the first line and compile again. Leave your thesis project as it is. A
missing `.cls` error means that class is not installed.

The pictures above are compiled from this example and show the first page of
each version. The counts in the example are invented for teaching.

<!-- class-demo-source -->
```latex
\documentclass{amsart}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\title{Grouping a Small Reading List}
\author{A teaching example}
\date{}
\begin{document}
\maketitle
\section{Start with a question}
A reading list can grow faster than the notes that explain it. A useful first
step is to give every note a purpose: background, method, or discussion.
These labels describe what a note contributes to the current question. They
do not rank the quality of a source or replace a careful reading of it.

This short document uses invented counts to demonstrate headings, a table,
an equation, a figure, and references to numbered items. It reports no
research findings. The same source can be compiled with two document classes
so that the effect of the formatting rules is visible.

Suppose a reader begins with a folder of notes collected during an early
literature search. Some notes define terms, others explain procedures, and
others record disagreements or open questions. The folder becomes easier to
navigate when those roles are explicit. A note may still link to more than
one topic; the group is only a starting point for finding it again.
\section{Describe the collection}
Table~\ref{tab:notes} gives a small example. The counts describe notes rather
than publications: one publication might produce several notes, and a
single note might connect ideas from several publications. Keeping that
unit clear avoids confusing the size of the collection with its coverage.

\begin{table}[htbp]
\caption{Invented counts for three groups of notes.}
\label{tab:notes}
\centering
\begin{tabular}{lr}
\hline
Group & Notes \\
\hline
Background & 12 \\
Methods & 18 \\
Discussion & 15 \\
\hline
\end{tabular}
\end{table}

The arithmetic mean provides one description of the group sizes:
\begin{equation}
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i.
\label{eq:mean}
\end{equation}
For the three counts in Table~\ref{tab:notes}, Equation~\ref{eq:mean} gives a
mean of fifteen notes per group. That number says nothing about whether the
reading list is complete. A small group might contain the most useful
source, while a large group might repeat the same point many times.
\section{Review the organization}
The sequence in Figure~\ref{fig:review} is a reminder to revisit the groups.
Read a source, record its contribution, then review where the note belongs.
A label chosen early in a project may become less useful when the question
changes. Moving a note is part of organizing the collection, rather than a
sign that the first arrangement was wrong.

\begin{figure}[htbp]
\centering
\setlength{\unitlength}{1pt}
\begin{picture}(210,34)
\put(0,7){\framebox(54,22){Read}}
\put(54,18){\vector(1,0){24}}
\put(78,7){\framebox(54,22){Group}}
\put(132,18){\vector(1,0){24}}
\put(156,7){\framebox(54,22){Review}}
\end{picture}
\caption{A short sequence for revisiting a reading list.}
\label{fig:review}
\end{figure}

A useful review asks whether each group still answers a distinct question.
If two groups always contain the same notes, they may be easier to use as
one group. If a group contains several unrelated topics, a more specific
label may help. The purpose is to make the next writing session easier,
without spending more time organizing than reading and thinking.
\section{Keep enough context}
A brief note should say why the source mattered when it was read. A copied
sentence without context can be hard to interpret later. Recording the
question, the relevant page, and the source's role gives the reader a route
back to the original material. The original source remains the place to
check an interpretation before using it in a draft.

It can also help to distinguish a summary from a question or a proposed
connection. Those are different kinds of notes, even when they sit beside
each other. A clear label preserves that distinction when the collection is
revisited after a long break. No particular note-taking application is
needed for this exercise.
\section{Read the page as well as the source}
The document class decides how the title, headings, captions, and columns
appear. The source identifies their roles rather than fixing each item at
a position on a page. Paragraphs wrap to the available width, and figures
or tables may move to make room for surrounding text.

In both versions, the equation, table, figure, and cross-references contain
the same information. The single-column and two-column pages arrange that
information differently. Look at the heading styles and caption numbering
as well as the column widths: several formatting choices follow from the
same class-name change.

This example uses commands shared by both classes. A real journal paper
also needs the venue's author instructions, suitable references, and a
check of every page. Reusing content can save repeated formatting work;
it does not remove the need to revise the argument for its audience.
\end{document}
```

</details>

## The honest costs

- **A first week of getting used to it.** You see the formatted page when you
  compile, not as you type.
- **Errors look scary.** They are long, but the useful part names a file and
  a line ([read an error message](troubleshooting.md#read-an-error-message)).
- **Advisors who prefer Word.** Send a PDF to comment on, or a Word copy, and
  apply their edits by hand ([common situations](going-further.md#common-situations)).
- **Tables take a bit more effort.** Copy the sample chapters' example and
  adapt it.
- **The Office of Graduate Education (OGE) can't debug LaTeX.** Its staff
  review your formatting, not your code
  ([ask for help](troubleshooting.md#ask-for-help)).

## When Word might still make sense

- Your thesis is short, with no equations and few figures or tables.
- Your committee edits only in Word, and you would rather not manage review copies.
- You must submit within days and have never used LaTeX.

OGE provides its own Word template, available from the
[OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation).
Either route can lead to a thesis OGE accepts.

An AI chat can help you get unstuck, as one route beside web search and
[community help](troubleshooting.md#ask-for-help)
([AI for technical help](going-further.md#use-ai-for-technical-help)).

## Your words and your formatting are separate

Each chapter is its own file, your sources live in `references.bib`, and your
images live in `figures/`. One more file, `rpi-thesis.cls`, is the **formatting
engine**: margins, spacing, page numbers, headings, captions, and the title
page. Your files hold content and settings, and never say how a page should
look.

![Swapping the class file. On the left, your files (metadata.tex, frontmatter, chapters, appendices, figures, references.bib, preamble.tex) stay exactly as they are. In the middle, an old rpi-thesis.cls is replaced with a new one, with a note that this is for compatible updates and to see the changelog. On the right, recompiling produces a PDF with the same words in the updated formatting.](diagrams/class-swap.svg)

*In words:* your files + `rpi-thesis.cls` give your PDF. Replace the class
file, recompile, and the same words come out with the updated formatting
(check the changelog first: an update may need other edits, see
[update the formatting safely](going-further.md#update-the-formatting-safely)).

So when OGE changes a rule or the toolkit fixes something, you usually replace
**one file** and your chapters are untouched.

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

**Compiling** turns your plain-text `.tex` files into a PDF. A full compile runs
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
your editor's compile ([your computer](get-started.md#step-3a-your-computer-route)
or [Overleaf](get-started.md#step-3b-overleaf-route));
if it does not clear, try a [clean recompile](troubleshooting.md#clean-recompile);
if you run each program yourself, follow the
[other-editor compile steps](get-started.md#other-editors-and-the-command-line).

| You see | It means | Fix |
| --- | --- | --- |
| A citation key in **bold**, like **lamport1994** | Not in the reference list yet | Run a full compile. If it stays bold, check the key's spelling in your citation command and in `references.bib` |
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

![Your computer compared with Overleaf. Both start from the same project files and run the same compile steps (pdfLaTeX, Biber, then pdfLaTeX twice, repeated as needed), so they produce matching PDFs when both use the same files, engine, packages, and fonts. On your computer the files live in a folder you control, LaTeX is installed locally, and you work offline in an editor. On Overleaf the files and the LaTeX installation live on Overleaf's servers and you work in a browser.](diagrams/overleaf-vs-local.svg)

Same files, same programs; only *where* things live differs. The PDFs match when
both use matching files, engine, packages, and fonts. Overleaf lets you choose
the TeX distribution version in its settings.
To move or use both, see [going further](going-further.md#use-your-computer-and-overleaf).

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

More recipes are in [going further](going-further.md).

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
[an advisor wants Word](going-further.md#an-advisor-wants-word-with-track-changes)).

### Reuse your material elsewhere

![One source, many destinations. Your content files (chapters, figures, and references.bib) sit in the middle. Arrows lead outward to: the thesis PDF, through rpi-thesis.cls; a journal or conference paper, through the venue's class such as IEEEtran or acmart; slides, through Beamer; a Word copy for reviewers, through Pandoc; and a web page. A caption reads "a world of possibilities, not a to-do list".](diagrams/one-source-many-outputs.svg)

*In words:* your chapters and sources sit in the middle; the thesis PDF is the
one destination you need, and the others are options.

Reuse is a head start, not a copy: each output needs its own template, some
cleanup, and a check against its own requirements, and this toolkit's
formatting is only for RPI graduate theses.
[Going further](going-further.md#turn-a-chapter-into-a-paper) has recipes.

One habit pays off everywhere: a citation typed as text, such as "(Lamport,
1994)", is not a citation key such as `lamport1994`. Only the key, matched to
an entry in `references.bib`, lets LaTeX build the citation and reference list,
so [collect real records early](citations.md#step-2-collect-and-cite-sources-with-zotero)
and keep their keys stable. For a tool for a specific task, try the
[helper picker](writing.md#helpers-for-common-tasks) or the
[How do I…? task index](how-do-i.md).

## Want to learn more LaTeX?

[Overleaf Learn](https://www.overleaf.com/learn) has friendly tutorials on
almost every topic, whichever editor you use. [CTAN](https://ctan.org/) holds
every package and its manual, including [biblatex](https://ctan.org/pkg/biblatex).
