# Fixing problems

For anyone whose compile stops with an error or whose PDF looks wrong, on
your computer or Overleaf. Errors are normal. Most take a minute to fix once
you know where to look.

Know the message? Jump to [common messages](#common-messages), or paste it
into [Explain my error](explain-my-error.md) to find the first real error and
its fix. Not in the list? Paste the first error into an [AI chat](#ask-an-ai-chat-to-explain-it)
or [ask for help](#ask-for-help). Want to know *why* something happens? See
[how it works](how-it-works.md).

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
  **RPI Thesis Toolkit: XeLaTeX + Biber** or **LuaLaTeX + Biber** (Biber is
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

### Setup and files

| What you see | What to try |
| --- | --- |
| `File rpi-thesis.cls not found` | Extract the whole ZIP and open the folder that contains `main.tex`. On Overleaf, `main.tex` must be at the top of the file list ([Overleaf route](get-started.md#step-3b-overleaf-route)). |
| `Missing title in metadata.tex` (or author, department, ...) | Fill in that setting inside `\thesissetup{...}`. |
| `Committee chair is missing` | Put `[Chair]` (or `[Co-Chair]`) on one `\committeemember` line, spelled exactly so: `[chair]` is not recognized. |
| `You have requested ... version ... of document class rpi-thesis` | Your `rpi-thesis.cls` is older than the rest of your starter files. Copy `rpi-thesis.cls` from the newest starter ([update safely](going-further.md#update-the-formatting-safely)). |
| `Unknown setting "..." in metadata.tex` | A setting name in `\thesissetup{...}` is misspelled. Compare it with [all thesis settings](going-further.md#all-thesis-settings). |
| `Unknown degree choice` | Use `masters`, `doctoral`, or `engineering-doctorate`, in lower case. |
| `Unknown graduation month` | Use `May`, `August`, or `December`, with a capital first letter. |
| `Graduation year must have four digits` | Write the year like `2027`. |
| `RPI seal not found`, or a seal placeholder on the title page | Save the seal as `assets/rpi-seal.jpg` ([add the RPI seal](get-started.md#add-the-rpi-seal-one-minute)). |
| `Unsupported class option` | Use `\documentclass{rpi-thesis}` with no options; settings go in `metadata.tex`. |
| A figure file cannot be found | The message reads ``LaTeX Error: File `figures/...' not found``. Check the file name, capital letters, extension, and the `figures/` path. |
| `Could not set up appendices` | A line above `\documentclass` in `main.tex`, or an outdated LaTeX installation, changed `\chapter`. Remove lines added above `\documentclass`, or update TeX Live. |
| A file can't be found, and the folder is in OneDrive or iCloud or its path has non-English letters | Set the folder to "Always keep on this device", or move it to a short, plain path such as `C:\thesis` or `~/thesis`. |

### Citations and references

| What you see | What to try |
| --- | --- |
| A citation key in **bold** | Compile again. VS Code with the starter's settings and Overleaf run the bibliography step for you; in other editors run it yourself ([other editors](get-started.md#other-editors)). Still bold? Check that the key is spelled the same in your citation command and in `references.bib`. |
| **??** instead of a number | Compile again. Check the `\label` and `\ref` spelling. |
| The reference list is empty | Cite at least one entry, for example with `\parencite{key}`, then compile again. |
| A new Zotero source doesn't appear | Re-export, compile again, and check that the key in your citation command matches the key in the `.bib` file exactly. |
| `Misplaced alignment tab character &` in the references | A title in the `.bib` file contains `&`. Write it as `\&`. |
| `File 'main.bbl' not created by biblatex` | A bibliography file from an earlier build, often one that used BibTeX or `natbib`, is in the way. Do a [clean recompile](#clean-recompile). |

### Layout and the PDF

| What you see | What to try |
| --- | --- |
| `Missing $ inserted` | Look for an unescaped `_` or a math command outside `$...$`. Write `\_` for an underscore. |
| `Runaway argument` or a brace error | Check your last edit for a missing `}`. |
| A special character (such as an accented letter, or one from another alphabet) is missing or garbled | Use a LaTeX accent command, or try another engine ([compile engines](going-further.md#choose-a-compile-engine)). |
| `STIX Two Math font not found` | On Overleaf, choose the newest available TeX Live version. On your computer, update your full LaTeX installation. Then do a [clean recompile](#clean-recompile) and inspect the affected math: a few symbols, such as `\bigstar`, `\digamma`, and `\subseteqq`, need this fallback font with LuaLaTeX or XeLaTeX. |
| `Overfull \hbox` | Something is wider than the text area: a long URL, table, equation, or image. Find it in the PDF and resize or break it. |
| `Overfull \vbox` on the title page | Remove manual line breaks from the title; check long names and committee lines. |
| A figure floats to a different page | Normal. Use `[htbp]` after `\begin{figure}` and write "Figure~\ref{...}", not "below". |
| An edit, the contents, or the references do not update | Save every file and check you are viewing the new PDF, not an old copy ([where it ends up](how-it-works.md#where-the-pdf-ends-up)). Still stale? Do a [clean recompile](#clean-recompile). |
| The optional [build helper](going-further.md#build-commands) prints "Pre-submission hints" | Your PDF was built. Fix each listed line before submitting ([web sources](citations.md#web-sources-need-an-access-date), [short captions](writing.md#use-one-full-caption-not-a-short-one)). |

### Tools and installs

| What you see | What to try |
| --- | --- |
| `latexmk`, `pdflatex`, or `biber` not found, or `spawn latexmk ENOENT` | Finish installing the full LaTeX distribution, then quit your editor completely and reopen it (on Windows, restart the computer if needed). On Linux, use VS Code's `.deb` or `.rpm`, not the Flatpak. Optional: the build helper's setup check names the missing tool ([build commands](going-further.md#build-commands)). |
| VS Code says **Restricted Mode**, or LaTeX Workshop does nothing | Click **Restricted Mode** in the status bar and choose **Trust**. LaTeX Workshop is off in untrusted folders. |
| Overleaf says the compile timed out | Try **Fast [draft]** from the Recompile menu, shrink large photos, export plots as PDF, or compile on your computer. **Fast draft** shows images as empty boxes, so switch back to **Normal** and check every figure and the seal before you share or submit ([Overleaf: compile timeouts](https://docs.overleaf.com/troubleshooting-and-support/fixing-and-preventing-compile-timeouts)). |

<details><summary>Rare messages: old TeX Live, a bibliography version mismatch, the bibliography step on a Mac, typed build commands</summary>

| What you see | What to try |
| --- | --- |
| `You have requested release '...' of LaTeX` | Your installed LaTeX is older than this starter needs. Install the current full [TeX Live from tug.org](https://tug.org/texlive/quickinstall.html), or use [Overleaf](get-started.md#step-3b-overleaf-route). |
| `Found biblatex control file version ..., expected version ...` | Try a [clean recompile](#clean-recompile) first. If it persists, the bibliography step and biblatex probably come from different LaTeX installations: keep one distribution and update it fully. |
| On a Mac, the bibliography step fails and the log mentions `biber` and `lipo` | An older Mac build of the bibliography program (Biber) that newer macOS can't start; your thesis is fine. Open **TeX Live Utility** (Applications → TeX), choose **Update all packages**, and compile again. |
| `I can't write on file build/chapters/...aux` (or `chapters/...aux`, `appendices/...aux`) | The starter's settings create those folders for you. If you see this, do a [clean recompile](#clean-recompile). If you typed your own build command, use one from [build commands](going-further.md#build-commands) instead. |

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
