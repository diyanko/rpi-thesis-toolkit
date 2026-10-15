# Put your figures here

Use short file names without spaces, such as `interview-themes.png`. PNG, JPEG,
and PDF work with the default compiler. The example in
`chapters/02-research.tex` shows exactly where to put your image command:

```tex
\includegraphics[width=\linewidth]{figures/interview-themes}
```

The file extension (`.png`, `.jpg`, `.pdf`) is optional. Replace the sample
`example-image` line with this command. Keep the caption and label. Describe
the figure in its caption and in the nearby text; do not rely on color alone
to communicate its meaning. Check legibility in the PDF.

The repository ignores generated PDFs. If a PDF is your source figure, track
that specific file with `git add -f figures/your-figure.pdf` when using Git.
Do not upload research data or figures you are not allowed to share publicly.
