#!/usr/bin/env python3
"""Release-bump failures must leave the original sources unchanged. Stdlib only."""
from contextlib import redirect_stdout
from datetime import date
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import bump


class Bump(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.files = {
            "rpi-thesis.cls": "\\ProvidesClass{rpi-thesis}[2026/10/16 v0.7.0 Toolkit]\n",
            "main.tex": "\\documentclass{rpi-thesis}[2026/10/16]\n",
            "scripts/build_site.py": 'RELEASE_VERSION = "0.7.0"\n',
            "README.md": "v0.7.0/rpi-thesis-starter-v0.7.0.zip\n",
            "docs/get-started.md": "v0.7.0%2Frpi-thesis-overleaf-v0.7.0.zip\n",
            "CITATION.cff": "version: 0.7.0\ndate-released: 2026-10-16\n",
            "CHANGELOG.md": "# Changes\n\n## Unreleased\n\n**Changes your PDF?** No.\n",
        }
        for name, text in self.files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def snapshot(self):
        return {name: (self.root / name).read_bytes() for name in self.files}

    def invoke(self, version="0.8.0"):
        with patch.object(bump, "ROOT", self.root), patch.object(sys, "argv", ["bump.py", version]), \
                redirect_stdout(io.StringIO()):
            bump.main()

    def test_missing_late_changelog_heading_changes_nothing(self):
        (self.root / "CHANGELOG.md").write_text("# Changes\n\n## 0.7.0\n", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(SystemExit, "CHANGELOG.md"):
            self.invoke()
        self.assertEqual(self.snapshot(), before)

    def test_missing_download_link_changes_nothing(self):
        (self.root / "docs/get-started.md").write_text("No release link.\n", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(SystemExit, "docs/get-started.md"):
            self.invoke()
        self.assertEqual(self.snapshot(), before)

    def test_reusing_or_lowering_version_changes_nothing(self):
        before = self.snapshot()
        for version in ("0.7.0", "0.6.9"):
            with self.subTest(version=version), self.assertRaisesRegex(SystemExit, "newer than"):
                self.invoke(version)
            self.assertEqual(self.snapshot(), before)

    def test_valid_plan_updates_every_source_and_preserves_changelog_body(self):
        with patch.object(bump, "ROOT", self.root):
            old, prepared = bump.plan("0.8.0", date(2026, 10, 17))
        self.assertEqual(old, "0.7.0")
        self.assertEqual(set(prepared), set(self.files))
        self.assertIn("2026/10/17 v0.8.0", prepared["rpi-thesis.cls"])
        self.assertIn("v0.8.0%2Frpi-thesis-overleaf-v0.8.0", prepared["docs/get-started.md"])
        self.assertIn("`v0.8.0`.\n\n**Changes your PDF?** No.", prepared["CHANGELOG.md"])
        self.invoke()
        self.assertTrue(all("0.7.0" not in (self.root / name).read_text(encoding="utf-8")
                            for name in self.files))


if __name__ == "__main__":
    unittest.main()
