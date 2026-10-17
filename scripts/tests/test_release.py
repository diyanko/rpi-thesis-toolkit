#!/usr/bin/env python3
"""Tests for scripts/release.py against a fake GitHub and website. Stdlib only.

    python3 -m unittest discover -s scripts/tests
"""

import hashlib
import io
import json
import subprocess
import tempfile
import unittest
import urllib.error
import zipfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import release
from release import Config, Net, NetworkError, ReleaseError

CFG = Config("https://github.com/owner/toolkit", "https://owner.example.io/toolkit")
OLD, NEW, NEWER = "1" * 40, "2" * 40, "3" * 40
# Starter ZIP members outside the offline guide (a sample, not package.py's list).
STARTER_TEXT = {name: f"% {name} as released\n" for name in (
    "rpi-thesis.cls", "main.tex", "metadata.tex", "preamble.tex", "latexmkrc", "scripts/build.py",
    ".vscode/settings.json", "README.md", "LICENSE.md")}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def starter_zip(files, guide="<p>guide</p>"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, text in files.items():
            archive.writestr(name, text)
        archive.writestr("guide/index.html", guide)
        archive.writestr("START-HERE.html", guide)
        archive.writestr("rpi-thesis-cheatsheet.pdf", guide)
    return buffer.getvalue()


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class FakeWorld:
    """GitHub API, release downloads, and the website, behind Net's opener."""

    def __init__(self):
        self.releases = []          # release dicts in creation order
        self.downloads = {}         # (tag, name) -> bytes
        self.refs = {"heads/main": NEW}
        self.site = {}              # path -> bytes
        self.failures = {}          # url -> list of exceptions raised before success
        self.site_timeline = []     # list of site dicts served on successive home-page looks
        self.next_id = 1
        self.requests = []
        self.history = [OLD, NEW, NEWER]  # main's commits, oldest first
        self.compare = {}           # (base, head) -> status, overriding history

    # -- state helpers
    def add_release(self, tag, commit, files=None, draft=False, digests=True):
        self.refs[f"tags/{tag}"] = commit
        assets = []
        for name, data in (files or {}).items():
            assets.append(self.asset(tag, name, data, digests))
        rel = {"tag_name": tag, "draft": draft, "prerelease": True, "assets": assets}
        self.releases.append(rel)
        return rel

    def asset(self, tag, name, data, digests=True, state="uploaded"):
        self.downloads[(tag, name)] = data
        self.next_id += 1
        entry = {"id": self.next_id, "name": name, "state": state}
        if digests:
            entry["digest"] = "sha256:" + digest(data)
        return entry

    def standard_release(self, tag, commit, root_files=STARTER_TEXT, **kw):
        files = {f"rpi-thesis-starter-{tag}.zip": starter_zip(root_files),
                 f"rpi-thesis-overleaf-{tag}.zip": b"overleaf " + tag.encode(),
                 "rpi-thesis.cls": root_files["rpi-thesis.cls"].encode()}
        return self.add_release(tag, commit, files, **kw), files

    def find(self, tag):
        return next((r for r in self.releases if r["tag_name"] == tag), None)

    # -- HTTP
    def opener(self, request, timeout=None):
        url = request.full_url
        self.requests.append(url)
        pending = self.failures.get(url) or self.failures.get(url.split("?")[0])
        if pending:
            raise pending.pop(0)
        body = self.route(url)
        if body is None:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        return Response(body)

    def route(self, url):
        api = CFG.api + "/"
        if url.startswith(api):
            path = url[len(api):]
            if path.startswith("compare/"):
                base, head = path[len("compare/"):].split("?")[0].split("...")
                status = self.compare.get((base, head))
                if status is None and base in self.history and head in self.history:
                    order = self.history.index(head) - self.history.index(base)
                    status = "ahead" if order > 0 else "behind" if order < 0 else "identical"
                return json.dumps({"status": status}).encode() if status else None
            if path.startswith("releases?"):
                if getattr(self, "hide_listing", 0):  # GitHub lists a new release late
                    self.hide_listing -= 1
                    return b"[]"
                page = int(path.rsplit("page=", 1)[1])
                return json.dumps(self.releases[(page - 1) * 100:page * 100]).encode() if page else b"[]"
            if path.startswith("releases/tags/"):
                rel = self.find(path[len("releases/tags/"):])
                return json.dumps(rel).encode() if rel and not rel["draft"] else None
            if path.startswith("git/ref/"):
                sha = self.refs.get(path[len("git/ref/"):])
                return json.dumps({"object": {"type": "commit", "sha": sha}}).encode() if sha else None
            return None
        prefix = CFG.repo + "/releases/download/"
        if url.startswith(prefix):
            tag, name = url[len(prefix):].split("/", 1)
            rel = self.find(tag)
            return self.downloads.get((tag, name)) if rel and not rel["draft"] else None
        if url.startswith(CFG.site):
            path = url[len(CFG.site):].split("?")[0]
            if path == "" and self.site_timeline:
                self.site = self.site_timeline.pop(0)
            return self.site.get(path)
        return None

    def net(self, tries=4):
        return Net(tries=tries, delay=0, sleep=lambda s: None, opener=self.opener)

    # -- gh
    def gh(self, fail_on=None):
        calls = []

        def run(args):
            calls.append(args)
            verb = args[0] if args[0] == "api" else args[1]
            tag = args[2] if args[0] == "release" else None
            files = [Path(a) for i, a in enumerate(args)
                     if a.startswith("/") and args[i - 1] != "--notes-file"]
            if verb == "create":
                rel = self.add_release(tag, self.refs[f"tags/{tag}"], draft=True)
                for path in files:  # gh uploads to a draft, then publishes
                    if fail_on == "create-upload" and path.name == "rpi-thesis.cls":
                        raise subprocess.CalledProcessError(1, "gh")
                    rel["assets"].append(self.asset(tag, path.name, path.read_bytes()))
                if fail_on == "create-publish":
                    raise subprocess.CalledProcessError(1, "gh")
                rel["draft"] = False
            elif verb == "upload":
                rel = self.find(tag)
                for path in files:
                    if any(a["name"] == path.name for a in rel["assets"]):
                        raise AssertionError("upload would clobber " + path.name)
                    rel["assets"].append(self.asset(tag, path.name, path.read_bytes()))
                if fail_on == "upload":
                    raise subprocess.CalledProcessError(1, "gh")
            elif verb == "edit":
                self.find(tag)["draft"] = False
            elif verb == "api":
                asset_id = int(args[-1].rsplit("/", 1)[1])
                for rel in self.releases:
                    rel["assets"] = [a for a in rel["assets"] if a["id"] != asset_id]
            else:
                raise AssertionError(args)
        run.calls = calls
        return run


class Base(unittest.TestCase):
    def setUp(self):
        self.built = dict(STARTER_TEXT)   # starter ZIP members built in this run
        self.world = FakeWorld()
        self.logs = []

    def live_site(self, commit):
        self.world.site["build.txt"] = f"commit={commit}\nrelease=v0.6.0\n".encode()

    def decide(self, ref_type="branch", ref_name="main", sha=NEW, stage="build", rollback=False,
               version="0.6.0", built=True, guide="<p>guide</p>"):
        built = starter_zip(self.built, guide) if built else None
        return release.decide(self.world.net(), CFG, ref_type=ref_type, ref_name=ref_name, sha=sha,
                              stage=stage, built=built, rollback=rollback, version=version,
                              log=self.logs.append)


class Versions(unittest.TestCase):
    def test_numeric_order(self):
        self.assertGreater(release.parse_version("v0.10.0"), release.parse_version("v0.9.0"))
        self.assertGreater(release.parse_version("v1.2.10"), release.parse_version("v1.2.9"))
        self.assertIsNone(release.parse_version("v1.2"))
        self.assertIsNone(release.parse_version("latest"))

    def test_latest_by_version_not_creation_order(self):
        world = FakeWorld()
        for tag in ("v0.10.0", "v0.9.0", "v0.9.10", "v0.9.9"):
            world.add_release(tag, OLD)
        world.add_release("v0.11.0", OLD, draft=True)  # drafts are not published
        self.assertEqual(release.latest_release(world.net(), CFG)[0], (0, 10, 0))

    def test_pagination(self):
        world = FakeWorld()
        for minor in range(150):
            world.add_release(f"v0.{minor}.0", OLD)
        self.assertEqual(release.latest_release(world.net(), CFG)[0], (0, 149, 0))


class ConfigTests(unittest.TestCase):
    def test_reads_site_json(self):
        cfg = Config.load()
        self.assertTrue(cfg.repo.startswith("https://github.com/"))
        self.assertTrue(cfg.site.endswith("/"))
        self.assertEqual(cfg.api, "https://api.github.com/repos/" + cfg.slug)

    def test_rejects_bad_repository(self):
        with self.assertRaises(ReleaseError):
            Config("", "https://example.org")
        with self.assertRaises(ReleaseError):
            Config("https://github.com/owner/toolkit", "")


class MainGate(Base):
    def setUp(self):
        super().setUp()
        self.world.standard_release("v0.6.0", OLD)

    def test_guide_only_change_deploys(self):
        decision = self.decide()
        self.assertTrue(decision.deploy, decision)
        self.assertTrue(self.decide(stage="deploy").deploy)

    def test_delayed_build_after_newer_commit(self):
        self.world.refs["heads/main"] = NEWER
        decision = self.decide(sha=NEW)
        self.assertFalse(decision.deploy)
        self.assertIn("moved on", decision.reason)

    def test_delayed_build_after_newer_release(self):
        self.world.standard_release("v0.6.1", NEWER)
        decision = self.decide(sha=NEW, version="0.6.0")
        self.assertFalse(decision.deploy)
        self.assertIn("v0.6.1 is the newest release", decision.reason)

    def test_version_not_yet_released(self):
        decision = self.decide(version="0.7.0")
        self.assertFalse(decision.deploy)
        self.assertIn("not published yet", decision.reason)

    def test_ordering_v0_9_vs_v0_10(self):
        self.world.standard_release("v0.10.0", NEWER)
        self.world.standard_release("v0.9.0", OLD)  # created later, still older
        self.assertFalse(self.decide(version="0.9.0").deploy)
        self.assertTrue(self.decide(version="0.10.0").deploy)

    def test_interface_change_waits_for_release(self):
        self.built["metadata.tex"] = "% a new key\n"
        decision = self.decide()
        self.assertFalse(decision.deploy)
        self.assertIn("metadata.tex", decision.reason)

    def test_class_change_waits_for_release(self):
        self.built["rpi-thesis.cls"] = "% changed\n"
        self.assertIn("rpi-thesis.cls", self.decide().reason)

    def test_editor_settings_change_waits_for_release(self):
        self.built[".vscode/settings.json"] = '{"latex-workshop.latex.recipes": []}\n'
        decision = self.decide()
        self.assertFalse(decision.deploy, decision)
        self.assertIn(".vscode/settings.json", decision.reason)

    def test_added_starter_file_waits_for_release(self):
        self.built["chapters/04-new.tex"] = "% new\n"
        self.assertIn("chapters/04-new.tex (not in the release)", self.decide().reason)

    def test_removed_starter_file_waits_for_release(self):
        del self.built["latexmkrc"]
        self.assertIn("latexmkrc (removed since the release)", self.decide().reason)

    def test_guide_and_cheat_sheet_changes_deploy(self):
        self.assertTrue(self.decide(guide="<p>a fixed guide page</p>").deploy)

    def test_missing_built_starter_fails(self):
        with self.assertRaisesRegex(ReleaseError, "package.py"):
            self.decide(built=False)

    def test_missing_build_txt_is_first_deploy(self):
        self.assertTrue(self.decide().deploy)
        self.assertIn("first deploy", self.logs[-1])

    def test_unreadable_build_txt_fails_closed(self):
        self.world.site["build.txt"] = b"garbage\n"
        with self.assertRaisesRegex(ReleaseError, "cannot be ordered safely"):
            self.decide()

    def test_live_site_older_deploys(self):
        self.live_site(OLD)
        self.assertTrue(self.decide(stage="deploy").deploy)

    def test_live_site_newer_is_not_replaced(self):
        self.live_site(NEWER)  # main was reset under a deployed commit
        decision = self.decide(stage="deploy")
        self.assertFalse(decision.deploy)
        self.assertIn("newer than", decision.reason)

    def test_live_site_diverged_fails(self):
        side = "4" * 40
        self.live_site(side)
        self.world.compare[(NEW, side)] = "diverged"
        with self.assertRaisesRegex(ReleaseError, "not an ancestor"):
            self.decide(stage="deploy")

    def test_live_site_unknown_commit_fails(self):
        self.live_site("5" * 40)
        with self.assertRaisesRegex(ReleaseError, "does not know"):
            self.decide(stage="deploy")

    def test_build_txt_outage_fails(self):
        self.world.failures[CFG.site + "build.txt"] = [urllib.error.URLError("dns")] * 4
        with self.assertRaises(NetworkError):
            self.decide(stage="deploy")

    def test_no_release_yet(self):
        self.world.releases.clear()
        self.assertFalse(self.decide().deploy)

    def test_rollback_on_main_is_refused(self):
        with self.assertRaises(ReleaseError):
            self.decide(rollback=True)

    def test_other_branch_never_deploys(self):
        self.assertFalse(self.decide(ref_name="feature").deploy)

    def test_corrupted_starter_zip_fails(self):
        self.world.downloads[("v0.6.0", "rpi-thesis-starter-v0.6.0.zip")] = b"PK\x03\x04 truncated"
        with self.assertRaisesRegex(ReleaseError, "corrupted"):
            self.decide()

    def test_transient_errors_are_retried(self):
        url = CFG.api + "/git/ref/heads/main"
        self.world.failures[url] = [urllib.error.HTTPError(url, 503, "busy", {}, None),
                                    urllib.error.URLError("temporary failure in name resolution")]
        self.assertTrue(self.decide().deploy)

    def test_persistent_outage_fails_instead_of_skipping(self):
        url = CFG.api + "/releases?per_page=100&page=1"
        self.world.failures[url] = [urllib.error.HTTPError(url, 502, "bad gateway", {}, None)] * 4
        with self.assertRaises(NetworkError):
            self.decide()

    def test_timeout_fails_after_retries(self):
        url = CFG.repo + "/releases/download/v0.6.0/rpi-thesis-starter-v0.6.0.zip"
        self.world.failures[url] = [TimeoutError("timed out")] * 4
        with self.assertRaises(NetworkError):
            self.decide()

    def test_forbidden_is_not_retried(self):
        url = CFG.api + "/git/ref/heads/main"
        self.world.failures[url] = [urllib.error.HTTPError(url, 403, "rate limited", {}, None)]
        with self.assertRaisesRegex(NetworkError, "403"):
            self.decide()


class TagGate(Base):
    def test_new_tag_build_stage_before_release(self):
        self.world.standard_release("v0.5.0", OLD)
        self.assertTrue(self.decide("tag", "v0.6.0", stage="build").deploy)

    def test_tag_must_match_release_version(self):
        with self.assertRaisesRegex(ReleaseError, "bump.py"):
            self.decide("tag", "v0.6.1", stage="build", version="0.6.0")

    def test_deploy_stage_after_release(self):
        self.world.standard_release("v0.6.0", NEW)
        self.assertTrue(self.decide("tag", "v0.6.0", stage="deploy").deploy)

    def test_reversed_completion(self):
        self.world.standard_release("v0.6.1", NEWER)   # finished first
        self.world.standard_release("v0.6.0", NEW)
        for stage in ("build", "deploy"):
            decision = self.decide("tag", "v0.6.0", stage=stage)
            self.assertFalse(decision.deploy)
            self.assertIn("rollback: true", decision.reason)

    def test_historical_tag_rerun(self):
        self.world.standard_release("v0.5.0", OLD)
        self.world.standard_release("v0.10.0", NEWER)
        self.assertFalse(self.decide("tag", "v0.5.0", sha=OLD, stage="deploy", version="0.5.0").deploy)

    def test_explicit_rollback(self):
        self.world.standard_release("v0.5.0", OLD)
        self.world.standard_release("v0.6.0", NEWER)
        decision = self.decide("tag", "v0.5.0", sha=OLD, stage="deploy", rollback=True, version="0.5.0")
        self.assertTrue(decision.deploy)
        self.assertIn("rollback", decision.reason)

    def test_explicit_rollback_can_repair_unreadable_build_identity(self):
        self.world.standard_release("v0.5.0", OLD)
        self.world.standard_release("v0.6.0", NEWER)
        self.world.site["build.txt"] = b"commit=truncated\n"
        self.assertTrue(self.decide("tag", "v0.5.0", sha=OLD, stage="deploy",
                                    rollback=True, version="0.5.0").deploy)

    def test_moved_tag_fails(self):
        self.world.standard_release("v0.6.0", NEWER)
        with self.assertRaisesRegex(ReleaseError, "now points at"):
            self.decide("tag", "v0.6.0", sha=NEW, stage="deploy")

    def test_release_missing_at_deploy_fails(self):
        with self.assertRaises(ReleaseError):
            self.decide("tag", "v0.6.0", stage="deploy")

    def test_release_starter_differs_fails(self):
        self.world.standard_release("v0.6.0", NEW, root_files=dict(STARTER_TEXT, **{"main.tex": "x"}))
        with self.assertRaisesRegex(ReleaseError, "main.tex"):
            self.decide("tag", "v0.6.0", stage="deploy")

    def test_release_starter_differs_from_built_in_readme_fails(self):
        self.world.standard_release("v0.6.0", NEW)
        self.built["README.md"] = "generated differently\n"
        with self.assertRaisesRegex(ReleaseError, "README.md"):
            self.decide("tag", "v0.6.0", stage="deploy")

    def test_build_stage_needs_no_built_starter(self):
        self.assertTrue(self.decide("tag", "v0.6.0", stage="build", built=False).deploy)

    def test_rerun_of_tag_does_not_replace_newer_guide(self):
        # v0.6.0 released at OLD; main moved to NEW (guide fix, same version) and deployed it.
        self.world.standard_release("v0.6.0", OLD)
        self.live_site(NEW)
        for stage in ("build", "deploy"):
            decision = self.decide("tag", "v0.6.0", sha=OLD, stage=stage)
            self.assertFalse(decision.deploy, decision)
            self.assertIn("rollback: true", decision.reason)

    def test_rollback_replaces_newer_guide(self):
        self.world.standard_release("v0.6.0", OLD)
        self.live_site(NEW)
        self.assertTrue(self.decide("tag", "v0.6.0", sha=OLD, stage="deploy", rollback=True).deploy)

    def test_rerun_after_deploy_is_idempotent(self):
        self.world.standard_release("v0.6.0", NEW)
        self.assertTrue(self.decide("tag", "v0.6.0", stage="deploy").deploy)
        self.assertTrue(self.decide("tag", "v0.6.0", stage="deploy").deploy)


class Publish(Base):
    TAG = "v0.6.0"

    def setUp(self):
        super().setUp()
        self.world.refs[f"tags/{self.TAG}"] = NEW
        self.files = {f"rpi-thesis-starter-{self.TAG}.zip": starter_zip(STARTER_TEXT),
                      f"rpi-thesis-overleaf-{self.TAG}.zip": b"overleaf",
                      "rpi-thesis.cls": STARTER_TEXT["rpi-thesis.cls"].encode()}

    def publish(self, gh, sha=NEW):
        release.publish(self.world.net(), CFG, gh, tag=self.TAG, sha=sha, files=self.files,
                        notes_text="notes", log=lambda *a: None, sleep=lambda s: None)

    def assertComplete(self):
        rel = self.world.find(self.TAG)
        self.assertFalse(rel["draft"])
        self.assertEqual(sorted(a["name"] for a in rel["assets"]), sorted(self.files))
        for asset in rel["assets"]:
            self.assertEqual(asset["digest"], "sha256:" + digest(self.files[asset["name"]]))

    def test_fresh_release(self):
        gh = self.world.gh()
        self.publish(gh)
        self.assertEqual([c[1] for c in gh.calls], ["create"])
        self.assertComplete()

    def test_new_release_listed_late_is_found(self):
        self.world.hide_listing = 3  # the lookup before create, then two after it
        gh = self.world.gh()
        self.publish(gh)
        self.assertEqual([c[1] for c in gh.calls], ["create"])
        self.assertComplete()

    def test_existing_complete_release_changes_nothing(self):
        self.world.add_release(self.TAG, NEW, self.files)
        gh = self.world.gh()
        self.publish(gh)
        self.assertEqual(gh.calls, [])

    def test_existing_without_digests_fails(self):
        self.world.add_release(self.TAG, NEW, self.files, digests=False)
        gh = self.world.gh()
        with self.assertRaisesRegex(ReleaseError, "no sha256 digest"):
            self.publish(gh)
        self.assertEqual(gh.calls, [])

    def test_partial_assets_upload_only_missing(self):
        partial = {k: v for k, v in self.files.items() if k != "rpi-thesis.cls"}
        self.world.add_release(self.TAG, NEW, partial)
        gh = self.world.gh()
        self.publish(gh)
        self.assertEqual(len(gh.calls), 1)
        self.assertEqual(gh.calls[0][1], "upload")
        self.assertTrue(gh.calls[0][-1].endswith("rpi-thesis.cls"))
        self.assertComplete()

    def test_conflicting_hash_fails_without_upload(self):
        changed = dict(self.files, **{"rpi-thesis.cls": b"% another class\n"})
        self.world.add_release(self.TAG, NEW, {"rpi-thesis.cls": changed["rpi-thesis.cls"]})
        gh = self.world.gh()
        with self.assertRaisesRegex(ReleaseError, "never changes its files"):
            self.publish(gh)
        self.assertEqual(gh.calls, [])

    def test_conflicting_commit_fails(self):
        self.world.add_release(self.TAG, NEWER, self.files)
        gh = self.world.gh()
        with self.assertRaisesRegex(ReleaseError, "points at"):
            self.publish(gh)
        self.assertEqual(gh.calls, [])

    def test_missing_tag_fails(self):
        del self.world.refs[f"tags/{self.TAG}"]
        with self.assertRaisesRegex(ReleaseError, "push it first"):
            self.publish(self.world.gh())

    def test_failure_during_create_upload_converges(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.publish(self.world.gh(fail_on="create-upload"))
        self.assertTrue(self.world.find(self.TAG)["draft"])
        gh = self.world.gh()
        self.publish(gh)
        self.assertEqual([c[1] for c in gh.calls], ["upload", "edit"])
        self.assertComplete()

    def test_failure_after_creation_converges(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.publish(self.world.gh(fail_on="create-publish"))
        gh = self.world.gh()
        self.publish(gh)
        self.assertEqual([c[1] for c in gh.calls], ["edit"])
        self.assertComplete()

    def test_failure_after_upload_converges(self):
        self.world.add_release(self.TAG, NEW, {k: v for k, v in self.files.items() if k != "rpi-thesis.cls"})
        with self.assertRaises(subprocess.CalledProcessError):
            self.publish(self.world.gh(fail_on="upload"))
        gh = self.world.gh()
        self.publish(gh)
        self.assertEqual(gh.calls, [])
        self.assertComplete()

    def test_incomplete_asset_is_replaced(self):
        rel = self.world.add_release(self.TAG, NEW, {k: v for k, v in self.files.items() if k != "rpi-thesis.cls"})
        rel["assets"].append(self.world.asset(self.TAG, "rpi-thesis.cls", b"half", state="starter"))
        gh = self.world.gh()
        self.publish(gh)
        self.assertEqual([c[0] if c[0] == "api" else c[1] for c in gh.calls], ["api", "upload"])
        self.assertComplete()


class Live(Base):
    TAG = "v0.6.0"

    def setUp(self):
        super().setUp()
        _, self.files = self.world.standard_release(self.TAG, NEW)
        self.cls = self.files["rpi-thesis.cls"]

    def site(self, sha=NEW, meta=None, cls=None, link=True, build=True):
        meta = sha if meta is None else meta
        home = f'<meta name="rpi-thesis-build" content="{meta}">' if meta else ""
        if link:
            home += f'<a href="x/rpi-thesis-starter-{self.TAG}.zip">Get the starter</a>'
        pages = {"": home.encode(), "downloads/rpi-thesis.cls": self.cls if cls is None else cls}
        if build:
            pages["build.txt"] = f"commit={sha}\nrelease={self.TAG}\n".encode()
        return pages

    def live(self, attempts=4, expected=None):
        logs = []
        release.live(self.world.net(), CFG, sha=NEW, tag=self.TAG, class_bytes=self.cls,
                     expected=expected if expected is not None else {"rpi-thesis.cls": digest(self.cls)},
                     attempts=attempts, delay=0,
                     sleep=lambda s: None, log=logs.append)
        return logs

    def test_exact_build_passes(self):
        self.world.site = self.site()
        expected = {name: digest(data) for name, data in self.files.items()}
        self.assertIn("PASS", self.live(expected=expected)[-1])

    def test_propagation_delay_is_tolerated(self):
        self.world.site_timeline = [self.site(sha=OLD), self.site(sha=OLD), self.site()]
        self.live(attempts=4)

    def test_never_propagates_fails(self):
        self.world.site = self.site(sha=OLD)
        with self.assertRaisesRegex(ReleaseError, "does not serve build"):
            self.live()

    def test_mixed_cdn_revisions_fail(self):
        self.world.site = self.site(sha=NEW, meta=OLD)
        with self.assertRaisesRegex(ReleaseError, "mixed CDN revisions"):
            self.live()

    def test_corrupted_class_download_fails(self):
        self.world.site = self.site(cls=self.cls[:-3])
        with self.assertRaisesRegex(ReleaseError, "rpi-thesis.cls has sha256"):
            self.live()

    def test_missing_home_link_fails(self):
        self.world.site = self.site(link=False)
        with self.assertRaisesRegex(ReleaseError, "does not link"):
            self.live()

    def test_missing_build_id_fails(self):
        self.world.site = self.site(meta="", build=False)
        with self.assertRaisesRegex(ReleaseError, "missing"):
            self.live()

    def test_corrupted_release_download_is_retried(self):
        self.world.site = self.site()
        url = CFG.asset_url(self.TAG, f"rpi-thesis-overleaf-{self.TAG}.zip")
        good = self.world.downloads[(self.TAG, f"rpi-thesis-overleaf-{self.TAG}.zip")]
        calls = []

        def flaky(request, timeout=None):
            if request.full_url == url and not calls:
                calls.append(1)
                return Response(good[:-1])
            return self.world.opener(request, timeout)
        net = Net(delay=0, sleep=lambda s: None, opener=flaky)
        release.live(net, CFG, sha=NEW, tag=self.TAG, class_bytes=self.cls, expected={},
                     attempts=1, sleep=lambda s: None, log=lambda *a: None)
        self.assertEqual(calls, [1])

    def test_persistently_corrupted_release_download_fails(self):
        self.world.site = self.site()
        self.world.downloads[(self.TAG, "rpi-thesis.cls")] = b"corrupted"
        with self.assertRaisesRegex(ReleaseError, "corrupted download"):
            self.live()

    def test_built_zip_differs_from_release_fails(self):
        self.world.site = self.site()
        expected = {name: digest(data) for name, data in self.files.items()}
        expected[f"rpi-thesis-starter-{self.TAG}.zip"] = digest(b"rebuilt differently")
        with self.assertRaisesRegex(ReleaseError, "this run built"):
            self.live(expected=expected)

    def test_live_rerun_after_failure_converges(self):
        self.world.site = self.site(sha=OLD)
        with self.assertRaises(ReleaseError):
            self.live(attempts=1)
        self.world.site = self.site()
        self.live(attempts=1)

    def test_outage_during_live_fails(self):
        self.world.site = self.site()
        url = CFG.site + "build.txt"
        self.world.failures[url] = [urllib.error.URLError("dns")] * 4
        with self.assertRaises(NetworkError):
            self.live()


class Notes(unittest.TestCase):
    def test_notes_use_site_json_address(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "CHANGELOG.md").write_text("# Changes\n\n## 0.6.0 (beta)\n\n- Fixed a thing.\n\n## 0.5.0\n\n- Old.\n", encoding="utf-8")
            text = release.notes_text(CFG, version="0.6.0", root=root)
        self.assertIn(CFG.site, text)
        self.assertIn("Fixed a thing.", text)
        self.assertNotIn("Old.", text)
        self.assertIn("rpi-thesis-starter-v0.6.0.zip", text)


if __name__ == "__main__":
    unittest.main()
