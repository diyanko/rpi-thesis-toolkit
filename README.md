# RPI Thesis Toolkit

An unofficial, community-made starter. Not affiliated with or endorsed by
Rensselaer Polytechnic Institute or its Office of Graduate Education (OGE).

**Write your RPI thesis or dissertation in LaTeX — even if you have never used it before.**

Draft anywhere, bring your text in, and let one swappable formatting file
(`rpi-thesis.cls`) handle margins, page numbers, headings, contents, and
references — on your own computer, on Overleaf, or both. No programming, Git, or
paid software required.

**[Read the guide on the website](https://diyanko.github.io/rpi-thesis-toolkit/)**
(or [in this repository](docs/get-started.md))

> [!IMPORTANT]
> The official requirements are on OGE's
> [thesis and dissertation submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation),
> and RPI's official LaTeX template and the RPI seal are on RPI ITS's
> [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation).
> This toolkit works alongside them; always check your document against
> OGE's current requirements.

## Download

Click the green **Code** button above, then **Download ZIP** (no account
needed). A student-only release ZIP with the guide included for offline
reading is planned. Write on your own computer or in your browser with
Overleaf — the [get-started guide](docs/get-started.md) covers both.

## Make your first change

1. Compile **`main.tex`** once, unchanged. You should see the sample PDF,
   with a placeholder box where the RPI seal goes.
2. Add the seal: download it from RPI and save it as `assets/rpi-seal.jpg`
   ([how](assets/README.md)).
3. Open **`metadata.tex`** and fill in your title, name, degree, department,
   graduation date, and committee.
4. Compile again and check the title page.
5. Replace the text in `frontmatter/abstract.tex` and `chapters/01-introduction.tex`.
6. Keep going with [writing basics](docs/writing.md).

## What's where

| File or folder | What it holds |
| --- | --- |
| `main.tex` | The file you compile; sets the order of sections |
| `metadata.tex` | Your name, degree, committee, and graduation date |
| `frontmatter/`, `chapters/`, `appendices/` | Your writing |
| `figures/` | Your images |
| `references.bib` | Your sources |
| `preamble.tex` | Citation style and extra packages |
| `rpi-thesis.cls` | Formatting rules (you normally never edit this) |
| `assets/` | The RPI seal, which you download yourself ([how](assets/README.md)) |
| `cheatsheet/` | A one-page printable reference |

Edit on your computer with VS Code and the LaTeX Workshop extension
(recommended; this starter suggests the extension when you open the folder)
or the simpler TeXShop (macOS) or TeXstudio, or in your browser with
Overleaf (nothing to install). More detail in [how it works](docs/how-it-works.md).

## Guide

The guide has four stages. Start at the top, or go straight to what you need.

- **Start:** [Get started](docs/get-started.md) (your computer or Overleaf,
  first compile, your first hour) · [Bring your draft](docs/bring-your-draft.md)
  (from Word, Google Docs, a paper, or RPI's official LaTeX template)
- **Write:** [How it works](docs/how-it-works.md) (files, compiling, where the
  PDF goes) · [Writing basics](docs/writing.md) (headings, figures, tables,
  equations) · [Citations](docs/citations.md) (Zotero, styles)
- **Fix and finish:** [Fixing problems](docs/troubleshooting.md) (errors and
  getting help) · [Submitting](docs/submission.md) (the path to graduation and
  final checks)
- **Go further:** [Workflows](docs/workflows.md) (advisor review, both
  your computer and Overleaf, backups, updates) ·
  [Advanced use](docs/advanced.md) (every setting and build command)

The formatting targets RPI graduate theses and dissertations. You can adapt
the structure for other projects, but their requirements need their own check.

## Feedback and help

Questions, bugs, and ideas are welcome as GitHub issues on this repository.
No GitHub account? See
[ask for help or give feedback without a GitHub account](docs/troubleshooting.md#ask-for-help).

## Credit and license

Written for this project by the people on the [credits page](CREDITS.md),
which also names the sources and tools it builds on. Want to help? See
[CONTRIBUTING.md](CONTRIBUTING.md) and our [code of conduct](CODE_OF_CONDUCT.md).
The class, scripts, guides, diagrams, and website are ours and use
[the MIT license](LICENSE.md). RPI's requirements, manual, original template,
seal, and name are RPI's, and tools such as LaTeX, Biber, Pandoc, and Zotero
belong to their own projects: see
[what's ours and what isn't](CREDITS.md#whats-ours-and-what-isnt). To cite
the toolkit itself, use `CITATION.cff`.
