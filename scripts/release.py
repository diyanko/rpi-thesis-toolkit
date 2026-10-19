#!/usr/bin/env python3
"""Release and deployment helpers for CI (.github/workflows/build.yml). Stdlib only.

    python3 scripts/release.py notes
        Print the GitHub release notes for the version in scripts/build_site.py.

    python3 scripts/release.py gate --stage build|deploy [--rollback]
        Decide whether this run may deploy the website. Writes deploy=true or
        deploy=false to $GITHUB_OUTPUT. Exits 0 with a notice when deploying is
        simply not this run's job, and 1 on a conflict or a network failure.
        Reads GITHUB_REF_TYPE, GITHUB_REF_NAME and GITHUB_SHA.
          main:  deploys only if this commit is still the tip of main, its
                 RELEASE_VERSION is the newest published release (by version
                 number), and the starter ZIP built in this run equals that
                 release's starter ZIP in every file except the offline guide
                 and cheat sheet (GUIDE_ONLY below). Guide-only changes
                 deploy; class or starter changes wait for a release.
          tag:   deploys only if the tag is RELEASE_TAG and no newer release
                 is published; --rollback (workflow_dispatch input) allows an
                 older tag on purpose. At --stage deploy the release must
                 exist, its tag must point at this commit, and its starter ZIP
                 must match the one built in this run.
          both:  the website must not already serve a newer commit: if the
                 live build.txt names another commit, GitHub's compare API
                 must show that commit is an ancestor of this one (unless
                 --rollback). A missing build.txt (first deploy) is allowed.
        The starter ZIP built in this run is read from --starter (default
        dist/rpi-thesis-starter-vX.Y.Z.zip).

    python3 scripts/release.py publish
        Create the GitHub pre-release for the tag, or resume one: checks the
        tag commit, compares existing assets by sha256 with dist/, uploads only
        missing ones, and fails on any difference. Needs gh and GH_TOKEN.

    python3 scripts/release.py live [--dist DIR]
        Wait (bounded) for the website to serve exactly this build, and check
        the release downloads by sha256. --dist also compares the release ZIPs
        with the ones built in this run (tag runs).

Repository and website addresses come from site/site.json. A maintainer
releases with scripts/bump.py X.Y.Z, verify, commit, and push the commit with
the tag vX.Y.Z (docs/project/maintenance.md, "Make a release").
"""

import argparse
import hashlib
import http.client
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
import zlib
from pathlib import Path

from build_site import OFFLINE_CHEATSHEET, RELEASE_VERSION
from common import ROOT, site_config

# Starter ZIP members the website may change without a release: the offline
# guide and the cheat sheet. Every other member (thesis files, class, build
# recipe, editor settings, README, LICENSE, ...) must be byte-identical to the
# released starter ZIP's before main deploys.
GUIDE_ONLY = ("guide/", "START-HERE.html", OFFLINE_CHEATSHEET)
# Build identity the published website carries (scripts/build_site.py --publish).
BUILD_FILE = "build.txt"          # lines "commit=<sha>" and "release=vX.Y.Z"
BUILD_META = "rpi-thesis-build"   # <meta name="rpi-thesis-build" content="<sha>"> in index.html
CLASS_DOWNLOAD = "downloads/rpi-thesis.cls"


class ReleaseError(Exception):
    """A conflict that a person must look at; the job fails."""


class NetworkError(Exception):
    """A network or service failure that persisted after retries; the job fails."""


class Config:
    def __init__(self, repository_url, site_url):
        self.repo = (repository_url or "").rstrip("/")
        match = re.fullmatch(r"https://github\.com/([\w.-]+)/([\w.-]+)", self.repo)
        if not match:
            raise ReleaseError("site/site.json: set repository_url to https://github.com/OWNER/REPO "
                               f"(found {repository_url!r})")
        if not (site_url or "").startswith("https://"):
            raise ReleaseError(f"site/site.json: set site_url to the website address (found {site_url!r})")
        self.slug = f"{match[1]}/{match[2]}"
        self.api = f"https://api.github.com/repos/{self.slug}"
        self.site = site_url.rstrip("/") + "/"

    @classmethod
    def load(cls, root=ROOT):
        data = site_config(root)
        return cls(data.get("repository_url"), data.get("site_url"))

    def asset_url(self, tag, name):
        return f"{self.repo}/releases/download/{tag}/{name}"


def asset_names(tag):
    return [f"rpi-thesis-starter-{tag}.zip", f"rpi-thesis-overleaf-{tag}.zip", "rpi-thesis.cls"]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def parse_version(text):
    """'v0.10.2' or '0.10.2' -> (0, 10, 2); anything else -> None."""
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", text or "")
    return tuple(int(part) for part in match.groups()) if match else None


def show(version):
    return "v%d.%d.%d" % version


class Net:
    """HTTP GET with retries. 404 gives None; 408, 429, 5xx, timeouts, DNS and
    connection errors are retried, then raise NetworkError; other errors raise
    at once. The token is sent only to api.github.com."""

    RETRY = {408, 429, 500, 502, 503, 504}

    def __init__(self, token=None, tries=4, delay=5.0, sleep=time.sleep, opener=urllib.request.urlopen):
        self.token, self.tries, self.delay, self.sleep, self.opener = token, tries, delay, sleep, opener

    def get(self, url):
        headers = {"User-Agent": "rpi-thesis-release-check"}
        if url.startswith("https://api.github.com/"):
            headers["Accept"] = "application/vnd.github+json"
            headers["X-GitHub-Api-Version"] = "2022-11-28"
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
        problem = "no attempt"
        for attempt in range(self.tries):
            if attempt:
                self.sleep(self.delay * 2 ** (attempt - 1))
            try:
                with self.opener(urllib.request.Request(url, headers=headers), timeout=30) as response:
                    return response.read()
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    return None
                if error.code not in self.RETRY:
                    raise NetworkError(f"{url}: HTTP {error.code}") from None
                problem = f"HTTP {error.code}"
            except (urllib.error.URLError, http.client.HTTPException, OSError) as error:
                problem = f"{type(error).__name__}: {error}"
        raise NetworkError(f"{url}: {problem} (after {self.tries} tries)")

    def json(self, url):
        body = self.get(url)
        return None if body is None else json.loads(body)


# GitHub reads ---------------------------------------------------------------

def releases(net, cfg):
    """Every release the token can see (drafts only with write access)."""
    found, page = [], 1
    while True:
        items = net.json(f"{cfg.api}/releases?per_page=100&page={page}")
        if items is None:
            raise NetworkError(f"{cfg.api}/releases: not found (check repository_url in site/site.json)")
        found += items
        if len(items) < 100:
            return found
        page += 1


def latest_release(net, cfg):
    """(version, release) of the highest published vX.Y.Z release, or None."""
    best = None
    for release in releases(net, cfg):
        version = parse_version(release.get("tag_name"))
        if version and not release.get("draft") and (best is None or version > best[0]):
            best = (version, release)
    return best


def find_release(net, cfg, tag):
    """The release (draft or not) for tag, or None. Two releases for one tag is a conflict."""
    matches = [r for r in releases(net, cfg) if r.get("tag_name") == tag]
    if len(matches) > 1:
        raise ReleaseError(f"{len(matches)} releases use tag {tag}; delete the extra drafts by hand")
    return matches[0] if matches else None


def main_tip(net, cfg):
    ref = net.json(f"{cfg.api}/git/ref/heads/main")
    if ref is None:
        raise NetworkError(f"{cfg.api}/git/ref/heads/main: not found")
    return ref["object"]["sha"]


def tag_commit(net, cfg, tag):
    """The commit a tag points at (following annotated tags), or None if no such tag."""
    ref = net.json(f"{cfg.api}/git/ref/tags/{tag}")
    if ref is None:
        return None
    target = ref["object"]
    for _ in range(5):
        if target["type"] == "commit":
            return target["sha"]
        if target["type"] != "tag":
            raise ReleaseError(f"tag {tag} points at a {target['type']}, not a commit")
        found = net.json(f"{cfg.api}/git/tags/{target['sha']}")
        if found is None:
            raise NetworkError(f"tag object {target['sha']} of {tag} not found")
        target = found["object"]
    raise ReleaseError(f"tag {tag}: too many nested tag objects")


def starter_members(zip_bytes, what):
    """{name: bytes} of a starter ZIP, without the offline guide and cheat sheet."""
    try:
        archive = zipfile.ZipFile(io.BytesIO(zip_bytes))
        return {name: archive.read(name) for name in archive.namelist()
                if not name.endswith("/") and not name.startswith(GUIDE_ONLY)}
    except (zipfile.BadZipFile, zlib.error, EOFError) as error:
        raise ReleaseError(f"{what} is not a readable ZIP ({error}); "
                           "the download or the file is corrupted") from None


def starter_differences(released, built, tag):
    """Members (guide and cheat sheet aside) that differ between the release's
    starter ZIP and the one built in this run, including added and removed ones."""
    old = starter_members(released, f"the starter ZIP of release {tag}")
    new = starter_members(built, "the starter ZIP built in this run")
    differ = [f"{name} (not in the release)" for name in sorted(new.keys() - old.keys())]
    differ += [f"{name} (removed since the release)" for name in sorted(old.keys() - new.keys())]
    differ += [name for name in sorted(old.keys() & new.keys()) if old[name] != new[name]]
    return differ


def live_commit(net, cfg):
    """The commit the website serves now (build.txt): a sha, "unreadable", or None
    if there is no build.txt. The query string asks the CDN for a fresh copy."""
    build = net.get(f"{cfg.site}{BUILD_FILE}?gate={int(time.time())}")
    if build is None:
        return None
    match = re.search(rb"^commit=([0-9a-f]{40})\s*$", build, re.M)
    return match[1].decode() if match else "unreadable"


def newer_live_site(net, cfg, sha, rollback, log=print):
    """None when this build may replace the live website, else a Decision not to
    deploy. Raises when the history needs a person to look."""
    live = live_commit(net, cfg)
    if live is None:
        log(f"::notice::{cfg.site}{BUILD_FILE} is missing; treating this as the first deploy")
        return None
    if live == "unreadable":
        if rollback:
            return None
        raise ReleaseError(f"{cfg.site}{BUILD_FILE} has no valid commit=<sha> line; "
                           "the live build cannot be ordered safely. Check the Pages deployment "
                           "by hand, or use an explicit release rollback to repair it.")
    if live == sha or rollback:
        return None
    found = net.json(f"{cfg.api}/compare/{sha}...{live}?per_page=1")
    if found is None:
        raise ReleaseError(f"the website serves build {live[:12]}, which GitHub does not know; "
                           "check the Pages deployments by hand before deploying")
    status = found.get("status")
    if status in ("behind", "identical"):
        return None
    if status == "ahead":
        return Decision(False, f"the website already serves {live[:12]}, which is newer than "
                        f"{sha[:12]}; an older build never replaces it. To roll back on purpose, "
                        "run the workflow on the release tag with rollback: true.")
    raise ReleaseError(f"the website serves {live[:12]}, which is not an ancestor of {sha[:12]} "
                       f"(compare status: {status}): history was rewritten, or a commit outside "
                       "main deployed. Deploy from the tip of main, or roll back on purpose.")


# Deployment gate ---------------------------------------------------------------

class Decision:
    def __init__(self, deploy, reason):
        self.deploy, self.reason = deploy, reason

    def __repr__(self):
        return f"Decision({self.deploy}, {self.reason!r})"


def decide(net, cfg, *, ref_type, ref_name, sha, stage, built=None, rollback=False,
           version=RELEASE_VERSION, log=print):
    """built: the starter ZIP built in this run (bytes); needed except at a tag's build stage."""
    decision = release_rules(net, cfg, ref_type=ref_type, ref_name=ref_name, sha=sha, stage=stage,
                             built=built, rollback=rollback, version=version)
    if decision.deploy:
        return newer_live_site(net, cfg, sha, rollback, log) or decision
    return decision


def compare_starter(net, cfg, tag, built):
    """Differences between the release's starter ZIP and built, or None if the release has none."""
    if built is None:
        raise ReleaseError(f"dist/{asset_names(tag)[0]} from this run is missing; run "
                           "scripts/package.py (the deploy job downloads the starter-zip artifact)")
    released = net.get(cfg.asset_url(tag, asset_names(tag)[0]))
    return None if released is None else starter_differences(released, built, tag)


def release_rules(net, cfg, *, ref_type, ref_name, sha, stage, built, rollback, version):
    mine, tag = parse_version(version), "v" + version
    if ref_type == "tag":
        if ref_name != tag:
            raise ReleaseError(f"tag {ref_name} does not match v{version} in scripts/build_site.py "
                               "(run scripts/bump.py before tagging)")
        latest = latest_release(net, cfg)
        if latest and latest[0] > mine and not rollback:
            return Decision(False, f"release {show(latest[0])} is newer than {tag}, so {tag} does not "
                            f"replace the website. To roll back on purpose, run the workflow on tag "
                            f"{tag} with rollback: true.")
        if stage == "build":
            return Decision(True, f"{tag} is the newest release" + (" (rollback)" if rollback else ""))
        release = net.json(f"{cfg.api}/releases/tags/{tag}")
        if release is None:
            raise ReleaseError(f"release {tag} is not published; the release job should have made it")
        commit = tag_commit(net, cfg, tag)
        if commit != sha:
            raise ReleaseError(f"tag {tag} now points at {commit}, but this run built {sha}; "
                               "run the workflow again for the tag as it is now")
        differ = compare_starter(net, cfg, tag, built)
        if differ is None:
            raise ReleaseError(f"release {tag} has no {asset_names(tag)[0]}")
        if differ:
            raise ReleaseError(f"release {tag}'s starter ZIP differs from the one built in this run: "
                               f"{', '.join(differ)}")
        return Decision(True, f"{tag} is published from this commit" + (" (rollback)" if rollback else ""))

    if rollback:
        raise ReleaseError("rollback: true works only when the workflow runs on a release tag vX.Y.Z")
    if ref_type != "branch" or ref_name != "main":
        return Decision(False, f"{ref_type} {ref_name} never deploys; only main and release tags do")
    latest = latest_release(net, cfg)
    if latest is None:
        return Decision(False, "no release is published yet; the first release tag deploys the website")
    if latest[0] != mine:
        if mine > latest[0]:
            return Decision(False, f"this commit links {tag}, which is not published yet; "
                            "its tag run deploys the website")
        return Decision(False, f"this commit links {tag}, but {show(latest[0])} is the newest release; "
                        "an older commit never replaces a newer release's website")
    tip = main_tip(net, cfg)
    if tip != sha:
        return Decision(False, f"main has moved on to {tip[:12]}; the run for that commit deploys")
    differ = compare_starter(net, cfg, tag, built)
    if differ is None:
        return Decision(False, f"release {tag} has no {asset_names(tag)[0]} yet; its tag run deploys")
    if differ:
        return Decision(False, f"the starter ZIP differs from release {tag}'s in {', '.join(differ)}; "
                        "release a new version to publish these changes")
    return Decision(True, f"main's starter ZIP matches release {tag}'s (guide and cheat sheet aside)")


# Publishing the release -----------------------------------------------------------

def run_gh(args):
    subprocess.run(["gh", *args], check=True)


def remote_digest(asset):
    """sha256 GitHub records for a release asset (every upload since mid-2025 has one)."""
    digest = asset.get("digest") or ""
    if not digest.startswith("sha256:"):
        raise ReleaseError(f"release asset {asset['name']} has no sha256 digest on GitHub; "
                           "compare it by hand, or release a new version")
    return digest[len("sha256:"):]


def publish(net, cfg, gh, *, tag, sha, files, notes_text, log=print, sleep=time.sleep):
    """Create the release for tag or resume one. files: {name: bytes} built here.
    gh(args) runs a gh command."""
    commit = tag_commit(net, cfg, tag)
    if commit is None:
        raise ReleaseError(f"tag {tag} is not on GitHub; push it first")
    if commit != sha:
        raise ReleaseError(f"tag {tag} points at {commit}, but this run built {sha}; "
                           "run the workflow again for the tag as it is now")
    wanted = {name: sha256(data) for name, data in files.items()}
    release = find_release(net, cfg, tag)
    with tempfile.TemporaryDirectory() as folder:
        paths = {}
        for name, data in files.items():
            paths[name] = Path(folder) / name
            paths[name].write_bytes(data)
        notes = Path(folder) / "notes.md"
        notes.write_text(notes_text, encoding="utf-8")
        if release is None:
            log(f"Creating pre-release {tag} with {', '.join(files)}")
            gh(["release", "create", tag, "--repo", cfg.slug, "--prerelease", "--title", tag,
                "--notes-file", str(notes), "--verify-tag", *[str(p) for p in paths.values()]])
            # GitHub's API can take a few seconds to list a release it just made.
            for wait in (0, 2, 4, 8, 16):
                sleep(wait)
                release = find_release(net, cfg, tag)
                if release is not None:
                    break
            else:
                raise ReleaseError(f"gh release create finished but release {tag} is not visible")
        else:
            log(f"Release {tag} exists (draft: {bool(release.get('draft'))}); checking its assets")
        present = set()
        for asset in release.get("assets", []):
            name = asset["name"]
            if name not in wanted:
                log(f"::warning::release {tag} has an extra asset {name}; left alone")
                continue
            if asset.get("state", "uploaded") != "uploaded":
                log(f"Removing incomplete upload of {name}")
                gh(["api", "-X", "DELETE", f"repos/{cfg.slug}/releases/assets/{asset['id']}"])
                continue
            remote = remote_digest(asset)
            if remote != wanted[name]:
                raise ReleaseError(f"release {tag} already has {name} with sha256 {remote}, but this "
                                   f"run built {wanted[name]}; a release never changes its files. "
                                   "Release a new version instead.")
            present.add(name)
        missing = [name for name in files if name not in present]
        if missing:
            log(f"Uploading {', '.join(missing)}")
            gh(["release", "upload", tag, "--repo", cfg.slug, *[str(paths[n]) for n in missing]])
        if release.get("draft"):
            log(f"Publishing draft {tag}")
            gh(["release", "edit", tag, "--repo", cfg.slug, "--draft=false", "--prerelease"])
    final = find_release(net, cfg, tag)
    if final is None or final.get("draft"):
        raise ReleaseError(f"release {tag} is still not published")
    uploaded = {a["name"]: a for a in final.get("assets", []) if a.get("state", "uploaded") == "uploaded"}
    for name, digest in wanted.items():
        if name not in uploaded:
            raise ReleaseError(f"release {tag} is missing {name} after upload")
        if remote_digest(uploaded[name]) != digest:
            raise ReleaseError(f"release {tag}: {name} on GitHub does not match the built file")
    log(f"OK: release {tag} at {sha[:12]} has {', '.join(wanted)} with matching sha256")


# Live check ----------------------------------------------------------------------

def site_identity(net, cfg):
    """(build.txt commit, index.html meta commit, index.html text, class bytes); None where absent."""
    build = net.get(cfg.site + BUILD_FILE)
    build_commit = None
    if build is not None:
        match = re.search(rb"^commit=([0-9a-f]{40})\s*$", build, re.M)
        build_commit = match[1].decode() if match else "unreadable"
    home = (net.get(cfg.site) or b"").decode("utf-8", "replace")
    match = re.search(r'<meta\s+name="%s"\s+content="([0-9a-f]{40})"' % BUILD_META, home)
    return build_commit, match[1] if match else None, home, net.get(cfg.site + CLASS_DOWNLOAD)


def check_site(observed, *, sha, tag, class_bytes):
    """Problems with one look at the website; [] when it serves exactly this build."""
    build_commit, meta_commit, home, live_class = observed
    problems = []
    ids = {"build.txt": build_commit, "index.html": meta_commit}
    for where, commit in ids.items():
        if commit != sha:
            problems.append(f"{where} is build {commit or 'missing'}, not {sha[:12]}")
    seen = {c for c in ids.values() if c}
    if len(seen) > 1:
        problems.append("mixed CDN revisions: " + ", ".join(f"{w}={c[:12]}" for w, c in ids.items() if c))
    if live_class is None:
        problems.append(f"{CLASS_DOWNLOAD} is missing")
    elif live_class != class_bytes:
        problems.append(f"{CLASS_DOWNLOAD} has sha256 {sha256(live_class)[:12]}, "
                        f"not {sha256(class_bytes)[:12]}")
    if f"rpi-thesis-starter-{tag}.zip" not in home:
        problems.append(f"home page does not link rpi-thesis-starter-{tag}.zip")
    return problems


def check_assets(net, cfg, *, tag, expected, tries=3, sleep=time.sleep):
    """Download every release asset; sha256 must equal GitHub's digest and expected[name]
    when given. A mismatch is retried (a corrupted transfer), then fails."""
    release = net.json(f"{cfg.api}/releases/tags/{tag}")
    if release is None:
        raise ReleaseError(f"release {tag} is not published")
    assets = {a["name"]: a for a in release.get("assets", [])}
    for name in asset_names(tag):
        if name not in assets:
            raise ReleaseError(f"release {tag} has no {name}")
        digest = (assets[name].get("digest") or "").removeprefix("sha256:") or None
        want = {d for d in (digest, expected.get(name)) if d}
        if len(want) > 1:
            raise ReleaseError(f"release {tag}: {name} on GitHub is {digest}, but this run built "
                               f"{expected[name]}")
        for attempt in range(tries):
            data = net.get(cfg.asset_url(tag, name))
            if data is not None and (not want or sha256(data) in want):
                break
            if attempt + 1 < tries:
                sleep(10)
        else:
            got = "missing" if data is None else sha256(data)
            raise ReleaseError(f"download of {name} from release {tag} is {got}, expected "
                               f"{' or '.join(want) or 'a file'} (corrupted download or changed asset)")


def live(net, cfg, *, sha, tag, class_bytes, expected, attempts=45,
         delay=20, sleep=time.sleep, log=print):
    """Wait for the website to serve this build (bounded), then check the release downloads."""
    problems = []
    for attempt in range(attempts):
        if attempt:
            sleep(delay)
        observed = site_identity(net, cfg)
        problems = check_site(observed, sha=sha, tag=tag, class_bytes=class_bytes)
        if not problems:
            break
    else:
        raise ReleaseError(f"after {attempts} looks the website still does not serve build "
                           f"{sha[:12]}: " + "; ".join(problems))
    check_assets(net, cfg, tag=tag, expected=expected, sleep=sleep)
    log(f"PASS: {cfg.site} serves build {sha[:12]} ({tag}); release downloads match by sha256")


# Command line ---------------------------------------------------------------------

def notes_text(cfg, version=RELEASE_VERSION, root=ROOT):
    tag = "v" + version
    starter, overleaf, _ = asset_names(tag)
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(version)} .*?\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not match:
        raise ReleaseError(f"CHANGELOG.md has no entry for {version}; run scripts/bump.py first.")
    header = (
        "Beta pre-release of the RPI Thesis Toolkit, an unofficial, community-made LaTeX "
        "starter and guide for RPI master's theses and doctoral dissertations.\n\n"
        f"**Guide:** {cfg.site}\n\n"
        f"**Downloads:** `{starter}` (thesis files, offline guide, cheat sheet), `{overleaf}` "
        "(thesis files only, for Overleaf), and `rpi-thesis.cls` (the class alone, to update "
        "an existing thesis). The RPI seal is a separate download from RPI.\n\n")
    return header + match[1].strip()


def env(name):
    value = os.environ.get(name, "")
    if not value:
        raise ReleaseError(f"{name} is not set (this command runs in GitHub Actions)")
    return value


def output(name, value):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=["notes", "gate", "publish", "live"])
    parser.add_argument("--stage", choices=["build", "deploy"], default="build")
    parser.add_argument("--rollback", action="store_true")
    parser.add_argument("--dist", type=Path)
    parser.add_argument("--starter", type=Path, help="gate: the starter ZIP built in this run")
    args = parser.parse_args(argv)
    tag = "v" + RELEASE_VERSION
    try:
        cfg = Config.load()
        net = Net(token=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
        if args.command == "notes":
            print(notes_text(cfg))
        elif args.command == "gate":
            ref_type = os.environ.get("GITHUB_REF_TYPE") or "branch"
            ref_name = os.environ.get("GITHUB_REF_NAME") or "main"
            sha = os.environ.get("GITHUB_SHA") or subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
            starter = args.starter or ROOT / "dist" / asset_names(tag)[0]
            built = starter.read_bytes() if starter.is_file() else None
            decision = decide(net, cfg, ref_type=ref_type, ref_name=ref_name, sha=sha,
                              stage=args.stage, built=built, rollback=args.rollback)
            output("deploy", "true" if decision.deploy else "false")
            print(("Deploying: " if decision.deploy else "::notice::Not deploying: ") + decision.reason)
        elif args.command == "publish":
            dist = args.dist or ROOT / "dist"
            files = {}
            for name in asset_names(tag):
                path = ROOT / name if name == "rpi-thesis.cls" else dist / name
                if not path.is_file():
                    raise ReleaseError(f"{path.relative_to(ROOT)} is missing; the build job makes it")
                files[name] = path.read_bytes()
            publish(net, cfg, run_gh, tag=tag, sha=env("GITHUB_SHA"), files=files,
                    notes_text=notes_text(cfg))
        elif args.command == "live":
            expected = {"rpi-thesis.cls": sha256((ROOT / "rpi-thesis.cls").read_bytes())}
            if args.dist:
                for name in asset_names(tag)[:2]:
                    expected[name] = sha256((args.dist / name).read_bytes())
            live(net, cfg, sha=env("GITHUB_SHA"), tag=tag,
                 class_bytes=(ROOT / "rpi-thesis.cls").read_bytes(), expected=expected)
    except (ReleaseError, NetworkError, subprocess.CalledProcessError) as error:
        sys.exit(f"::error::{error}")


if __name__ == "__main__":
    main()
