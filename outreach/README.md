# Outreach print material

Printable pages that point people to the RPI Thesis Toolkit website. They are
maintainer material: not shipped in the starter ZIP and not part of the
website. Like the rest of the project, they say the toolkit is unofficial and
community-made, and not affiliated with or endorsed by RPI or its Office of
Graduate Education (OGE).

## What is here

| File | What it is |
| --- | --- |
| `handout.html` | Two-sided half-letter pamphlet (5.5 x 8.5 in). Page 1, the front: the hook, the three ways in, the browser tools, and a QR code to the website. Page 2, the back: a first-person note from the maintainer asking for feedback, a QR code to the feedback form, and the disclaimer. |
| `poster.html` | US letter poster (8.5 x 11 in, single-sided) for noticeboards: headline, the home page drawing, the three ways in, the tools, a QR code to the website, a smaller one to the feedback form, and the disclaimer. |
| `outreach.css` | Shared styles: the website's fonts (from `site/fonts/`) and light color tokens (from `site/site.css`), plus the handout, two-up, and poster layouts. |
| `icons.svg` | The doodle icons, copied from `site/index.html`. |
| `qr-site.svg`, `qr-feedback.svg` | QR codes for the website and the feedback form. |

`scripts/outreach.py` also builds **`handout-2up.pdf`** from `handout.html`:
each side twice on US letter landscape, for printing two pamphlets per sheet.
It is made on the fly, so the handout's words live only in `handout.html`.

Any other `outreach/**/*.html` page is printed too, at the size its own CSS
`@page` rule sets (for example a slide deck at `outreach/workshop/slides.html`).
Files or folders whose name starts with an underscore are skipped.

## Build the PDFs

Optional, needs Chrome or Chromium (set `CHROME` to its path if it is not
found). From the repository root:

```sh
python3 scripts/outreach.py
```

The PDFs land in `build/outreach/` (never tracked). The script prints each
PDF's page count and size (checked with pypdf when it is installed), and warns
when text runs into a page's print-safe margin. Add words to print only some
pages, for example `python3 scripts/outreach.py poster`.

## Print

- **Handout, two per sheet** (`handout-2up.pdf`): US letter, double-sided,
  **flip on short edge**, actual size (100%, not "fit to page"). Cut the stack
  in the middle, at the faint marks on the top and bottom edges. Each sheet
  gives two identical pamphlets. Print one test sheet first and hold it to the
  light: the two sides should line up.
- **Handout, one per sheet** (`handout.pdf`): for a printer that takes
  half-letter paper; double-sided, flip on long edge.
- **Poster** (`poster.pdf`): US letter, single-sided, actual size.

Everything is readable in black and white. Every page keeps at least 0.3 in
between the text and the trim, and the website QR code is printed at least
1 in wide with a quiet zone of four modules.

## Keep it from going stale

The pages name no versions, dates, deadlines, or staff, and send readers to
the website for everything else. Recheck them when any of these change:

- **The three ways in:** Open in Overleaf, Download the starter, and "already
  have a LaTeX thesis: add only the class file".
- **The browser tools' names:** Settings builder, Convert to LaTeX, Check your
  references, Explain my error, Check your PDF.
- **The website address** (`site/site.json`) and the QR code `qr-site.svg`.
- **The feedback form address**, which also lives in the "Ask for help"
  section of `docs/troubleshooting.md`, and the QR code `qr-feedback.svg`.
- **The repository address** on the back of the handout.
- **The drawing** `site/art/home-equation.svg` (the poster uses it as is) and
  the icons copied from `site/index.html` into `icons.svg`.

The feedback note is in the first person on purpose: it is a personal request
from the maintainer, unlike the guide's neutral voice. It is signed once, in
the sign-off near the end of the back page in `handout.html`.
