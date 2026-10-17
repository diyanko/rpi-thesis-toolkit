#!/usr/bin/env python3
"""Tests for how build.py reports a failed build. Stdlib only, no TeX needed.

    python3 scripts/tests/test_build.py
"""
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import build


class FirstError(unittest.TestCase):
    def check(self, log, first_line, place="l.10 \\foo"):
        found = build.first_error(log)
        self.assertEqual(found.splitlines()[0], first_line)
        self.assertIn(place, found)

    def test_windows_forward_slash_path(self):
        # Review: a drive letter's colon hid the whole file:line: prefix.
        line = "C:/thesis/chapters/a.tex:10: Undefined control sequence."
        self.check(f"(C:/thesis/main.tex\n{line}\nl.10 \\foo\n\n", line)

    def test_windows_backslash_path(self):
        line = "C:\\thesis\\a.tex:10: Undefined control sequence."
        self.check(f"{line}\nl.10 \\foo\n", line)

    def test_path_with_spaces(self):
        line = "./my chapters/a.tex:10: Undefined control sequence."
        self.check(f"{line}\nl.10 \\foo\n", line)

    def test_auxiliary_files(self):
        for name in ("./build/main.aux", "./build/main.toc", "./build/main.lof",
                     "./build/main.bbl", "build/main.lot"):
            with self.subTest(name=name):
                line = f"{name}:10: Missing \\endcsname inserted."
                self.check(f"{line}\nl.10 \\foo\n", line)

    def test_earliest_real_error_beats_generic_lines(self):
        # A missed real error left only TeX's generic stop lines to report.
        log = ("C:/thesis/a.tex:10: Undefined control sequence.\nl.10 \\foo\n\n"
               "C:/thesis/a.tex:10: Emergency stop.\nl.10 \\foo\n"
               "!  ==> Fatal error occurred, no output PDF file produced!\n")
        self.check(log, "C:/thesis/a.tex:10: Undefined control sequence.")

    def test_generic_line_still_reported_when_alone(self):
        log = "./main.tex:3: Emergency stop.\nl.3 \\foo\n"
        self.check(log, "./main.tex:3: Emergency stop.", "l.3 \\foo")

    def test_plain_bang_error(self):
        self.check("! Undefined control sequence.\nl.10 \\foo\n", "! Undefined control sequence.")

    def test_no_error(self):
        self.assertEqual(build.first_error("Output written on main.pdf (3 pages).\n"), "")


class BiberErrors(unittest.TestCase):
    CACHED = ("Latexmk: Nothing to do for 'main.tex'.\n"
              "Collected error summary (may duplicate other messages):\n"
              "  biber build/main: gave an error in previous invocation of latexmk.\n")

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.output = Path(self.folder.name)
        blg = self.output / "main.blg"
        blg.write_text("INFO - ok\nERROR - BibTeX subsystem: line 25, syntax error\n",
                       encoding="utf-8")
        old = time.time() - 600
        os.utime(blg, (old, old))

    def tearDown(self):
        self.folder.cleanup()

    def test_old_blg_ignored_when_biber_did_not_fail(self):
        self.assertEqual(build.biber_errors(self.output, time.time(), "Latexmk: done\n"), [])

    def test_cached_biber_failure_shows_old_blg(self):
        # Review: latexmk reported the earlier Biber error without rerunning
        # Biber, and the still-relevant main.blg was dropped as too old.
        errors = build.biber_errors(self.output, time.time(), self.CACHED)
        self.assertEqual(errors, ["ERROR - BibTeX subsystem: line 25, syntax error"])

    def test_cached_latex_failure_is_not_a_biber_failure(self):
        text = "  pdflatex: gave an error in previous invocation of latexmk.\n"
        self.assertEqual(build.biber_errors(self.output, time.time(), text), [])


if __name__ == "__main__":
    unittest.main()
