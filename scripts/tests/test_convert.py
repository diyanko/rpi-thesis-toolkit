#!/usr/bin/env python3
"""Tests for "Bring your work in" (site/convert/core.js and ui.js).

    python3 scripts/tests/test_convert.py

Runs the converter in headless Chrome, as the page does, on the synthetic
pasted text in scripts/tests/convert_fixtures/: escaping, a Word-like and a
Google-Docs-like paste, spreadsheet cells (HTML and tab-separated, with
quoted tabs), and Markdown. Each case checks that the words arrive and the
markup is right, not only that it compiles. The page part is tested with a
real paste event, including one full of things that would load or run:
nothing may reach the server and nothing may run. Finally the converted
fixtures go into one chapter of a temporary copy of the starter, which must
compile with latexmk. Skipped without Chrome; the compile is skipped without
TeX Live. Standard library only.
"""
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
from chrome import Chrome, LocalServer  # noqa: E402
from common import ROOT, find_chrome  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "convert_fixtures"
HARNESS = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>convert</title>
<script src="/convert/core.js"></script><script src="/tools-highlight.js"></script></head><body></body></html>"""
# The page part with the guide page's own markup and the links it reads.
UI_HARNESS = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>convert ui</title></head>
<body><main class="guide-content"><a href="writing.html">w</a> <a href="bring-your-draft.html">b</a>
%s</main><script src="/tools-highlight.js"></script><script src="/convert/ui.js"></script></body></html>"""
STARTER = ["main.tex", "metadata.tex", "preamble.tex", "rpi-thesis.cls", "references.bib", "latexmkrc"]
STARTER_FOLDERS = ["chapters", "frontmatter", "appendices", "assets", "figures"]


def fixture(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


def widget_markup():
    found = re.search(r'(?m)^<div class="[^"]*\bconvert\b[^"]*" .*$', (ROOT / "docs/bring-your-work-in.md").read_text(encoding="utf-8"))
    if not found:
        raise RuntimeError('docs/bring-your-work-in.md has no <div class="convert" ...> line')
    return found[0]


REQUESTS = []


def dynamic(path, query):
    REQUESTS.append(path)
    if path == "/__convert__.html":
        return HARNESS.encode(), "text/html; charset=utf-8"
    if path == "/__convert_ui__.html":
        return (UI_HARNESS % widget_markup()).encode(), "text/html; charset=utf-8"
    if path.startswith("/__probe__/"):
        return b"", "text/plain"
    return None


@unittest.skipUnless(find_chrome(), "no Chrome or Chromium found")
class Convert(unittest.TestCase):
    outputs = {}

    @classmethod
    def setUpClass(cls):
        cls.server = LocalServer(ROOT / "site", dynamic)
        cls.browser = Chrome(find_chrome())
        cls.browser.open(cls.server.url + "/__convert__.html")

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.close()

    def convert(self, html="", text="", chapter=False, key=None):
        result = self.browser.evaluate("ConvertCore.convert(%s, %s)" % (
            json.dumps({"html": html, "text": text}), json.dumps({"chapter": chapter})))
        if key:
            Convert.outputs[key] = result["latex"]
        return result

    def call(self, name, *args):
        return self.browser.evaluate("ConvertCore.%s(%s)" % (name, ", ".join(json.dumps(a) for a in args)))

    def notes(self, result):
        return {note["id"]: note["text"] for note in result["notes"]}

    def test_highlighter_matches_build(self):
        # Tool output (site/tools-highlight.js) and guide code blocks (build_site.py)
        # must color LaTeX the same way.
        import build_site
        samples = [block for path in sorted((ROOT / "docs").glob("*.md"))
                   for block in re.findall(r"```(?:tex|latex)\n(.*?)```", path.read_text(encoding="utf-8"), flags=re.S)]
        samples += [r"\section{A} 100\% $x$ \(y\) [opt \cmd]{b} % c", "\\begin{a}[x\ny] \\\\[1em] $$a$$ \\[b\\]"]
        painted = self.browser.evaluate("""%s.map(text => ToolsHighlight.tokens(text).map(t => {
          const plain = t.text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
          return t.type ? '<span class="tok-' + t.type + '">' + plain + '</span>' : plain;
        }).join(''))""" % json.dumps(samples))
        for text, html in zip(samples, painted):
            with self.subTest(text=text[:40]):
                self.assertEqual(html, build_site.highlight_latex(text))

    def test_escaping(self):
        cases = {
            "50% & R&D_x #1 $5": r"50\% \& R\&D\_x \#1 \$5",
            "{a} ~ ^ \\": r"\{a\} \textasciitilde{} \textasciicircum{} \textbackslash{}",
            "α ± ≤ Ω": r"\ensuremath{\alpha} \ensuremath{\pm} \ensuremath{\leq} \ensuremath{\Omega}",
            "a\u2013b \u2014 c\u2026": r"a--b --- c\dots{}",
            "20\u00a0°C café “quoted”": "20~°C café “quoted”",
            "soft\u00adhyphen\u200b": "softhyphen",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(self.call("escapeText", source, {"escaped": 0, "odd": []}), expected)
        self.assertEqual(self.call("escapeUrl", "https://a.org/x_y?q=1&r=%20#top"), r"https://a.org/x_y?q=1&r=\%20\#top")
        self.assertEqual(self.call("escapeUrl", "https://a.org/a b{c}"), r"https://a.org/a\%20b\%7Bc\%7D")
        self.assertEqual(self.call("slug", "Résultats: Field & Lab!", "x"), "resultats-field-lab")
        self.assertEqual(self.call("safeLink", "javascript:alert(1)"), "")
        self.assertEqual(self.call("safeLink", "https://www.google.com/url?q=https://example.org/a%3Fb%3D1&sa=D"),
                         "https://example.org/a?b=1")
        # Characters the fonts may not have are kept and listed.
        result = self.convert(text="Plain words and 中文.")
        self.assertIn("中文", result["latex"])
        self.assertIn("中 文", self.notes(result)["odd"])
        # Math kept only in Markdown; elsewhere $ is a dollar sign.
        self.assertIn("$x^2$", self.convert(text="# T\n\nSee $x^2$ here.")["latex"])
        self.assertIn(r"\$x\textasciicircum{}2\$", self.convert(text="See $x^2$ here.")["latex"])

    def test_word_paste(self):
        result = self.convert(html=fixture("word-paste.html"), text="ignored", key="word")
        latex = result["latex"]
        self.assertEqual(result["source"], "word")
        for piece in [r"\section{Field Methods}", r"\subsection{Sites and Steps}",
                      r"We visited \textbf{three sites} over \emph{two seasons}, spending 40\% of the R\&D budget on site \#2 at \$12 each.[1]",
                      r"20~°C, with \ensuremath{\alpha}~=~0.05.",
                      "\\begin{itemize}\n  \\item Site A, on the river\n  \\begin{itemize}\n    \\item North bank\n  \\end{itemize}\n  \\item Site B, in the hills\n\\end{itemize}",
                      "\\begin{enumerate}\n  \\item Collect the samples\n  \\item Label each one\n\\end{enumerate}",
                      r"\caption{Visits by site}", r"\label{tab:visits-by-site}", r"\begin{tabular}{lrl}",
                      r"\textbf{Site} & \textbf{Visits} & \textbf{Notes} \\", r"{[}B] & 18 & 50\% wet\_ground \\",
                      '% A picture was here ("Map of the three sites")',
                      r"The rate was [equation] per day, as in the \href{https://example.org/field_guide?ed=2&ch=3\#tables}{field guide}.",
                      "[1] Measured at noon."]:
            self.assertIn(piece, latex)
        for absent in ["Check this number", "AB1", "Calibri", "mso-", "·", "clip_image", "Table 1"]:
            self.assertNotIn(absent, latex)
        notes = self.notes(result)
        self.assertEqual(sorted(notes), ["comment", "equation", "footnote", "picture"])
        self.assertTrue(notes["footnote"].startswith("1 footnote"))
        chapter = self.convert(html=fixture("word-paste.html"), chapter=True, key="word-chapter")["latex"]
        self.assertTrue(chapter.startswith("% !TEX root = ../main.tex\n\\chapter{FIELD METHODS}\n\\label{chap:field-methods}\n"))
        self.assertIn(r"\section{Sites and Steps}", chapter)

    def test_google_docs_paste(self):
        result = self.convert(html=fixture("gdocs-paste.html"), key="gdocs")
        latex = result["latex"]
        self.assertEqual(result["source"], "gdocs")
        for piece in [r"\section{Interview Themes}", r"\subsection{Themes}",
                      r"Participants described \textbf{cost} and \emph{access} as the main themes (\$30 per trip, 25\% of income); see the \href{https://example.org/report_2024?page=2}{full report}.[1]Comment here",
                      "\\begin{itemize}\n  \\item Cost of travel\n  \\begin{itemize}\n    \\item Fuel and tolls\n  \\end{itemize}\n  \\item Access to sites\n\\end{itemize}",
                      "\\begin{enumerate}\n  \\item Code the transcripts\n  \\item Compare the codes\n\\end{enumerate}",
                      "A risky link and a photo:", "[1] Interviews ran in 2024."]:
            self.assertIn(piece, latex)
        # The wrapper <b style="font-weight:normal"> is not bold.
        self.assertEqual(latex.count(r"\textbf"), 1)
        for absent in ["javascript", "googleusercontent", "google.com/url", "[a]", "Should this say travel"]:
            self.assertNotIn(absent, latex)
        self.assertEqual(sorted(self.notes(result)), ["comment", "footnote", "link", "picture"])

    def test_equation_only_paragraph(self):
        for equation in ['<span style="font-family:Cambria Math">x = y</span>',
                         '<math><mi>x</mi></math>']:
            with self.subTest(equation=equation):
                result = self.convert(html="<p>" + equation + "</p>")
                self.assertEqual(result["latex"], "[equation]\n")
                self.assertEqual(sorted(self.notes(result)), ["equation"])
                self.assertTrue(self.notes(result)["equation"].startswith("1 equation"))

    def test_html_lists_inside_quotes(self):
        for items, env in [('<ul><li>Site A<ul><li>North bank</li></ul></li><li>Site B</li></ul>', "itemize"),
                           ('<ol><li>Site A</li><li>Site B</li></ol>', "enumerate"),
                           ('<p style="mso-list:l0 level1 lfo1">Site A</p>'
                            '<p style="mso-list:l0 level1 lfo1">Site B</p>', "itemize")]:
            for depth in (1, 2):
                with self.subTest(items=items, depth=depth):
                    latex = self.convert(html="<blockquote>" * depth + items + "</blockquote>" * depth)["latex"]
                    self.assertEqual(latex.count(r"\begin{quote}"), depth)
                    self.assertIn(r"\begin{" + env + "}", latex)
                    self.assertIn(r"\end{" + env + "}", latex)
                    start = latex.index(r"\begin{" + env + "}")
                    end = latex.rindex(r"\end{" + env + "}")
                    self.assertLess(latex.index(r"\begin{quote}"), start)
                    self.assertLess(end, latex.rindex(r"\end{quote}"))
                    self.assertIn(r"\item Site A", latex[start:end])
                    self.assertIn(r"\item Site B", latex[start:end])
                    if "North bank" in items:
                        self.assertIn(r"\item North bank", latex[start:end])

    def test_spreadsheet_cells(self):
        result = self.convert(html=fixture("sheets-cells.html"), key="sheets")
        latex = result["latex"]
        self.assertEqual((result["source"], result["kind"]), ("sheets", "table"))
        self.assertIn(r"\textbf{Theme} & \textbf{People} & \textbf{Share} \\", latex)
        self.assertIn(r"Cost\_of\_travel & 12 & 40\% \\", latex)
        self.assertIn(r"Access \& time \{see notes\} &  & 60\% \\", latex)
        self.assertIn(r"\begin{tabular}{lrr}", latex)
        self.assertEqual(sorted(self.notes(result)), ["caption", "merged"])

    def test_tab_separated_cells_with_quotes(self):
        result = self.convert(text=fixture("excel-cells.tsv"), key="tsv")
        latex = result["latex"]
        self.assertEqual(result["source"], "tsv")
        self.assertIn(r"Sample & Mass (g) & Note \\", latex)
        self.assertIn(r'Soil, "dry" & 12.5 & two parts \\', latex)
        self.assertIn(r"Water \#2 & 3,400 & first line second line \\", latex)
        self.assertIn(r"Rock\_C & -7 & \textasciitilde{} 50\% \\", latex)
        self.assertIn(r"\begin{tabular}{lrl}", latex)
        self.assertEqual(latex.count(r"\midrule"), 1)
        # Uneven rows are not a grid: read as text instead.
        self.assertEqual(self.convert(text="a\tb\nc\n")["source"], "text")

    def test_markdown(self):
        result = self.convert(text=fixture("sample.md"), key="markdown")
        latex = result["latex"]
        self.assertEqual(result["source"], "markdown")
        for piece in [r"\section{Results}", r"\subsection{Yield by site}",
                      r"Across \textbf{three sites} and \emph{two seasons}, yield rose by 12\% (see [@lamport1994]).",
                      r"The model is $y = mx + b$, fitted with \texttt{lm\_fit()} and costs of \$5 each.",
                      r"\item Site A: higher in the \emph{second} season",
                      "\\item Site B\n  \\begin{itemize}\n    \\item north plot",
                      "\\begin{enumerate}\n  \\item Sort the samples",
                      r"\begin{tabular}{lrl}", r"A & 4.2 & R\&D plot \\", r"B & 3.9 & under\_review \\",
                      "\\begin{equation}\n  y = mx + b\n  \\label{eq:results-1}\n\\end{equation}",
                      "\\begin{quote}\n  Field notes are the record of what happened.\n\\end{quote}",
                      "\\begin{verbatim}\nx_1 = {a} % raw\n\\end{verbatim}",
                      '% A picture was here ("Yield map")',
                      r"\url{https://example.org/results_2024}", r"\href{https://example.org/a?b=1&c=\%20}{the archive}"]:
            self.assertIn(piece, latex)
        self.assertEqual(sorted(self.notes(result)), ["caption", "citation", "code", "display-math", "picture"])
        # Plain text: one paragraph per line, every symbol escaped.
        plain = self.convert(text="Line one 100% * 2\nLine_two\n")
        self.assertEqual((plain["source"], plain["latex"]), ("text", "Line one 100\\% * 2\n\nLine\\_two\n"))

    def test_single_row_tab_separated_cells(self):
        for ending in ("", "\n", "\r\n"):
            with self.subTest(ending=ending):
                result = self.convert(text="Site\tVisits\tWeather" + ending)
                self.assertEqual((result["source"], result["kind"]), ("tsv", "table"))
                self.assertIn(r"\begin{tabular}{lll}", result["latex"])
                self.assertIn(r"Site & Visits & Weather \\", result["latex"])
                self.assertNotIn(r"\midrule", result["latex"])
                self.assertEqual(sorted(self.notes(result)), ["caption"])

    def test_markdown_block_starts_end_list_continuation(self):
        cases = [("## Results", r"\section{Results}"),
                 ("```\nx = 1\n```", r"\begin{verbatim}"),
                 ("~~~\nx = 1\n~~~", r"\begin{verbatim}"),
                 ("> Field notes", r"\begin{quote}"),
                 ("$$x = y$$", r"\begin{equation}"),
                 ("| Site | Visits |\n| -- | -- |\n| A | 2 |", r"\begin{table}"),
                 ("---\nResults", "Results"),
                 ("- - -\nResults", "Results")]
        for block, expected in cases:
            for indent in ("", "  "):
                with self.subTest(block=block, indent=indent):
                    latex = self.convert(text="- Item\n" + indent + block)["latex"]
                    self.assertIn("\\item Item\n\\end{itemize}", latex)
                    self.assertEqual(latex.count(r"\item"), 1)
                    self.assertIn(expected, latex.split(r"\end{itemize}", 1)[1])
        latex = self.convert(text="- Item\ncontinued\n  further details")["latex"]
        self.assertIn(r"\item Item continued further details", latex)

    def test_numbered_list_alone_is_a_list(self):
        latex = self.convert(text="1. Collect samples\n2. Compare results")["latex"]
        self.assertIn("\\begin{enumerate}", latex)
        self.assertEqual(latex.count("\\item"), 2)

    def test_list_type_change_starts_a_new_list(self):
        latex = self.convert(text="- Site A\n  1. first\n  2. second\n  - a bullet\n- Site B")["latex"]
        self.assertIn("\\begin{enumerate}", latex)
        self.assertEqual(latex.count("\\begin{itemize}"), 2)   # outer list and the bulleted sublist

    def test_malformed_input(self):
        for html in ["<p><b>unclosed <i>tags", "<table><tr><td>a<td>b<tr><td>c</table>", "<" * 50 + "p>x",
                     "<div>" * 3000 + "deep" + "</div>" * 3000]:
            with self.subTest(html=html[:30]):
                result = self.convert(html=html, text="fallback")
                self.assertIsInstance(result["latex"], str)
        self.assertIn("deep", self.convert(html="<div>" * 3000 + "deep" + "</div>" * 3000)["latex"])
        self.assertEqual(self.convert(text="   \n")["latex"], "")

    def test_ui_paste_loads_and_runs_nothing(self):
        page = self.server.url + "/__convert_ui__.html"
        self.browser.open(page)
        self.browser.evaluate("new Promise(r => { const t = setInterval(() => { if (window.ConvertCore) { clearInterval(t); r(true); } }, 20); })")
        evil = ('<link rel="stylesheet" href="/__probe__/style.css"><style>@import url(/__probe__/import.css);'
                'body { background: url(/__probe__/bg.png) }</style><p style="background:url(/__probe__/inline.png)">'
                'Hello <b>there</b> <a href="javascript:window.pwned=1">x</a><img src="/__probe__/img.png" '
                'onerror="window.pwned=1"><img src=x onerror="window.pwned=2"></p><iframe src="/__probe__/frame.html"></iframe>'
                '<script>window.pwned=3</script><svg onload="window.pwned=4"><image href="/__probe__/svg.png"/></svg>'
                '<video poster="/__probe__/poster.png"><source src="/__probe__/v.mp4"></video>'
                '<object data="/__probe__/obj"></object><table background="/__probe__/t.png"><tr><td>1</td><td>2</td></tr></table>')
        REQUESTS.clear()
        before = self.browser.evaluate("performance.getEntriesByType('resource').length")
        self.browser.evaluate("""(function (html) {
          const box = document.querySelector('.convert-input'), data = new DataTransfer();
          data.setData('text/html', html); data.setData('text/plain', 'Hello there x');
          box.focus();
          box.dispatchEvent(new ClipboardEvent('paste', { clipboardData: data, bubbles: true, cancelable: true }));
          return new Promise(r => setTimeout(() => r(true), 800));
        })(%s)""" % json.dumps(evil))
        self.assertEqual(REQUESTS, [], "the paste made the page ask the server for something")
        self.assertEqual(self.browser.evaluate("performance.getEntriesByType('resource').length"), before)
        self.assertIsNone(self.browser.evaluate("window.pwned === undefined ? null : window.pwned"))
        latex = self.browser.evaluate("document.querySelector('.convert-output').textContent")
        self.assertIn(r"Hello \textbf{there} x", latex)
        self.assertNotIn("javascript", latex)
        self.assertNotIn("probe", latex)
        # The only elements in the output are the highlighter's own text spans.
        self.assertTrue(self.browser.evaluate("[...document.querySelectorAll('.convert-output *')].every("
                                              "n => n.tagName === 'SPAN' && /^tok-[a-z]+$/.test(n.className) && !n.children.length)"))
        self.assertGreater(self.browser.evaluate("document.querySelectorAll('.convert-output .tok-cmd').length"), 0)
        self.assertEqual(self.browser.evaluate("document.querySelector('.convert-input').value"), "Hello there x")
        self.assertIn("Rich text", self.browser.evaluate("document.querySelector('.convert-status').textContent"))
        # The options re-run the conversion; editing the box reads it as typed.
        self.browser.evaluate("document.querySelector('input[value=chapter]').click(); true")
        self.assertIn(r"\chapter{TITLE}", self.browser.evaluate("document.querySelector('.convert-output').textContent"))
        self.browser.evaluate("""(function () { const box = document.querySelector('.convert-input');
          box.value = '## Methods\\n\\nNew **text**'; box.dispatchEvent(new Event('input', { bubbles: true }));
          return new Promise(r => setTimeout(() => r(true), 400)); })()""")
        latex = self.browser.evaluate("document.querySelector('.convert-output').textContent")
        self.assertIn("\\chapter{METHODS}\n\\label{chap:methods}", latex)
        self.assertIn(r"New \textbf{text}", latex)
        self.assertIn(r"\include{chapters/methods}", self.browser.evaluate("document.querySelector('.convert-results').textContent"))
        self.assertFalse(self.browser.evaluate("document.querySelector('.convert-download').disabled"))
        self.assertEqual(REQUESTS, [])


@unittest.skipUnless(find_chrome(), "no Chrome or Chromium found")
@unittest.skipUnless(all(shutil.which(tool) for tool in ("latexmk", "pdflatex", "biber")), "no TeX Live")
class Typeset(unittest.TestCase):  # named to run after Convert
    """The converted fixtures, together in one chapter, compile in the starter."""

    def test_combined_output_compiles(self):
        missing = {"word-chapter", "word", "gdocs", "sheets", "tsv", "markdown"} - set(Convert.outputs)
        if missing:  # this class runs after Convert; on its own, convert here
            suite = unittest.TestSuite(Convert(name) for name in (
                "test_word_paste", "test_google_docs_paste", "test_spreadsheet_cells",
                "test_tab_separated_cells_with_quotes", "test_markdown"))
            self.assertTrue(unittest.TextTestRunner(stream=io.StringIO()).run(suite).wasSuccessful())
        chapter = "\n".join(Convert.outputs[k] for k in ("word-chapter", "gdocs", "sheets", "tsv", "markdown"))
        with tempfile.TemporaryDirectory(prefix="test_convert_") as tmp:
            folder = Path(tmp)
            for name in STARTER:
                shutil.copy2(ROOT / name, folder / name)
            for name in STARTER_FOLDERS:
                if (ROOT / name).is_dir():
                    shutil.copytree(ROOT / name, folder / name)
            (folder / "chapters/99-converted.tex").write_text(chapter, encoding="utf-8")
            main = (folder / "main.tex").read_text(encoding="utf-8")
            line = "\\include{chapters/03-conclusion}"
            self.assertIn(line, main)
            (folder / "main.tex").write_text(main.replace(line, line + "\n\\include{chapters/99-converted}"), encoding="utf-8")
            run = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape",
                                  "-outdir=out", "-auxdir=out", "main.tex"], cwd=folder, capture_output=True, text=True, timeout=600)
            self.assertEqual(run.returncode, 0, "\n".join((run.stdout + run.stderr).splitlines()[-25:]))
            self.assertTrue((folder / "out/main.pdf").exists())
            log = (folder / "out/main.log").read_text(encoding="utf-8", errors="replace")
            for problem in ["Undefined control sequence", "Unicode character", "multiply defined", "Missing character"]:
                self.assertNotIn(problem, log)
            self.assertIn("FIELD METHODS", (folder / "out/main.toc").read_text(encoding="utf-8", errors="replace"))


if __name__ == "__main__":
    unittest.main()
