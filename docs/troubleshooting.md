# Fixing problems

For anyone whose compile stops with an error or whose PDF looks wrong, on
your computer or Overleaf. Errors are normal. Most take a minute to fix once
you know where to look.

Know the message? Jump to [common messages](#common-messages). Not in the
list? Paste the first error into an [AI chat](#ask-an-ai-chat-to-explain-it)
or [ask for help](#ask-for-help). Want to know *why* something happens? See
[how it works](how-it-works.md).

## When a compile stops

A failed compile never changes your files. Your writing is exactly as you
left it.

![What to do when a compile stops: find the first error, open the file and line it names, check the usual culprits (typo in a command, missing brace, unescaped special character, wrong file name), fix, and compile again. Still stuck: look it up in the common messages, then ask for help.](diagrams/error-triage.svg)

*In words:* find the **first** error, look at the file and line it names (and
the line before), check the usual culprits, fix, and compile again.

Compile after each small change so you know what caused a problem. A warning
still produces a PDF, but review warnings before you submit.

## Read an error message

LaTeX errors look long, but the useful part is short. This is the real error
from the sample thesis after one typo, `\cit` instead of `\cite` in chapter 1:

```text
./chapters/01-introduction.tex:10: Undefined control sequence.
l.10 example~\cit
                 {lamport1994}. Replace it with literature relevant to your ...
```

1. **The file:** `chapters/01-introduction.tex`. Open this file, not `main.tex`.
2. **The line:** `10`, the number after the file name.
3. **The message:** "Undefined control sequence" means LaTeX does not know a
   command, usually because of a typo after a backslash.
4. **Where it stopped:** the line starting `l.10` ends where LaTeX stopped
   reading, so the last thing on it, `\cit`, is the problem.

Fix: write `\cite{lamport1994}` and compile again. With several errors, fix
only the first; the later ones are often side effects.

### Ask an AI chat to explain it

An AI chat is a quick way to decode a cryptic error. Paste the first error and
the few lines around it, and say whether you use Overleaf or your computer.
Never paste confidential or unpublished material. Try one change, compile,
and undo it if the PDF gets worse.

```prompt
Here is the first LaTeX error and a short example. I use Overleaf (or: my computer, with macOS/Windows/Linux). Explain what it means and suggest the smallest fix. Keep my text, data, citations, and template formatting unchanged. Show the lines to change.
```

More, including assistants that can edit your files:
[AI for technical help](workflows.md#use-ai-for-technical-help). A web search
or [Overleaf Learn](https://www.overleaf.com/learn) works too.

## Clean recompile

A clean recompile throws away LaTeX's scratch files and builds everything
again. Try it when the PDF will not update, numbers stay as **??**, or an error
looks impossible. It never changes your writing. You can do it without a
terminal.

- **Overleaf:** open the **Recompile** menu (the small arrow beside the
  button) and choose **Recompile from scratch**. To change the engine, open
  **Settings** (the gear icon) and, under **Compiler**, pick pdfLaTeX, XeLaTeX,
  or LuaLaTeX ([Overleaf: selecting a compiler](https://docs.overleaf.com/getting-started/recompiling-your-project/selecting-a-tex-live-version-and-latex-compiler)).
- **VS Code:** open the Command Palette (Ctrl+Shift+P, or Cmd+Shift+P on
  macOS), run **LaTeX Workshop: Clean up auxiliary files**, then build again.
  To change the engine, run **LaTeX Workshop: Build with recipe** and pick
  **RPI Thesis Toolkit: XeLaTeX + Biber** or **LuaLaTeX + Biber**; the
  starter's settings keep your last choice for later builds.
  <!-- TODO(verify): recipe picker and lastUsed persistence not hand-tested in VS Code. -->
- **TeXShop, TeXstudio, or TeXworks:** each editor has its own way to remove
  auxiliary files and to choose an engine, and the steps differ by version.
  Look in that editor's own documentation
  ([TeXShop](https://pages.uoregon.edu/koch/texshop/),
  [TeXstudio](https://texstudio.org/),
  [TeXworks](https://tug.org/texworks/)), or use the terminal command in the
  next item. Then run the steps from
  [Get started](get-started.md#other-editors-and-the-command-line) again.
  <!-- TODO(verify): menu names in current TeXShop, TeXstudio, and TeXworks were not checked, so none are named here. -->
- **Any editor, in a terminal (optional):** `python3 scripts/build.py --fresh`
  (on Windows, `py scripts/build.py --fresh`).

Switch engine only to fix characters pdfLaTeX cannot handle, then check
the whole PDF ([compile engines](advanced.md#choose-a-compile-engine)).

## Common messages

### Setup and files

| What you see | What to try |
| --- | --- |
| `File rpi-thesis.cls not found` | Extract the whole ZIP and open the folder that contains `main.tex`. On Overleaf, `main.tex` must be at the top of the file list ([Overleaf route](get-started.md#step-3b-overleaf-route)). |
| `Missing title in metadata.tex` (or author, department, ...) | Fill in that setting inside `\thesissetup{...}`. |
| `Committee chair is missing` | Put `[Chair]` (or `[Co-Chair]`) on one `\committeemember` line. |
| `You have requested ... version ... of document class rpi-thesis` | Your `rpi-thesis.cls` is older than the rest of your starter files. Copy `rpi-thesis.cls` from the newest starter ([update safely](workflows.md#update-the-formatting-safely)). |
| `Unknown degree choice` | Use `masters`, `doctoral`, or `engineering-doctorate`. |
| `Unknown graduation month` | Use `May`, `August`, or `December`. |
| `Graduation year must have four digits` | Write the year like `2027`. |
| `RPI seal not found`, or a seal placeholder on the title page | Save the seal as `assets/rpi-seal.jpg` ([add the RPI seal](get-started.md#add-the-rpi-seal-one-minute)). |
| `Unsupported class option` | Use `\documentclass{rpi-thesis}` with no options; settings go in `metadata.tex`. |
| A figure file cannot be found | Check the file name, capital letters, extension, and the `figures/` path. |
| A file can't be found, and the folder is in OneDrive or iCloud or its path has non-English letters | Set the folder to "Always keep on this device", or move it to a short, plain path such as `C:\thesis` or `~/thesis`. |

### Citations and references

| What you see | What to try |
| --- | --- |
| A citation key in **bold** | Run the bibliography step (Biber), then compile twice. Check the key spelling. |
| **??** instead of a number | Compile again. Check the `\label` and `\ref` spelling. |
| The reference list is empty | Cite at least one entry with `\cite{key}`, then run Biber. |
| A new Zotero source doesn't appear | Re-export, run Biber, and check that `\cite{key}` matches the key in the `.bib` file exactly. |
| `Misplaced alignment tab character &` in the references | A title in the `.bib` file contains `&`. Write it as `\&`. |

### Layout and the PDF

| What you see | What to try |
| --- | --- |
| `Missing $ inserted` | Look for an unescaped `_` or a math command outside `$...$`. Write `\_` for an underscore. |
| `Runaway argument` or a brace error | Check your last edit for a missing `}`. |
| A special character (such as an accented letter, or one from another alphabet) is missing or garbled | Use a LaTeX accent command, or try another engine ([compile engines](advanced.md#choose-a-compile-engine)). |
| `Overfull \hbox` | Something is wider than the text area: a long URL, table, equation, or image. Find it in the PDF and resize or break it. |
| `Overfull \vbox` on the title page | Remove manual line breaks from the title; check long names and committee lines. |
| A figure floats to a different page | Normal. Use `[htbp]` after `\begin{figure}` and write "Figure~\ref{...}", not "below". |
| An edit, the contents, or the references do not update | Save every file and check you are viewing the new PDF, not an old copy ([where it ends up](how-it-works.md#where-the-pdf-ends-up)). Still stale? Do a [clean recompile](#clean-recompile). |
| The build helper prints "Pre-submission hints" | Your PDF was built. Fix each listed line before submitting ([web sources](citations.md#web-sources-need-an-access-date), [short captions](writing.md#use-one-full-caption-not-a-short-one)). |

### Tools and installs

| What you see | What to try |
| --- | --- |
| `latexmk`, `pdflatex`, or `biber` not found, or `spawn latexmk ENOENT` | Finish installing the full LaTeX distribution, then quit your editor completely and reopen it (on Windows, restart the computer if needed). On Linux, use VS Code's `.deb` or `.rpm`, not the Flatpak. Optional, in a terminal: `python3 scripts/build.py --doctor` (Windows: `py scripts/build.py --doctor`) names the missing tool. |
| VS Code says **Restricted Mode**, or LaTeX Workshop does nothing | Click **Restricted Mode** in the status bar and choose **Trust**. LaTeX Workshop is off in untrusted folders. |
| Overleaf says the compile timed out | Try **Fast [draft]** from the Recompile menu, shrink large photos, export plots as PDF, or compile on your computer. **Fast draft** shows images as empty boxes, so switch back to **Normal** and check every figure and the seal before you share or submit ([Overleaf: compile timeouts](https://docs.overleaf.com/troubleshooting-and-support/fixing-and-preventing-compile-timeouts)). |
| `python3` is not recognized, or opens the Microsoft Store (Windows) | On Windows, `python3` may open the Microsoft Store or say it is not recognized. Close the Store and type `py scripts/build.py` instead. Python is optional: editors compile without it. |

<details><summary>Rare messages: old TeX Live, Biber version mismatch, Biber on a Mac, hand-typed builds</summary>

| What you see | What to try |
| --- | --- |
| `You have requested release '2022-06-01' of LaTeX` | Your TeX Live is older than the 2022 release this starter is written for (common with Ubuntu 22.04's packages). The sample compiled with TeX Live 2021 in a test, so you can usually continue; if something looks wrong, install [TeX Live from tug.org](https://tug.org/texlive/quickinstall.html). |
| `Found biblatex control file version ..., expected version ...` | Try a [clean recompile](#clean-recompile) first. If it persists, Biber and biblatex probably come from different TeX installations: keep one distribution, update it fully, and use its `biber`. |
| On a Mac, Biber fails and the log mentions `lipo` | An older Mac build of Biber that newer macOS can't start; your thesis is fine. Update TeX Live and build again. On macOS (MacTeX), use TeX Live Utility, **Update all packages**, or run `sudo tlmgr update --self --all`. On Linux with apt, update with your package manager: first `sudo apt update`, then `sudo apt upgrade`. |
| `I can't write on file build/chapters/...aux` (or `chapters/...aux`, `appendices/...aux`) | The starter's settings create those folders for you. If you see this, do a [clean recompile](#clean-recompile). If you typed your own `latexmk -outdir=...` command, build with `python3 scripts/build.py` (Windows: `py scripts/build.py`) or `latexmk -norc -pdf main.tex` instead. |

</details>

Please don't make an error disappear by changing margins, spacing, or the
class file. Adjust the object instead, or ask for help.

## Ask for help

Stuck on something odd? Every question helps the next student, and questions
about LaTeX, Zotero, files, or "where does this go?" are all welcome.

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
     [how to open an issue](../CONTRIBUTING.md#open-an-issue).

Copy and fill in:

```text
Where I write:   Overleaf / TeXShop / TeXstudio / VS Code / other: ...
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
