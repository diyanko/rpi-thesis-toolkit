# Citations and references

For anyone adding sources to a thesis or dissertation that already compiles
([get started](get-started.md) if not). List each source once in
`references.bib`, cite it with `\cite{key}`, and LaTeX builds the reference list.

![How a citation travels. A source's details go into references.bib, either pasted by hand or exported from a citation manager such as Zotero. In a chapter you write \cite with the source's key. When you compile, Biber matches the key to the entry and formats it in your chosen style. The PDF shows the in-text citation and the entry in the reference list.](diagrams/citation-flow.svg)

*In words:* `references.bib` → `\cite{key}` in a chapter → Biber formats the
entry when you compile → citation and reference list in the PDF.

## Step 1: Agree on a style with your advisor

The sample's numbered style only shows citations working; it is **not** an
official style for any department, and neither are LaTeX defaults such as
`plain`. RPI's citation guidance is under *Additional Resources* on the
[OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation).
Use one style throughout ([change the citation style](#change-the-citation-style)).

## Step 2: Collect and cite sources with Zotero

We recommend [Zotero](https://www.zotero.org/): free, keeps your papers and
PDFs together, shares libraries with co-authors, and also works with Word.

1. **Install Zotero and its browser connector**
   ([Zotero quick start](https://www.zotero.org/support/quick_start_guide)).
   Optionally add [Better BibTeX](https://retorque.re/zotero-better-bibtex/)
   for stable citation keys.
2. **Save sources while you read** with the connector button, into one
   thesis collection. Check each item; imported details are often incomplete.
3. **Export the collection to `references.bib`** in your thesis folder, in
   **BibLaTeX** (or **Better BibLaTeX**) format
   ([Zotero: exporting](https://www.zotero.org/support/kb/exporting)). This
   replaces the sample file. On Overleaf, upload it in place of the old one,
   and again whenever it changes
   ([auto-export](#set-it-and-forget-it) can automate this).
4. **Cite with `\cite{key}`.** The key is the word after `@article{` (or
   `@book{`, ...) in the exported entry; Better BibTeX also shows it in Zotero:

   ```tex
   An earlier account explains this approach~\cite{lamport1994}.
   ```

5. **Compile.** Only sources you cite appear in the reference list.

A key in **bold** means Biber has not run or the key is not in the file
([bold keys](how-it-works.md#bold-citation-keys-and-question-marks)); the
sample chapters' citations stay bold until you replace that text. The style
chosen inside Zotero does not affect your PDF.

### Where Zotero keeps your library

**Never put the Zotero data folder in OneDrive, Dropbox, iCloud, or Google
Drive**; it can corrupt the database ([Zotero: syncing](https://www.zotero.org/support/sync)).
Use Zotero sync plus your [computer backup](workflows.md#back-up-your-work).
`references.bib` is not a library backup, but it is safe in a synced folder.

<details id="set-it-and-forget-it"><summary>For experienced users: Zotero storage, sync, Overleaf, and auto-export</summary>

- **Storage:** data sync is free and unlimited; file (PDF) sync has limited
  free storage, and group files count against the group owner's
  ([Zotero: storage](https://www.zotero.org/support/storage_faq)). If it
  fills up, buy more, use WebDAV, or keep PDFs only on your computer.
  <!-- Maintainer: checked 14 Oct 2026 against zotero.org/support/sync and storage_faq. Neither page says what happens at a full quota, so the guide does not describe it. -->
- **New computer:** use Zotero sync, or copy the whole data folder while
  Zotero is closed on both computers
  ([Zotero: moving your library](https://www.zotero.org/support/kb/transferring_a_library)).
- **Overleaf:** its built-in [Zotero integration](https://docs.overleaf.com/integrations-and-add-ons/reference-manager-integrations/zotero)
  is available only on some
  [Overleaf plans](https://docs.overleaf.com/getting-started/free-and-premium-plans).
  Free routes: upload `references.bib` again when it changes, or link it (below).
- **Auto-export:** with [Better BibTeX](https://retorque.re/zotero-better-bibtex/exporting/auto/),
  tick **Keep updated** when exporting, into your thesis folder or a synced
  folder. On Overleaf, use **Upload → From external URL** with a
  direct-download link ([Overleaf: file from a URL](https://docs.overleaf.com/managing-projects-and-files/adding-files-to-a-project/adding-a-file-from-a-url)),
  then click **Refresh** on the file to pull changes. It is not listed as a
  [premium feature](https://docs.overleaf.com/getting-started/free-and-premium-plans/premium-features);
  if your **Upload** menu lacks it, check your plan.
  <!-- Maintainer: checked 14 Oct 2026. Overleaf's premium-features page does not mention "From external URL"; its Google Drive page says linked files "can be refreshed at any time" (manual). Recheck both pages yearly. -->
- **Cautions:** export only a thesis collection; anyone with the share link
  can read it; pin [citation keys](https://retorque.re/zotero-better-bibtex/citing/).
  To keep hand-written entries too, export to `zotero.bib` and add
  `\addbibresource{zotero.bib}` in `preamble.tex`; keys must be unique.

</details>

## If you can't use Zotero: paste an entry by hand

Paste a BibTeX entry from the publisher, a library database, or Google
Scholar. These are often slightly wrong, so check each one.

1. Copy the source's BibTeX or BibLaTeX entry. It looks like:

   ```bibtex
   @book{lamport1994,
     author    = {Leslie Lamport},
     title     = {{LaTeX}: A Document Preparation System},
     edition   = {2},
     publisher = {Addison-Wesley},
     date      = {1994}
   }
   ```

2. Paste it into `references.bib`. The word after `@book{` is the **key**,
   here `lamport1994`. Every key must be unique.
3. Cite it with `\cite{lamport1994}` and compile.

Wrap capitals that must stay capitalized in braces, like `{RPI}`.

## Web sources need an access date

OGE requires an **access date for every reference with a URL**, even if your
citation style would normally leave it out. Add `urldate` with the date *you*
read it (year-month-day):

```bibtex
@online{rpi-submission,
  author  = {{Rensselaer Polytechnic Institute}},
  title   = {Submit Your Thesis / Dissertation},
  url     = {https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation},
  urldate = {2026-10-14}
}
```

Check that the date actually **prints** in your PDF; some styles hide it.
The build helper flags any `url` without a `urldate`. DOIs need no access date.

## Change the citation style

In `preamble.tex`, find this line; it is the only one you need to change:

```tex
\usepackage[backend=biber,style=numeric,sorting=none]{biblatex}
```

Replace `style=numeric,sorting=none` with a starting point from this table:

| Style family | Replace with | Package (included in full TeX Live and Overleaf) |
| --- | --- | --- |
| Numbered in order of citation (sample) | `style=numeric,sorting=none` | built in |
| Generic author–year | `style=authoryear` | built in |
| IEEE | `style=ieee` | [biblatex-ieee](https://ctan.org/pkg/biblatex-ieee) |
| APA | `style=apa` | [biblatex-apa](https://ctan.org/pkg/biblatex-apa) |
| Chicago | not a one-word swap; follow its manual | [biblatex-chicago](https://ctan.org/pkg/biblatex-chicago) |

These are starting points, not validated department presets; see each
package's manual. For a paper in a classic-BibTeX venue template, see
[turn a chapter into a paper](workflows.md#turn-a-chapter-into-a-paper).

## Check the output yourself

Citation managers handle journal articles well but are much less reliable for
**websites, reports, theses, datasets, software, standards, and archival
sources**. Compare every reference in the PDF with your official style guide.

OGE expects reference 1 to be the first citation in Chapter 1. BibLaTeX
numbers a citation in a caption where the figure or table appears, not in
the list of figures, so keep citations out of the front matter.

## If co-authors use Word

A Zotero group library lets Word users (with the
[Word plugin](https://www.zotero.org/support/word_processor_integration)) cite
the same sources, but citations do not convert between Word and LaTeX. Agree
on one main copy ([co-authors](workflows.md#co-authors-and-lab-mates)).
