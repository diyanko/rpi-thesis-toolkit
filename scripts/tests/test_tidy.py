#!/usr/bin/env python3
"""Tests for when tidy.py may remove a merged worktree. Stdlib only.

    python3 scripts/tests/test_tidy.py
"""
import os
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import tidy


def run(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


class Keep(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        run("git", "init", "-q", "-b", "main", cwd=self.repo)
        run("git", "config", "user.email", "t@example.com", cwd=self.repo)
        run("git", "config", "user.name", "t", cwd=self.repo)
        (self.repo / ".gitignore").write_text("_local/\nbuild/\ndist/\n.venv\n__pycache__/\n", encoding="utf-8")
        (self.repo / "a.txt").write_text("a\n", encoding="utf-8")
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
            (self.repo / name).write_text("x", encoding="utf-8")
        os.symlink(self.tmp.name, self.repo / ".venv")
        self.assertIsNone(self.reason())

    def test_ignored_notes_are_kept(self):
        (self.repo / "_local").mkdir()
        (self.repo / "_local" / "notes.md").write_text("mine", encoding="utf-8")
        self.assertIn("ignored", self.reason())

    def test_untracked_hidden_by_config_are_kept(self):
        run("git", "config", "status.showUntrackedFiles", "no", cwd=self.repo)
        (self.repo / "new.txt").write_text("new", encoding="utf-8")
        self.assertIsNotNone(self.reason())

    def test_modified_file_is_kept(self):
        (self.repo / "a.txt").write_text("b\n", encoding="utf-8")
        self.assertIn("uncommitted", self.reason())

    def prepare_rebase_merge(self, filename="a.txt"):
        run("git", "checkout", "-qb", "feature", cwd=self.repo)
        (self.repo / filename).write_text("feature\n", encoding="utf-8")
        run("git", "add", "--", filename, cwd=self.repo)
        run("git", "commit", "-qm", "feature", cwd=self.repo)
        tip = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        run("git", "checkout", "-q", "main", cwd=self.repo)
        run("git", "-c", "user.name=merger", "cherry-pick", tip, cwd=self.repo)
        run("git", "update-ref", "refs/remotes/origin/main", "HEAD", cwd=self.repo)
        return tip

    @contextlib.contextmanager
    def in_repo(self):
        original = tidy.git
        with patch.object(tidy, "git", side_effect=lambda *a, cwd=None: original(*a, cwd=cwd or str(self.repo))):
            yield

    def test_rebased_commits_and_final_files_are_recognized(self):
        tip = self.prepare_rebase_merge()
        with self.in_repo():
            self.assertEqual(tidy.rebased_into_main("feature"), tip)

    def test_later_edits_to_merged_files_keep_the_branch(self):
        for filename in ("a.txt", " leading[1].txt"):
            with self.subTest(filename=filename):
                if filename != "a.txt":
                    run("git", "branch", "-D", "feature", cwd=self.repo)
                self.prepare_rebase_merge(filename)
                (self.repo / filename).write_text("edited after merge\n", encoding="utf-8")
                run("git", "add", "--", filename, cwd=self.repo)
                run("git", "commit", "-qm", "later edit", cwd=self.repo)
                run("git", "update-ref", "refs/remotes/origin/main", "HEAD", cwd=self.repo)
                with self.in_repo():
                    self.assertIsNone(tidy.rebased_into_main("feature"))

    def test_unique_unmerged_commit_keeps_the_branch(self):
        self.prepare_rebase_merge()
        run("git", "checkout", "-q", "feature", cwd=self.repo)
        (self.repo / "research.txt").write_text("unmerged\n", encoding="utf-8")
        run("git", "add", ".", cwd=self.repo)
        run("git", "commit", "-qm", "more work", cwd=self.repo)
        run("git", "checkout", "-q", "main", cwd=self.repo)
        with self.in_repo():
            self.assertIsNone(tidy.rebased_into_main("feature"))

    def test_compare_and_delete_preserves_a_branch_moved_after_proof(self):
        tip = self.prepare_rebase_merge()
        run("git", "update-ref", "refs/heads/feature", "main", cwd=self.repo)
        with self.in_repo():
            self.assertNotEqual(tidy.delete_branch("feature", tip)[0], 0)
        run("git", "show-ref", "--verify", "refs/heads/feature", cwd=self.repo)

    def set_up_origin(self):
        remote = self.repo / "_local/origin.git"
        remote.parent.mkdir(exist_ok=True)
        run("git", "init", "--bare", "-q", str(remote), cwd=self.repo)
        run("git", "remote", "add", "origin", str(remote), cwd=self.repo)
        run("git", "push", "-qu", "origin", "main", cwd=self.repo)

    def test_current_worktree_with_trailing_space_in_name_stays(self):
        self.prepare_rebase_merge()
        self.set_up_origin()
        worktree = self.repo / "_local/current "
        run("git", "worktree", "add", "-q", str(worktree), "feature", cwd=self.repo)
        result = subprocess.run([sys.executable, "-B", str(Path(tidy.__file__)), "--apply"],
                                cwd=worktree, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(worktree.exists(), result.stdout)
        run("git", "show-ref", "--verify", "refs/heads/feature", cwd=self.repo)

    def test_apply_removes_only_safe_rebased_worktrees(self):
        self.prepare_rebase_merge()
        self.set_up_origin()
        worktree = self.repo / "_local/Thèse étudiante"
        run("git", "worktree", "add", "-q", str(worktree), "feature", cwd=self.repo)
        (worktree / "_local").mkdir()
        (worktree / "_local/notes.md").write_text("keep this\n", encoding="utf-8")
        with self.in_repo(), patch.object(sys, "argv", ["tidy.py", "--apply"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tidy.main(), 0)
        self.assertTrue((worktree / "_local/notes.md").exists())
        (worktree / "_local/notes.md").unlink()
        (worktree / "_local").rmdir()
        with self.in_repo(), patch.object(sys, "argv", ["tidy.py", "--apply"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tidy.main(), 0)
        self.assertFalse(worktree.exists())
        found = subprocess.run(["git", "show-ref", "--verify", "refs/heads/feature"],
                               cwd=self.repo, capture_output=True)
        self.assertNotEqual(found.returncode, 0)


if __name__ == "__main__":
    unittest.main()
