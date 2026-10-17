#!/usr/bin/env python3
"""Maintainer-only: clean up merged branches and worktrees after a merge.

Usage:
    python3 scripts/tidy.py            # dry run: print what would be removed
    python3 scripts/tidy.py --apply    # remove merged, clean worktrees and branches

Fetches origin, then lists every local branch and worktree. A branch whose
commits are all in origin/main is "merged"; with --apply its worktree (if
clean) and the branch are deleted and `git worktree prune` runs. Never touched:
main, the current worktree, anything with uncommitted, untracked, or ignored
files other than build outputs (build/, dist/, .venv, __pycache__), locked
worktrees, and unmerged branches (these are only listed).
Python standard library only.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BASE = "origin/main"
PROTECTED = {"main", "master"}


def git(*args: str, cwd: str | None = None) -> tuple[int, str]:
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return res.returncode, (res.stdout if res.returncode == 0 else res.stderr).strip()


def worktrees() -> list[dict]:
    _, out = git("worktree", "list", "--porcelain")
    items, cur = [], {}
    for line in out.splitlines() + [""]:
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
    _, top = git("rev-parse", "--show-toplevel")
    here = Path(top).resolve()
    _, current = git("branch", "--show-current")

    rows = []  # [kind, name, action, why]
    wt_branches = set()
    for i, wt in enumerate(worktrees()):
        path = Path(wt["worktree"])
        branch = str(wt.get("branch", "")).removeprefix("refs/heads/")
        if branch:
            wt_branches.add(branch)
        label = branch or "(detached)"
        if i == 0 or path.resolve() == here or branch in PROTECTED:
            rows.append(["worktree", label, "keep", "main or current"])
        elif "locked" in wt:
            rows.append(["worktree", label, "keep", "locked"])
        elif not branch or branch not in merged:
            rows.append(["worktree", label, "keep", "unmerged"])
        elif reason := keep_reason(str(path)):
            rows.append(["worktree", label, "keep", reason])
        else:
            rows.append(["worktree", label, "remove", f"merged into {BASE}"])
            if args.apply:
                code, err = git("worktree", "remove", str(path))
                if code:
                    rows[-1][2:] = ["keep", err.splitlines()[-1] if err else "failed"]

    removed = {r[1] for r in rows if r[0] == "worktree" and r[2] == "remove"}
    _, branches = git("branch", "--format=%(refname:short)")
    for b in branches.split():
        if b in PROTECTED or b == current:
            continue
        if b in wt_branches and b not in removed:
            continue  # already shown as a worktree row
        if b in merged:
            rows.append(["branch", b, "delete", f"merged into {BASE}"])
            if args.apply:
                code, err = git("branch", "-d", b)
                if code:
                    rows[-1][2:] = ["keep", err.splitlines()[-1] if err else "failed"]
        else:
            rows.append(["branch", b, "keep", "unmerged"])

    git("worktree", "prune", *([] if args.apply else ["--dry-run"]))

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
