# Attribution, provenance, and licensing

The RPI Thesis Toolkit is an unofficial, community-made project. It is not
affiliated with or endorsed by Rensselaer Polytechnic Institute (RPI) or its
Office of Graduate Education (OGE), and OGE has not reviewed or approved the
class. It works with RPI's requirements and links to RPI's own resources.

## What's ours and what isn't

| Whose | What | How this project treats it |
| --- | --- | --- |
| **Ours** (the maintainer and [contributors](../../CREDITS.md#people)) | The class implementation (`rpi-thesis.cls`), starter examples, scripts, guides, diagrams, cheat sheet, and website | Written for this project; offered under [our license](../../LICENSE.md) |
| **RPI's** | The formatting requirements and the OGE *Dissertation and Thesis Manual* and checklists; the original LaTeX template; the seal; the institution's name | We follow and link to them. We do not include, copy, or claim them, and our license does not cover them |
| **The open-source ecosystem's** | LaTeX and its packages (including BibLaTeX), Biber, latexmk, Pandoc, Zotero and Better BibTeX, and the website fonts (SIL Open Font License) | Used as tools or loaded by their public interfaces, under their own licenses, with credit below |

## RPI's materials

The class is an independent implementation. It was informed by RPI's
publicly available LaTeX template and by the OGE manual, but it contains no
RPI files, and none are redistributed: not in the repository, the starter
ZIP, or the website.

| Material | Credit and source | Treatment |
| --- | --- | --- |
| OGE *Dissertation and Thesis Manual* (2026) | RPI Office of Graduate Education; [submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation) | Read as the formatting authority; requirements explained in our own words in the [requirements map](requirements.md); not bundled |
| Formatting and degree checklists (September 2025) | RPI Office of Graduate Education; same submission page | Used for cross-checking; not bundled |
| RPI's official LaTeX template | `thesis.cls` names Harriet Borton (ITS, 1996) and Michael Sofka (2018 changes); `rpithesis-doc.tex` names Client Information Services; available from RPI ITS's [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation) | Compared, not copied; differences recorded in the [requirements map](requirements.md#differences-from-rpis-official-latex-template). Maintainers keep a reference copy in `_local/legacy/` (ignored by Git) |
| RPI seal | Rensselaer Polytechnic Institute; RPI ITS's Thesis Preparation page | Not distributed. Each student downloads it and saves it as `assets/rpi-seal.jpg` ([assets/README.md](../../assets/README.md)); without it, the title page shows a placeholder |

`docs/project/upstream-files.json` is our own record of the original template
files (names and SHA-256 hashes), so a maintainer can tell whether a local
reference copy has changed. A hash is not a license and does not prove that a
copy is the latest download.

Maintainer decision (14 Oct 2026): do not redistribute RPI materials, and
point students to the current seal on RPI ITS's Thesis Preparation page to
download themselves. Because nothing RPI-owned is redistributed, the project
does not need redistribution permission. This is a project decision, not OGE
approval or endorsement.

## Open-source tools and fonts

| Material | Credit / source | Treatment in this project |
| --- | --- | --- |
| LaTeX and installed packages | The LaTeX Project and the respective package authors; [CTAN](https://ctan.org/) | Loaded by their public interfaces; no package source bundled or relicensed |
| Biber and latexmk | Their authors, distributed with TeX Live and MiKTeX | Run by the build helper; not bundled |
| Pandoc | John MacFarlane and contributors; [pandoc.org](https://pandoc.org/) | Builds the website and offline guide; not bundled |
| pdf.js | Mozilla and contributors; [project page](https://github.com/mozilla/pdf.js) (Apache License 2.0) | Bundled, unchanged, for the optional "Check your PDF" page: the legacy build of the `pdfjs-dist` npm package at the version pinned in `site/pdf-check/core.js`, in `site/pdf-check/pdfjs/` with its license text (`LICENSE`); shipped with the website only (the offline guide leaves the checker out); not covered by our license |
| Zotero and Better BibTeX | The Zotero project and the Better BibTeX authors | Recommended in the guide; not bundled |
| Fraunces typeface (website headings) | Phaedra Charles and Flavia Zimbardi (Undercase Type); [github.com/undercasetype/Fraunces](https://github.com/undercasetype/Fraunces) | Latin-subset WOFF2 files from Google Fonts in `site/fonts/`; SIL Open Font License 1.1, text in `site/fonts/OFL-Fraunces.txt`; not covered by our license |
| Atkinson Hyperlegible Next typeface (website body text) | Braille Institute of America, designed with Applied Design Works; [github.com/googlefonts/atkinson-hyperlegible-next](https://github.com/googlefonts/atkinson-hyperlegible-next) | Latin-subset WOFF2 files from Google Fonts in `site/fonts/`; SIL Open Font License 1.1, text in `site/fonts/OFL-Atkinson-Hyperlegible-Next.txt`; not covered by our license |
| Sample bibliography item | Leslie Lamport, *LaTeX: A Document Preparation System*, second edition, 1994 | Bibliographic record shows a real citation; no book content reproduced |

## License boundaries

[LICENSE.md](../../LICENSE.md) applies only to our original work listed
above. It grants no rights to RPI's name, seal, manuals, checklists, or
original template, or to anyone's thesis text, figures, data, publications,
or permission documents.

Do not copy student research examples from the manual into new samples. The
examples here are newly written teaching text and invented table values.
Contributions containing material from others need their own source and
permission record.

## Before publication

1. Confirm that no RPI-owned file is tracked or in Git history, and that the
   starter ZIP and website contain none (see the
   [public-release checklist](maintenance.md#public-release-readiness)).
2. Confirm that every public page presents the project as unofficial
   ([style guide](style-guide.md#talking-about-rpi)).
3. Obtain maintainer authorization before publication or any communication
   on the project's behalf.

Credit for the original template's authors does not imply that they, RPI, or
OGE contributed to, support, or endorse this project.
