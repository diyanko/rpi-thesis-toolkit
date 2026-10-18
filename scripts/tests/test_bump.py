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


    def test_release_leaves_out_the_version_line(self):
        (self.root / "CHANGELOG.md").write_text("# Changes\n\n## Unreleased\n\n**Changes your PDF?** No.\n\n"
                                                "**Version:** minor\n\n- A change.\n\n## 0.7.0 (beta), 16 Oct 2026\n",
                                                encoding="utf-8")
        with patch.object(bump, "ROOT", self.root):
            _, prepared = bump.plan("0.8.0", date(2026, 10, 17))
        self.assertNotIn("**Version:**", prepared["CHANGELOG.md"])
        self.assertIn("**Changes your PDF?** No.\n\n- A change.", prepared["CHANGELOG.md"])

    def test_version_is_chosen_from_the_unreleased_section(self):
        cases = [("**Changes your PDF?** No.\n\n- Guide fix.", "0.7.1"),
                 ("**Changes your PDF?** **Yes**, spacing.", "0.8.0"),
                 ("**Changes your PDF?** Only if you use LuaLaTeX.", "0.8.0"),
                 ("**Changes your PDF?** No.\n\n- A new setting, `foo`.", "0.8.0")]
        for body, expected in cases:
            with self.subTest(body=body):
                log = f"# Changes\n\n## Unreleased\n\n{body}\n\n## 0.7.0\n\n**Changes your PDF?** Yes.\n"
                self.assertEqual(bump.choose("0.7.0", log)[0], expected)

    def test_no_argument_uses_the_chosen_version(self):
        with patch.object(bump, "ROOT", self.root), patch.object(sys, "argv", ["bump.py"]), \
                redirect_stdout(io.StringIO()) as out:
            bump.main()
        self.assertIn("version 0.7.1 (patch", out.getvalue())
        self.assertIn("v0.7.1", (self.root / "rpi-thesis.cls").read_text(encoding="utf-8"))

    def test_no_argument_refuses_without_unreleased_or_pdf_line(self):
        for log in ("# Changes\n\n## 0.7.0\n", "# Changes\n\n## Unreleased\n\n- Fix.\n"):
            with self.subTest(log=log):
                (self.root / "CHANGELOG.md").write_text(log, encoding="utf-8")
                before = self.snapshot()
                with patch.object(bump, "ROOT", self.root), patch.object(sys, "argv", ["bump.py"]), \
                        self.assertRaisesRegex(SystemExit, "CHANGELOG.md"):
                    bump.main()
                self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
