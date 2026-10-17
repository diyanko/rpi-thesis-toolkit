#!/usr/bin/env python3
"""task.py start and finish in a scratch repository with fake gh and codex.
No network. Stdlib only.

    python3 scripts/tests/test_task.py
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TASK = Path(__file__).resolve().parents[1] / "task.py"

FAKE_GH = """#!/bin/sh
echo "$@" >> "$FAKE_LOG"
case "$1 $2" in
  "issue view") echo '{"title": "Fix the: Title page, seal!"}' ;;
  "pr view") exit 1 ;;
  "pr create") echo "https://github.com/example/repo/pull/7" ;;
  "pr merge") ;;
esac
"""
FAKE_CODEX = """#!/bin/sh
echo "codex $@" >> "$FAKE_LOG"
printf '%s\\n' "$FAKE_REVIEW"
"""
FAKE_VERIFY = "print('PASS  hygiene'); print('verify quick: hygiene passed in 1s (logs: build/verify/)')\n"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class Task(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.origin, self.main, self.bin = base / "origin.git", base / "main", base / "bin"
        self.log = base / "calls.log"
        self.bin.mkdir()
        for name, text in (("gh", FAKE_GH), ("codex", FAKE_CODEX)):
            (self.bin / name).write_text(text, encoding="utf-8")
            (self.bin / name).chmod(0o755)
        git("init", "-q", "--bare", "-b", "main", str(self.origin), cwd=base)
        git("init", "-q", "-b", "main", str(self.main), cwd=base)
        for key, value in (("user.email", "t@example.com"), ("user.name", "t")):
            git("config", key, value, cwd=self.main)
        (self.main / "scripts").mkdir()
        (self.main / "scripts/verify.py").write_text(FAKE_VERIFY, encoding="utf-8")
        (self.main / ".gitignore").write_text("_local/\nbuild/\n.venv\n", encoding="utf-8")
        git("add", ".", cwd=self.main)
        git("commit", "-qm", "init", cwd=self.main)
        git("remote", "add", "origin", str(self.origin), cwd=self.main)
        git("push", "-q", "origin", "main", cwd=self.main)
        (self.main / ".venv").mkdir()
        self.env = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}",
                        FAKE_LOG=str(self.log), CHROME="/nonexistent", FAKE_REVIEW="No findings.\nREVIEW-RESULT: PASS",
                        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
        self.env.pop("TASK_ACCEPT_REVIEW", None)

    def tearDown(self):
        self.tmp.cleanup()

    def task(self, *args, cwd=None, **env):
        return subprocess.run([sys.executable, "-B", str(TASK), *args], cwd=cwd or self.main,
                              env=dict(self.env, **env), capture_output=True, text=True)

    def started(self):
        result = self.task("start", "12")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return self.main / "_local/wt/issue-12"

    def test_start_names_branch_from_issue_and_links_venv(self):
        tree = self.started()
        self.assertEqual(git("branch", "--show-current", cwd=tree), "issue-12-fix-the-title-page-seal")
        self.assertTrue((tree / ".venv").is_symlink())
        upstream = subprocess.run(["git", "config", "branch.issue-12-fix-the-title-page-seal.merge"],
                                  cwd=tree, capture_output=True)
        self.assertNotEqual(upstream.returncode, 0)  # a plain push never targets main

    def test_start_refuses_existing_worktree(self):
        self.started()
        result = self.task("start", "12", "--slug", "other words")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stdout)

    def test_start_without_gh_needs_slug(self):
        result = self.task("start", "3", PATH="/usr/bin:/bin")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--slug", result.stdout)

    def test_finish_refuses_main(self):
        result = self.task("finish")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("main", result.stdout)

    def test_finish_needs_message_for_uncommitted_changes(self):
        tree = self.started()
        (tree / "new.md").write_text("x\n", encoding="utf-8")
        result = self.task("finish", cwd=tree)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--message", result.stdout)

    def test_serious_review_stops_before_push(self):
        tree = self.started()
        (tree / "new.md").write_text("x\n", encoding="utf-8")
        result = self.task("finish", "-m", "docs(guide): add a page", cwd=tree,
                           FAKE_REVIEW="Findings:\n[P1] new.md:1 breaks the build\nREVIEW-RESULT: BLOCK")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[P1] new.md:1", result.stdout)
        self.assertIn("P1", (tree / "build/review.md").read_text(encoding="utf-8"))
        # committed locally first (no stash), but never pushed or proposed
        self.assertEqual(git("ls-remote", "--heads", "origin", "issue-*", cwd=tree), "")
        self.assertNotIn("pr create", self.log.read_text(encoding="utf-8"))

    def test_finish_commits_pushes_and_opens_pr(self):
        tree = self.started()
        (tree / "new.md").write_text("x\n", encoding="utf-8")
        result = self.task("finish", "-m", "docs(guide): add a page", cwd=tree)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("verify quick: hygiene passed", result.stdout)
        self.assertTrue(result.stdout.strip().endswith("https://github.com/example/repo/pull/7"))
        git("--git-dir", str(self.origin), "rev-parse", "refs/heads/issue-12-fix-the-title-page-seal",
            cwd=self.main)
        calls = self.log.read_text(encoding="utf-8")
        self.assertIn("codex exec -s read-only", calls)
        self.assertIn("pr create --title docs(guide): add a page", calls)
        self.assertIn("Closes #12", calls)
        self.assertIn("pr merge --auto --rebase", calls)
        self.assertTrue(calls.isascii())

    def test_accept_review_and_no_review(self):
        tree = self.started()
        (tree / "a.md").write_text("x\n", encoding="utf-8")
        result = self.task("finish", "-m", "docs: a", cwd=tree, FAKE_REVIEW="[P2] a.md:1 typo",
                           TASK_ACCEPT_REVIEW="1")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.log.write_text("", encoding="utf-8")
        result = self.task("finish", "--no-review", cwd=tree)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("codex", self.log.read_text(encoding="utf-8"))

    def test_rebase_conflict_stops_with_a_fix(self):
        tree = self.started()
        for where, text in ((tree, "branch\n"), (self.main, "main\n")):
            (where / "notes.md").write_text(text, encoding="utf-8")
            git("add", "notes.md", cwd=where)
            git("commit", "-qm", "edit", cwd=where)
        git("push", "-q", "origin", "main", cwd=self.main)
        result = self.task("finish", "--no-review", cwd=tree)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("git rebase --continue", result.stdout)


if __name__ == "__main__":
    unittest.main()


class Severity(unittest.TestCase):
    def test_mentions_are_not_findings(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import task
        self.assertEqual(task.VERDICT.findall("No P0, P1, or P2 findings.\nREVIEW-RESULT: PASS"), ["PASS"])
        self.assertEqual(task.VERDICT.findall("1. **P1** broken\nREVIEW-RESULT: BLOCK"), ["BLOCK"])
        self.assertEqual(task.VERDICT.findall("[P2] a.md:1 typo"), [])   # no verdict: finish blocks

