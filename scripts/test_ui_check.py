#!/usr/bin/env python3
"""Tests for how ui_check.py saves a screenshot baseline. Stdlib only.

    python3 scripts/test_ui_check.py
"""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ui_check


class SaveBaseline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.shots, self.base = root / "run", root / "baseline"
        self.shots.mkdir()
        self.base.mkdir()
        (self.base / "old.png").write_bytes(b"old")

    def tearDown(self):
        self.tmp.cleanup()

    def test_failed_run_keeps_old_baseline(self):
        (self.shots / "new.png").write_bytes(b"new")
        self.assertFalse(ui_check.save_baseline(self.shots, self.base, ["shot failed"]))
        self.assertEqual(sorted(p.name for p in self.base.iterdir()), ["old.png"])

    def test_empty_run_keeps_old_baseline(self):
        self.assertFalse(ui_check.save_baseline(self.shots, self.base, []))
        self.assertTrue((self.base / "old.png").exists())

    def test_good_run_replaces_baseline(self):
        (self.shots / "new.png").write_bytes(b"new")
        self.assertTrue(ui_check.save_baseline(self.shots, self.base, []))
        self.assertEqual(sorted(p.name for p in self.base.iterdir()), ["new.png"])
        self.assertEqual([p.name for p in self.base.parent.iterdir() if p.name.startswith(".")], [])


if __name__ == "__main__":
    unittest.main()
