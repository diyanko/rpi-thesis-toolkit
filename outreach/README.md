# Outreach print material

Printable pages that point people to the RPI Thesis Toolkit website. They are
maintainer material: not shipped in the starter ZIP and not part of the
website. They say the toolkit is unofficial, community-made, and free, and
ask readers to check the current requirements of RPI's Office of Graduate
Education (OGE).

## What is here

| File | What it is |
| --- | --- |
| `handout.html` | Two-sided half-letter pamphlet (5.5 x 8.5 in). Front: "From any draft to a tidy thesis.", a drawing of drafts, plots, and references pouring through the starter into one thesis, and a QR code to the website. Back: the RPI parts the starter sets up, the three steps a student takes, two short notes (change one piece, use the tools when stuck), a QR code to the feedback form, and the short disclaimer. |
| `poster.html` | US letter poster (8.5 x 11 in, single-sided) for noticeboards: the same headline and funnel drawing, one line on what it does, QR codes to the website and to the feedback form, and the short disclaimer. |
| `outreach.css` | Shared styles: the website's fonts (from `site/fonts/`) and light color tokens (from `site/site.css`), the doodle drawing style, and the handout, two-up, and poster layouts. |
| `icons.svg` | The doodle icons, copied from `site/index.html` (the poster uses the feedback icon). |
| `qr-site.svg`, `qr-feedback.svg` | QR codes for the website and the feedback form, with error correction level H, so a small disc can sit in the middle (the brace mark for the website, a speech bubble for the form; about 26% of the code's width, on a white ring). |

`scripts/outreach.py` also builds a two-up version of every top-level
`handout*.html` (for example **`handout-2up.pdf`** from `handout.html`): each
side twice on US letter landscape, for printing two pamphlets per sheet. It is
made on the fly, so the handout's words live only in its own file.

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
  in the middle, at the faint ticks on the top and bottom edges. Each sheet
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

- **The steps on the back of the handout** and the names of the browser
  tools they mention (Convert to LaTeX, Explain my error, Check your
  references, Check your PDF).
- **What the starter sets up**, as listed on the back of the handout.
- **The website address** (`site/site.json`) and the QR code `qr-site.svg`.
- **The feedback form address**, which also lives in the "Ask for help"
  section of `docs/troubleshooting.md`, and the QR code `qr-feedback.svg`.
