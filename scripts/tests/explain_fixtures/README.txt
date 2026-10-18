Real LaTeX logs for scripts/tests/test_explain.py ("Explain my error",
site/explain/). Made with TeX Live 2026 on a copy of the starter or a few-line
test file; no real thesis or research is in them.

starter-failed.log   latexmk -pdf -file-line-error on the starter with a
                     \textbff typo (chapter 2), an underscore outside math
                     (chapter 3), \parencite{smith2099} and \ref{fig:nothere},
                     a too-wide \mbox and a \linebreak (chapter 1). First
                     LaTeX run only, so Biber has not run yet.
starter-built.log    the same with the typo fixed, after latexmk finished:
                     only warnings are left.
pdflatex-unicode.log           pdflatex, a long arrow character in the text.
lualatex-missing-character.log lualatex with fontspec, a Georgian letter and a CJK
                               character the default font does not have.
xelatex-font-missing.log       xelatex -file-line-error, \setmainfont with a
                               font name that is not installed.
