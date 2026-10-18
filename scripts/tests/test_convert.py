#!/usr/bin/env python3
"""Tests for "Convert to LaTeX" (site/convert/core.js and ui.js).

    python3 scripts/tests/test_convert.py

Runs the converter in headless Chrome, as the page does, on the synthetic
pasted text in scripts/tests/convert_fixtures/: escaping, a Word-like and a
Google-Docs-like paste, spreadsheet cells (HTML and tab-separated, with
quoted tabs), Markdown, and a whole Markdown chapter. Each case checks that
the words arrive and the markup is right, not only that it compiles; each
note must point at the lines it is about, and the preview must read the
LaTeX back with its numbers, captions, and characters. The page part is
tested with a real paste event, including one full of things that would load
or run: nothing may reach the server and nothing may run. The LaTeX / Preview
switch and "Show where" are tested by keyboard. Finally the converted
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
    found = re.search(r'(?m)^<div class="[^"]*\bconvert\b[^"]*" .*$', (ROOT / "docs/convert-to-latex.md").read_text(encoding="utf-8"))
    if not found:
        raise RuntimeError('docs/convert-to-latex.md has no <div class="convert" ...> line')
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

    def places(self, result, note_id):
        """The LaTeX lines each place of a note covers, as text."""
        lines = result["latex"].split("\n")
        note = next(n for n in result["notes"] if n["id"] == note_id)
        return ["\n".join(lines[p["from"]:p["to"] + 1]) for p in note["places"]]

    def preview(self, latex):
        return self.call("preview", latex)["blocks"]

    @staticmethod
    def words(nodes):
        """The text a preview's inline pieces show."""
        return "".join(n.get("text", "") if "children" not in n else Convert.words(n["children"]) for n in nodes)

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

    def test_notes_point_at_their_lines(self):
        word = self.convert(html=fixture("word-paste.html"))
        self.assertEqual(len(self.places(word, "picture")), 1)
        self.assertTrue(self.places(word, "picture")[0].startswith('% A picture was here ("Map of the three sites")'))
        self.assertIn("[equation]", self.places(word, "equation")[0])
        self.assertIn(r"site \#2 at \$12 each.[1]", self.places(word, "footnote")[0])
        self.assertEqual(next(n for n in word["notes"] if n["id"] == "comment")["places"], [])
        gdocs = self.convert(html=fixture("gdocs-paste.html"))
        self.assertIn("A risky link", self.places(gdocs, "link")[0])
        sheets = self.convert(html=fixture("sheets-cells.html"))
        merged = self.places(sheets, "merged")[0]
        self.assertTrue(merged.startswith("\\begin{table}") and merged.endswith("\\end{table}"))
        chapter = self.convert(text=fixture("chapter.md"), chapter=True, key="chapter")
        self.assertEqual([p.split(".")[0] for p in self.places(chapter, "picture")],
                         ['% A picture was here ("Map of the three sites")', '% A picture was here ("Photo of the probe")'])
        self.assertEqual(len(self.places(chapter, "citation")), 2)
        self.assertTrue(all("[@lamport1994]" in p for p in self.places(chapter, "citation")))
        display = self.places(chapter, "display-math")[0]
        self.assertTrue(display.startswith("\\begin{equation}") and display.endswith("\\end{equation}"))
        self.assertEqual(self.places(chapter, "caption"), ["  \\caption{Your full caption, ending with a period.}"])
        # A "Table 2: ..." line next to a Markdown table is its caption;
        # "Table 3 shows ..." is a sentence and stays.
        self.assertIn(r"\caption{Yield by site and season}", chapter["latex"])
        self.assertNotIn("Table 2:", chapter["latex"])
        kept = self.convert(text="Table 3 shows the visits.\n\n| A | B |\n| - | - |\n| 1 | 2 |\n")["latex"]
        self.assertIn("Table 3 shows the visits.", kept)
        # Places count the final lines: blank lines collapse, and every place
        # is inside the LaTeX.
        for result in (word, gdocs, sheets, chapter):
            count = len(result["latex"].split("\n"))
            for note in result["notes"]:
                for place in note["places"]:
                    self.assertTrue(0 <= place["from"] <= place["to"] < count, (note["id"], place))

    def test_table_limits_count_only_cells_with_text(self):
        # Empty rows do not use up the row limit (they used to push the last row out).
        result = self.convert(text="A\tB\n" + "\t\n" * 499 + "LOST\tEND\n")
        self.assertIn(r"LOST & END \\", result["latex"])
        self.assertNotIn("big", self.notes(result))
        # More rows with text than the limit: cut, said, and located.
        rows = "".join("r%d\t%d\n" % (n, n) for n in range(502))
        result = self.convert(text=rows)
        self.assertIn(r"r499 & 499 \\", result["latex"])
        self.assertNotIn("r500 &", result["latex"])
        self.assertIn("big", self.notes(result))
        self.assertTrue(self.places(result, "big")[0].startswith("\\begin{table}"))
        html = "<table>" + "<tr><td></td><td></td></tr>" * 600 + "<tr><td>LAST</td><td>ROW</td></tr></table>"
        self.assertIn(r"LAST & ROW \\", self.convert(html=html)["latex"])

    def test_rich_text_over_the_limit_keeps_the_plain_text_and_says_so(self):
        result = self.browser.evaluate("""ConvertCore.convert({ html: '<p><b>' + 'x'.repeat(2000001) + '</b></p>',
                                                            text: 'Plain words, 50%' }, {})""")
        self.assertEqual(result["latex"], "Plain words, 50\\%\n")
        self.assertEqual(sorted(self.notes(result)), ["plain"])

    def test_preview_reads_the_latex_back(self):
        blocks = self.preview(self.convert(text=fixture("chapter.md"), chapter=True)["latex"])
        headings = [(b["number"], self.words(b["children"])) for b in blocks if b["type"] == "heading"]
        self.assertEqual(headings, [("N.", "FIELD STUDY"), ("N.1", "Sites"), ("N.2", "Methods"),
                                    ("N.2.1", "Instruments"), ("N.3", "Results")])
        tables = [b for b in blocks if b["type"] == "table"]
        self.assertEqual([(t["number"], t["placeholder"], t["head"], t["align"]) for t in tables],
                         [("N.1", True, 1, ["l", "r", "r", "l"]), ("N.2", False, 1, ["l", "r", "r"])])
        self.assertEqual(self.words(tables[1]["caption"]), "Yield by site and season")
        self.assertEqual([self.words(c) for c in tables[0]["rows"][2]["cells"]], ["B", "18", "6", "Clay & silt"])
        paras = [self.words(b["children"]) for b in blocks if b["type"] == "para"]
        self.assertIn("Site C had a 15% slope", paras[1])
        self.assertIn("g with σ ≈ 0.8 g.", paras[2])
        math = next(b for b in blocks if b["type"] == "math")
        self.assertEqual((math["text"], math["number"]), (r"\bar{m} = \frac{1}{n} \sum_{i=1}^{n} m_i", "(N.1)"))
        self.assertEqual([b["alt"] for b in blocks if b["type"] == "picture"], ["Map of the three sites", "Photo of the probe"])
        nested = next(b for b in blocks if b["type"] == "list")
        self.assertTrue(nested["ordered"])
        self.assertEqual(self.words(nested["items"][1]["lists"][0]["items"][1]["children"]), "cleaned after each plot")
        last = blocks[-1]["children"]
        self.assertEqual([n["t"] for n in last], ["text", "code", "text", "link", "text"])
        self.assertEqual((last[1]["text"], last[3]["href"]), ("field_tools/", "https://example.org/field_study?v=2&p=%20"))
        # Every fixture: no LaTeX command is left in the words shown, only in math and code.
        def shown(nodes):
            return "".join(shown(n["children"]) if "children" in n else n["text"] if n["t"] in ("text", "mark") else "" for n in nodes)
        def walk(items):
            for b in items:
                for key in ("children", "caption"):
                    if b.get(key):
                        yield shown(b[key])
                for row in b.get("rows", []):
                    for cell in row["cells"]:
                        yield shown(cell)
                for item in b.get("items", []):
                    yield shown(item["children"])
                    yield from walk(item["lists"])
                yield from walk(b.get("blocks", []))
        for name, source in [("word", {"html": fixture("word-paste.html")}), ("gdocs", {"html": fixture("gdocs-paste.html")}),
                             ("sheets", {"html": fixture("sheets-cells.html")}), ("tsv", {"text": fixture("excel-cells.tsv")}),
                             ("markdown", {"text": fixture("sample.md")}), ("chapter", {"text": fixture("chapter.md")})]:
            for chapter in (False, True):
                with self.subTest(name=name, chapter=chapter):
                    for text in walk(self.preview(self.convert(chapter=chapter, **source)["latex"])):
                        self.assertNotRegex(text, r"\\[A-Za-z]|\\[%&_#${}]|\{\[\}")
        word = self.preview(self.convert(html=fixture("word-paste.html"))["latex"])
        self.assertIn("[B]", [self.words(row["cells"][0]) for b in word if b["type"] == "table" for row in b["rows"]])
        self.assertIn("20\u00a0°C, with α\u00a0=\u00a00.05.", " ".join(self.words(b["children"]) for b in word if b["type"] == "para"))
        # Text the writer never produces stays as text; nothing is lost.
        self.assertEqual(self.words(self.preview("\\unknown{x} y\n")[0]["children"]), "\\unknownx y")

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
        # The only elements in the output are one span per line holding the
        # highlighter's own text spans.
        self.assertTrue(self.browser.evaluate("[...document.querySelectorAll('.convert-output > *')].every("
                                              "n => n.tagName === 'SPAN' && n.className === 'convert-line' && [...n.children].every("
                                              "c => c.tagName === 'SPAN' && /^tok-[a-z]+$/.test(c.className) && !c.children.length))"))
        # The preview holds only the page's own elements; its links are web links.
        self.browser.evaluate("document.querySelector('#convert-view-preview').click(); true")
        self.assertTrue(self.browser.evaluate("document.querySelector('.convert-output').hidden && !document.querySelector('.convert-preview').hidden"))
        self.assertIn("Hello there x", self.browser.evaluate("document.querySelector('.convert-preview').textContent"))
        self.assertTrue(self.browser.evaluate("[...document.querySelectorAll('.convert-preview *')].every(n => "
                                              "/^(P|SPAN|STRONG|EM|CODE|MARK|A|UL|OL|LI|DIV|TABLE|CAPTION|THEAD|TBODY|TR|TH|TD|BLOCKQUOTE|PRE|SUP|SUB)$/.test(n.tagName) && "
                                              "[...n.attributes].every(a => /^(class|data-from|data-to|href|target|rel|scope)$/.test(a.name)))"))
        self.assertTrue(self.browser.evaluate("[...document.querySelectorAll('.convert-preview a')].every(a => /^(https?|mailto):/.test(a.href))"))
        self.browser.evaluate("document.querySelector('#convert-view-latex').click(); true")
        self.assertGreater(self.browser.evaluate("document.querySelectorAll('.convert-output .tok-cmd').length"), 0)
        self.assertEqual(self.browser.evaluate("document.querySelector('.convert-input').value"), "Hello there x")
        self.assertIn("rich text", self.browser.evaluate("document.querySelector('.convert-status').textContent"))
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


    def ui(self):
        self.browser.open(self.server.url + "/__convert_ui__.html")
        self.browser.evaluate("new Promise(r => { const t = setInterval(() => { if (window.ConvertCore) { clearInterval(t); r(true); } }, 20); })")

    def key(self, name, code, text=""):
        for kind in ("keyDown", "keyUp"):
            self.browser.call("Input.dispatchKeyEvent", type=kind, key=name, code=name if len(name) > 1 else code,
                              windowsVirtualKeyCode=code, text=text if kind == "keyDown" else "")

    def test_ui_preview_and_show_where_by_keyboard(self):
        self.ui()
        REQUESTS.clear()
        self.browser.evaluate("document.querySelector('input[value=chapter]').click(); true")
        self.browser.evaluate("""(function (text) { const box = document.querySelector('.convert-input');
          box.value = text; box.dispatchEvent(new Event('input', { bubbles: true }));
          return new Promise(r => setTimeout(() => r(true), 400)); })(%s)""" % json.dumps(fixture("chapter.md")))
        status = "document.querySelector('.convert-status').textContent"
        buttons = "[...document.querySelectorAll('.convert-where button')]"
        self.assertEqual(self.browser.evaluate(buttons + ".map(b => b.textContent)"),
                         ["Show where (2 places)", "Show where", "Show where (2 places)", "Show where"])
        # The pictures note, by keyboard: Enter marks the first place, Enter again the next.
        self.browser.evaluate(buttons + "[0].focus(); true")
        self.key("Enter", 13, "\r")
        marked = "[...document.querySelectorAll('.convert-output .is-current')].map(n => n.textContent).join('')"
        self.assertTrue(self.browser.evaluate(marked).startswith('% A picture was here ("Map of the three sites")'))
        self.assertIn("place 1 of 2", self.browser.evaluate(status))
        self.assertEqual(self.browser.evaluate("document.querySelectorAll('.convert-output .is-marked').length"), 2)
        self.assertTrue(self.browser.evaluate("document.activeElement === " + buttons + "[0]"))
        self.key("Enter", 13, "\r")
        self.assertTrue(self.browser.evaluate(marked).startswith('% A picture was here ("Photo of the probe")'))
        self.assertIn("line 48 of the LaTeX: place 2 of 2", self.browser.evaluate(status))
        # The marked line is scrolled into the LaTeX box.
        self.assertTrue(self.browser.evaluate("""(function () { const box = document.querySelector('.convert-output').getBoundingClientRect(),
          line = document.querySelector('.convert-output .is-current').getBoundingClientRect();
          return line.top >= box.top && line.bottom <= box.bottom; })()"""))
        # Arrow keys move between LaTeX and Preview; the marks follow.
        self.browser.evaluate("document.querySelector('#convert-view-latex').focus(); true")
        self.key("ArrowRight", 39)
        self.assertTrue(self.browser.evaluate("document.querySelector('#convert-view-preview').checked"))
        self.assertTrue(self.browser.evaluate("document.querySelector('.convert-output').hidden"))
        self.assertEqual(self.browser.evaluate("document.querySelector('.convert-preview .is-current').textContent"),
                         "Picture not copied: Photo of the probe. Add it from figures/.")
        preview = "document.querySelector('.convert-preview')"
        self.assertIn("not your PDF", self.browser.evaluate(preview + ".querySelector('.convert-preview-note').textContent"))
        self.assertEqual(self.browser.evaluate("[..." + preview + ".querySelectorAll('.convert-heading')].map(h => h.textContent)"),
                         ["N.FIELD STUDY", "N.1Sites", "N.2Methods", "N.2.1Instruments", "N.3Results"])
        self.assertEqual(self.browser.evaluate("[..." + preview + ".querySelectorAll('caption')].map(c => c.textContent)"),
                         ["Table N.1: Your full caption, ending with a period.", "Table N.2: Yield by site and season"])
        self.assertEqual(self.browser.evaluate(preview + ".querySelectorAll('thead th').length"), 7)
        self.assertEqual(self.browser.evaluate(preview + ".querySelector('.convert-equation').textContent"),
                         "\\bar{m} = \\frac{1}{n} \\sum_{i=1}^{n} m_i(N.1)")
        # In the preview: the citation note marks both paragraphs, the caption note the caption.
        self.browser.evaluate(buttons + "[2].click(); true")
        self.assertEqual(self.browser.evaluate("[..." + preview + ".querySelectorAll('.is-marked')].map(n => n.tagName)"), ["P", "P"])
        self.browser.evaluate(buttons + "[3].click(); true")
        self.assertEqual(self.browser.evaluate("[..." + preview + ".querySelectorAll('.is-marked')].map(n => n.tagName)"), ["CAPTION"])
        self.assertIn("in the preview, from line 15", self.browser.evaluate(status))
        self.browser.evaluate(buttons + "[1].click(); true")   # the display equation, lines 32 to 35
        self.assertEqual(self.browser.evaluate("[..." + preview + ".querySelectorAll('.is-marked')].map(n => n.className)"),
                         ["convert-equation is-marked is-current"])
        # A new conversion clears the marks and draws the preview again.
        self.browser.evaluate("document.querySelector('input[value=body]').click(); true")
        self.assertEqual(self.browser.evaluate("document.querySelectorAll('.is-marked').length"), 0)
        self.assertEqual(self.browser.evaluate(preview + ".querySelector('.convert-heading').textContent"), "N.1Field Study")
        self.assertEqual(REQUESTS, [])

    def test_ui_late_file_read_is_ignored(self):
        self.ui()
        # A dropped file whose read finishes only after Clear is pressed.
        self.browser.evaluate("""(function () {
          window.finish = null;
          File.prototype.text = function () { const file = this; return new Promise(r => { window.finish = () => r('# Late\\n\\nOld text'); }); };
          const box = document.querySelector('.convert-input'), data = new DataTransfer();
          data.items.add(new File(['x'], 'draft.md', { type: 'text/markdown' }));
          box.dispatchEvent(new DragEvent('drop', { dataTransfer: data, bubbles: true, cancelable: true }));
          document.querySelector('.convert-clear').click();
          window.finish();
          return new Promise(r => setTimeout(() => r(true), 300)); })()""")
        self.assertEqual(self.browser.evaluate("document.querySelector('.convert-input').value"), "")
        self.assertEqual(self.browser.evaluate("document.querySelector('.convert-output').textContent"), "")
        # Without anything newer, the read is used.
        self.browser.evaluate("""(function () {
          const box = document.querySelector('.convert-input'), data = new DataTransfer();
          data.items.add(new File(['x'], 'draft.md', { type: 'text/markdown' }));
          box.dispatchEvent(new DragEvent('drop', { dataTransfer: data, bubbles: true, cancelable: true }));
          window.finish();
          return new Promise(r => setTimeout(() => r(true), 300)); })()""")
        self.assertIn(r"\section{Late}", self.browser.evaluate("document.querySelector('.convert-output').textContent"))


@unittest.skipUnless(find_chrome(), "no Chrome or Chromium found")
@unittest.skipUnless(all(shutil.which(tool) for tool in ("latexmk", "pdflatex", "biber")), "no TeX Live")
class Typeset(unittest.TestCase):  # named to run after Convert
    """The converted fixtures, together in one chapter, compile in the starter."""

    def test_combined_output_compiles(self):
        missing = {"word-chapter", "word", "gdocs", "sheets", "tsv", "markdown", "chapter"} - set(Convert.outputs)
        if missing:  # this class runs after Convert; on its own, convert here
            suite = unittest.TestSuite(Convert(name) for name in (
                "test_word_paste", "test_google_docs_paste", "test_spreadsheet_cells",
                "test_tab_separated_cells_with_quotes", "test_markdown", "test_notes_point_at_their_lines"))
            self.assertTrue(unittest.TextTestRunner(stream=io.StringIO()).run(suite).wasSuccessful())
        chapter = "\n".join(Convert.outputs[k] for k in ("word-chapter", "gdocs", "sheets", "tsv", "markdown", "chapter"))
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
