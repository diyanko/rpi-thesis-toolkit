# Field guide cheat sheet

`cheatsheet.tex` is a one-page, printable reference for the thesis starter:
which file does what, and short copyable snippets for writing, citing,
cross-references, figures, tables, equations, published chapters, and
compiling. It is landscape US letter, and it stays readable when printed in
black and white.

It is a stand-alone document, not part of your thesis or dissertation, and
you never need to compile it. The starter ZIP includes a compiled copy,
`rpi-thesis-cheatsheet.pdf`.

## Rebuild it

**Overleaf or any editor:** open `cheatsheet.tex` on its own and compile with
pdfLaTeX. It needs no other files.

**Command line (optional):** from the repository root, run

```sh
latexmk -norc -pdf -outdir=build/cheatsheet cheatsheet/cheatsheet.tex
```

The PDF appears at `build/cheatsheet/cheatsheet.pdf`. The `build/` folder is
ignored by Git.

It uses only packages included in TeX Live and Overleaf: `geometry`, `fix-cm`,
`libertinus`, `zi4` (Inconsolata), `xcolor`, `tcolorbox` (with TikZ and
`listings`), `array`, and `hyperref` (live links in the PDF). It does not
need shell escape. The version in its footer is set by `scripts/bump.py`.

## Keep it accurate

Every snippet copies the starter's own conventions (`metadata.tex`,
`preamble.tex`, `chapters/02-research.tex`, `references.bib`). When those
files, `docs/writing.md`, `docs/citations.md`, or
`docs/project/requirements.md` change, update the matching box here, then
rebuild and check that the sheet is still one page.
