# Fixing problems

For anyone whose compile stops with an error or whose PDF looks wrong, on
your own computer or Overleaf. Errors are normal — every LaTeX writer sees
them, and most take a minute to fix once you know where to look.

Quick habits that save the day:

1. Compile after each small change, so you know what caused a problem.
2. Undo the last change if you are stuck, then try again more slowly.
3. Warnings still produce a PDF, but review them before submission.

Want to know *why* something happens? See [how it works](how-it-works.md).

## When a compile stops

A failed compile never changes your files: your writing is exactly as you
left it.

![What to do when a compile stops, in six steps. 1: the build stopped. 2: find the first error in the messages. 3: it names a file and a line number; look at that line and the line before it. 4: check the common culprits: a typo in a command, a missing closing brace or dollar sign, one of the special characters & % _ # $ typed without a backslash, or a wrong file name or path. 5: fix it and compile again. 6: still stuck, or the error is about a tool such as latexmk or Biber: look it up in the table of common messages, then ask for help.](diagrams/error-triage.svg)

*In words:* find the **first** error, look at the file and line it names (and
the line before), check the usual culprits, fix, and compile again. Still
stuck? See [common messages](#common-messages), then [ask for help](#ask-for-help).

## Read an error message

LaTeX errors look long, but the useful part is short. This is the real error
from the sample thesis after one typo, `\cit` instead of `\cite` in chapter 1:

```text
./chapters/01-introduction.tex:10: Undefined control sequence.
l.10 example~\cit
                 {lamport1994}. Replace it with literature relevant to your ...
```

1. **The file:** `chapters/01-introduction.tex`. Open this file, not `main.tex`.
2. **The line:** `10`, the number after the file name. Most editors show line
   numbers in the margin.
3. **The message:** "Undefined control sequence" means LaTeX does not know a
   command, usually because of a typo after a backslash.
4. **Where it stopped:** the line starting `l.10` ends exactly where LaTeX
   stopped reading, so the last thing on it, `\cit`, is the problem. The line
   below is the rest of your text, not read yet.

Here the fix is to write `\cite{lamport1994}`, then compile again. Some editors
show the message as `! Undefined control sequence.` without the file name; the
`l.10` line still tells you where to look.

If there are several errors, fix the first one only, then compile again;
the later ones are often side effects that disappear with it.

### Ask an AI chat to explain it

An AI chat you already have access to can explain the first error and
suggest the smallest fix, alongside a web search, [Overleaf Learn](https://www.overleaf.com/learn),
or [asking for help](#ask-for-help). Share only the first error and a short
example, never confidential material. Try one change, compile, and check
the PDF; undo it if it doesn't help.

```text
Here is the first LaTeX error and a short example. Explain what it means and
suggest the smallest fix. Keep my text, data, citations, and template
formatting unchanged. Show the lines to change.
```

More, including assistants that can edit your files:
[AI for technical help](workflows.md#use-ai-for-technical-help).

## Common messages

| What you see | What to try |
| --- | --- |
| `File rpi-thesis.cls not found` | Extract the whole ZIP, not only `main.tex`, and open the folder that contains `main.tex`. On Overleaf, `main.tex` must be at the top of the file list, not inside a folder ([Overleaf route](get-started.md#step-3b-overleaf-route)). |
| `Missing title in metadata.tex` (or author, department, …) | Fill in that setting inside `\thesissetup{...}`. |
| `Committee chair is missing` | Put `[Chair]` (or `[Co-Chair]`) on one `\committeemember` line. |
| `Unknown degree choice` | Use `masters`, `doctoral`, or `engineering-doctorate`. |
| `Unknown graduation month` | Use `May`, `August`, or `December`. |
| `Graduation year must have four digits` | Write the year like `2027`. |
| `RPI seal not found`, or a seal placeholder on the title page | Download the seal and save it as `assets/rpi-seal.jpg` ([add the RPI seal](get-started.md#add-the-rpi-seal-one-minute)). |
| `Unsupported class option` | Leave `\documentclass{rpi-thesis}` without options; settings go in `metadata.tex`. |
| `Missing $ inserted` | Look for an unescaped `_` or a math command outside `$...$`. Write `\_` for an underscore. |
| `Runaway argument` or a brace error | Check your last edit for a missing `}`. |
| A citation key in **bold** | Run the bibliography step (Biber), then compile twice. Check the key spelling. |
| **??** instead of a number | Compile again. Check the `\label` and `\ref` spelling. |
| The reference list is empty | Cite at least one entry with `\cite{key}`, then run Biber. |
| A figure file cannot be found | Check the file name, capital letters, extension, and the `figures/` path. |
| A special character (such as an accented letter, or one from another alphabet) is missing or garbled | Use a LaTeX accent command, or try the LuaLaTeX/XeLaTeX engine (see [advanced use](advanced.md#build-commands)). |
| `Overfull \hbox` | Something is wider than the text area: a long URL, wide table, equation, or image. Find it in the PDF and resize or break it. |
| `Overfull \vbox` on the title page | Remove manual line breaks from the title; check long names and committee lines. |
| The contents or references will not update | Save all files and rebuild from scratch: Overleaf's "recompile from scratch", `python3 scripts/build.py --fresh`, or rerun pdfLaTeX → Biber → pdfLaTeX → pdfLaTeX. Make sure you open the right PDF ([where it ends up](how-it-works.md#where-the-pdf-ends-up)). |
| An edit doesn't show up in the PDF | Save every file, then check you are viewing the newly built PDF, not an old copy ([where it ends up](how-it-works.md#where-the-pdf-ends-up)). |
| A new Zotero source doesn't appear | Re-export (or let auto-export finish), compile with Biber, and check that the `\cite{key}` matches the key in the `.bib` file exactly. |
| `Misplaced alignment tab character &` in the references | A title in the `.bib` file contains `&`. Write it as `\&`. |
| A figure floats to a different page | That's normal LaTeX behavior. Use `[htbp]` after `\begin{figure}` and refer to it as "Figure~\ref{...}" rather than "below". |
| Overleaf says the compile timed out | The free plan's time limit is short. Try **Fast [draft]** from the Recompile menu, shrink large photos and export plots as PDF, or compile on your computer, which has no limit ([Overleaf: compile timeouts](https://docs.overleaf.com/troubleshooting-and-support/fixing-and-preventing-compile-timeouts)). |
| `latexmk`, `pdflatex`, or `biber` not found, or `spawn latexmk ENOENT` | Finish installing the full LaTeX distribution, then quit your editor or terminal completely and reopen it (on Windows, restart the computer if that isn't enough). On Linux, use VS Code's `.deb` or `.rpm`, not the Flatpak. Optional, in a terminal: `python3 scripts/build.py --doctor` names the missing tool and the next step. |
| VS Code says **Restricted Mode**, or LaTeX Workshop does nothing | Trust the folder: click **Restricted Mode** in the status bar and choose **Trust**. LaTeX Workshop is off in untrusted folders. |
| `You have requested release '2022-06-01' of LaTeX` | Your TeX Live is older than the 2022 release this starter is written for (common with Ubuntu 22.04's packages). The sample still compiled with TeX Live 2021 in a test, so you can usually continue; if something looks wrong, install [TeX Live from tug.org](https://tug.org/texlive/quickinstall.html). |
| `Found biblatex control file version ..., expected version ...` | Biber and biblatex come from different TeX installations or years. Keep one TeX distribution, update it completely, and make sure `biber` comes from it. |
| `I can't write on file chapters/...aux` (or `appendices/...aux`) after typing a build command | Only hand-typed builds with an output folder (`latexmk -outdir=...` or `pdflatex -output-directory=...`) do this; latexmk usually retries by itself. Build with `python3 scripts/build.py`, or with `latexmk -norc -pdf main.tex` without `-outdir`. Editors and Overleaf are not affected. |
| A file can't be found, and the folder is in OneDrive or iCloud or its path has non-English letters | Set the folder to "Always keep on this device". If it still fails, move the project to a short, plain path such as `C:\thesis` or `~/thesis`. |
| `python3` is not recognized (Windows) | Type `python` or `py` instead. Python is optional: editors compile without it. |
| On a Mac, Biber fails and the log mentions `lipo` | An older Mac build of Biber that newer macOS can't start; your thesis is fine. Update TeX Live (TeX Live Utility, **Update all packages**, or `sudo tlmgr update --self --all`) and build again. `python3 scripts/build.py --doctor` shows whether Biber starts. |
| The build helper prints "Pre-submission hints" | Your PDF was built. Fix each listed file and line before submitting — see [web sources](citations.md#web-sources-need-an-access-date) or [short captions](writing.md#use-one-full-caption-not-a-short-one). |

Please don't make an error disappear by changing margins, spacing, or the
class file. Adjust the object instead, or ask for help.

## Ask for help

Stuck on something odd? That's what this community is for. Weird edge cases
are normal, and every question helps the next student. Questions about
LaTeX, Zotero, files, or "where does this go?" are all welcome.

1. **Make it easy to see.** On Overleaf, use the share menu to create a
   view-only link. On your own computer, make the smallest made-up example
   that still shows the problem.
2. **Copy the first error**, including its file and line number.
3. **Send it** through either channel:
   <!-- Maintainer: the form URL below is the ONLY place it appears. README.md,
   CONTRIBUTING.md, and the website footer link to this section
   (#ask-for-help); change the URL here and nowhere else. -->
   - **No account needed:** the
     [help and feedback form](https://forms.gle/fjfiLfkmVhkcyRNCA).
   - **With a GitHub account:** open an issue with the **LaTeX help or bug**
     form. Answers stay public and searchable for the next person. Never
     opened one? See [how to open an issue](../CONTRIBUTING.md#open-an-issue).

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
> Remove unpublished research and personal details before sharing anything.
> A view-only link shows your whole project, so share it only with someone
> you trust, and turn link sharing off afterwards.

[Overleaf Learn](https://www.overleaf.com/learn) also explains many common errors.

Found a fix, a tip, or a tool worth passing on? The help and feedback form takes
those too, and [ways to contribute](../CONTRIBUTING.md) lists the other options.
