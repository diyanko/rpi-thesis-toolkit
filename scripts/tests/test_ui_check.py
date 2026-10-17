#!/usr/bin/env python3
"""Tests for how ui_check.py takes screenshots and saves a baseline. Stdlib only.

    python3 scripts/tests/test_ui_check.py
"""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import ui_check  # noqa: E402
from chrome import LocalServer  # noqa: E402


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

    def test_failed_screenshot_is_reported_and_preserves_old_baseline(self):
        for reply in (RuntimeError("Page.captureScreenshot: target closed"), b"", b"<html>"):
            with self.subTest(reply=reply):
                error = ui_check.take_shot(FakeBrowser(reply), "http://127.0.0.1:1", "index.html", 390,
                                           self.shots / "phone.png")
                self.assertIsNotNone(error)
                self.assertFalse((self.shots / "phone.png").exists())
                self.assertFalse(ui_check.save_baseline(self.shots, self.base, [error]))
                self.assertEqual((self.base / "old.png").read_bytes(), b"old")

    def test_good_screenshot_is_saved_at_the_asked_size(self):
        browser = FakeBrowser(b"\x89PNG fake")
        self.assertIsNone(ui_check.take_shot(browser, "http://127.0.0.1:1", ui_check.GALLERY, 390,
                                             self.shots / "gallery.png"))
        self.assertEqual((self.shots / "gallery.png").read_bytes(), b"\x89PNG fake")
        self.assertEqual(browser.size, (390, ui_check.GALLERY_HEIGHT))
        self.assertEqual(browser.opened, "http://127.0.0.1:1/" + ui_check.GALLERY)


class FakeBrowser:
    """Stands in for chrome.Chrome: screenshot() returns or raises `reply`."""

    def __init__(self, reply):
        self.reply, self.size, self.opened = reply, None, None

    def viewport(self, width, height, mobile=False):
        self.size = (width, height)

    def open(self, url):
        self.opened = url

    def evaluate(self, expression):
        return True

    def screenshot(self):
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


class Local404Preview(unittest.TestCase):
    def test_preview_uses_local_assets_and_keeps_external_links(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "site").mkdir()
            (root / "site/site.json").write_text(json.dumps({"site_url": "https://toolkit.example/base"}),
                                                 encoding="utf-8")
            built = root / "built"
            built.mkdir()
            (built / "404.html").write_text('<link href="https://toolkit.example/base/site.css">'
                                            '<a href="https://official.example/help">Help</a>', encoding="utf-8")
            with patch.object(ui_check, "ROOT", root), LocalServer(built, ui_check.routes(built, {})) as server:
                with urlopen(server.url + "/404.html", timeout=5) as response:
                    text = response.read().decode()
            self.assertIn('href="/site.css"', text)
            self.assertNotIn("https://toolkit.example/", text)
            self.assertIn('href="https://official.example/help"', text)


if __name__ == "__main__":
    unittest.main()
