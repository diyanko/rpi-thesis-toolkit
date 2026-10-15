# Get started

For anyone starting out; no LaTeX experience needed. By the end, you will
*compile* the sample thesis (turn its files into a PDF) with your name on it.
New to LaTeX? Read [Why LaTeX for your thesis?](why-latex.md) first, or jump in.

Have a draft? Do these steps first, then [bring your draft](bring-your-draft.md).
Still drafting elsewhere? Set up now anyway, and keep drafting where you are
([the suggested workflow](how-it-works.md#the-suggested-workflow-and-why)).

Writing an undergraduate thesis, a course paper, or a poster? The writing and
citation help works for you too. The title page and page layout follow RPI's
graduate rules, so check your own program's requirements.

## Step 1: Choose your LaTeX workspace

This is where your thesis compiles into a PDF. Both routes use the same
files and run the same programs, so they make the same PDF when their TeX
versions match ([Step 3b](#step-3b-overleaf-route) sets Overleaf to the
newest).

| | Your computer | Overleaf (in your browser) |
| --- | --- | --- |
| **Setting up** | A one-time install (a large download) and an editor you choose | Nothing to install; works from any computer |
| **Cost** | Free | Free plan; track changes, full history, Git and GitHub sync, more collaborators, and longer compiles need a [paid plan](https://www.overleaf.com/user/subscription/plans) |
| **Compiling** | No time limits | The free plan's [compile time limit](https://docs.overleaf.com/getting-started/free-and-premium-plans/plan-limits) is short; a long thesis with many figures can exceed it |
| **Internet** | Works offline | Needed |
| **Your files** | Stay on your machine, under your control; backing up is copying a folder ([backups](workflows.md#back-up-your-work)) | Live on Overleaf's servers; the free plan keeps only recent history |
| **Working with others** | Share the PDF, or use Git | Real-time co-editing, comments, and review, which advisors and co-authors find easy; the free plan limits collaborators |
| **Other tools** | Any you like: Git, Zotero auto-export, scripts | Overleaf's built-in tools |

For a full thesis, this guide suggests your own computer: no compile
limits, and your files stay with you. Overleaf is the quickest start and the easiest
way to write with others. Either is a convenience choice, not an OGE
requirement, and you can
[move between them](workflows.md#use-your-computer-and-overleaf) at any time.

## Step 2: Get the files

<!-- Maintainer: at each release, update the two download links in this
step and the Overleaf link in Step 3b to the new tag (maintenance.md, "Make a
release"). The landing page's "Get the starter" button opens this step. -->

1. **[Download the starter (ZIP)](https://github.com/diyanko/rpi-thesis-toolkit/releases/download/v0.1.0-beta/rpi-thesis-starter-v0.1.0.zip)**: the thesis files, plus this
   guide for offline reading (open `START-HERE.html`) and the one-page cheat
   sheet. A ZIP is one compressed file that holds a whole folder. No account
   is needed.
2. Or, for every file in the project, open the
   [project's GitHub page](https://github.com/diyanko/rpi-thesis-toolkit),
   click the green **Code** button, then **Download ZIP**.
3. **Your computer:** extract (unzip) the ZIP, then move the folder that
   contains `main.tex` somewhere normal, such as `Documents`. You can rename
   it, for example to `thesis`.
   - **Windows:** right-click the ZIP and choose **Extract All**. Double-clicking
     only shows the files inside the ZIP, and LaTeX can't use them there.
     Extracting may create a folder inside a folder; use the inner one.
   - **macOS:** double-click the ZIP (Safari may have unzipped it already).
   - **OneDrive, iCloud Drive, or Dropbox folders** work if you set the thesis folder
     to "Always keep on this device" ([why](workflows.md#back-up-your-work)).

   **Overleaf:** keep the ZIP as it is. (Did Safari unzip it? Right-click the
   folder and choose **Compress** to make a ZIP again.)

Ignore extra folders such as `docs/` and `site/`; they don't change your PDF.
A tidier student-only download is planned.

## Step 3a: Your-computer route

You need **LaTeX** (the programs that make the PDF) and **an editor** (where
you type). Every editor runs the same programs (pdfLaTeX and Biber, usually
driven by a helper called `latexmk`), so they all make the same PDF.

1. **Install LaTeX**, choosing the **full** installation. It is a large
   download; allow an hour or more. Use TeX Live 2022 or newer if you can.
   - **Windows:** [TeX Live for Windows](https://tug.org/texlive/windows.html).
     Keep the default install folder (`C:\texlive\...`). Choose TeX Live
     rather than MiKTeX: it includes the Perl that `latexmk` needs.
   - **macOS:** [MacTeX](https://tug.org/mactex/), for Apple silicon and
     Intel Macs.
   - **Linux:** in a terminal, install your distribution's full package:
     `sudo apt install texlive-full` (Ubuntu, Debian) or `sudo dnf install
     texlive-scheme-full latexmk biber` (Fedora). Ubuntu 22.04 ships TeX Live 2021: the sample
     still compiled in a test, with a version warning. If anything looks
     wrong, install [TeX Live from tug.org](https://tug.org/texlive/quickinstall.html).

   **Check:** Windows shows a **TeX Live** folder in the Start menu; macOS
   has a `TeX` folder in Applications; on Linux, typing `latexmk -v` in a new
   terminal window prints a version.
2. **macOS only: update once.** Open **TeX Live Utility** (in
   Applications → TeX) and choose **Update all packages**. MacTeX is a
   snapshot, and updates fix known problems such as Biber not starting on
   newer macOS. (Windows and tug.org installs download current packages;
   distribution packages update with your system.)
3. **Choose an editor.** The steps below use [VS Code](https://code.visualstudio.com/)
   with the LaTeX Workshop extension (an add-on that gives VS Code LaTeX
   buttons): the suggested editor, free on every
   system, and set up by this starter. It is one good choice among several;
   to use another, see [other editors](#other-editors-and-the-command-line),
   then go to Step 4.
4. **Install VS Code.** Already open? Quit it completely (all windows) and
   reopen it, so it finds LaTeX. On Linux, use the `.deb` or `.rpm` from the
   VS Code site, not the Flatpak, which [can't see programs installed
   outside it](https://github.com/flathub/com.visualstudio.code).
5. **Open the folder:** choose **File → Open Folder** and pick the folder
   that contains `main.tex` (not a single file, and not the ZIP). If VS Code
   asks whether you trust the authors of the files, choose **Yes**: LaTeX
   Workshop is turned off in Restricted Mode.
6. **Install LaTeX Workshop:** accept the offer to install the recommended
   extension. No offer? Search the Extensions view for "LaTeX Workshop" by
   James Yu.
7. **Compile:** open `main.tex` and save it (Ctrl+S, or Cmd+S on macOS), or
   click the **Build LaTeX project** button (a triangle) at the top right.
   A build takes a few seconds.
8. **See the PDF:** click **View LaTeX PDF file**, the button next to the
   triangle, or run it from the Command Palette (Ctrl+Shift+P, or
   Cmd+Shift+P on macOS). The file is `build/main.pdf` in your thesis folder.

Build failed? The **Problems** panel (**View → Problems**) shows the first
error. "latexmk not found" or `spawn latexmk ENOENT` right after installing
LaTeX means VS Code can't see it yet: quit VS Code completely and reopen it
(on Windows, restart the computer if that isn't enough). Then see
[fixing problems](troubleshooting.md#common-messages).

> [!NOTE]
> What has been tested: on fresh Windows 11, macOS, and Ubuntu machines,
> installing TeX as described here and compiling the starter (with the build
> helper and with `latexmk`); on Overleaf's free plan, opening and compiling
> the starter; and on a Mac, VS Code with LaTeX Workshop and TeXShop. Other
> editors and systems should work the same way. Tried one? Share how it
> went through the [help and feedback form](troubleshooting.md#ask-for-help).

<details><summary>If the LaTeX installation fails: fixes for Windows, macOS, and Linux</summary>

- **Windows:** virus scanners can lock folders and stop the installer; pause
  scanning during the install, or run the installer again. Never install into
  a folder whose path has non-English letters
  ([TeX Live's Windows notes](https://tug.org/texlive/windows.html)).
- **macOS:** stuck at "Verifying"? Restart the Mac and run the installer
  again. "The installation failed" usually means a damaged download;
  download MacTeX again ([MacTeX's install notes](https://tug.org/mactex/mactex-download.html)).
- **Linux, TeX Live from tug.org:** add its `bin` folder to your `PATH` (the
  list of folders where your computer looks for programs), as
  the [quick install guide](https://tug.org/texlive/quickinstall.html)
  describes, then open a new terminal. `tlmgr` updates only this kind of
  install, not distribution packages.

</details>

### Other editors and the command line

Pick what you like; they all run the same programs and make the same PDF.
Editors other than VS Code don't read this starter's `.vscode` settings, so
the PDF usually appears next to `main.tex` instead of in `build/`.

- **LaTeX apps that need no setup:** [TeXShop](https://pages.uoregon.edu/koch/texshop/)
  (macOS; comes with MacTeX), [TeXworks](https://tug.org/texworks/) (comes
  with TeX Live on Windows; also on macOS and Linux), and
  [TeXstudio](https://www.texstudio.org/) (all systems). Open `main.tex` and
  run pdfLaTeX, then Biber, then pdfLaTeX twice.
- **Your own editor with a LaTeX plugin,** such as Vim ([VimTeX](https://github.com/lervag/vimtex)),
  Emacs ([AUCTeX](https://www.gnu.org/software/auctex/)), or Sublime Text
  ([LaTeXTools](https://github.com/SublimeText/LaTeXTools)). Most run
  `latexmk` for you.
- **For experienced users, any editor plus the command line** (optional;
  you type commands in a terminal, a text window for commands): in the
  thesis folder, run
  `latexmk -norc -pdf main.tex`, or the starter's helper,
  `python3 scripts/build.py`, which writes `build/main.pdf` and checks
  your setup with `--doctor` ([build commands](advanced.md#build-commands)).
- **Online:** [Overleaf](#step-3b-overleaf-route).

<details><summary>If you use TeXShop, TeXworks, or TeXstudio: step by step</summary>

- **TeXShop:** choose **Typeset → Typeset**, then **Typeset → BibTeX** (it
  runs Biber because of the `% !BIB program = biber` line at the top of
  `main.tex`), then **Typeset → Typeset** twice.
- **TeXworks:** pick **pdfLaTeX** in the menu beside the green Typeset
  button and click Typeset; pick **Biber** and click it; then pick
  **pdfLaTeX** again and click it twice.
- **TeXstudio:** click **Build & View**; it also reads the `% !BIB` line.
  If the references are missing, run **Tools → Bibliography**, then
  **Build & View** twice ([compiling guide](https://texstudio-org.github.io/compiling.html)).

</details>

<details><summary>For experienced users: VS Code details, MiKTeX, and Python</summary>

- The starter's recipe is **RPI Thesis Toolkit: pdfLaTeX + Biber**, which
  runs `latexmk`. Ctrl+click (Cmd+click on macOS) in the PDF jumps to the
  source. See the [LaTeX Workshop wiki](https://github.com/James-Yu/LaTeX-Workshop/wiki).
- **MiKTeX** works only if you also install Perl, because `latexmk` is a
  Perl script; TeX Live includes Perl.
- **Python is optional.** Only `scripts/build.py` needs it (3.9 or newer);
  editors don't. On Windows, type `python` or `py` instead of `python3`. On
  macOS, the first `python3` may offer to install the command line developer
  tools; accept, or use `latexmk` instead.

</details>

Then go to [Step 4](#step-4-your-first-compile).

## Step 3b: Overleaf route

1. Sign in to [Overleaf](https://www.overleaf.com/) (the free plan is enough
   to start).
2. **[Open the starter in Overleaf](https://www.overleaf.com/docs?snip_uri=https%3A%2F%2Fgithub.com%2Fdiyanko%2Frpi-thesis-toolkit%2Freleases%2Fdownload%2Fv0.1.0-beta%2Frpi-thesis-overleaf-v0.1.0.zip)**. Overleaf creates a new project
   from the thesis files in one step.
   - Or upload it yourself: choose **New project → Upload project** and pick
     the ZIP from [Step 2](#step-2-get-the-files)
     ([Overleaf: uploading a project](https://docs.overleaf.com/managing-projects-and-files/uploading-a-project)).
     Overleaf removes the single outer folder that GitHub's ZIP adds; if your
     files still sit inside a folder, re-zip the items *inside* it.
   <!-- Checked 14 Oct 2026: Overleaf's "open from a ZIP link" created a
   project from GitHub's ZIP with main.tex at the top level and as the main
   document; recheck the release-ZIP link after each release. -->
3. **Check the file list:** `main.tex` should be at the top level.
4. Open **Settings** (the gear icon, or **File → Settings**) and, under
   **Compiler**, check that the main document is **`main.tex`**, the compiler
   is **pdfLaTeX**, and the TeX Live version is the newest
   ([Overleaf: the main document](https://docs.overleaf.com/getting-started/recompiling-your-project/the-main-document)).
5. Click **Recompile**. The sample PDF appears beside the editor.

Compile timed out? See [fixing problems](troubleshooting.md#common-messages).
<!-- Checked 14 Oct 2026: the unchanged sample compiled on a free Overleaf
account with the default settings (TeX Live 2026, 12 pages). Large figures
are the usual cause of timeouts later. -->

Then go to [Step 4](#step-4-your-first-compile).

## Step 4: Your first compile

> [!TIP]
> **You can't break it.** Compiling reads your files and makes a PDF; it
> never changes your writing. An error means "fix this spot and compile again". Overleaf keeps a
> version history, and on your computer, keep a copy ([backups](workflows.md#back-up-your-work)).

Compile the **unchanged** sample first, so any problem is the installation. You should see a title page reading "YOUR THESIS TITLE" with a
placeholder where the seal goes, the contents, and three short chapters.
Can't find the PDF? See [where the PDF ends up](how-it-works.md#where-the-pdf-ends-up).

### Add the RPI seal (one minute)

The seal belongs to RPI, so this unofficial starter doesn't include it.

1. Download the current seal from RPI ITS's
   [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation).
2. Save it in your project's `assets` folder as **`rpi-seal.jpg`** (or
   `rpi-seal.png` if it is a PNG). On Overleaf, upload it into `assets`.
3. Compile again. The seal replaces the placeholder.

## Step 5: Your first hour

### Put your name on it

Open **`metadata.tex`** and replace the words inside the braces. Keep the
commas and braces.

![How metadata.tex fills the title page: numbered lines in metadata.tex (left) match places on a simplified title page (right). 1, title: the title in capitals at the top. 2, author: your name. 3, degree: doctoral gives DOCTOR OF PHILOSOPHY, masters gives MASTER OF SCIENCE, engineering-doctorate gives DOCTOR OF ENGINEERING. 4, each \committeemember line: one name under "Approved by", with ", Chair" after the chair. 5, department: the department name, above Rensselaer Polytechnic Institute, Troy, New York. 6, graduation month and year: the bracketed date at the bottom, such as [May 2027]. A dashed circle marks the seal's place.](diagrams/metadata-to-title-page.svg)

*In words:* each setting fills one place on the title page; the class adds
the fixed wording and the seal.

| Setting | What to write |
| --- | --- |
| `title` | Your title in normal capitalization; the title page prints it in capitals |
| `degree` | `doctoral` (Doctor of Philosophy, the sample's setting), `masters` (Master of Science), or `engineering-doctorate` (Doctor of Engineering) |
| `department` | Your full department name, e.g. `Department of Physics, Applied Physics and Astronomy` (not just `Department of Physics`) |
| `graduation-month` | `May`, `August`, or `December`: when you graduate, not when you submit |
| `graduation-year` | Four digits, e.g. `2027` |
| `copyright-page` | `true` only if you will file for copyright (OGE manual §1.2), otherwise `false` |
| `list-of-tables`, `list-of-figures` | `true` unless you have no tables (or figures) at all |

Then list **every** approved committee member, one per line, with `[Chair]`
(or `[Co-Chair]`) on your chair's line:

```tex
\committeemember[Chair]{Professor Ada Example}
\committeemember{Professor Grace Sample}
```

Compile and check the title page. For an `&` in your title, type `\&`. Need
a different degree name? See the [`degree-name` setting](advanced.md#all-thesis-settings).

### Write, cite, and back up

1. **Write:** replace a paragraph in `chapters/01-introduction.tex` and
   compile ([writing basics](writing.md)).
2. **Cite:** see [citations and references](citations.md).
3. **Back up:** copy your project folder somewhere safe (on Overleaf, download
   the source ZIP), and make it a habit ([backups](workflows.md#back-up-your-work)).
   If you put it on GitHub, make its repository (its project space there) private.

Have a draft already? [Bring your draft](bring-your-draft.md). Still drafting
elsewhere? Move one small section in now, ideally with a figure and a few
citations, and compile it: you find conversion problems while there is still
time. Curious what just happened? See [how it works](how-it-works.md).
