#!/usr/bin/env python3
"""Tests for how ui_check.py saves a screenshot baseline. Stdlib only.

    python3 scripts/test_ui_check.py
"""
from pathlib import Path
import http.server
import json
import sys
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen
from unittest.mock import patch

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

    def test_failed_crop_is_reported_and_preserves_old_baseline(self):
        for crop_exit in (0, 1):  # even a tool claiming success must produce its file
            with self.subTest(crop_exit=crop_exit):
                def run(command, **kwargs):
                    if command[0] != "sips":
                        shot = next(arg.split("=", 1)[1] for arg in command if arg.startswith("--screenshot="))
                        Path(shot).write_bytes(b"screenshot")
                        return subprocess.CompletedProcess(command, 0)
                    return subprocess.CompletedProcess(command, crop_exit)
                with patch.object(ui_check.subprocess, "run", side_effect=run), \
                        patch.object(ui_check.shutil, "which", return_value="sips"):
                    error = ui_check.take_shot("chrome", 1234, "index.html", 390, False, self.shots / "phone.png")
                self.assertIn("crop failed", error)
                self.assertFalse(ui_check.save_baseline(self.shots, self.base, [error]))
                self.assertEqual((self.base / "old.png").read_bytes(), b"old")

    def test_nonzero_browser_exit_is_not_a_successful_screenshot(self):
        def run(command, **kwargs):
            shot = next(arg.split("=", 1)[1] for arg in command if arg.startswith("--screenshot="))
            Path(shot).write_bytes(b"partial screenshot")
            return subprocess.CompletedProcess(command, 7)
        with patch.object(ui_check.subprocess, "run", side_effect=run):
            error = ui_check.take_shot("chrome", 1234, "index.html", 1280, False, self.shots / "laptop.png")
        self.assertIn("Chrome screenshot failed", error)
        self.assertFalse(any(self.shots.iterdir()))


class Local404Preview(unittest.TestCase):
    def test_preview_uses_local_assets_and_keeps_external_links(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "site").mkdir()
            (root / "site/site.json").write_text(json.dumps({"site_url": "https://toolkit.example/base"}))
            built = root / "built"
            built.mkdir()
            (built / "404.html").write_text('<link href="https://toolkit.example/base/site.css">'
                                            '<a href="https://official.example/help">Help</a>')
            with patch.object(ui_check, "ROOT", root):
                server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), ui_check.make_handler(built, {}))
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    with urlopen(f"http://127.0.0.1:{server.server_port}/404.html", timeout=5) as response:
                        text = response.read().decode()
                    self.assertIn('href="/site.css"', text)
                    self.assertNotIn("https://toolkit.example/", text)
                    self.assertIn('href="https://official.example/help"', text)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
