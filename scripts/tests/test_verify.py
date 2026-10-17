#!/usr/bin/env python3
"""Tests for how verify.py reads a unit-test run. Stdlib only.

    python3 scripts/tests/test_verify.py
"""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import common
import verify

BROWSER = "no Chrome or Chromium found"


def log(skips=(), ran=10, failed=False):
    """A unittest -v log with the given skip reasons."""
    lines = [f"test_{n} (test_x.Case.test_{n}) ... ok" for n in range(ran - len(skips))]
    lines += [f"test_s{n} (test_x.Case.test_s{n}) ... skipped '{why}'" for n, why in enumerate(skips)]
    lines += ["", "-" * 70, f"Ran {ran} tests in 1.234s", ""]
    if failed:
        lines.append("FAILED (failures=1)")
    else:
        lines.append(f"OK (skipped={len(skips)})" if skips else "OK")
    return "\n".join(lines) + "\n"


class UnitTestResult(unittest.TestCase):
    def result(self, text, ok=True, strict=False, allow=False):
        return verify.unit_test_result(text, ok, strict=strict, allow_no_browser=allow)

    def test_no_skips(self):
        self.assertEqual(self.result(log(), strict=True), (True, "10 run, 0 skipped"))

    def test_local_skips_pass_and_are_not_counted_as_run(self):
        # Review: "10 unit test(s) passed, 3 skipped" counted skipped tests as passed.
        ok, note = self.result(log([BROWSER, BROWSER, "Pandoc not installed"]))
        self.assertTrue(ok)
        self.assertTrue(note.startswith("7 run, 3 skipped"), note)
        self.assertIn("Pandoc not installed", note)

    def test_strict_fails_on_any_skip(self):
        # Review: on CI and in release mode a skipped test still passed.
        ok, note = self.result(log(["Pandoc not installed"]), strict=True, allow=True)
        self.assertFalse(ok)
        self.assertIn("Pandoc not installed", note)

    def test_strict_fails_on_browser_skip_without_permission(self):
        ok, note = self.result(log([BROWSER]), strict=True)
        self.assertFalse(ok)
        self.assertIn("VERIFY_ALLOW_NO_BROWSER", note)

    def test_strict_allows_labelled_browser_skips(self):
        ok, note = self.result(log([BROWSER] * 3), strict=True, allow=True)
        self.assertEqual((ok, note), (True, "7 run, 3 skipped (no browser, allowed in CI)"))

    def test_strict_mixed_skips_fail(self):
        ok, _ = self.result(log([BROWSER, "no TeX Live"]), strict=True, allow=True)
        self.assertFalse(ok)

    def test_failed_run_fails(self):
        ok, note = self.result(log(failed=True), ok=False)
        self.assertFalse(ok)
        self.assertIn("10", note)

    def test_nothing_ran(self):
        self.assertFalse(self.result("Ran 0 tests in 0.000s\n\nOK\n")[0])


class Strict(unittest.TestCase):
    def test_ci_variables_turn_strict_on(self):
        for env in ({"CI": "true"}, {"GITHUB_ACTIONS": "true"}):
            with self.subTest(env=env), patch.dict(os.environ, env, clear=True):
                self.assertTrue(verify.strict_mode("full"))
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(verify.strict_mode("full"))
            self.assertTrue(verify.strict_mode("release"))


class FindChrome(unittest.TestCase):
    def test_chrome_set_to_a_missing_path_means_no_browser(self):
        # $CHROME names the browser to use; a wrong one must not fall back silently.
        with patch.dict(os.environ, {"CHROME": "/nonexistent/chrome"}):
            self.assertIsNone(common.find_chrome())


if __name__ == "__main__":
    unittest.main()
