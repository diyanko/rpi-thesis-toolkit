#!/usr/bin/env python3
"""Tests for "Explain my error" (site/explain/core.js) and the known-problems
table it shares with the build helper (KNOWN_PROBLEMS in scripts/build.py).

    python3 scripts/tests/test_explain.py

Each made-up log below is what a student might paste: an editor's or
Overleaf's log, a wrapped line, a Windows path, or latexmk's own output. The
table is checked with Python's re module (what build.py uses); the page's
reading runs in headless Chrome, skipped when Chrome is missing. Standard
library only.
"""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import build  # noqa: E402
from chrome import Chrome  # noqa: E402
from common import ROOT, find_chrome  # noqa: E402

TYPO = ("./chapters/01-introduction.tex:13: Undefined control sequence.\n"
        "l.13 example~\\parencit\n"
        "                      {lamport1994}. Replace it with literature relevant to\n")
LONG_NAME = "./chapters/02-a-chapter-with-a-rather-long-file-name-for-the-log.tex"
WRAPPED = LONG_NAME + ":8: Undefined control sequence."
assert len(WRAPPED) > 79

# name -> (pasted text, known problem id or None, file, line); file and line
# are None when the text has no error block.
FIXTURES = {
    "typo": (TYPO, "undefined-command", "chapters/01-introduction.tex", "13"),
    "typo-crlf": (TYPO.replace("\n", "\r\n"), "undefined-command", "chapters/01-introduction.tex", "13"),
    "typo-with-log-around": (
        "This is pdfTeX, Version 3.141592653-2.6-1.40.26 (TeX Live 2024)\n"
        "(./main.tex\nLaTeX2e <2024-06-01>\n(./chapters/01-introduction.tex\n"
        "LaTeX Warning: Citation `smith2020' on page 1 undefined on input line 4.\n\n"
        + TYPO + "\n! Emergency stop.\n<*> main.tex\n", "undefined-command", "chapters/01-introduction.tex", "13"),
    "windows-path": (
        "C:\\Users\\student\\thesis\\chapters\\02-research.tex:7: Undefined control sequence.\n"
        "l.7 \\foo\n", "undefined-command", "C:\\Users\\student\\thesis\\chapters\\02-research.tex", "7"),
    "wrapped-79": (WRAPPED[:79] + "\n" + WRAPPED[79:] + "\nl.8 \\sectoin\n", "undefined-command",
                   LONG_NAME[2:], "8"),
    "missing-figure": (
        "! LaTeX Error: File `figures/plot.png' not found.\n\n"
        "See the LaTeX manual or LaTeX Companion for explanation.\n"
        "Type  H <return>  for immediate help.\n ...                                              \n\n"
        "l.20 \\includegraphics{figures/plot.png}\n", "figure-missing", "", "20"),
    "missing-figure-pdftex": (
        "./chapters/02-research.tex:31: Package pdftex.def Error: File `figures/plot' not found: using draft setting.\n"
        "l.31 \\includegraphics{figures/plot}\n", "figure-missing", "chapters/02-research.tex", "31"),
    "missing-chapter": (
        "./main.tex:40: LaTeX Error: File `chapters/04-results.tex' not found.\n"
        "l.40 \\input{chapters/04-results}\n", "tex-missing", "main.tex", "40"),
    "missing-class": (
        "./main.tex:1: LaTeX Error: File `rpi-thesis.cls' not found.\n"
        "l.1 \\documentclass{rpi-thesis}\n\n! Emergency stop.\n", "class-missing", "main.tex", "1"),
    "missing-brace-eof": (
        "./chapters/03-conclusion.tex:30: File ended while scanning use of \\textbf.\n"
        "<inserted text> \n                \\par \n<*> main.tex\n", "brace", "chapters/03-conclusion.tex", "30"),
    "missing-brace-paragraph": (
        "Runaway argument?\n{This is bold \n"
        "./chapters/01-introduction.tex:20: Paragraph ended before \\textbf was complete.\n"
        "<to be read again> \n                   \\par \nl.21 \n", "brace", "chapters/01-introduction.tex", "20"),
    "underscore": (
        "./chapters/02-research.tex:44: Missing $ inserted.\n<inserted text> \n                $\n"
        "l.44 The file my_data\n", "missing-dollar", "chapters/02-research.tex", "44"),
    "undefined-citation": (
        "LaTeX Warning: Citation `smith2020' on page 3 undefined on input line 12.\n\n"
        "LaTeX Warning: There were undefined references.\n", "undefined-reference", None, None),
    "undefined-reference": (
        "LaTeX Warning: Reference `fig:plot' on page 5 undefined on input line 30.\n",
        "undefined-reference", None, None),
    "biber-not-run": (
        "Package biblatex Warning: Please (re)run Biber on the file:\n(biblatex)                main\n"
        "(biblatex)                and rerun LaTeX afterwards.\n", "biber-not-run", None, None),
    "biber-missing-unix": (
        "Latexmk: applying rule 'biber main'...\nsh: biber: command not found\n"
        "Latexmk: Errors, so I did not complete making targets\n", "tool-missing", None, None),
    "biber-missing-windows": (
        "'biber' is not recognized as an internal or external command,\noperable program or batch file.\n",
        "tool-missing", None, None),
    "latexmk-missing-vscode": ("spawn latexmk ENOENT\n", "tool-missing", None, None),
    "biber-mac": ("biber: lipo: can't figure out the architecture type of: biber\n", "biber-mac", None, None),
    # An error nobody listed: the page shows the generic reading steps.
    "unknown-error": ("./main.tex:9: Something nobody has seen before.\nl.9 \\weird\n", None, "main.tex", "9"),
    "only-emergency-stop": ("! Emergency stop.\n<*> main.tex\n*** (job aborted, no legal \\end found)\n",
                            None, "", ""),
    "no-error": ("Output written on build/main.pdf (12 pages, 345678 bytes).\n", None, None, None),
}


def unwrap(text):
    """What core.js does before reading: one line per log line, 79-byte wraps joined."""
    lines, out, index = text.replace("\r\n", "\n").split("\n"), [], 0
    while index < len(lines):
        line = lines[index]
        while len(lines[index].encode()) == 79 and index + 1 < len(lines):
            index += 1
            line += lines[index]
        out.append(line)
        index += 1
    return "\n".join(out)


class SharedTable(unittest.TestCase):
    def test_fixtures_map_to_the_right_problem_in_python(self):
        for name, (text, expected, _, _) in FIXTURES.items():
            with self.subTest(name):
                text = unwrap(text)
                where = build.first_error(text) or text
                found = [entry["id"] for entry in build.KNOWN_PROBLEMS if build.re.search(entry["pattern"], where)]
                self.assertEqual(found[:1], [expected] if expected else [])

    def test_patterns_read_the_same_in_javascript(self):
        for entry in build.KNOWN_PROBLEMS:
            for python_only in ("(?P", "(?i", "(?m", "(?s", "(?x", "\\A", "\\Z", "(?#"):
                self.assertNotIn(python_only, entry["pattern"], entry["id"])

    def test_every_entry_names_a_guide_section(self):
        ids = [entry["id"] for entry in build.KNOWN_PROBLEMS]
        self.assertEqual(len(ids), len(set(ids)))
        for entry in build.KNOWN_PROBLEMS:
            page, anchor, _ = entry["guide"]
            self.assertTrue((ROOT / "docs" / (page + ".md")).is_file(), entry["id"])
            self.assertIn(entry["when"], ("failed", "built", "any"), entry["id"])

    def test_build_helper_prints_the_same_advice(self):
        advice = build.known_problem(FIXTURES["typo"][0], "failed")
        self.assertEqual(len(advice), 1)
        self.assertTrue(advice[0].startswith("LaTeX does not know a command"))
        self.assertIn("docs/troubleshooting.md (Read an error message)", advice[0])


@unittest.skipUnless(find_chrome(), "Chrome is not installed")
class Page(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser = Chrome(find_chrome())
        cls.browser.evaluate((ROOT / "site/explain/core.js").read_text(encoding="utf-8"))
        cls.problems = json.dumps(build.KNOWN_PROBLEMS)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()

    def explain(self, text):
        return self.browser.evaluate(f"ExplainCore.explain({json.dumps(text)}, {self.problems})")

    def test_fixtures(self):
        for name, (text, expected, file, line) in FIXTURES.items():
            with self.subTest(name):
                found = self.explain(text)
                self.assertEqual((found["problem"] or {}).get("id"), expected)
                if file is None:
                    self.assertIsNone(found["error"])
                else:
                    self.assertEqual((found["error"]["file"], found["error"]["line"]), (file, line))

    def test_same_first_error_as_the_build_helper(self):
        for name, (text, _, file, _) in FIXTURES.items():
            if file is not None:
                with self.subTest(name):
                    self.assertEqual(self.explain(text)["error"]["block"], build.first_error(unwrap(text)))


if __name__ == "__main__":
    unittest.main()
