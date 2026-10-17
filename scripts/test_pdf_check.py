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

OK, DIFFERS, CHECK, UNKNOWN, INFO = "ok", "differs", "check", "unknown", "info"
STARTER = {"paper": OK, "same-size": OK, "numbering": OK, "position": OK, "distance": OK, "headings": OK, "margins": OK,
           "contents": OK, "listed": OK, "fonts": OK, "blank": OK, "size": INFO, "version": OK}
TEXT_CHECKS = ["numbering", "position", "distance", "headings", "margins", "contents", "listed"]

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
    "font-not-embedded": {**STARTER, "numbering": CHECK, "position": UNKNOWN, "distance": UNKNOWN,
                          "headings": UNKNOWN, "contents": UNKNOWN,
                          "listed": UNKNOWN, "fonts": CHECK, "version": INFO},
    "report-class": {**STARTER, "numbering": CHECK, "position": CHECK, "distance": DIFFERS, "headings": CHECK,
                     "version": INFO},
    "no-text": {**STARTER, **{name: UNKNOWN for name in TEXT_CHECKS}, "version": INFO},
    # Audit: a superscript, an accent, and numbers ending the title and its first
    # contents line once hid the chapter and made "2026" a page number.
    "heading-details": STARTER,
    # Layouts that were flagged before: misreadings pass, and small
    # differences from the manual's wording say so, softer than "Look at this".
    "chapter-label": STARTER,
    "wrapped-heading": STARTER,
    "contents-continuation": STARTER,
    "figure-caps": STARTER,
    "extra-last-page": STARTER,
    "number-distance": {**STARTER, "distance": DIFFERS},
    "number-far": {**STARTER, "distance": CHECK},
    "margin-overrun-small": {**STARTER, "margins": DIFFERS},
    # Audit: /UserUnit 2 on half-size pages is US letter in physical size.
    "user-unit": {"paper": OK, "same-size": OK},
    "many-pages": {"paper": OK, "same-size": OK},  # for Upload
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
    ("extra-last-page", "numbering", "It is the last page"),
    ("number-distance", "distance", "0.58 in from the bottom edge"),
    ("number-distance", "distance", "0.58 in from the top edge"),
    ("number-far", "distance", "0.20 in from the bottom edge"),
    ("margin-overrun-small", "margins", "0.05 in into the side margin"),
]


FIXTURES = {}


def fixtures():
    """Compile every fixture once for all the tests: (folder, {name: error})."""
    if not FIXTURES:
        FIXTURES["tmp"] = tempfile.TemporaryDirectory(prefix="test_pdf_check_")
        folder = Path(FIXTURES["tmp"].name)
        FIXTURES["made"] = (folder, pdf_fixtures.make(folder, EXPECTED))
    return FIXTURES["made"]


def tearDownModule():
    if FIXTURES:
        FIXTURES["tmp"].cleanup()


@unittest.skipUnless(check_pdfs.find_chrome(), "no Chrome or Chromium found")
@unittest.skipUnless(pdf_fixtures.tex_available(), "no TeX Live (latexmk, pdflatex, lualatex, biber)")
class CheckPdf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder, cls.errors = fixtures()
        made = [name for name in EXPECTED if name not in cls.errors]
        results = check_pdfs.check([str(folder / f"{name}.pdf") for name in made], current=check_pdfs.class_version())
        cls.results = {Path(pdf).stem: found for pdf, found in results}

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


def item(text, x, y, size=11.96, width=None):
    """One pdf.js text item, upright."""
    return {"str": text, "transform": [size, 0, 0, size, x, y],
            "width": width if width is not None else len(text) * size * 0.5, "height": size}


def page(items):
    return {"width": 612, "height": 792, "rotate": 0, "items": items, "fonts": [], "drawn": True}


def body_page(label, text, number=None, extra=()):
    """A body page printed `label`: one line, and its number top right unless
    number = (text, x, y) says otherwise."""
    label, x, y = number or (label, 534, 738)
    return page([item(text, 72, 708), item(label, x, y, width=5.98)] + list(extra))


def document(more, contents=(("1. INTRODUCTION", "1"),), contents_extra=(), chapter_title=None,
             chapter_lines=(), creator="LaTeX with rpi-thesis 2026/10/16 v0.7.0"):
    """A small PDF as core.read returns it: a title page, a contents page with
    the given (title, page) entries, Chapter 1 on PDF page 3, then `more`."""
    title = page([item("A THESIS", 250, 600)])
    toc = [item("CONTENTS", 266, 708, size=14.35), item("ii", 302, 54, width=5)]
    for k, (text, label) in enumerate(contents):
        y = 668 - 24 * k
        toc += [item(text, 72, y), item(". . . . . . . .", 300, y, width=190), item(label, 534, y, width=5.98)]
    chapter = (list(chapter_title) if chapter_title else [item("1. INTRODUCTION", 240, 708, size=14.35)])
    chapter += [item(line, 72, 668 - 24 * k) for k, line in enumerate(chapter_lines)] + [item("1", 303, 54, width=5.98)]
    return {"fileSize": 1000, "pages": [title, page(toc + list(contents_extra)), page(chapter)] + list(more),
            "info": {"Creator": creator}, "outline": None}


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

    def test_the_hand_written_document_passes(self):
        # The control for the cases below: each changes one thing.
        found = self.analyse(document([body_page("2", "Ordinary body text.")]))
        states = {key: found[key]["state"] for key in TEXT_CHECKS + ["paper", "version"]}
        self.assertEqual(states, {key: OK for key in states}, found)

    def test_nonpositive_measurement_stops(self):
        # A zero or negative measurement would make every distance pass or fail.
        expression = ("(() => { const r = " + check_pdfs.RULES + "; r.measures.margin.pt = 0; "
                      "return PdfCheckCore.analyse({fileSize: 0, pages: [], info: {}, outline: null}, "
                      "{current: '0.7.0', rules: r}); })()")
        with self.assertRaisesRegex(RuntimeError, "measurement margin"):
            self.evaluate(expression)

    def test_off_page_number_is_not_top_right(self):
        found = self.analyse(document([body_page("2", "Ordinary body text.", number=("2", 650, 738))]))
        self.assertEqual(found["position"]["state"], CHECK, found["position"])
        self.assertTrue(any("PDF page 4" in line for line in found["position"]["pages"]))

    def test_digit_top_is_not_the_baseline(self):
        # Review: 62.4 pt from the top to the baseline passed as 54 pt.
        # Now 0.87 in is a difference from the manual's wording, not a pass.
        found = self.analyse(document([body_page("2", "Ordinary body text.", number=("2", 534, 792 - 62.4))]))
        self.assertEqual(found["distance"]["state"], DIFFERS, found["distance"])
        self.assertTrue(any("0.87 in from the top edge" in line for line in found["distance"]["pages"]))

    def test_a_section_entry_does_not_list_the_chapter(self):
        # Review: an entry for 1.1 on the chapter's page satisfied the chapter heading.
        data = document([], contents=[("1.1 Background", "1")])
        found = self.analyse(data)
        self.assertEqual(found["listed"]["state"], CHECK, found["listed"])
        self.assertTrue(any("1. INTRODUCTION" in line for line in found["listed"]["pages"]))

    def test_running_header_in_the_side_margin(self):
        # Review: header and footer text was never measured across the page.
        found = self.analyse(document([body_page("2", "Ordinary body text.", extra=[item("Running head", 5, 740)])]))
        self.assertEqual(found["margins"]["state"], CHECK, found["margins"])

    def test_sideways_number_in_a_table_is_measured(self):
        # Review: every sideways number was taken as a page number and skipped.
        cell = {"str": "42", "transform": [0, 12, -12, 0, 70, 400], "width": 12, "height": 12}
        found = self.analyse(document([body_page("2", "Ordinary body text.", extra=[cell])]))
        self.assertEqual(found["margins"]["state"], CHECK, found["margins"])

    def test_a_phrase_in_a_paragraph_is_not_the_heading(self):
        data = document([], contents=[("1. INTRODUCTION", "1"), ("1.1 Methods", "1")],
                        chapter_lines=["We discuss 1.1 Methods in this paragraph, not in a heading."])
        self.assertEqual(self.analyse(data)["contents"]["state"], CHECK)
        data = document([], contents=[("1. INTRODUCTION", "1"), ("1.1 Methods", "1")],
                        chapter_lines=["Some opening text.", "1.1 Methods"])
        self.assertEqual(self.analyse(data)["contents"]["state"], OK)

    def test_a_lone_number_in_the_contents_is_not_an_entry(self):
        data = document([], contents=[("1. INTRODUCTION", "1")], contents_extra=[item("2", 200, 650, size=8.8)])
        found = self.analyse(data)
        self.assertEqual(found["contents"]["state"], OK, found["contents"])
        self.assertIn("The only entry matches", found["contents"]["summary"])

    def test_superscript_stays_on_its_line(self):
        data = document([], contents=[("1. RESULTS IN R2", "1")],
                        chapter_title=[item("1. RESULTS IN R", 240, 708, size=14.35),
                                       item("2", 348, 713.25, size=10.46)])
        found = self.analyse(data)
        self.assertEqual(found["contents"]["state"], OK, found["contents"])
        self.assertEqual(found["headings"]["state"], OK, found["headings"])
        self.assertEqual(found["numbering"]["state"], OK, found["numbering"])
        self.assertEqual(found["listed"]["state"], OK, found["listed"])

    def test_class_baseline_only_for_this_class(self):
        # 90 pt is above the general limit but not the class's own 84 pt.
        low = [item("1. INTRODUCTION", 240, 792 - 90, size=14.35)]
        self.assertEqual(self.analyse(document([], chapter_title=low))["headings"]["state"], CHECK)
        other = document([], chapter_title=low, creator="Another program")
        self.assertEqual(self.analyse(other)["headings"]["state"], OK)

    def test_a_slightly_low_heading_differs_and_a_far_one_is_flagged(self):
        # 1.40 in differs from the manual's wording; far lower stays "Look at this".
        for depth, state in ((101, DIFFERS), (130, CHECK)):
            low = [item("1. INTRODUCTION", 240, 792 - depth, size=14.35)]
            found = self.analyse(document([], chapter_title=low, creator="Another program"))["headings"]
            self.assertEqual(found["state"], state, found)
            if state == DIFFERS:
                self.assertIn("1.40 in", found["summary"])
                self.assertIn("confirm it with OGE", found["summary"])

    def test_tiny_capitals_open_nothing(self):
        # Labels inside a figure (4.5 pt capitals) once counted as a chapter opening.
        labels = [item("ACCURACY RUNTIME MMLU", 180, 712, size=4.5)]
        found = self.analyse(document([page(labels + [item("Ordinary body text.", 72, 500),
                                                       item("2", 534, 738, width=5.98)])]))
        for key in ("position", "headings", "listed"):
            self.assertEqual(found[key]["state"], OK, found[key])

    def test_newer_version_is_not_called_the_newest(self):
        found = self.analyse(document([], creator="LaTeX with rpi-thesis 2030/01/01 v9.0.0"))["version"]
        self.assertIn("newer than", found["summary"])
        self.assertNotIn("the newest version", found["summary"])

    def test_unread_fonts_and_drawing_are_unknown(self):
        page = {"width": 612, "height": 792, "items": [], "fonts": None, "drawn": None}
        found = self.analyse({"fileSize": 10, "pages": [page], "info": {}, "outline": None})
        self.assertEqual(found["fonts"]["state"], UNKNOWN)
        self.assertEqual(found["blank"]["state"], UNKNOWN)
        self.assertEqual(found["paper"]["state"], OK)



# Page helpers for Upload: choose(n, name) picks PDF n of the server (or broken
# bytes for n = -1) as the file input does; settle(test) waits for test().
UI_HELPERS = """
window.choose = async function (n, name) {
  const bytes = n < 0 ? new Blob(["%PDF-1.4 not really a PDF"]) : await (await fetch("/__pdf__/" + n)).blob();
  const transfer = new DataTransfer();
  transfer.items.add(new File([bytes], name, { type: "application/pdf" }));
  const input = document.querySelector("#pdf-check-file");
  input.files = transfer.files;
  input.dispatchEvent(new Event("change", { bubbles: true }));
};
window.settle = function (test, what) {
  // Tested on every change to the page, so a passing status is never missed.
  return new Promise(function (resolve, reject) {
    const observer = new MutationObserver(check), timer = setInterval(check, 20);
    const limit = setTimeout(function () {
      stop();
      reject(new Error("timed out waiting for " + what + "; status: " + statusText()));
    }, 20000);
    function stop() { observer.disconnect(); clearInterval(timer); clearTimeout(limit); }
    function check() { if (test()) { stop(); resolve(true); } }
    observer.observe(document.body, { subtree: true, childList: true, characterData: true, attributes: true });
    check();
  });
};
window.heading = () => (document.querySelector(".pdf-check-results h3") || {}).textContent || "";
window.statusText = () => document.querySelector(".pdf-check-status").textContent;
true"""


@unittest.skipUnless(check_pdfs.find_chrome(), "no Chrome or Chromium found")
@unittest.skipUnless(pdf_fixtures.tex_available(), "no TeX Live (latexmk, pdflatex, lualatex, biber)")
class Upload(unittest.TestCase):
    """The page part (ui.js) with the real pdf.js on real fixtures: each check
    releases its reader, a new choice replaces an old one, and Cancel stops one."""

    @classmethod
    def setUpClass(cls):
        folder, errors = fixtures()
        if {"starter", "a4-paper", "many-pages"} & set(errors):
            raise unittest.SkipTest("the fixtures did not compile")
        names = ["starter", "a4-paper", "many-pages"]
        cls.server = check_pdfs.Server(check_pdfs.ROOT / "site", [folder / f"{name}.pdf" for name in names])
        cls.browser = check_pdfs.Chrome(check_pdfs.find_chrome())

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.close()

    def setUp(self):
        self.browser.open(self.server.url + "/__pdf_ui__.html")
        self.run_js(UI_HELPERS)

    def run_js(self, script):
        return self.browser.evaluate(script)

    def released(self):
        # pdf.js ends its worker shortly after the reader is destroyed.
        self.run_js("settle(() => window.liveWorkers === 0, 'the pdf.js worker to end')")

    def test_a_check_shows_results_and_releases_the_reader(self):
        self.run_js("choose(0, 'starter.pdf').then(() => settle(() => heading(), 'results'))")
        self.assertEqual(self.run_js("heading()"), "Results for starter.pdf")
        self.assertTrue(self.run_js("document.activeElement === document.querySelector('.pdf-check-results h3')"))
        self.released()

    def test_a_broken_file_releases_the_reader(self):
        self.run_js("choose(-1, 'broken.pdf').then(() => settle(() => /could not be read/.test(statusText()), 'the error'))")
        self.released()
        self.assertTrue(self.run_js("document.querySelector('.pdf-check-cancel').hidden"))

    def test_cancel_stops_the_check_and_a_new_one_runs(self):
        self.run_js("choose(2, 'long.pdf').then(() => settle(() => /Reading page 5 /.test(statusText()), 'reading'))")
        self.assertFalse(self.run_js("document.querySelector('.pdf-check-cancel').hidden"))
        # By keyboard: focus Cancel and press Enter.
        self.run_js("document.querySelector('.pdf-check-cancel').focus(); true")
        for kind in ("keyDown", "keyUp"):
            self.browser.call("Input.dispatchKeyEvent", type=kind, key="Enter", code="Enter",
                              windowsVirtualKeyCode=13, text="\r" if kind == "keyDown" else "")
        self.run_js("settle(() => /cancelled/i.test(statusText()), 'the cancel message')")
        self.released()
        self.run_js("new Promise(r => setTimeout(r, 1500))")
        self.assertEqual(self.run_js("heading()"), "", "a cancelled check showed results")
        self.assertTrue(self.run_js("document.querySelector('.pdf-check-cancel').hidden"))
        self.assertTrue(self.run_js("document.activeElement === document.querySelector('#pdf-check-file')"))
        self.run_js("choose(1, 'again.pdf').then(() => settle(() => heading(), 'results'))")
        self.assertEqual(self.run_js("heading()"), "Results for again.pdf")
        self.released()

    def test_a_new_choice_replaces_a_running_check(self):
        self.run_js("choose(2, 'first.pdf').then(() => settle(() => /Reading page 5 /.test(statusText()), 'reading'))")
        self.run_js("choose(1, 'second.pdf').then(() => settle(() => heading(), 'results'))")
        self.run_js("new Promise(r => setTimeout(r, 1500))")
        self.assertEqual(self.run_js("heading()"), "Results for second.pdf")
        self.assertIn("8.27", self.run_js("document.querySelector('.pdf-check-results').textContent"))
        self.released()

    def test_the_printout_goes_after_printing_and_with_a_new_choice(self):
        self.run_js("choose(0, 'starter.pdf').then(() => settle(() => heading(), 'results'))")
        self.run_js("window.print = function () {}; document.querySelector('.pdf-check-results button').click(); true")
        self.assertTrue(self.run_js("Boolean(document.querySelector('.pdf-check-print'))"))
        self.run_js("window.dispatchEvent(new Event('afterprint')); true")
        self.assertFalse(self.run_js("Boolean(document.querySelector('.pdf-check-print'))"))
        self.assertFalse(self.run_js("document.documentElement.classList.contains('pdf-check-printing')"))
        self.run_js("document.querySelector('.pdf-check-results button').click(); true")
        self.run_js("choose(1, 'next.pdf').then(() => settle(() => heading(), 'results'))")
        self.assertFalse(self.run_js("Boolean(document.querySelector('.pdf-check-print'))"),
                         "a printout of the previous PDF stayed in the page")


if __name__ == "__main__":
    unittest.main()
