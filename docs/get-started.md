# Get started

No LaTeX experience needed. By the end of this page you will *compile* the
sample thesis (turn its files into a PDF) with your own name on its title
page. Pick one of two setups; both work the same way: edit, save, see the PDF.

- **An editor on your computer** (suggested): an editor with a LaTeX
  extension rebuilds the PDF each time you save and shows it beside your text.
  The one-time install takes an hour or more, mostly waiting for a download.
- **Overleaf** (no install): the same in your browser, ready in minutes.

Have a draft? Do these steps first, then [bring your draft](bring-your-draft.md).
Not sure LaTeX suits you? Read [why LaTeX](how-it-works.md#why-latex-for-a-thesis).

## Step 1: Choose your LaTeX workspace

Both make the same PDF from the same files; choose the one that fits you.

| | Your computer (an editor) | Overleaf (in your browser) |
| --- | --- | --- |
| **Setting up** | One-time install, large download | Nothing to install |
| **Cost** | Free | Free plan; [paid plans](https://www.overleaf.com/user/subscription/plans) add features |
| **Compiling** | No time limit | Free plan has a [time limit](https://docs.overleaf.com/getting-started/free-and-premium-plans/plan-limits) |
| **Internet** | Works offline | Needed |
| **Your files** | On your machine | On Overleaf's servers |
| **Working with others** | Share the PDF, or Git | Real-time co-editing |

Your own computer suits a full thesis: no compile limit, and the files stay
with you. Overleaf suits you if you would rather install nothing or co-edit in
real time. It is your choice, not an OGE requirement, and you can
[switch later](going-further.md#use-your-computer-and-overleaf).

## Step 2: Get the files

<!-- Maintainer: scripts/bump.py moves the download link in this step and
the Overleaf link in Step 3b to the new tag, and build_site.py stops if they
do not match the release (maintenance.md, "Make a release"). The landing
page's computer card opens this step. -->

<p class="tool-actions"><a class="button" data-icon="download" href="https://github.com/diyanko/rpi-thesis-toolkit/releases/download/v0.9.0/rpi-thesis-starter-v0.9.0.zip">Download the starter (ZIP)</a></p>

1. **What's inside:** the thesis files, this guide for offline reading (open
   `START-HERE.html`), and a cheat sheet. A ZIP is one compressed file that
   holds a folder. No account needed. Reading this in `START-HERE.html`? You
   already have the files: continue to your route below.
2. **Your computer:** extract (unzip) it and move the folder that contains
   `main.tex` somewhere normal, such as `Documents`.
   - **Windows:** right-click the ZIP and choose **Extract All**. Opening it
     by double-click only previews the files. Use the inner folder if you get
     a folder inside a folder.
   - **macOS:** double-click the ZIP (Safari may have done it already).
   - **OneDrive, iCloud Drive, or Dropbox:** set the folder to "Always keep on
     this device" ([why](going-further.md#back-up-your-work)).
3. **Overleaf:** keep the ZIP as it is. (Safari unzipped it? Right-click the
   folder and choose **Compress**.)

Or: on the [project's GitHub page](https://github.com/diyanko/rpi-thesis-toolkit),
use the green **Code** button, then **Download ZIP**, for every file in the
project. You can ignore `docs/` and `site/`.

Next: [set up your computer](#step-3a-your-computer-route) or
[open the starter on Overleaf](#step-3b-overleaf-route).

## Step 3a: Your-computer route

On Overleaf? Skip to [Step 3b](#step-3b-overleaf-route).

You need **LaTeX** (the programs that make the PDF) and **an editor with a
LaTeX extension** (an add-on that compiles when you save and shows the PDF
beside your text). This guide walks through VS Code with the LaTeX Workshop
extension, a popular free editor the starter's settings are made for. Already
happy with TeXstudio or another LaTeX editor? Keep it
([other editors](#other-editors)).

1. **Install a current, full LaTeX distribution.** Allow an hour or more.
   - **Windows:** [TeX Live for Windows](https://tug.org/texlive/windows.html).
     Keep the default install folder. Choose TeX Live rather than MiKTeX: it
     includes everything this starter needs.
   - **macOS:** [MacTeX](https://tug.org/mactex/). When it finishes, open
     **TeX Live Utility** (in Applications → TeX) and choose **Update all
     packages** once. This fixes known problems, such as the bibliography step
     failing on newer macOS.
   - **Linux:** the install needs a terminal (a text window for commands);
     see the Linux steps below, or use [Overleaf](#step-3b-overleaf-route).

   **Check:** Windows shows a **TeX Live** folder in the Start menu; macOS
   has a `TeX` folder in Applications.
2. **Install [VS Code](https://code.visualstudio.com/)**, a free editor.
   Already open? Quit it completely and reopen it, so it finds LaTeX.
3. **Open the folder:** **File → Open Folder**, then pick the folder that
   contains `main.tex` (not a single file, and not the ZIP). If VS Code asks
   whether you trust the authors, choose **Yes**.
4. **Install LaTeX Workshop:** VS Code offers the extension this starter
   recommends; choose **Install**. No offer? Open the Extensions view (the
   squares icon on the left) and search for "LaTeX Workshop" by James Yu.
5. **Save to compile:** open `main.tex` and save it (Ctrl+S, or Cmd+S on
   macOS). LaTeX Workshop compiles the whole thesis, bibliography included,
   every time you save. The first compile can take a minute.
6. **See the PDF:** click **View LaTeX PDF file** (the icon at the top right
   of the editor) once. The PDF opens in a tab beside your text, refreshes
   each time you save, and scrolls to the spot you are editing. Ctrl+click
   (Cmd+click on macOS) in the PDF jumps to that line in your text.

Compile failed? **View → Problems** lists the errors with their file and line;
start with the first. "latexmk not found" or `spawn latexmk ENOENT` right
after installing means VS Code can't see LaTeX yet: quit it completely and
reopen it (on Windows, restart the computer). For anything else, paste the
error into [Explain my error](explain-my-error.md), or see
[fixing problems](troubleshooting.md#common-messages).

<details><summary>If you use Linux: install LaTeX and VS Code</summary>

Install your distribution's full LaTeX package. Ubuntu or Debian: first
refresh the package list, then install.

```sh
sudo apt update
```

```sh
sudo apt install texlive-full
```

Fedora:

<!-- TODO(verify): Fedora package names not tested on a Fedora machine; CI tests Ubuntu 24.04. -->

```sh
sudo dnf install texlive-scheme-full latexmk biber
```

Check with `latexmk -v`, which prints a version. Older distributions may
supply a TeX Live release that this starter does not support. If the compile
reports that LaTeX is too old, install the current full
[TeX Live from tug.org](https://tug.org/texlive/quickinstall.html) and add its
`bin` folder to your `PATH` (the folders where your computer looks for
programs) as its quick install guide describes, or use
[Overleaf](#step-3b-overleaf-route).

For VS Code, use the `.deb` or `.rpm`, not the Flatpak, which
[can't see programs installed outside it](https://github.com/flathub/com.visualstudio.code).

</details>

<details><summary>If the LaTeX installation fails: fixes for Windows and macOS</summary>

- **Windows:** virus scanners can stop the installer; pause scanning or run
  it again. Don't install into a folder whose path has non-English letters
  ([TeX Live's Windows notes](https://tug.org/texlive/windows.html)).
- **macOS:** stuck at "Verifying"? Restart the Mac and run the installer
  again. "The installation failed" usually means a damaged download; download
  MacTeX again ([install notes](https://tug.org/mactex/mactex-download.html)).
- **Still stuck?** Tell an AI chat your operating system and paste the
  installer's last message or the first error. Try one suggested fix at a
  time, or [ask for help](troubleshooting.md#ask-for-help).

</details>

<details id="other-editors"><summary>If you use another editor: TeXShop, TeXworks, TeXstudio, Vim, Emacs, or Sublime Text</summary>

Any editor with a LaTeX extension can compile this starter, including AI
assistants that can edit files and open a local folder. Open the folder that
contains `main.tex`. With the same files, engine, packages, and fonts the PDF
should match. Other editors don't read the starter's `.vscode` settings, so
the PDF usually appears next to `main.tex`, not in `build/`.

- **LaTeX apps with a PDF view built in:** [TeXShop](https://pages.uoregon.edu/koch/texshop/)
  (macOS), [TeXworks](https://tug.org/texworks/) (comes with TeX Live on
  Windows), and [TeXstudio](https://www.texstudio.org/) (all systems). They
  need a few clicks for the bibliography step; see the steps below.
- **An editor with a LaTeX plugin,** such as Vim ([VimTeX](https://github.com/lervag/vimtex)),
  Emacs ([AUCTeX](https://www.gnu.org/software/auctex/)), or Sublime Text
  ([LaTeXTools](https://github.com/SublimeText/LaTeXTools)).
- **Prefer typing commands?** See the optional
  [build commands](going-further.md#build-commands).

This guide's step-by-step help (cleaning up, changing the engine) covers
VS Code and Overleaf; for other editors, use their own help pages.

<details><summary>If you use TeXShop, TeXworks, or TeXstudio: step by step</summary>

Each app compiles once, then runs the bibliography step (labelled Biber or
BibTeX in its menus), then compiles twice more.

- **TeXShop:** **Typeset → Typeset**, then **Typeset → BibTeX** (it runs
  the right program because of the `% !BIB program = biber` line in
  `main.tex`), then **Typeset → Typeset** twice.
- **TeXworks:** pick **pdfLaTeX** beside the green Typeset button and click
  it; pick **Biber** and click it; then **pdfLaTeX** twice more.
- **TeXstudio:** **Build & View**. References missing? Run **Tools →
  Bibliography**, then **Build & View** twice
  ([compiling guide](https://texstudio-org.github.io/compiling.html)).

</details>

</details>

Then go to [Step 4](#step-4-check-your-first-pdf).

## Step 3b: Overleaf route

1. Sign in to [Overleaf](https://www.overleaf.com/); the free plan is enough
   to start.
2. **[Open the starter in Overleaf](https://www.overleaf.com/docs?snip_uri=https%3A%2F%2Fgithub.com%2Fdiyanko%2Frpi-thesis-toolkit%2Freleases%2Fdownload%2Fv0.9.0%2Frpi-thesis-overleaf-v0.9.0.zip)**.
   - Or upload the ZIP from [Step 2](#step-2-get-the-files) yourself:
     **New project → Upload project**
     ([Overleaf's steps](https://docs.overleaf.com/managing-projects-and-files/uploading-a-project)).
     If your files end up inside a folder, re-zip the items *inside* it.
   <!-- Checked 14 Oct 2026: Overleaf's "open from a ZIP link" created a
   project from GitHub's ZIP with main.tex at the top level and as the main
   document; recheck the release-ZIP link after each release. -->
3. **Check the file list:** `main.tex` should be at the top level.
4. Open **Settings** (the gear icon) and, under **Compiler**, check that the
   main document is **`main.tex`**, the compiler is **pdfLaTeX**, and the TeX
   Live version is the newest
   ([Overleaf: the main document](https://docs.overleaf.com/getting-started/recompiling-your-project/the-main-document)).
5. Click **Recompile**. The sample PDF appears beside the editor. Overleaf
   runs the bibliography step for you.

Compile failed or timed out? Overleaf's log, the **Logs and output files**
button beside **Recompile**, lists the errors; start with the first. Paste it
into [Explain my error](explain-my-error.md), or see
[fixing problems](troubleshooting.md#common-messages).
<!-- TODO(verify): Overleaf's log button label ("Logs and output files") was not rechecked in the current editor. -->
<!-- Checked 14 Oct 2026: the unchanged sample compiled on a free Overleaf
account with the default settings (TeX Live 2026, 12 pages). Large figures
are the usual cause of timeouts later. -->

<details><summary>What has been tested</summary>

Automated runs on fresh Windows Server 2025, macOS, and Ubuntu machines:
installing TeX as described here and compiling the starter. No separate
Windows 11 test is recorded. Overleaf's free plan: opening and compiling
it. A Mac: VS Code with LaTeX Workshop, and TeXShop. Other editors and
systems should work the same way. Tried one? Share how it went through the
[help and feedback form](troubleshooting.md#ask-for-help).

</details>

## Step 4: Check your first PDF

> [!TIP]
> **You can't break it.** Compiling reads your files and makes a PDF; it
> never changes your writing. An error means "fix this spot and compile
> again".

Your first compile uses the **unchanged** sample, so any problem comes from
the installation, not from your edits. You should see a title page reading "YOUR THESIS TITLE" with a seal
placeholder, the contents, and three short chapters. Can't find the PDF? See
[where the PDF ends up](how-it-works.md#where-the-pdf-ends-up).

### Add the RPI seal (one minute)

The seal belongs to RPI, so this unofficial starter doesn't include it.

1. Download the current seal from RPI ITS's
   [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation).
2. Save it in your project's `assets` folder as **`rpi-seal.jpg`** (or
   `rpi-seal.png` if it is a PNG). On Overleaf, upload it into `assets`.
3. Compile again. The seal replaces the placeholder.

## Step 5: Make it yours

### Put your name on it

Open **`metadata.tex`** and replace the value after each `=`. Keep the
setting names, braces, and commas. Check `degree`: write `masters` for a
master's thesis. Prefer a form? The [Settings builder](settings-builder.md)
writes the whole block for you and shows a sketch of the title page as you
type.

![How metadata.tex fills the title page: numbered lines in metadata.tex (left) match places on a simplified title page (right). 1, title: the title in capitals at the top. 2, author: your name. 3, degree: doctoral gives DOCTOR OF PHILOSOPHY, masters gives MASTER OF SCIENCE, engineering-doctorate gives DOCTOR OF ENGINEERING. 4, each \committeemember line: one name under "Approved by", with ", Chair" after the chair. 5, department: the department name, above Rensselaer Polytechnic Institute, Troy, New York. 6, graduation month and year: the bracketed date at the bottom, such as [May 2027]. A dashed circle marks the seal's place.](diagrams/metadata-to-title-page.svg)

*In words:* each setting fills one place on the title page; the class adds
the fixed wording and the seal.

| Setting | What to write |
| --- | --- |
| `title` | Normal capitalization; the title page prints capitals |
| `author` | Your full name |
| `degree` | `doctoral`, `masters`, or `engineering-doctorate` |
| `department` | Your full department name, e.g. `Department of Physics, Applied Physics and Astronomy` |
| `graduation-month` | `May`, `August`, or `December`: when you graduate, not when you submit |
| `graduation-year` | Four digits, e.g. `2027` |
| `copyright-page` | `true` adds the optional copyright page (page ii; {{cite:copyright-page}}); read that part of the current OGE manual before choosing |
| `list-of-tables`, `list-of-figures` | `true` unless you have no tables (or figures) |

<!-- TODO(verify): re-read the current manual §1.2, printed p. 3, before describing any connection between the optional copyright page and copyright registration. -->

Then list **every** approved committee member, one per line, with `[Chair]`
(or `[Co-Chair]`) on your chair's line:

```tex
\committeemember[Chair]{Professor Ada Example}
\committeemember{Professor Grace Sample}
```

Save (or click **Recompile** on Overleaf) and check the title page. For an
`&` in your title, type `\&`. Different degree name? See the
[`degree-name` setting](going-further.md#all-thesis-settings).

### Write, cite, and back up

1. **Write:** replace a paragraph in `chapters/01-introduction.tex` and
   compile ([writing basics](writing.md)).
2. **Cite:** [try the citation already in the starter](citations.md#try-the-sample-citation),
   then add your own sources.
3. **Back up** off your computer: keep the folder in a cloud-synced folder
   (OneDrive, Google Drive, Dropbox, or iCloud) or a **private** GitHub
   repository. On Overleaf, download the source ZIP now and then
   ([backups](going-further.md#back-up-your-work)).

### Stuck on something technical?

Paste the error into [Explain my error](explain-my-error.md), or ask an AI
chat for technical help only, never for writing your thesis
([how to ask well](going-further.md#use-ai-for-technical-help)).

**Next step: [writing basics](writing.md)**, for chapters, figures, tables,
and equations. Have a draft? [Bring one small section in](bring-your-draft.md)
first. Curious what just happened? See [how it works](how-it-works.md).

Writing an undergraduate thesis or a poster? The writing and citation help
works for you too, but the title page and layout follow RPI's graduate rules.
For a proposal or qualifying exam, the starter makes a good model
([how](going-further.md#write-a-proposal-or-qualifying-exam)).
