# Get started

For anyone starting out; no LaTeX experience needed. By the end, the sample
thesis compiles into a PDF with your name on it. Have a draft? Do these steps
first, then [bring your draft](bring-your-draft.md).

## Step 1: Choose where to write

Both routes use the same files and make the same PDF.

| | Your computer (VS Code + LaTeX Workshop) | Overleaf (in your browser) |
| --- | --- | --- |
| **Setting up** | A one-time install (a large download) and a little setup | Nothing to install; works from any computer |
| **Cost** | Free | Free plan; track changes, Git and GitHub sync, more collaborators, and longer compiles need a [paid plan](https://www.overleaf.com/user/subscription/plans) |
| **Compiling** | Fast, with no time limits or timeouts | The free plan limits compile time |
| **Internet** | Works offline | Needed |
| **Your files** | Stay on your machine, under your control; backing up is copying a folder ([backups](workflows.md#back-up-your-work)) | Live on a third-party service, with version history |
| **Working with others** | Through Git, with no project-size or collaborator limits, or by sharing the PDF | Real-time co-editing, comments, and review, suited to advisors and co-authors; the free plan limits collaborators |
| **Other tools** | Any you like: Git, Zotero auto-export, scripts | Overleaf's built-in tools |

We recommend your own computer for a full thesis. Overleaf is a great place
to start, or to co-write with others, and you can
[move between them](workflows.md#use-your-computer-and-overleaf) at any time.

## Step 2: Get the files

<!-- Maintainer: at the first release, link <repository_url>/releases/latest here (maintenance.md, "Make a release"). The landing page's "Get the starter" button opens this step. -->

1. Open the [project's GitHub page](https://github.com/diyanko/rpi-thesis-toolkit).
2. Click the green **Code** button, then **Download ZIP**. No account is needed.
3. **Your computer:** extract it into a normal folder such as
   `Documents/thesis`, keeping the folders together. **Overleaf:** keep the
   ZIP as it is.

Ignore extra folders such as `docs/` and `site/`; a tidier student-only
download is planned.

## Step 3a: Your-computer route

You need **LaTeX** (makes the PDF) and **an editor** (where you type). We
recommend VS Code with the LaTeX Workshop extension.

1. **Install LaTeX**, choosing the **full** installation (a large download;
   allow an hour or more).
   - macOS: [MacTeX](https://tug.org/mactex/)
   - Windows: [TeX Live for Windows](https://tug.org/texlive/windows.html)
     (not MiKTeX)
   - Linux: [TeX Live](https://tug.org/texlive/), or your distribution's full
     package (often `texlive-full`)

   Then **update it once**, because installers ship a snapshot and later
   fixes arrive as updates: on macOS, open **TeX Live Utility** and choose
   **Update all packages**; on Windows, open **TeX Live Manager** from the
   Start menu and update all; with TeX Live from tug.org on Linux, run
   `sudo tlmgr update --self --all`. A distribution package updates with
   your system's software updates.
2. Install [VS Code](https://code.visualstudio.com/).
3. In VS Code, choose **File → Open Folder** and open your thesis **folder**,
   not a single file.
4. Accept the offer to install the recommended **LaTeX Workshop** extension.
   No offer? Search the Extensions view for "LaTeX Workshop" by James Yu.
5. Open `main.tex` and save it. The PDF builds and opens in a tab beside your
   text. The file is `build/main.pdf`.

Build fails right after installing LaTeX? Close and reopen VS Code (on
Windows, sign out and back in once), then see [fixing problems](troubleshooting.md).

> [!NOTE]
> Tested so far only on macOS with TeXShop and the build helper. Tried
> another route? Please [tell us how it went](../CONTRIBUTING.md).

<details><summary>For experienced users: VS Code tips, MiKTeX, and terminal builds</summary>

- Saving runs the starter's recipe, **RPI Thesis Toolkit: pdfLaTeX + Biber**.
  Ctrl+click (Cmd+click on macOS) in the PDF jumps to the source. See the
  [LaTeX Workshop wiki](https://github.com/James-Yu/LaTeX-Workshop/wiki).
- **Why not MiKTeX:** the build uses `latexmk`, which needs Perl; TeX Live
  includes it, MiKTeX does not.
- **Terminal:** `python3 scripts/build.py --doctor` checks your install, and
  `python3 scripts/build.py` writes `build/main.pdf` (on Windows, `py -3`).
  Without Python, `latexmk -norc -pdf -no-shell-escape main.tex` also works.
  More in [advanced use](advanced.md).

</details>

<details><summary>Other editors: TeXShop or TeXstudio</summary>

**TeXShop** (macOS, comes with MacTeX): open `main.tex`, then choose
**Typeset → Typeset**, **Typeset → BibTeX** (it runs Biber, set by the
`!BIB program = biber` line in `main.tex`), and **Typeset → Typeset** twice.

**TeXstudio:** open `main.tex` in [TeXstudio](https://www.texstudio.org/)
and run pdfLaTeX, Biber, then pdfLaTeX twice
([compiling guide](https://texstudio-org.github.io/compiling.html)).

</details>

Then go to [Step 4](#step-4-your-first-compile).

## Step 3b: Overleaf route

1. Sign in to [Overleaf](https://www.overleaf.com/) (the free plan is enough).
2. Create a new project by **uploading** the ZIP from
   [Step 2](#step-2-get-the-files)
   ([Overleaf: creating a project](https://docs.overleaf.com/getting-started/creating-a-project)).
3. In the project menu, set the main document to **`main.tex`** and the
   compiler to **pdfLaTeX**
   ([Overleaf: the main document](https://docs.overleaf.com/getting-started/recompiling-your-project/the-main-document)).
4. Click **Recompile**. The sample PDF appears beside the editor.

Then go to [Step 4](#step-4-your-first-compile).

## Step 4: Your first compile

Compile the **unchanged** sample first, so any problem is the installation. You should see a title page reading "YOUR THESIS TITLE" with a
placeholder where the seal goes, the contents, and three short chapters.
Can't find the PDF? See [where the PDF ends up](how-it-works.md#where-the-pdf-ends-up).

### Add the RPI seal (one minute)

The seal belongs to RPI, so this unofficial starter doesn't include it.

1. Download the seal from RPI ITS's
   [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation).
2. Save it in your project's `assets` folder as **`rpi-seal.jpg`** (or
   `rpi-seal.png` if it is a PNG). On Overleaf, upload it into `assets`.
3. Compile again. The seal replaces the placeholder.

## Step 5: Your first hour

### Put your name on it

Open **`metadata.tex`** and replace the words inside the braces. Keep the
commas and braces.

![How metadata.tex fills the title page: numbered lines in metadata.tex (left) match places on a simplified title page (right). 1, title: the title in capitals at the top. 2, author: your name. 3, degree: masters gives MASTER OF SCIENCE, doctoral gives DOCTOR OF PHILOSOPHY, engineering-doctorate gives DOCTOR OF ENGINEERING. 4, each \committeemember line: one name under "Approved by", with ", Chair" after the chair. 5, department: the department name, above Rensselaer Polytechnic Institute, Troy, New York. 6, graduation month and year: the bracketed date at the bottom, such as [May 2027]. A dashed circle marks the seal's place.](diagrams/metadata-to-title-page.svg)

*In words:* each setting fills one place on the title page; the class adds
the fixed wording and the seal.

| Setting | What to write |
| --- | --- |
| `title` | Your title in normal capitalization; the title page prints it in capitals |
| `degree` | `masters` (Master of Science), `doctoral` (Doctor of Philosophy), or `engineering-doctorate` (Doctor of Engineering) |
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
   If you put it on GitHub, make the repository private.

Have a draft already? [Bring your draft](bring-your-draft.md). Curious what
just happened? See [how it works](how-it-works.md).
