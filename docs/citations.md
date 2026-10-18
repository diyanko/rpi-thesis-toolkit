# Citations and references

For anyone adding sources to a thesis or dissertation that already compiles
([get started](get-started.md) if not). List each source once in
`references.bib`, cite it with a command such as `\parencite{key}`, and
LaTeX builds the reference list for you.

## Try the sample citation

Try it on the source already in the starter; leave `references.bib` alone.
`\parencite{key}` cites in brackets in this numbered style, and
`\textcite{key}` puts the author in your sentence
([all the commands](#change-the-citation-style)).

1. Open `chapters/01-introduction.tex`.
2. Add this as a new paragraph:

   ```tex
   This example cites the sample book~\parencite{lamport1994}.
   ```

3. Compile `main.tex` and find the new sentence in your PDF. You should see
   another [1] pointing to Lamport's book, already listed under REFERENCES.

That is a working citation. Ready for your own sources? Pick a style below,
then collect them with Zotero or
[paste an entry by hand](#if-you-cant-use-zotero-paste-an-entry-by-hand).

![How a citation travels. A source's record (author, title, year) gets a citation key such as lamport1994 and goes into references.bib, from Zotero or pasted by hand. The chapter contains only \parencite{lamport1994}. When you compile, Biber prints [1] in the text and the full entry under REFERENCES.](diagrams/citation-flow.svg)

*In words:* a source's **key** goes into `references.bib` and into
`\parencite{key}` in your chapter. When you compile, the bibliography step (a
program called Biber) turns that into [1] and a full reference-list entry.

## Step 1: Agree on a style with your advisor

Fields differ: the humanities often use Chicago or MLA, the social sciences
APA, and engineering IEEE. The sample's numbered style only shows citations
working; it is **not** a department's style. RPI's citation guidance is under
*Additional Resources* on the
[OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation).
Use one style throughout ([change the citation style](#change-the-citation-style)).

## Step 2: Collect and cite sources with Zotero

This guide suggests [Zotero](https://www.zotero.org/), a free citation
manager that keeps your papers together and shares libraries with co-authors.
It is a convenience, not an OGE requirement.

1. **Install Zotero and its browser connector**
   ([Zotero quick start](https://www.zotero.org/support/quick_start_guide)).
   Optionally add [Better BibTeX](https://retorque.re/zotero-better-bibtex/),
   which keeps citation keys stable between exports.
2. **Save sources while you read** with the connector button, into one
   thesis collection. Check each item; imported details are often incomplete.
3. **Export to `references.bib`.** Do these three things:
   1. Export the collection in **BibLaTeX** (or **Better BibLaTeX**) format
      to `references.bib` in your thesis folder, replacing the sample
      ([Zotero: exporting](https://www.zotero.org/support/kb/exporting)).
   2. Replace or remove the sample citations `lamport1994` in
      `chapters/01-introduction.tex` and `rpi-submission` in
      `appendices/additional-material.tex`, so every citation uses a key from
      your file.
   3. On Overleaf, upload the new file over the old one, and again whenever
      it changes. [Auto-export](#set-it-and-forget-it) keeps the file on your
      computer current; you still upload it to Overleaf.
4. **Cite with `\parencite{your-key}`** (or `\textcite`). The key is the word
   after `@article{` (or `@book{`, ...) in the exported entry; Better BibTeX
   also shows it in Zotero.

5. **Compile.** Only sources you cite appear in the reference list.

A key in **bold**? Compile again, then check its spelling
([bold keys](how-it-works.md#bold-citation-keys-and-question-marks)). The
style chosen inside Zotero does not affect your PDF.

### Where Zotero keeps your library

**Never put the Zotero data folder in OneDrive, Dropbox, iCloud, or Google
Drive**; it can corrupt the database ([Zotero: syncing](https://www.zotero.org/support/sync)).
Use Zotero sync plus your [computer backup](going-further.md#back-up-your-work).
`references.bib` is safe in a synced folder, but it is not a library backup.

<details id="set-it-and-forget-it"><summary>Optional: Zotero storage, sync, Overleaf, and auto-export</summary>

- **Storage:** data sync is free; PDF sync has limited free storage, and
  group files count against the group owner's
  ([Zotero: storage](https://www.zotero.org/support/storage_faq)). If it
  fills up, buy more, use WebDAV, or keep PDFs on your computer.
  <!-- Maintainer: checked 14 Oct 2026 against zotero.org/support/sync and storage_faq. Neither page says what happens at a full quota, so the guide does not describe it. -->
- **New computer:** use Zotero sync, or copy the data folder while Zotero is
  closed ([Zotero: moving your library](https://www.zotero.org/support/kb/transferring_a_library)).
- **Overleaf:** its built-in [Zotero integration](https://docs.overleaf.com/integrations-and-add-ons/reference-manager-integrations/zotero)
  needs some [Overleaf plans](https://docs.overleaf.com/getting-started/free-and-premium-plans).
  Free route: export `references.bib` to your computer and upload it to
  Overleaf again whenever it changes.
- **Auto-export:** with [Better BibTeX](https://retorque.re/zotero-better-bibtex/exporting/auto/),
  tick **Keep updated** when exporting into your thesis folder, and Zotero
  rewrites that file whenever your library changes. On Overleaf, upload the
  file again after changes (or use the Zotero integration above); linking a
  file on your computer by web address needs a public link, which exposes
  your whole bibliography, so this guide leaves it out.
- **Cautions:** export only a thesis collection and pin
  [citation keys](https://retorque.re/zotero-better-bibtex/citing/).
  **The exporter owns the file it writes to.** Every export or auto-export
  replaces it completely, so edits made inside it are lost. To keep
  hand-written entries too, export to `zotero.bib`, leave `references.bib`
  for your own entries, and add `\addbibresource{zotero.bib}` in
  `preamble.tex`. Keys must be unique across both files.

</details>

## If you can't use Zotero: paste an entry by hand

Paste a BibTeX entry from the publisher, a library database, or Google
Scholar. They are often slightly wrong, so check each one.

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

   This example is already in the starter; do not add it twice.

2. Paste your source's entry into `references.bib`. The word after `@book{`
   is the **key**, here `lamport1994`. Every key must be unique.
3. Cite it with `\parencite{key}`, using your entry's key, and compile.

Wrap capitals that must stay capitalized in braces, like `{RPI}`. Two more
things to get right in the `author` field:

- **Several people:** join the names with the word `and`, typed literally:
  `author = {Alice Smith and Bob Jones}`. Commas and semicolons do not
  separate authors.
- **An organization:** use double braces so it is not read as a person's
  name: `author = {{Example Research Institute}}`.

Only have a messy reference? An AI chat can turn it into a BibTeX entry.
Then compare every field with the source, and paste only published
references, never confidential material.

## Web sources need an access date

OGE requires an **access date for every reference with a URL**, even if your
style would normally leave it out. Add `urldate` with the date *you* read it
(year-month-day).

If the entry came from Zotero, fill in the item's **Accessed** field in
Zotero and export again; Zotero writes it as `urldate`. Do not type it into
an exported file, because the next export replaces it. Edit the entry
directly only in a file you maintain by hand, like this one:

```bibtex
@online{rpi-submission,
  author  = {{Rensselaer Polytechnic Institute}},
  title   = {Submit Your Thesis / Dissertation},
  url     = {https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation},
  urldate = {2026-10-14}
}
```

Check that the date **prints** in your PDF; some styles hide it.
[Check your references](check-references.md) lists any `url` without a
`urldate`, in your browser. DOIs need no access date.

## Change the citation style

Four parts work together: the **class** sets the page layout, **biblatex**
provides the citation commands, the **style** decides what they print, and
**Biber** (the bibliography step) processes `references.bib`. In `preamble.tex` (the file for the
citation style and extra packages), find this line:

```tex
\usepackage[backend=biber,style=numeric,sorting=none]{biblatex}
```

Replace `style=numeric,sorting=none` with a starting point from this table.
An extra package is an add-on; the ones listed are included in full TeX Live
and Overleaf. Do not also load `natbib`; it is a separate system.

| Style family | Replace with | Extra package |
| --- | --- | --- |
| Numbered in order of citation (sample) | `style=numeric,sorting=none` | built in |
| Generic author–year | `style=authoryear` | built in |
| IEEE | `style=ieee` | [biblatex-ieee](https://ctan.org/pkg/biblatex-ieee) |
| ACS (chemistry) | `style=chem-acs` | [biblatex-chem](https://ctan.org/pkg/biblatex-chem) |
| APA | `style=apa` | [biblatex-apa](https://ctan.org/pkg/biblatex-apa) |
| MLA | `style=mla` | [biblatex-mla](https://ctan.org/pkg/biblatex-mla) |
| Chicago | not a one-word swap; replace the whole line ([tested setup](#print-a-full-reference-in-the-text)) | [biblatex-chicago](https://ctan.org/pkg/biblatex-chicago) |

Whatever the style, the class keeps the reference list single-spaced with one
blank line between entries, as OGE asks, and lets long web addresses wrap.
It replaces the style's own spacing, so leave `\bibitemsep` out of
`preamble.tex`; a setting there, below the biblatex line, would override the
class.

These are starting points, not validated department presets; see each
package's manual. After changing the style, check what the citation
commands print, and choose the command by what you want to read:

| You want | Type | Numeric sample | APA |
| --- | --- | --- | --- |
| A citation in brackets or parentheses | `\parencite{key}` | [1] | (Lamport, 1994) |
| The author as part of the sentence | `\textcite{key}` | Lamport [1] | Lamport (1994) |
| A page or section | `\parencite[23]{key}` | [1, p. 23] | (Lamport, 1994, p. 23) |
| Whatever the style calls a plain citation | `\cite{key}` | [1] | Lamport, 1994 (no parentheses) |
| The full reference in the text | `\fullcite{key}` | see below | see below |

`\parencite` and `\textcite` are the usual choices in biblatex styles. Look at
what your style prints before relying on them. A paper template that uses
classic BibTeX with `natbib` has the matching commands `\citep` (like
`\parencite`) and `\citet` (like `\textcite`); see
[turn a chapter into a paper](going-further.md#turn-a-chapter-into-a-paper).

### Print a full reference in the text

[Chapter attribution](writing.md#chapters-based-on-published-papers) and
[reproduced figure captions](writing.md#reproduced-figures-and-permissions)
need the whole reference where it is cited. `\fullcite{key}` does this in the
styles below. It was tested with compiled examples (pdfLaTeX and Biber) of a
journal article, books, and web pages, with personal and organization
authors, in a chapter attribution, a figure caption, the list of figures, and
after ordinary citations of the same source. Check your own entries.

| Style | `\fullcite{key}` |
| --- | --- |
| numeric, authoryear, IEEE, APA | Prints the full reference |
| Chicago author-date | **Needs the setup below.** Without it, a source cited earlier prints as "id." or a bare year |
| ACS (`chem-acs`) | Prints the reference in ACS form, with abbreviated first names; with many authors it shortens the list to the first author and "et al.", unlike the reference list, and it omits a DOI that the reference list may show. Check that this is enough |
| MLA (`mla`) | **Prints nothing, then needs the setup below** |

If your style or a source does not print right, type the full reference into
the caption or attribution by hand, copied from your reference list, in your
style's wording.

<details><summary>If you use Chicago author-date: the setup for <code>\fullcite</code></summary>

In `preamble.tex`, replace the `\usepackage[...]{biblatex}`
line with the first line below (the class and the other lines stay), and put
the rest under `\addbibresource{references.bib}`:

```tex
\usepackage[authordate,backend=biber]{biblatex-chicago}
\DeclareCiteCommand{\fullcite}{\usebibmacro{prenote}}
  {\usedriver{\DeclareNameAlias{sortname}{default}}{\thefield{entrytype}}}
  {\multicitedelim}{\usebibmacro{postnote}}
```

Tested: after the setup, every full reference printed in full (author, year,
and title) in the text, captions, the list of figures, and a chapter
attribution, including a source already cited with `\parencite`. Not tested:
Chicago notes-bibliography, thesis, report, and archival entries.
`style=chicago-authordate` alone is not the tested route.

</details>

<details><summary>If you use MLA: the setup for <code>\fullcite</code></summary>

Put this under `\addbibresource{references.bib}` in `preamble.tex`.
It makes `\fullcite` print the full reference, with the author's name every
time. The two `\csgundef` lines stop MLA from replacing a repeated author
with a long dash in a caption or attribution, and stop that dash from leaking
into the first entry of the reference list:

```tex
\DeclareCiteCommand{\fullcite}{\usebibmacro{prenote}}
  {\csgundef{bbx@lasthash}%
   \usedriver{\DeclareNameAlias{sortname}{default}}{\thefield{entrytype}}%
   \csgundef{bbx@lasthash}}
  {\multicitedelim}{\usebibmacro{postnote}}
```

Tested with `style=mla`: articles, books, and web pages, by one person, two
people, and an organization, cited back to back and from the same author
repeatedly. Captions, the list of figures, and attributions kept the name,
and the reference list kept MLA's own dash for a repeated author. Not tested:
`mla-strict`, `mla7`, other entry types.
<!-- TODO(verify): Chicago and MLA overrides were checked on a small fixture with pdfLaTeX and Biber only; entry types beyond article, book, and online, and other biblatex-mla variants, were not tested. -->

</details>

## Check the output yourself

Citation managers handle journal articles well but are far less reliable for
**websites, reports, theses, datasets, software, standards, and archival
sources**. Compare every reference in the PDF with your style guide.

Optional: [check your references](check-references.md) in your browser before
compiling. It looks for common key, field, name, and date problems; nothing
is uploaded.

### Numbered styles: check delayed figures and tables

In a style numbered in order of first citation (such as IEEE, or the
sample), OGE's formatting checklist expects reference 1 to be the first
citation in Chapter 1, and a caption's citation to be numbered where its
figure or table appears in the body. The abstract has no citations (OGE
manual §1.8).

LaTeX numbers citations in the order they appear in your `.tex` files, not
where they land in the PDF. A figure that floats to a later page can show
[2] after text that already shows [3]. Check each figure and table that
moved away from its first mention. To fix one:

- move its whole `figure` or `table` block (`\begin` to `\end`) to directly
  after the paragraph that first mentions it, then compile; or
- cite the same source in that paragraph, before the figure.

Never renumber by hand.

Not every style numbers in order. SIAM, for example, numbers from an
alphabetical reference list (OGE manual §3.3), and author–year styles have no
numbers. Use the style you agreed with your advisor
([step 1](#step-1-agree-on-a-style-with-your-advisor)).

## If co-authors use Word

A Zotero group library lets Word users (with the
[Word plugin](https://www.zotero.org/support/word_processor_integration)) cite
the same sources, but citations do not convert between Word and LaTeX. Agree
on one main copy ([co-authors](going-further.md#co-authors-and-lab-mates)).
