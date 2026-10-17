#!/usr/bin/env python3
"""Tests for the OGE page watch in health.py, against a local web server. Stdlib only.

    python3 scripts/tests/test_health.py

Nothing leaves this computer: every watched page is served from 127.0.0.1, and
oge-watch.json is a temporary copy.
"""
import contextlib
import http.server
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import health  # noqa: E402

PAGE = """<!doctype html><html><body><nav><a href="/elsewhere">menu</a></nav>
<main><h1>Submit your thesis</h1><p>Read the manual.</p>
<a href="{manual}">Manual</a> <a href="https://example.org/checklist">Checklist</a>
<a href="#top">Top</a></main></body></html>"""
PAGES = {
    "/watch": PAGE.format(manual="/files/manual-old.pdf"),
    "/watch-relative-new": PAGE.format(manual="/files/manual-new.pdf"),
    "/no-main": "<html><body><p>Maintenance</p></body></html>",
}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/slow":
            time.sleep(1.0)
        body = PAGES.get(self.path, PAGES["/watch"] if self.path == "/slow" else None)
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class WatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.saved = health.WATCH_FILE, health.WATCHED, health.TIMEOUT
        health.WATCH_FILE = Path(self.folder.name) / "oge-watch.json"
        health.TIMEOUT = 0.3

    def tearDown(self):
        health.WATCH_FILE, health.WATCHED, health.TIMEOUT = self.saved
        self.folder.cleanup()

    def watch(self, *paths, update=False):
        health.WATCHED = [self.base + path for path in paths]
        with contextlib.redirect_stdout(io.StringIO()):
            return health.watch(update)

    def record(self, path="/watch"):
        report, problems = self.watch(path, update=True)
        self.assertEqual(problems, 0, report)
        return health.WATCH_FILE.read_bytes()

    def assert_update_keeps_baseline(self, failing):
        before = self.record()
        report, problems = self.watch("/watch", failing, update=True)
        self.assertGreater(problems, 0)
        self.assertEqual(health.WATCH_FILE.read_bytes(), before)
        self.assertIn("left unchanged", "\n".join(report))
        self.assertEqual([p.name for p in Path(self.folder.name).iterdir()], ["oge-watch.json"])

    def test_update_records_and_check_passes(self):
        self.record()
        self.assertEqual(self.watch("/watch")[1], 0)

    def test_update_timeout_keeps_baseline(self):
        self.assert_update_keeps_baseline("/slow")

    def test_update_404_keeps_baseline(self):
        self.assert_update_keeps_baseline("/gone")

    def test_update_malformed_keeps_baseline(self):
        self.assert_update_keeps_baseline("/no-main")

    def test_check_fails_without_baseline(self):
        report, problems = self.watch("/watch")
        self.assertEqual(problems, 1)
        self.assertIn("No recorded baseline", report[0])
        self.assertFalse(health.WATCH_FILE.exists())

    def test_check_fails_on_unreadable_baseline(self):
        health.WATCH_FILE.write_text("{not json", encoding="utf-8")
        report, problems = self.watch("/watch")
        self.assertEqual(problems, 1)
        self.assertIn("cannot be read", report[0])

    def test_check_fails_when_page_missing_from_baseline(self):
        self.record()
        data = json.loads(health.WATCH_FILE.read_text(encoding="utf-8"))
        health.WATCH_FILE.write_text(json.dumps({"https://example.org/other": data.popitem()[1]}), encoding="utf-8")
        self.assertEqual(self.watch("/watch")[1], 1)

    def test_malformed_nested_records_fail_and_can_be_repaired(self):
        for malformed in ({"links": None, "text": "invalid"},
                          {"links": "a link", "text": "0" * 64},
                          {"links": [None], "text": "0" * 64},
                          {"links": [], "text": None},
                          {"links": [], "text": "short hash"}):
            with self.subTest(record=malformed):
                self.record()
                health.WATCH_FILE.write_text(json.dumps({self.base + "/watch": malformed}), encoding="utf-8")
                report, problems = self.watch("/watch")
                self.assertEqual(problems, 1, report)
                self.assertIn("No recorded baseline", report[0])
                report, problems = self.watch("/watch", update=True)
                self.assertEqual(problems, 0, report)
                self.assertEqual(self.watch("/watch")[1], 0)

    def test_check_reports_malformed_page(self):
        self.record()
        health.WATCHED = [self.base + "/no-main"]
        report, problems = self.watch("/no-main")
        self.assertEqual(problems, 1)
        self.assertIn("could not be read", report[0])

    def test_relative_links_are_resolved_and_compared(self):
        self.record()
        stored = json.loads(health.WATCH_FILE.read_text(encoding="utf-8"))
        links = stored[self.base + "/watch"]["links"]
        self.assertIn(self.base + "/files/manual-old.pdf", links)
        self.assertNotIn(self.base + "/elsewhere", links)  # outside <main>
        self.assertFalse(any("#" in link for link in links))
        # Same text, only the relative manual link moves.
        stored[self.base + "/watch-relative-new"] = stored.pop(self.base + "/watch")
        health.WATCH_FILE.write_text(json.dumps(stored), encoding="utf-8")
        report, problems = self.watch("/watch-relative-new")
        self.assertEqual(problems, 1)
        joined = "\n".join(report)
        self.assertIn("new link: " + self.base + "/files/manual-new.pdf", joined)
        self.assertIn("removed link: " + self.base + "/files/manual-old.pdf", joined)


if __name__ == "__main__":
    unittest.main()
