# Why LaTeX for your thesis?

For anyone deciding how to write a thesis, dissertation, or other long
document, whether or not you have used LaTeX before.

**Learn a few commands, then let the shared formatting handle the repetition.**
You type or paste your text, and one file of formatting rules (the *class
file*, `rpi-thesis.cls`) keeps headings, numbering, and spacing consistent.
You still check the PDF.

<span id="what-you-stop-doing-by-hand"></span>
<span id="when-your-thesis-changes"></span>

## Write a chapter. Keep the thesis consistent.

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

For references, [choose the citation style and matching commands](citations.md#change-the-citation-style).

- **Margins, spacing, and the title page.** Set once in the class file. If a
  rule changes, you usually replace the class file and your chapters stay untouched; check
  the steps first ([update the formatting safely](workflows.md#update-the-formatting-safely)).
- **Equations.** LaTeX was built for mathematics; displayed equations are
  laid out and numbered for you.

It is free, and your files are plain text that
[back up like any folder](workflows.md#back-up-your-work).

**You only need about 10 commands.** A *command* is a short instruction that
starts with a backslash, such as `\section{Methods}`. Headings, citations,
cross-references, figures, tables, and equations cover most of a thesis, and
they fit in one table at the top of
[writing basics](writing.md#the-10-commands-youll-actually-use).

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
[chapter-to-paper move](workflows.md#turn-a-chapter-into-a-paper) also means
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

## Bring your words in, take them elsewhere

You don't have to draft in LaTeX. Draft where you and your advisor work
comfortably, then move each chapter in when it is ready
([bring your draft](bring-your-draft.md), and
[the suggested workflow](how-it-works.md#the-suggested-workflow-and-why)).
Later, the same files can start a Word review copy, slides, or a journal
version of a chapter; each needs its own template, some cleanup, and its own
requirements check
([reuse your material elsewhere](how-it-works.md#reuse-your-material-elsewhere)).

## AI can help you get unstuck

Optional, and one route alongside web search, documentation, and
[community help](troubleshooting.md#ask-for-help). An AI chat you already
have access to can explain an error message, find a missing brace, or turn
data you supply into a LaTeX table. Try one change at a time and compile to
check ([AI for technical help](workflows.md#use-ai-for-technical-help)).

## The honest costs

- **A first week of getting used to it.** You see the formatted page when you
  compile, not as you type.
- **Errors look scary.** They are long, but the useful part names a file and
  a line ([read an error message](troubleshooting.md#read-an-error-message)).
- **Advisors who prefer Word.** Send a PDF to comment on, or a Word copy, and
  apply their edits by hand ([workflows](workflows.md#common-situations)).
- **Tables take a bit more effort.** Copy the sample chapters' example and
  adapt it.
- **OGE staff can't debug LaTeX.** The Office of Graduate Education (OGE)
  reviews your formatting, not your code
  ([ask for help](troubleshooting.md#ask-for-help)).

## When Word might still make sense

- Your thesis is short, with no equations and few figures or tables.
- Your committee edits only in Word, and you would rather not manage review copies.
- You must submit within days and have never used LaTeX.

OGE provides its own Word template, available from the
[OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation).
Either route can lead to a thesis OGE accepts.
