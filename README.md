# RPI Thesis Toolkit

An unofficial, community-made starter. Not affiliated with or endorsed by
Rensselaer Polytechnic Institute or its Office of Graduate Education (OGE).

**Write your RPI thesis or dissertation in LaTeX — even if you have never used it before.**

Get the starter, compile your first PDF, and let one shared formatting file
(`rpi-thesis.cls`) handle margins, page numbers, headings, contents, and
references — on your own computer, on Overleaf, or both. Draft wherever you
and your advisor work best, and bring each chapter in when it is ready. No programming, Git, or
paid software required.

Writing an undergraduate thesis, a course paper, slides, or a poster? The
writing, citation, and figure help works for you too. The title page and page
layout follow RPI's graduate rules, so check your own program's requirements.

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

**[Download the starter (ZIP)](https://github.com/diyanko/rpi-thesis-toolkit/releases/download/v0.3.0/rpi-thesis-starter-v0.3.0.zip)**: the thesis files, the guide for
offline reading, and the cheat sheet (no account needed). Prefer Overleaf?
**[Open the starter in Overleaf](https://www.overleaf.com/docs?snip_uri=https%3A%2F%2Fgithub.com%2Fdiyanko%2Frpi-thesis-toolkit%2Freleases%2Fdownload%2Fv0.3.0%2Frpi-thesis-overleaf-v0.3.0.zip)**. The
[get-started guide](docs/get-started.md) covers both your computer and Overleaf.

## Make your first change

1. Compile **`main.tex`** once, unchanged. (To *compile* is to turn your
   files into a PDF.) You should see the sample PDF, with a placeholder box
   where the RPI seal goes.
2. Add the seal: download it from RPI and save it as `assets/rpi-seal.jpg`
   ([how to add the seal](assets/README.md)).
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
| `preamble.tex` | Citation style and extra packages (add-ons for LaTeX) |
| `rpi-thesis.cls` | Formatting rules (you normally never edit this) |
| `assets/` | The RPI seal, which you download yourself ([how to add it](assets/README.md)) |
| `cheatsheet/` | A one-page printable reference |

Write on your computer in any LaTeX editor, or in your browser with
Overleaf (nothing to install); every route runs the same programs on the
same files. The guide's steps use VS Code with the LaTeX Workshop extension,
which this starter sets up, and also cover TeXShop, TeXworks, TeXstudio, other
editors, and the command line if you prefer it ([choose an editor](docs/get-started.md#other-editors-and-the-command-line)).
More detail in [how it works](docs/how-it-works.md).

## Guide

The guide has four stages. Start at the top, or go straight to what you need.

- **Start:** [Why LaTeX for your thesis?](docs/why-latex.md) (what it does
  for you, and the honest costs) · [Get started](docs/get-started.md) (your
  computer or Overleaf, first compile, your first hour) · [Bring your draft](docs/bring-your-draft.md)
  (from Markdown, Google Docs, Word, a paper, or RPI's official LaTeX template)
- **Write:** [How it works](docs/how-it-works.md) (files, compiling, and a
  suggested workflow) · [Writing basics](docs/writing.md) (headings, figures, tables,
  equations) · [Citations](docs/citations.md) (Zotero, styles)
- **Fix and finish:** [Fixing problems](docs/troubleshooting.md) (errors and
  getting help) · [Submitting](docs/submission.md) (the path to graduation and
  final checks)
- **Go further:** [Workflows](docs/workflows.md) (advisor review, both
  your computer and Overleaf, backups, updates, AI help) ·
  [Advanced use](docs/advanced.md) (every setting and build command)

Looking for one task? [How do I…?](docs/how-do-i.md) links each common task
to the section that answers it.

## Feedback and help

Questions, bugs, tips, and ideas are all welcome, whichever way suits you:
the [help and feedback form](docs/troubleshooting.md#ask-for-help) (no
account needed), a GitHub issue, or a pull request, including one built with
an AI assistant. [CONTRIBUTING.md](CONTRIBUTING.md#pick-the-way-that-suits-you)
walks through each.

## Credit and license

Written for this project by the people on the [credits page](CREDITS.md),
which also names the sources and tools it builds on. Want to help? See
[CONTRIBUTING.md](CONTRIBUTING.md) and the [code of conduct](CODE_OF_CONDUCT.md).
The class, scripts, guides, diagrams, and website were written for this
project and use [the MIT license](LICENSE.md). RPI's requirements, manual, original template,
seal, and name are RPI's, and tools such as LaTeX, Biber, Pandoc, and Zotero
belong to their own projects: see
[what's ours and what isn't](CREDITS.md#whats-ours-and-what-isnt). To cite
the toolkit itself, use `CITATION.cff`.
