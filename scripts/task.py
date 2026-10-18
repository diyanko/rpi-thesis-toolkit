#!/usr/bin/env python3
"""Start and finish one issue: the standard development cycle (AGENTS.md).

    python3 scripts/task.py start N [--slug words]
    python3 scripts/task.py finish [--message "..."] [--no-review] [--accept-review]

start: makes branch issue-N-<slug> and a worktree at _local/wt/issue-N of the
main checkout, from a freshly fetched origin/main. The slug comes from the
issue title (gh) or --slug. Links .venv from the main checkout when present.

finish: run inside that worktree. Rebases on origin/main, runs verify.py quick,
and when site/ or docs/ changed runs the ui_check.py layout sweep (problems
stop here) and compares screenshots (Chrome only, informational), then
asks Codex for a review (when installed; P0 or P1 findings stop here unless
--accept-review or TASK_ACCEPT_REVIEW=1), commits anything uncommitted
(--message), pushes, opens the pull request, and turns on auto-merge.
Every step prints one line; the first failure stops with the fix.
Python standard library only; needs git, and gh for the pull request.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from common import find_chrome, main_checkout

# The one review prompt; AGENTS.md ("Development cycle") points here.
REVIEW_PROMPT = (
    "Review this branch's changes against origin/main (git diff origin/main, plus untracked "
    "files in git status) in this repo; read AGENTS.md. Report concrete defects with file:line "
    "and a failure scenario, most severe first. Label each P0 (breaks students or a release), "
    "P1 (wrong behavior), P2 (should fix before merge), or P3 (minor); say 'No findings' if none. "
    "End with exactly one last line: 'REVIEW-RESULT: BLOCK' if there is any P0 or P1 "
    "finding, otherwise 'REVIEW-RESULT: PASS' (P2 and P3 are reported, not blocking)."
)
# The review's own verdict line decides; a missing verdict blocks (fail closed).
VERDICT = re.compile(r"(?m)^\s*REVIEW-RESULT:\s*(PASS|BLOCK)\s*$")


def say(step, note):
    print(f"{step:<8} {note}", flush=True)


def stop(step, fix):
    print(f"FAIL     {step}: {fix}", flush=True)
    sys.exit(1)


def run(*args, cwd=None):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    except OSError as error:
        return subprocess.CompletedProcess(args, 127, "", str(error))


def git(*args, cwd=None):
    return run("git", *args, cwd=cwd)


def slugify(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return "-".join(words[:6])


def start(args):
    main = main_checkout(Path.cwd())
    if args.slug:
        slug = slugify(args.slug)
    elif shutil.which("gh"):
        found = run("gh", "issue", "view", str(args.number), "--json", "title", cwd=main)
        if found.returncode:
            stop("issue", f"gh could not read issue {args.number}; check the number or pass --slug words.")
        slug = slugify(json.loads(found.stdout)["title"])
    else:
        stop("issue", "gh is not installed; pass --slug words to name the branch.")
    if not slug:
        stop("issue", "the branch name came out empty; pass --slug words.")
    branch, path = f"issue-{args.number}-{slug}", main / "_local" / "wt" / f"issue-{args.number}"
    if git("rev-parse", "--verify", "--quiet", "refs/heads/" + branch, cwd=main).returncode == 0:
        stop("branch", f"{branch} already exists; continue in it or delete it with git branch -D.")
    if path.exists():
        stop("worktree", f"{path} already exists; continue there or remove it with git worktree remove.")
    if git("fetch", "origin", cwd=main).returncode:
        stop("fetch", "git fetch origin failed; check the network and try again.")
    say("fetch", "origin/main is up to date")
    made = git("worktree", "add", "--no-track", "-b", branch, str(path), "origin/main", cwd=main)
    if made.returncode:
        stop("worktree", (made.stderr.strip().splitlines() or ["git worktree add failed"])[-1])
    say("branch", f"{branch} at {path}")
    if (main / ".venv").exists():
        (path / ".venv").symlink_to(main / ".venv")
        say("venv", "linked .venv from the main checkout")
    say("next", f"cd {path}  (change, then: python3 scripts/task.py finish)")


def changed_files(top):
    names = git("diff", "--name-only", "origin/main", cwd=top).stdout.split()
    names += git("ls-files", "--others", "--exclude-standard", cwd=top).stdout.split()
    return sorted(set(names))


def finish(args):
    top = git("rev-parse", "--show-toplevel").stdout.strip()
    if not top:
        stop("branch", "run this inside the issue's worktree.")
    branch = git("branch", "--show-current", cwd=top).stdout.strip()
    if branch in ("", "main", "master"):
        stop("branch", "you are on main or a detached HEAD; start a branch with task.py start N.")
    dirty = bool(git("status", "--porcelain", "--untracked-files=all", cwd=top).stdout.strip())
    if dirty and not args.message:
        stop("commit", 'there are uncommitted changes; pass --message "type(scope): summary" or commit them.')
    say("branch", branch)
    if dirty:   # commit first, so the rebase never has to stash and restore edits
        git("add", "-A", cwd=top)
        made = git("commit", "-q", "-m", args.message, cwd=top)
        if made.returncode:
            stop("commit", (made.stderr.strip() or made.stdout.strip() or "git commit failed").splitlines()[-1])
        say("commit", args.message)

    if git("fetch", "origin", cwd=top).returncode:
        stop("fetch", "git fetch origin failed; check the network and try again.")
    # Never overwrite commits someone else pushed to this branch: the remote
    # branch, if any, must already be part of this one before we rebase.
    remote = git("rev-parse", "--verify", "-q", f"origin/{branch}", cwd=top).stdout.strip()
    pushed_mark = Path(git("rev-parse", "--git-dir", cwd=top).stdout.strip(), "task-last-push")
    if not pushed_mark.is_absolute():
        pushed_mark = Path(top) / pushed_mark
    ours = pushed_mark.read_text(encoding="utf-8").strip() if pushed_mark.exists() else ""
    if remote and remote != ours and git("merge-base", "--is-ancestor", remote, "HEAD", cwd=top).returncode:
        stop("fetch", f"origin/{branch} has commits this worktree lacks; "
             f"run git pull --rebase origin {branch}, then finish again.")
    if remote:   # accepted: a retry after this run's rebase recognizes it
        pushed_mark.write_text(remote, encoding="utf-8")
    if remote:   # accepted: a retry after this run's rebase recognizes it
        pushed_mark.write_text(remote, encoding="utf-8")
    rebased = git("rebase", "origin/main", cwd=top)
    if rebased.returncode:
        stop("rebase", "conflict with origin/main; fix the files, git add them, "
             "git rebase --continue, then run finish again.")
    say("rebase", "on origin/main")

    verify = subprocess.run([sys.executable, "scripts/verify.py", "quick"], cwd=top, text=True,   # CI runs the full suite
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    summary = ([line for line in verify.stdout.splitlines() if line.startswith("verify ")] or ["verify: no summary"])[-1]
    say("verify", summary)
    if verify.returncode:
        stop("verify", "fix what the summary names (logs in build/verify/), then run finish again.")

    files = changed_files(top)
    if any(name.startswith(("site/", "docs/")) for name in files):
        if not (Path(top) / "dist/site/index.html").exists():
            say("shots", "skipped: the site was not built (Pandoc not installed?)")
        elif find_chrome():
            sweep = run(sys.executable, "scripts/ui_check.py", cwd=top)   # layout problems stop finish
            if sweep.returncode:
                print(sweep.stdout.strip())
                stop("layout", "fix the layout problems ui_check.py lists, then run finish again.")
            shots = run(sys.executable, "scripts/ui_check.py", "--baseline", "compare", cwd=top)
            lines = shots.stdout.splitlines()
            for line in lines:
                if line.startswith("CHANGED "):
                    print(f"         {line}")
            say("shots", ([l for l in lines if l.startswith("baseline")] or
                          [(shots.stderr.strip() or "no comparison").splitlines()[-1]])[-1])
        else:
            say("shots", "skipped: no Chrome")

    if args.no_review or not shutil.which("codex"):
        say("review", "skipped" + ("" if args.no_review else ": codex not installed"))
    else:
        review = subprocess.run(["codex", "exec", "-s", "read-only", REVIEW_PROMPT], cwd=top, text=True,
                                stdin=subprocess.DEVNULL, capture_output=True)
        out = Path(top) / "build" / "review.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(review.stdout, encoding="utf-8")
        if review.returncode:
            stop("review", "codex failed; rerun, or pass --no-review and review the diff yourself.")
        print(findings(review.stdout))
        verdicts = VERDICT.findall(review.stdout)
        serious = not verdicts or verdicts[-1] != "PASS"
        accepted = args.accept_review or os.environ.get("TASK_ACCEPT_REVIEW") == "1"
        say("review", ("P0-P1 findings accepted" if accepted else "P0-P1 findings") if serious
            else "no blocking findings")
        if serious and not accepted:
            stop("review", "fix the findings in build/review.md and run finish again "
                 "(or --accept-review if each is noted).")

    subjects = git("log", "--reverse", "--format=%s", "origin/main..HEAD", cwd=top).stdout.splitlines()
    if not subjects:
        stop("commit", "this branch has no commits beyond origin/main; nothing to propose.")

    lease = f"--force-with-lease={branch}:{remote}" if remote else "--force-with-lease"
    pushed = git("push", lease, "-u", "origin", "HEAD", cwd=top)
    if pushed.returncode:
        stop("push", "git push failed; check your access to origin and try again.")
    pushed_mark.write_text(git("rev-parse", "HEAD", cwd=top).stdout.strip(), encoding="utf-8")
    say("push", f"origin/{branch}")

    if not shutil.which("gh"):
        stop("pr", "gh is not installed; open the pull request on GitHub with the template.")
    existing = run("gh", "pr", "view", "--json", "url", cwd=top)
    if existing.returncode == 0:
        url = json.loads(existing.stdout)["url"]
        say("pr", f"already open: {url}")
    else:
        issue = re.match(r"issue-(\d+)-", branch)
        body = "## What does this change?\n\n" + "\n".join(f"- {s}" for s in subjects)
        body += f"\n\n## Checks\n\n{summary}\n"
        if issue:
            body += f"\nCloses #{issue[1]}\n"
        made = run("gh", "pr", "create", "--title", subjects[0], "--body", body, "--base", "main", cwd=top)
        if made.returncode:
            stop("pr", "gh pr create failed; run gh auth status, then finish again.")
        url = made.stdout.strip().splitlines()[-1]
        say("pr", url)
    merged = run("gh", "pr", "merge", "--auto", "--rebase", cwd=top)
    if merged.returncode:
        stop("merge", "auto-merge could not be turned on; merge by hand once CI passes.")
    say("merge", "auto-merge on; it merges when CI passes")
    print(url)


def findings(text):
    """The findings part of a review: from the first line naming findings or a
    P0-P3 label, else the last 20 lines."""
    lines = text.strip().splitlines()
    for i, line in enumerate(lines):
        if re.search(r"(?i)findings|\bP[0-3]\b", line):
            return "\n".join(lines[i:])
    return "\n".join(lines[-20:])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    begin = sub.add_parser("start", help="make the branch and worktree for issue N")
    begin.add_argument("number", type=int, help="GitHub issue number")
    begin.add_argument("--slug", help="words for the branch name (needed without gh)")
    end = sub.add_parser("finish", help="verify, review, push, and open the pull request")
    end.add_argument("--message", "-m", help="commit message for uncommitted changes")
    end.add_argument("--no-review", action="store_true", help="skip the Codex review")
    end.add_argument("--accept-review", action="store_true", help="continue past P0-P1 review findings")
    args = parser.parse_args()
    (start if args.command == "start" else finish)(args)


if __name__ == "__main__":
    main()
