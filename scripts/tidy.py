#!/usr/bin/env python3
"""Maintainer-only: clean up merged branches and worktrees after a merge.

Usage:
    python3 scripts/tidy.py            # dry run: print what would be removed
    python3 scripts/tidy.py --apply    # remove merged, clean worktrees and branches

Fetches origin, then lists every local branch and worktree. A branch whose
commits are all in origin/main is "merged". Rebase merges also count when
every unique commit has the same patch in main and the final contents and
modes of all changed paths still match main. A branch also counts when gh
reports a merged pull request whose head commit is exactly the branch tip
(without gh, or offline, only the git checks apply). With --apply its worktree
(if clean) and the branch are deleted and `git worktree prune` runs. Never touched:
main, the current worktree, anything with uncommitted, untracked, or ignored
files other than build outputs (build/, dist/, .venv, __pycache__), locked
worktrees, and unmerged branches (these are only listed).
It also lists entries of the main checkout's _local/design/ and _local/shots/
untouched for 14 days and deletes them with --apply; the screenshot baseline
(_local/shots/baseline) and the rest of _local/ are never touched.
Python standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE = "origin/main"
PROTECTED = {"main", "master"}


def git(*args: str, cwd: str | None = None) -> tuple[int, str]:
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    out = res.stdout if res.returncode == 0 else res.stderr
    return res.returncode, out if "-z" in args else out.strip()


def worktrees() -> list[dict]:
    code, out = git("worktree", "list", "--porcelain", "-z")
    if code:
        raise RuntimeError("cannot list worktrees: " + out)
    items, cur = [], {}
    for line in out.split("\0") + [""]:
        if not line:
            if cur:
                items.append(cur)
            cur = {}
            continue
        key, _, val = line.partition(" ")
        cur[key] = val or True
    return items


# Ignored paths a worktree may lose: rebuilt by the scripts. Anything else
# ignored (notes in _local/, a seal copy) keeps the worktree.
DISPOSABLE_TOP = {"build", "dist", ".venv"}
# Scratch folders in the main checkout's _local/ whose old entries may go.
SCRATCH = ("design", "shots")
KEEP_SCRATCH = {"shots/baseline"}
MAX_AGE_DAYS = 14


def newest_change(path: Path) -> float:
    """The latest modification time of path or anything inside it."""
    newest = path.lstat().st_mtime
    if path.is_dir() and not path.is_symlink():
        for folder, dirs, files in os.walk(path):
            for name in dirs + files:
                newest = max(newest, os.lstat(os.path.join(folder, name)).st_mtime)
    return newest


def stale_scratch(main: Path, now: float | None = None) -> list[Path]:
    """Entries of _local/design/ and _local/shots/ unchanged for MAX_AGE_DAYS."""
    cutoff = (now or time.time()) - MAX_AGE_DAYS * 86400
    found = []
    for folder in SCRATCH:
        base = main / "_local" / folder
        if not base.is_dir() or base.is_symlink():
            continue
        for entry in sorted(base.iterdir()):
            if f"{folder}/{entry.name}" not in KEEP_SCRATCH and newest_change(entry) < cutoff:
                found.append(entry)
    return found


def remove(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def rebased_into_main(branch: str) -> str | None:
    """The branch tip when both its patches and final changed files are in main.
    Any missing evidence keeps the branch, including merge/empty commits that
    git cherry does not account for, or files edited again after the merge."""
    code, tip = git("rev-parse", "--verify", "refs/heads/" + branch)
    if code:
        return None
    code, base = git("merge-base", BASE, tip)
    if code:
        return None
    code, commits = git("rev-list", f"{BASE}..{tip}")
    if code or not commits:
        return None
    code, patches = git("cherry", BASE, tip)
    lines = patches.splitlines()
    if code or not lines or any(not line.startswith("- ") for line in lines):
        return None
    if {line[2:] for line in lines} != set(commits.splitlines()):
        return None
    code, names = git("diff", "--name-only", "--no-renames", "-z", base, tip)
    paths = [name for name in names.split("\0") if name]
    if code or not paths:
        return None
    a, original = git("--literal-pathspecs", "ls-tree", "-z", tip, "--", *paths)
    b, integrated = git("--literal-pathspecs", "ls-tree", "-z", BASE, "--", *paths)
    return tip if not a and not b and original == integrated else None


def merged_pr(branch: str, tip: str) -> int | None:
    """The number of a merged pull request whose head commit is exactly tip.
    None when gh is missing, offline, or reports no such pull request."""
    if not shutil.which("gh"):
        return None
    try:
        res = subprocess.run(["gh", "pr", "list", "--head", branch, "--state", "merged",
                              "--json", "number,headRefOid"],
                             capture_output=True, text=True, timeout=30)
        prs = json.loads(res.stdout) if res.returncode == 0 else []
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None
    for pr in prs if isinstance(prs, list) else []:
        if isinstance(pr, dict) and pr.get("headRefOid") == tip and isinstance(pr.get("number"), int):
            return pr["number"]
    return None


def pr_merged(branch: str) -> tuple[str, int] | None:
    """(tip, PR number) when GitHub merged a pull request at the branch tip."""
    code, tip = git("rev-parse", "--verify", "refs/heads/" + branch)
    if code:
        return None
    number = merged_pr(branch, tip)
    return (tip, number) if number else None


def delete_branch(branch: str, rebased_tip: str | None = None) -> tuple[int, str]:
    if rebased_tip is None:
        return git("branch", "-d", branch)
    # Compare-and-delete: a commit added after the proof above must survive.
    code, message = git("update-ref", "-d", "refs/heads/" + branch, rebased_tip)
    if not code:
        git("config", "--remove-section", "branch." + branch)
    return code, message


def keep_reason(path: str) -> str | None:
    """Why the worktree at path must stay, or None when removing it loses nothing."""
    code, out = git("status", "--porcelain", "-z", "--ignored", "--untracked-files=all", cwd=path)
    if code:
        return "cannot read status"
    ignored = False
    for entry in out.split("\0"):
        if not entry:
            continue
        state, name = entry[:2], entry[3:]
        if state != "!!":
            return "uncommitted changes" if state != "??" else "untracked files"
        parts = Path(name.rstrip("/")).parts
        if parts and (parts[0] in DISPOSABLE_TOP or "__pycache__" in parts):
            continue
        ignored = True
    return "has ignored files" if ignored else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Remove merged branches and worktrees.")
    ap.add_argument("--apply", action="store_true", help="delete (default is a dry run)")
    args = ap.parse_args()

    code, out = git("fetch", "origin", "--prune")
    if code:
        print(f"tidy: git fetch failed: {out}", file=sys.stderr)
        return 1
    code, out = git("branch", "--merged", BASE, "--format=%(refname:short)")
    if code:
        print(f"tidy: cannot read {BASE}: {out}", file=sys.stderr)
        return 1
    merged = set(out.split())
    code, branches = git("branch", "--format=%(refname:short)")
    if code:
        print(f"tidy: cannot list local branches: {branches}", file=sys.stderr)
        return 1
    why = {b: f"merged into {BASE}" for b in merged}
    rebased = {}  # branch -> tip it may be deleted at (compare-and-delete)
    for branch in branches.split():
        if branch not in merged and branch not in PROTECTED:
            if tip := rebased_into_main(branch):
                rebased[branch] = tip
                merged.add(branch)
                why[branch] = f"merged into {BASE}"
            elif found := pr_merged(branch):
                rebased[branch], number = found
                merged.add(branch)
                why[branch] = f"PR #{number} merged"
    _, top = git("rev-parse", "--show-toplevel")
    here = Path(top).resolve()
    _, current = git("branch", "--show-current")

    rows = []  # [kind, name, action, why]
    wt_branches = set()
    trees = worktrees()
    for i, wt in enumerate(trees):
        path = Path(wt["worktree"])
        branch = str(wt.get("branch", "")).removeprefix("refs/heads/")
        if branch:
            wt_branches.add(branch)
        label = branch or "(detached)"
        if i == 0 or path.resolve() == here or branch in PROTECTED or branch == current:
            rows.append(["worktree", label, "keep", "main or current"])
        elif "locked" in wt:
            rows.append(["worktree", label, "keep", "locked"])
        elif not branch or branch not in merged:
            rows.append(["worktree", label, "keep", "unmerged"])
        elif reason := keep_reason(str(path)):
            rows.append(["worktree", label, "keep", reason])
        else:
            rows.append(["worktree", label, "remove", why[branch]])
            if args.apply:
                code, err = git("worktree", "remove", str(path))
                if code:
                    rows[-1][2:] = ["keep", err.splitlines()[-1] if err else "failed"]

    removed = {r[1] for r in rows if r[0] == "worktree" and r[2] == "remove"}
    for b in branches.split():
        if b in PROTECTED or b == current:
            continue
        if b in wt_branches and b not in removed:
            continue  # already shown as a worktree row
        if b in merged:
            rows.append(["branch", b, "delete", why[b]])
            if args.apply:
                code, err = delete_branch(b, rebased.get(b))
                if code:
                    rows[-1][2:] = ["keep", err.splitlines()[-1] if err else "failed"]
        else:
            rows.append(["branch", b, "keep", "unmerged"])

    git("worktree", "prune", *([] if args.apply else ["--dry-run"]))

    main_tree = Path(trees[0]["worktree"])
    for entry in stale_scratch(main_tree):
        rows.append(["local", str(entry.relative_to(main_tree)), "delete", f"untouched {MAX_AGE_DAYS}+ days"])
        if args.apply:
            try:
                remove(entry)
            except OSError as error:
                rows[-1][2:] = ["keep", str(error)]

    w = max([len(r[1]) for r in rows] + [4])
    print(f"{'kind':<9} {'name':<{w}}  {'action':<7} why")
    for kind, name, action, why in rows:
        print(f"{kind:<9} {name:<{w}}  {action:<7} {why}")
    todo = sum(1 for r in rows if r[2] in ("remove", "delete"))
    verb = "removed" if args.apply else "would remove"
    note = "" if args.apply else " (dry run; use --apply)"
    print(f"tidy: {verb} {todo}, kept {len(rows) - todo}{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
