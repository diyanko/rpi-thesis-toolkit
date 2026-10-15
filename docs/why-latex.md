# Why LaTeX for your thesis?

For anyone deciding how to write a thesis, dissertation, or other long
document, whether or not you have used LaTeX before.

**A little harder this week, much easier every week after.** With this
starter you type or paste your text, and one file of formatting rules (the
*class file*, `rpi-thesis.cls`) does most of the work you would otherwise do
by hand. The result
looks right, stays consistent from the first page to the last, can be
adjusted in one place, and can be converted to other formats, with some
cleanup, when you need to.

## What you stop doing by hand

![Two columns compare who keeps a long document right. Left, a word processor: you keep chapter and section numbers, figure, table, and equation numbers and their cross-references, the contents and lists, citation numbering and the reference list, and consistent styles and margins right by hand. Right, this starter: the same items update every time you compile, and the formatting is set once, in rpi-thesis.cls. A note says Word can automate some of this with styles and fields, but it takes care across 150 or more pages.](diagrams/by-hand-vs-automatic.svg)

*In words:* numbering, cross-references, the contents, citations, and
consistent styles update every time you compile (turn your files into a PDF),
instead of by hand.

- **Numbers and cross-references.** Chapters, sections, figures, tables, and
  equations number themselves, and every "see Figure 3.1" follows along.
- **Contents and lists.** The contents and the lists of figures and tables
  are built from your headings and captions.
- **Citations.** Cite a source by its short name (its key); the citation and
  the reference list follow your field's style, such as APA, Chicago, MLA,
  or IEEE ([citation styles](citations.md#change-the-citation-style)).
- **Margins, spacing, and the title page.** Set once in the class file, the
  same on every page. If a rule changes, you
  [replace one file](workflows.md#update-the-formatting-safely) and your
  chapters stay untouched.
- **Equations, if you have them.** LaTeX was built for mathematics; displayed
  equations are laid out and numbered for you.

It is all free, your files are plain text that back up like any folder
([backups](workflows.md#back-up-your-work)), and a 200-page dissertation works
the same way as a 20-page draft.

## See it in action

![Moving a chapter. On the left, main.tex lists the chapters in order; the include line for one chapter is moved earlier in the list. On the right, after the next compile, every chapter number has changed to match the new order, the figure and equation numbers inside each chapter follow, every "see Figure 3.1" in the text points to the new number, and the contents list the chapters in their new order with the right page numbers. No number was typed by hand.](diagrams/move-a-chapter.svg)

*In words:* move one line in `main.tex`, compile, and every number,
cross-reference, and contents entry updates to match.

## Bring your words from anywhere

You don't have to draft in LaTeX. Draft where you and your advisor work
comfortably, such as a Markdown app, Google Docs, or Word, then move each
chapter in when it is ready: paste the text, mark up the headings, and
rebuild tables, equations, and citations.
[Bring your draft](bring-your-draft.md) shows what goes where, and
[the suggested workflow](how-it-works.md#the-suggested-workflow-and-why)
explains how drafting, sources, and figures fit together.

## Reuse your work elsewhere

Your thesis PDF is the main output, but the same files can later start a
Word review copy, slides or a poster, or a journal version of a chapter. Each
needs its own template, some cleanup, and its own requirements check, and you
use only what you need
([reuse your material elsewhere](how-it-works.md#reuse-your-material-elsewhere)).

## AI can help you get unstuck

Optional, and one route alongside web search, documentation, and
[community help](troubleshooting.md#ask-for-help): an AI chat you already
have access to can save time in the first weeks, for example by explaining
an error message, finding a missing brace, or turning data you supply into a
LaTeX table. Try one suggested change at a time and compile to check it
([AI for technical help](workflows.md#use-ai-for-technical-help)).

## The honest costs

- **A first week of getting used to it.** You see the formatted page when you
  compile, not as you type, and a few commands take looking up at first.
- **Errors look scary.** They are long, but the useful part names a file and
  a line ([read an error message](troubleshooting.md#read-an-error-message)).
- **Co-authors or advisors who prefer Word.** Send a PDF to comment on, or a
  Word copy, and apply their edits by hand
  ([workflows](workflows.md#common-situations)).
- **Tables take a bit more effort.** Copy the example in the sample chapters
  and adapt it.
- **OGE staff can't debug LaTeX.** The Office of Graduate Education (OGE)
  reviews your formatting, not your code. For LaTeX questions, this community
  helps ([ask for help](troubleshooting.md#ask-for-help)).

## When Word might still make sense

- Your thesis is short, with no equations and few figures or tables.
- Your committee edits only in Word, and you would rather not manage review copies.
- You must submit within days and have never used LaTeX.

OGE provides its own Word template, available from the
[OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation).
Either route can lead to a thesis OGE accepts.

## You only need about 10 commands

A *command* is a short instruction that starts with a backslash, such as
`\section{Methods}`. Headings, paragraphs, emphasis, citations,
cross-references, figures, tables, and equations: that covers most of a thesis. They fit in one table at
the top of [writing basics](writing.md#the-10-commands-youll-actually-use).
You can compile on your own computer or in your browser with Overleaf; both
use the same files and programs ([choose your LaTeX workspace](get-started.md#step-1-choose-your-latex-workspace)).

**Next:** [get started](get-started.md) and compile the sample in a few steps.
