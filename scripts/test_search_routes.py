#!/usr/bin/env python3
"""Tests for which guide row site/search.js offers for a pasted log line. Stdlib only.

The patterns in `logRoutes` use only syntax that JavaScript and Python read
the same way, so they are run here with Python's re module.

    python3 scripts/test_search_routes.py
"""
from pathlib import Path
import re
import unittest

SCRIPT = (Path(__file__).resolve().parent.parent / "site/search.js").read_text(encoding="utf-8")
BLOCK = re.search(r"var logRoutes = \[(.*?)\n  \];", SCRIPT, flags=re.S).group(1)
ROUTES = [(re.compile(m.group(1), re.I), m.group(2))
          for m in re.finditer(r'\[/(.+?)/i,\s*\["([^"]+)"', BLOCK)]


def first_row(message):
    return next((row for pattern, row in ROUTES if pattern.search(message)), None)


class LogRoutes(unittest.TestCase):
    def test_missing_figure(self):
        self.assertEqual(first_row("! Package pdftex.def Error: File `figures/plot' not found: using draft setting."),
                         "A figure file cannot be found")

    def test_other_pdftex_def_errors_are_not_missing_files(self):
        self.assertIsNone(first_row("! Package pdftex.def Error: PDF inclusion: required page does not exist <3>."))


if __name__ == "__main__":
    unittest.main()
