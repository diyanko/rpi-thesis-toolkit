#!/usr/bin/env python3
"""Tests for the "Check your PDF" checks (site/pdf-check/core.js).

    python3 scripts/test_pdf_check.py

Compiles the test PDFs of scripts/pdf_fixtures.py (the starter, variants that
break one point each, and documents from other classes) in a temporary
folder, runs the checks on each in headless Chrome exactly as the page does
(scripts/check_pdfs.py), and compares every check's result with the table
below. Skipped when Chrome or TeX Live is missing. Standard library only.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_pdfs  # noqa: E402
import pdf_fixtures  # noqa: E402

OK, CHECK, UNKNOWN, INFO = "ok", "check", "unknown", "info"
STARTER = {"paper": OK, "same-size": OK, "numbering": OK, "position": OK, "headings": OK, "margins": OK,
           "contents": OK, "listed": OK, "fonts": OK, "blank": OK, "size": INFO, "version": OK}
TEXT_CHECKS = ["numbering", "position", "headings", "margins", "contents", "listed"]

# fixture -> the result of every check (check ids as in check_pdfs.ORDER).
EXPECTED = {
    "starter": STARTER,
    "starter-lualatex": STARTER,
    "a4-paper": {**STARTER, "paper": CHECK},
    "narrow-margins": {**STARTER, "margins": CHECK},
    "number-moved": {**STARTER, "position": CHECK},
    "sideways-table": {**STARTER, "margins": CHECK},
    "section-at-top": STARTER,
    "unlisted-heading": {**STARTER, "listed": CHECK},
    "blank-page": {**STARTER, "numbering": CHECK, "blank": CHECK},
    "font-not-embedded": {**STARTER, "numbering": CHECK, "position": UNKNOWN, "headings": UNKNOWN, "contents": UNKNOWN,
                          "listed": UNKNOWN, "fonts": CHECK, "version": INFO},
    "report-class": {**STARTER, "numbering": CHECK, "position": CHECK, "headings": CHECK, "version": INFO},
    "no-text": {**STARTER, **{name: UNKNOWN for name in TEXT_CHECKS}, "version": INFO},
}
# Points a flagged check must name (fixture, check id, text in one of its lines).
DETAILS = [
    ("a4-paper", "paper", "8.27 × 11.69 in"),
    ("sideways-table", "margins", "into the side margin"),
    ("number-moved", "position", "found bottom left"),
    ("number-moved", "position", "found top left"),
    ("unlisted-heading", "listed", "AN UNLISTED CHAPTER"),
    ("blank-page", "numbering", "no page number found"),
    ("font-not-embedded", "fonts", "Times-Roman: not embedded"),
    ("report-class", "headings", "Chapter 1"),
]


@unittest.skipUnless(check_pdfs.find_chrome(), "no Chrome or Chromium found")
@unittest.skipUnless(pdf_fixtures.tex_available(), "no TeX Live (latexmk, pdflatex, lualatex, biber)")
class CheckPdf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="test_pdf_check_")
        folder = Path(cls.tmp.name)
        cls.errors = pdf_fixtures.make(folder, EXPECTED)
        made = [name for name in EXPECTED if name not in cls.errors]
        results = check_pdfs.check([str(folder / f"{name}.pdf") for name in made], current=check_pdfs.class_version())
        cls.results = {Path(pdf).stem: found for pdf, found in results}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def found(self, name):
        self.assertNotIn(name, self.errors, f"{name} did not compile: {self.errors.get(name)}")
        found = self.results[name]
        self.assertIsInstance(found, list, f"{name} could not be read: {found}")
        return {f["id"]: f for f in found}

    def test_every_check_on_every_fixture(self):
        for name, expected in EXPECTED.items():
            with self.subTest(fixture=name):
                found = self.found(name)
                self.assertEqual(sorted(found), sorted(check_pdfs.ORDER))
                states = {key: found[key]["state"] for key in expected}
                self.assertEqual(states, expected, "\n".join(
                    f"{key}: {f['summary']}" for key, f in found.items() if states.get(key) != expected.get(key)))

    def test_flags_name_the_page_and_point(self):
        for name, check, text in DETAILS:
            with self.subTest(fixture=name, check=check):
                lines = self.found(name)[check]["pages"]
                self.assertTrue(any(text in line for line in lines), f"{text!r} not in {lines}")

    def test_rule_checks_cite_the_manual_and_others_say_information(self):
        for key, f in self.found("starter").items():
            with self.subTest(check=key):
                self.assertTrue(bool(f.get("rules")) != bool(f.get("info")), f)

    def test_could_not_tell_says_why(self):
        for name in EXPECTED:
            if name in self.errors:
                continue
            for key, f in self.found(name).items():
                if f["state"] == UNKNOWN:
                    with self.subTest(fixture=name, check=key):
                        self.assertGreater(len(f["summary"]), 40)


@unittest.skipUnless(check_pdfs.find_chrome(), "no Chrome or Chromium found")
class Measurements(unittest.TestCase):
    """The analysis alone, on page data written by hand."""

    def evaluate(self, expression):
        server = check_pdfs.Server(check_pdfs.ROOT / "site")
        browser = check_pdfs.Chrome(check_pdfs.find_chrome())
        try:
            browser.open(server.url + "/__pdf_check__.html")
            return browser.evaluate(expression)
        finally:
            browser.close()
            server.close()

    def analyse(self, data):
        found = self.evaluate(f"PdfCheckCore.analyse({json.dumps(data)}, {{current: '0.7.0', rules: {check_pdfs.RULES}}})")
        return {f["id"]: f for f in found}

    def test_needs_the_rules_data(self):
        # Without the requirements map's measurements the checks stop instead of guessing.
        with self.assertRaisesRegex(RuntimeError, "measurement paper-width"):
            self.evaluate("PdfCheckCore.analyse({fileSize: 0, pages: [], info: {}, outline: null}, {current: '0.7.0'})")

    def test_nothing_passes_without_pages(self):
        found = self.analyse({"fileSize": 0, "pages": [], "info": {}, "outline": None})
        passed = [key for key, f in found.items() if f["state"] == OK]
        self.assertEqual(passed, ["fonts", "blank"])  # nothing to flag: no fonts, no blank pages

    def test_unread_fonts_and_drawing_are_unknown(self):
        page = {"width": 612, "height": 792, "items": [], "fonts": None, "drawn": None}
        found = self.analyse({"fileSize": 10, "pages": [page], "info": {}, "outline": None})
        self.assertEqual(found["fonts"]["state"], UNKNOWN)
        self.assertEqual(found["blank"]["state"], UNKNOWN)
        self.assertEqual(found["paper"]["state"], OK)


if __name__ == "__main__":
    unittest.main()
