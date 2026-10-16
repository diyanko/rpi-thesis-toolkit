# Get started

No LaTeX experience needed. You will *compile* the sample thesis (turn its
files into a PDF) with your name on it. Overleaf gets you there in minutes;
installing LaTeX on your computer takes longer, often an hour or more, mostly
waiting for a download. Curious whether LaTeX suits you? See [why LaTeX](how-it-works.md#why-latex-for-a-thesis), or jump in.

Have a draft? Do these steps first, then [bring your draft](bring-your-draft.md).
Still drafting elsewhere? That is fine
([the suggested workflow](how-it-works.md#the-suggested-workflow-and-why)).

## Step 1: Choose your LaTeX workspace

This is where your thesis becomes a PDF. With the same files, engine,
packages, and fonts, both routes make the same PDF. Your first checkpoint is
the same on either route: the sample PDF with your name on it ([Step 4](#step-4-your-first-compile)
and [Step 5](#step-5-make-it-yours)).

| | Your computer | Overleaf (in your browser) |
| --- | --- | --- |
| **Setting up** | One-time install, large download | Nothing to install |
| **Cost** | Free | Free plan; [paid plans](https://www.overleaf.com/user/subscription/plans) add features |
| **Compiling** | No time limit | Free plan has a [time limit](https://docs.overleaf.com/getting-started/free-and-premium-plans/plan-limits) |
| **Internet** | Works offline | Needed |
| **Your files** | On your machine | On Overleaf's servers |
| **Working with others** | Share the PDF, or Git | Real-time co-editing |

Overleaf is the quickest start. Your own computer suits a full thesis (no
compile limit, files stay with you). Either is your choice, not an OGE
requirement, and you can
[switch later](going-further.md#use-your-computer-and-overleaf).

## Step 2: Get the files

<!-- Maintainer: at each release, update the two download links in this
step and the Overleaf link in Step 3b to the new tag (maintenance.md, "Make a
release"). The landing page's computer card opens this step. -->

1. **[Download the starter (ZIP)](https://github.com/diyanko/rpi-thesis-toolkit/releases/download/v0.5.0/rpi-thesis-starter-v0.5.0.zip)**:
   the thesis files, this guide for offline reading (open `START-HERE.html`),
   and a cheat sheet. A ZIP is one compressed file that holds a folder. No
   account needed. (Opened `START-HERE.html` from the starter ZIP? You
   already have the files: continue to your route below.)
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

You need **LaTeX** (the programs that make the PDF) and **an editor** (where
you type). Every editor runs the same programs, so with the same files, engine,
packages, and fonts they make the same PDF.

1. **Install a current, full LaTeX distribution** using the route for your
   system below. Allow an hour or more.
   - **Windows:** [TeX Live for Windows](https://tug.org/texlive/windows.html).
     Keep the default install folder. Choose TeX Live rather than MiKTeX: it
     includes the Perl that `latexmk` needs.
   - **macOS:** [MacTeX](https://tug.org/mactex/).
   - **Linux:** this install needs terminal commands (a terminal is a text
     window for commands). If you would rather avoid the terminal, use
     [Overleaf](#step-3b-overleaf-route). Otherwise, install your
     distribution's full package. Ubuntu or Debian: first refresh the package list, then install.

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

     Older distributions may supply a TeX Live release that this starter
     does not support. If setup reports that LaTeX is too old, install the
     current full [TeX Live from tug.org](https://tug.org/texlive/quickinstall.html),
     or use [Overleaf](#step-3b-overleaf-route).

   **Check:** Windows shows a **TeX Live** folder in the Start menu; macOS
   has a `TeX` folder in Applications; on Linux, `latexmk -v` prints a
   version. Open a new terminal window after installing, so it finds LaTeX.
2. **macOS only: update once.** Open **TeX Live Utility** (in
   Applications → TeX) and choose **Update all packages**. This fixes known
   problems, such as Biber not starting on newer macOS.
3. **Install [VS Code](https://code.visualstudio.com/)**, the suggested
   editor: free, and set up by this starter. Already open? Quit it completely
   and reopen it, so it finds LaTeX. On Linux, use the `.deb` or `.rpm`, not
   the Flatpak, which [can't see programs installed outside
   it](https://github.com/flathub/com.visualstudio.code). Prefer another
   editor? See [other editors](#other-editors-and-the-command-line), then go
   to Step 4.
4. **Open the folder:** **File → Open Folder**, then pick the folder that
   contains `main.tex` (not a single file, and not the ZIP). If VS Code asks
   whether you trust the authors, choose **Yes**.
5. **Install LaTeX Workshop** (an add-on that gives VS Code LaTeX buttons):
   accept the recommended extension. No offer? Search the Extensions view
   for "LaTeX Workshop" by James Yu.
6. **Compile:** open `main.tex` and save it (Ctrl+S, or Cmd+S on macOS), or
   click the **Build LaTeX project** triangle at the top right.
7. **See the PDF:** click **View LaTeX PDF file**, next to the triangle. The
   file is `build/main.pdf`.

Build failed? **View → Problems** shows the first error. "latexmk not found"
or `spawn latexmk ENOENT` right after installing means VS Code can't see
LaTeX yet: quit it completely and reopen it (on Windows, restart the
computer). Then see [fixing problems](troubleshooting.md#common-messages).

<details><summary>If the LaTeX installation fails: fixes for Windows, macOS, and Linux</summary>

- **Still stuck?** Tell an AI chat your operating system and paste the
  installer's last message or the first build error. Try one suggested fix
  at a time.
- **Windows:** virus scanners can stop the installer; pause scanning or run
  it again. Don't install into a folder whose path has non-English letters
  ([TeX Live's Windows notes](https://tug.org/texlive/windows.html)).
- **macOS:** stuck at "Verifying"? Restart the Mac and run the installer
  again. "The installation failed" usually means a damaged download; download
  MacTeX again ([install notes](https://tug.org/mactex/mactex-download.html)).
- **Linux, TeX Live from tug.org:** add its `bin` folder to your `PATH` (the
  folders where your computer looks for programs), as the [quick install
  guide](https://tug.org/texlive/quickinstall.html) describes, then open a
  new terminal.

</details>

### Other editors and the command line

They run the same programs, so with the same files, engine, packages, and
fonts the PDF should match. Other editors don't read this starter's
`.vscode` settings, so the PDF usually appears next to `main.tex`, not in
`build/`.

- **Apps that need no setup:** [TeXShop](https://pages.uoregon.edu/koch/texshop/)
  (macOS), [TeXworks](https://tug.org/texworks/) (comes with TeX Live on
  Windows), and [TeXstudio](https://www.texstudio.org/) (all systems). Open
  `main.tex` and run pdfLaTeX, then Biber, then pdfLaTeX twice. This guide's
  step-by-step help (cleaning up, changing the engine) covers VS Code and
  Overleaf; for these apps, use their own help pages.
- **Your own editor with a LaTeX plugin,** such as Vim ([VimTeX](https://github.com/lervag/vimtex)),
  Emacs ([AUCTeX](https://www.gnu.org/software/auctex/)), or Sublime Text
  ([LaTeXTools](https://github.com/SublimeText/LaTeXTools)).
- **The command line** (a terminal is a text window for commands). In the
  thesis folder, run:

  ```sh
  latexmk -norc -pdf main.tex
  ```

  Or use the starter's helper, `python3 scripts/build.py` (on Windows,
  `py scripts/build.py`), which writes `build/main.pdf` and checks your setup
  with `--doctor`
  ([build commands](going-further.md#build-commands)).
- **Online:** [Overleaf](#step-3b-overleaf-route).

<details><summary>If you use TeXShop, TeXworks, or TeXstudio: step by step</summary>

- **TeXShop:** **Typeset → Typeset**, then **Typeset → BibTeX** (it runs
  Biber because of the `% !BIB program = biber` line in `main.tex`), then
  **Typeset → Typeset** twice.
- **TeXworks:** pick **pdfLaTeX** beside the green Typeset button and click
  it; pick **Biber** and click it; then **pdfLaTeX** twice more.
- **TeXstudio:** **Build & View**. References missing? Run **Tools →
  Bibliography**, then **Build & View** twice
  ([compiling guide](https://texstudio-org.github.io/compiling.html)).

</details>

<details><summary>Want more control? VS Code details, MiKTeX, and Python</summary>

- The starter's recipe is **RPI Thesis Toolkit: pdfLaTeX + Biber**, which
  runs `latexmk`. Ctrl+click (Cmd+click on macOS) in the PDF jumps to the
  source ([LaTeX Workshop wiki](https://github.com/James-Yu/LaTeX-Workshop/wiki)).
- **MiKTeX** needs Perl installed too, because `latexmk` is a Perl script.
- **Python is optional;** only `scripts/build.py` needs it (3.9 or newer).
  On Windows, type `py` instead of `python3`. On macOS, the first
  `python3` may offer to install developer tools; accept, or use `latexmk`.

</details>

Then go to [Step 4](#step-4-your-first-compile).

## Step 3b: Overleaf route

1. Sign in to [Overleaf](https://www.overleaf.com/); the free plan is enough
   to start.
2. **[Open the starter in Overleaf](https://www.overleaf.com/docs?snip_uri=https%3A%2F%2Fgithub.com%2Fdiyanko%2Frpi-thesis-toolkit%2Freleases%2Fdownload%2Fv0.5.0%2Frpi-thesis-overleaf-v0.5.0.zip)**.
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
5. Click **Recompile**. The sample PDF appears beside the editor.

Compile timed out? See [fixing problems](troubleshooting.md#common-messages).
<!-- Checked 14 Oct 2026: the unchanged sample compiled on a free Overleaf
account with the default settings (TeX Live 2026, 12 pages). Large figures
are the usual cause of timeouts later. -->

<details><summary>What has been tested</summary>

Automated runs on fresh Windows Server 2025, macOS, and Ubuntu machines:
installing TeX as described here and compiling the starter. No separate
Windows 11 test is recorded. Overleaf's free plan: opening and compiling
it. A Mac: VS Code with LaTeX Workshop, and TeXShop. Other editors and
systems should work the same way. Tried one? Tell us through the
[help and feedback form](troubleshooting.md#ask-for-help).

</details>

Then go to [Step 4](#step-4-your-first-compile).

## Step 4: Your first compile

> [!TIP]
> **You can't break it.** Compiling reads your files and makes a PDF; it
> never changes your writing. An error means "fix this spot and compile
> again".

Compile the **unchanged** sample first, so any problem is the installation.
You should see a title page reading "YOUR THESIS TITLE" with a seal
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
master's thesis.

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
| `copyright-page` | `true` only if you will file for copyright (OGE manual §1.2) |
| `list-of-tables`, `list-of-figures` | `true` unless you have no tables (or figures) |

Then list **every** approved committee member, one per line, with `[Chair]`
(or `[Co-Chair]`) on your chair's line:

```tex
\committeemember[Chair]{Professor Ada Example}
\committeemember{Professor Grace Sample}
```

Compile and check the title page. For an `&` in your title, type `\&`.
Different degree name? See the [`degree-name` setting](going-further.md#all-thesis-settings).

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

An AI chat can explain an error or walk you through an install. It is
optional, and for technical help only, never for writing your thesis. Give it
your operating system and the first error, try one change at a time, keep
your original, and don't paste confidential or unpublished material
([more](going-further.md#use-ai-for-technical-help)).

**Next step: [writing basics](writing.md)**, for chapters, figures, tables,
and equations. Have a draft? [Bring one small section in](bring-your-draft.md)
first. Curious what just happened? See [how it works](how-it-works.md).

Writing an undergraduate thesis or a poster? The writing and citation help
works for you too, but the title page and layout follow RPI's graduate rules.
