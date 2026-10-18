# Fixing problems

Errors are normal, and most take a minute once you know where to look. The
fastest route: paste the error into [Explain my error](explain-my-error.md).
Or find it in [common messages](#common-messages), ask an
[AI chat](#ask-an-ai-chat-to-explain-it), or [ask for help](#ask-for-help).

## When a compile stops

A failed compile never changes your files. Your writing is exactly as you
left it.

![What to do when a compile stops: find the first error, open the file and line it names, check the usual culprits (typo in a command, missing brace, unescaped special character, wrong file name), fix, and compile again. Still stuck: look it up in the common messages, then ask for help.](diagrams/error-triage.svg)

*In words:* find the **first** error, look at the file and line it names (and
the line before), check the usual culprits, fix, and compile again.

Where the errors are:

- **VS Code:** **View → Problems** lists each error with its file and line;
  click one to jump there. The full log is in the **Output** panel, under
  **LaTeX Compiler**.
- **Overleaf:** the **Logs and output files** button beside **Recompile**
  lists the errors; click one to jump there. **Raw logs**, at the bottom of
  that list, shows the full log.
- **Another editor:** look for its log or messages panel, or open
  `main.log` (in `build/` or next to `main.tex`).
<!-- TODO(verify): Overleaf's "Logs and output files" and "Raw logs" labels and VS Code's "LaTeX Compiler" output channel name were not rechecked in the current versions. -->

Compile after each small change so you know what caused a problem. A warning
still produces a PDF, but review warnings before you submit.

## Read an error message

LaTeX errors look long, but the useful part is short. This is the real error
from the sample thesis after one typo, `\parencit` instead of `\parencite` in
chapter 1:

```text
./chapters/01-introduction.tex:13: Undefined control sequence.
l.13 example~\parencit
                      {lamport1994}. Replace it with literature relevant to ...
```

1. **The file:** `chapters/01-introduction.tex`. Open this file, not `main.tex`.
2. **The line:** `13`, the number after the file name.
3. **The message:** "Undefined control sequence" means LaTeX does not know a
   command, usually because of a typo after a backslash.
4. **Where it stopped:** the line starting `l.13` ends where LaTeX stopped
   reading, so the last thing on it, `\parencit`, is the problem.

Fix: write `\parencite{lamport1994}` and compile again. With several errors, fix
only the first; the later ones are often side effects.

### Ask an AI chat to explain it

An AI chat is a quick way to decode a cryptic error. Paste the first error and
the few lines around it (or the whole log from your editor or Overleaf), and
say whether you use Overleaf or your computer.
Never paste confidential or unpublished material. Try one change, compile,
and undo it if the PDF gets worse.

```prompt
Here is the first LaTeX error and a short example. I use Overleaf (or: my computer, with macOS/Windows/Linux). Explain what it means and suggest the smallest fix. Keep my text, data, citations, and template formatting unchanged. Show the lines to change.
```

More, including assistants that can edit your files and
[prompts for setup, errors, and conversions](going-further.md#prompts-to-copy):
[AI for technical help](going-further.md#use-ai-for-technical-help). A web search
or [Overleaf Learn](https://www.overleaf.com/learn) works too.

## Clean recompile

A clean recompile throws away LaTeX's scratch files and builds everything
again. Try it when the PDF will not update, numbers stay as **??**, or an error
looks impossible. It never changes your writing.

- **Overleaf:** open the **Recompile** menu (the small arrow beside the
  button) and choose **Recompile from scratch**. To change the engine, open
  **Settings** (the gear icon) and, under **Compiler**, pick pdfLaTeX, XeLaTeX,
  or LuaLaTeX ([Overleaf: selecting a compiler](https://docs.overleaf.com/getting-started/recompiling-your-project/selecting-a-tex-live-version-and-latex-compiler)).
- **VS Code:** open the Command Palette (Ctrl+Shift+P, or Cmd+Shift+P on
  macOS), run **LaTeX Workshop: Clean up auxiliary files**, then compile again.
  To change the engine, run **LaTeX Workshop: Build with recipe** and pick
  **RPI Thesis Toolkit: XeLaTeX + Biber (Unicode)** or **LuaLaTeX + Biber (Unicode)** (Biber is
  the bibliography step). Saving keeps using that choice until you close
  VS Code; after you reopen it, pick it again the same way.
  <!-- TODO(verify): read from LaTeX Workshop 10.19 source (the last recipe is remembered in memory only); not hand-tested in VS Code. -->
- **TeXShop, TeXstudio, or TeXworks:** each editor has its own way to remove
  auxiliary files and to choose an engine, and the steps differ by version.
  Look in that editor's own documentation
  ([TeXShop](https://pages.uoregon.edu/koch/texshop/),
  [TeXstudio](https://texstudio.org/),
  [TeXworks](https://tug.org/texworks/)). Then run the steps from
  [Get started](get-started.md#other-editors) again.
  <!-- TODO(verify): menu names in current TeXShop, TeXstudio, and TeXworks were not checked, so none are named here. -->
- **Optional, in a terminal:** see [build commands](going-further.md#build-commands).

Switch engine only to fix characters pdfLaTeX cannot handle, then check
the whole PDF ([compile engines](going-further.md#choose-a-compile-engine)).

## Common messages

The same table drives [Explain my error](explain-my-error.md) and the
optional [build helper](going-further.md#build-commands), so all three give
the same advice.

### Setup and files

{{common-messages:setup-and-files}}

### Citations and references

{{common-messages:citations-and-references}}

### Layout and the PDF

{{common-messages:layout-and-the-pdf}}

### Tools and installs

{{common-messages:tools-and-installs}}

<details><summary>Rare messages: an old LaTeX installation, version mismatches, the bibliography step on a Mac, typed build commands</summary>

{{common-messages:rare}}

</details>

Please don't make an error disappear by changing margins, spacing, or the
class file. Adjust the object instead, or ask for help.

## Ask for help

Stuck on something odd? You are probably not the first, and your question
helps everyone writing after you. Questions about LaTeX, Zotero, files, or
"where does this go?" are all welcome.

1. **Make it easy to see.** On Overleaf, create a view-only link from the
   share menu. On your computer, make the smallest made-up example that still
   shows the problem.
2. **Copy the first error**, with its file and line number.
3. **Send it** through either channel:
   <!-- Maintainer: the form URL below is the ONLY place it appears. README.md,
   CONTRIBUTING.md, and the website footer link to this section
   (#ask-for-help); change the URL here and nowhere else. -->
   - **No account needed:** the
     [help and feedback form](https://forms.gle/fjfiLfkmVhkcyRNCA).
   - **With a GitHub account:** open an issue with the **LaTeX help or bug**
     form. Answers stay public and searchable. Never opened one? See
     [how to open an issue](../CONTRIBUTING.md#three-ways-to-help).

Copy and fill in:

```text
Where I write:   Overleaf / VS Code / other editor: ...
Computer:        macOS / Windows / Linux
What I did:      ...
What I expected: ...
What happened (first error, with file and line): ...
View-only link or small example: ...
```

> [!WARNING]
> Remove unpublished research and personal details before sharing. A
> view-only link shows your whole project, so share it only with someone you
> trust, then turn link sharing off.

Found a fix or a tip worth passing on? The form takes those too, and
[ways to contribute](../CONTRIBUTING.md) lists other options.
