#!/usr/bin/env python3
"""Tests for when tidy.py may remove a merged worktree. Stdlib only.

    python3 scripts/test_tidy.py
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tidy


def run(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


class Keep(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        run("git", "init", "-q", cwd=self.repo)
        run("git", "config", "user.email", "t@example.com", cwd=self.repo)
        run("git", "config", "user.name", "t", cwd=self.repo)
        (self.repo / ".gitignore").write_text("_local/\nbuild/\ndist/\n.venv\n__pycache__/\n")
        (self.repo / "a.txt").write_text("a\n")
        run("git", "add", ".", cwd=self.repo)
        run("git", "commit", "-qm", "init", cwd=self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def reason(self):
        return tidy.keep_reason(str(self.repo))

    def test_clean_worktree_may_go(self):
        self.assertIsNone(self.reason())

    def test_build_outputs_may_go(self):
        for name in ("build/main.pdf", "dist/x.zip", "scripts/__pycache__/a.pyc"):
            (self.repo / name).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / name).write_text("x")
        os.symlink(self.tmp.name, self.repo / ".venv")
        self.assertIsNone(self.reason())

    def test_ignored_notes_are_kept(self):
        (self.repo / "_local").mkdir()
        (self.repo / "_local" / "notes.md").write_text("mine")
        self.assertIn("ignored", self.reason())

    def test_untracked_hidden_by_config_are_kept(self):
        run("git", "config", "status.showUntrackedFiles", "no", cwd=self.repo)
        (self.repo / "new.txt").write_text("new")
        self.assertIsNotNone(self.reason())

    def test_modified_file_is_kept(self):
        (self.repo / "a.txt").write_text("b\n")
        self.assertIn("uncommitted", self.reason())


if __name__ == "__main__":
    unittest.main()
