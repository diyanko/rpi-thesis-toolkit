# Workshop exercises: your thesis in LaTeX

Pick one or more, in any order, once the sample thesis compiles on Overleaf
(or on your computer). Recompile after each change. Stuck? Raise a hand, or
paste the first error into Explain my error. Everything here is in the guide:
**diyanko.github.io/rpi-thesis-toolkit**.

## A. Put your name on the title page

1. Open the **Settings builder** (diyanko.github.io/rpi-thesis-toolkit/guide/settings-builder.html)
   and fill in the form. Check `degree`: `masters` for a master's thesis.
   Mark one committee member as Chair.
2. Click **Copy settings**.
3. In `metadata.tex`, replace the `\thesissetup{...}` block and all
   `\committeemember` lines with the copied block.
4. Click **Recompile**.

**You should see:** your title in capitals, your name, your degree's
wording, your committee under "Approved by", and your graduation month and
year in brackets. The seal box stays until you add the seal from RPI ITS's
Thesis Preparation page as `assets/rpi-seal.jpg`.

## B. Add a figure and a table

In `chapters/01-introduction.tex`, paste this after a paragraph. Upload a
picture into `figures/` as `my-plot.png`, or write `example-image` in place
of `figures/my-plot` if you have none.

```tex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{figures/my-plot}
  \caption{Your full caption, ending with a period.}
  \label{fig:my-plot}
\end{figure}

As Figure~\ref{fig:my-plot} shows, ...
```

Then paste this table below it:

```tex
\begin{table}[htbp]
  \centering
  \caption{Your full caption, ending with a period.}
  \label{tab:my-table}
  \begin{tabular}{lr}
    \toprule
    Group & Value \\
    \midrule
    A & 12 \\
    B & 18 \\
    \bottomrule
  \end{tabular}
\end{table}
```

**You should see:** Figure 1.1 with its caption **below** the picture,
Table 1.1 with its caption **above** the table, "As Figure 1.1 shows" in
your text, and new lines in the List of Figures and List of Tables. Either
may move to the next page; that is normal.

## C. Cite a source

1. In `chapters/01-introduction.tex`, add this as a new paragraph and
   recompile. Leave `references.bib` alone: the book is already in it.

   ```tex
   This example cites the sample book~\parencite{lamport1994}.
   ```

2. **You should see** another [1] pointing to Lamport's book, already listed
   under REFERENCES.
3. Optional: copy the BibTeX entry of a source you use (from Google Scholar,
   a library database, or the publisher), paste it into `references.bib`,
   and cite it with `\parencite{key}`, where the key is the word after
   `@article{` or `@book{`. Recompile: a new number and a new entry under
   REFERENCES. With Zotero, export your collection as **BibLaTeX** to
   `references.bib` instead.

## D. Bring one section of your draft

1. Open **Convert to LaTeX** (diyanko.github.io/rpi-thesis-toolkit/guide/convert-to-latex.html).
   Keep your original file untouched.
2. Paste one short section from Word, Google Docs, or Markdown. Choose
   **Part of a chapter**, then click **Copy**.
3. Paste it into a chapter file, below the `\chapter{...}` and `\label{...}`
   lines, and recompile.

**You should see:** your text with numbered headings, bold, italics, and
lists. Under the result, the page lists what it left for you, such as
pictures, footnotes, and citations. Compare every heading and number with
your original.

---

The RPI Thesis Toolkit is unofficial and community-made: not affiliated with
or endorsed by RPI or its Office of Graduate Education (OGE). OGE's current
requirements always come first. Tell the facilitator, or the help and
feedback form (forms.gle/fjfiLfkmVhkcyRNCA), where you got stuck.
