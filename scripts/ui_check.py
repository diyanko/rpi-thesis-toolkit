#!/usr/bin/env python3
"""Maintainer-only visual and layout checks for the generated static site.

Usage:
    python3 scripts/ui_check.py [--site dist/site] [--shots] [--pages PAT ...] [--quick]

What it does:
  * Finds Chrome or Chromium (or $CHROME). If none is found it prints
    "SKIP ui_check: no Chrome found" and exits 0.
  * Serves the site folder on a free localhost port with the standard library.
    A synthetic test page (/__ui_check__.html) is generated in memory, so the
    site folder is never modified.
  * Loads every page in iframes at several widths (headless Chrome cannot make
    windows narrower than about 500 px) and measures layout problems:
    horizontal overflow, elements past the viewport outside intentional scroll
    boxes, images that failed to load, tables that scroll on wide screens,
    clipped code at phone widths, duplicate ids, and a 200% root font size pass
    at 390 px. Image loading is checked in light and dark mode.
  * With --shots, saves PNG screenshots (390 and 1280 px, light and dark) to
    _local/shots/<timestamp>/ (ignored by git). Each shot is the first screen,
    except the component gallery (project/components.html), shot at full length.
  * With --baseline save, also copies that set to _local/shots/baseline/.
    With --baseline compare, takes shots and lists the pages, widths and
    themes whose image differs from the baseline (informational; exit status
    is not affected). Images are compared by inflated PNG data, so a changed
    compression level does not count as a change.

Output: one "FAIL page width: issue" line per problem, a summary line, and
JSON details in build/verify/ui_check.json. Exit status is 1 on any problem.
Python standard library only; requires Chrome, not installed by this project.
"""

from __future__ import annotations

import argparse
import fnmatch
import html
import http.server
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FULL_WIDTHS = [320, 390, 768, 1280, 1920]
QUICK_WIDTHS = [390, 1280]
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
]

# The in-page script. CONFIG is substituted by the server per request.
TEST_PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>ui_check</title>
<style>body{margin:0}iframe{border:0;display:block;height:900px}</style></head>
<body><pre id="out">pending</pre><div id="host"></div>
<script>
const CONFIG = __CONFIG__;
const EXEMPT = ".table-wrap, figure.shot, pre, dialog, .anatomy-lens, .visually-hidden, .skip-link, .class-demo";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function describe(el) {
  let s = el.tagName.toLowerCase();
  if (el.id) s += "#" + el.id;
  const c = (el.getAttribute("class") || "").trim().split(/\s+/).filter(Boolean).slice(0, 2);
  if (c.length) s += "." + c.join(".");
  const t = (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 24);
  return t ? s + ' "' + t + '"' : s;
}
function loadFrame(url, width) {
  return new Promise((resolve) => {
    const f = document.createElement("iframe");
    f.style.width = width + "px";
    let done = false;
    const fin = (ok) => { if (!done) { done = true; resolve([f, ok]); } };
    f.onload = () => fin(true);
    setTimeout(() => fin(false), 20000);
    f.src = url;
    document.getElementById("host").appendChild(f);
  });
}
async function checkImages(doc, problems, add) {
  const imgs = Array.from(doc.images);
  imgs.forEach((i) => { if (i.loading === "lazy") i.loading = "eager"; });
  // Lazy or hidden images may never be fetched by the browser, so probe each
  // unloaded image's resolved URL with a fresh Image(). Event-driven, because
  // virtual time can run ahead of the network.
  await sleep(100);
  const probe = (url) => new Promise((res) => {
    const t = new Image();
    t.onload = () => res(t.naturalWidth > 0);
    t.onerror = () => res(false);
    t.src = url;
  });
  for (const i of imgs) {
    if (i.complete && i.naturalWidth > 0) continue;
    const url = i.currentSrc || i.src;
    if (!url || !(await probe(url))) add("image failed to load: " + (i.getAttribute("src") || "(no src)"));
  }
}
function measure(win, doc, width, opts, add) {
  const de = doc.documentElement;
  const vw = de.clientWidth;
  if (de.scrollWidth > vw + 1) {
    add("horizontal document overflow (scrollWidth " + de.scrollWidth + " > " + vw + ")");
  }
  let n = 0;
  const bad = [];
  for (const el of doc.body.querySelectorAll("*")) {
    if (el.closest(EXEMPT)) continue;
    const cs = win.getComputedStyle(el);
    if (cs.display === "none" || cs.position === "fixed") continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    if (r.right > vw + 1.5 || r.left < -1.5) {
      // Skip if a clipping ancestor (overflow other than visible) contains it.
      let p = el.parentElement, clipped = false;
      while (p && p !== doc.body) {
        const o = win.getComputedStyle(p).overflowX;
        if (o !== "visible") { clipped = true; break; }
        p = p.parentElement;
      }
      if (clipped) continue;
      n++;
      if (bad.length < 3) bad.push(describe(el) + " [" + Math.round(r.left) + ".." + Math.round(r.right) + "]");
    }
  }
  if (n) add(n + " element(s) past viewport " + vw + ": " + bad.join("; "));
  if (width >= 1024) {
    doc.querySelectorAll(".table-wrap").forEach((w) => {
      if (w.scrollWidth > w.clientWidth + 1) add("table scrolls at wide width: " + describe(w));
    });
  }
  if (width <= 390 && opts.code) {
    doc.querySelectorAll("pre").forEach((p) => {
      const o = win.getComputedStyle(p).overflowX;
      if (p.scrollWidth > p.clientWidth + 1 && o !== "auto" && o !== "scroll") {
        add("code clipped (overflow-x " + o + "): " + describe(p));
      }
    });
  }
}
async function main() {
  const out = { scheme: matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
                mode: CONFIG.mode, problems: [], pages: CONFIG.pages.length, widths: CONFIG.widths.length };
  const imgWidth = CONFIG.widths.includes(1280) ? 1280 : CONFIG.widths[CONFIG.widths.length - 1];
  const tasks = [];
  for (const page of CONFIG.pages) for (const w of CONFIG.widths) tasks.push([page, w]);
  const dupDone = new Set();
  async function worker() {
    while (tasks.length) {
      const [page, w] = tasks.shift();
      let [f, ok] = await loadFrame("/" + page, w);
      if (ok && !f.contentDocument) { f.remove(); [f, ok] = await loadFrame("/" + page, w); }
      const add = (m, label) => out.problems.push({ page, width: label || String(w), issue: m });
      if (!ok) { add("page did not finish loading"); f.remove(); continue; }
      try {
        const win = f.contentWindow, doc = f.contentDocument;
        if (doc.fonts && doc.fonts.ready) await doc.fonts.ready;
        await sleep(30);
        if (CONFIG.mode === "full") {
          measure(win, doc, w, { code: true }, add);
          if (!dupDone.has(page)) {
            dupDone.add(page);
            const seen = {}, dups = [];
            doc.querySelectorAll("[id]").forEach((e) => { if (seen[e.id]) dups.push(e.id); seen[e.id] = 1; });
            if (dups.length) add("duplicate id(s): " + Array.from(new Set(dups)).slice(0, 5).join(", "), "all");
          }
          if (w === 390) {
            doc.documentElement.style.fontSize = "200%";
            await sleep(60);
            measure(win, doc, w, { code: false }, (m) => add(m, "390@200%"));
          }
        }
        if (w === imgWidth) await checkImages(doc, out.problems, (m) => add(m, w + (out.scheme === "dark" ? " dark" : " light")));
      } catch (e) {
        add("check error: " + e);
      }
      f.remove();
    }
  }
  await Promise.all(Array.from({ length: 6 }, worker));
  out.done = true;
  document.getElementById("out").textContent = JSON.stringify(out).replace(/</g, "\\u003c");
}
main().catch((e) => { document.getElementById("out").textContent = JSON.stringify({ error: String(e) }); });
</script></body></html>
"""

SHOT_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>shot</title>
<style>html,body{margin:0;background:#888}iframe{border:0;display:block;margin:0 auto;
width:__W__px;height:__H__px;background:#fff}</style></head>
<body><iframe src="__SRC__"></iframe></body></html>"""


def find_chrome() -> str | None:
    env = os.environ.get("CHROME")
    if env and (shutil.which(env) or Path(env).exists()):
        return env
    for cand in CHROME_CANDIDATES:
        if Path(cand).is_absolute():
            if Path(cand).exists():
                return cand
        elif shutil.which(cand):
            return cand
    return None


def discover_pages(site: Path, patterns: list[str] | None) -> list[str]:
    pages = []
    if (site / "index.html").is_file():
        pages.append("index.html")
    for sub in ("guide", "project"):
        pages += sorted(p.relative_to(site).as_posix() for p in (site / sub).glob("*.html"))
    if patterns:
        pages = [p for p in pages
                 if any(fnmatch.fnmatch(p, pat) or pat in p for pat in patterns)]
    return pages


def make_handler(site: Path, config: dict):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(site), **kw)

        def log_message(self, *args):  # keep output quiet
            pass

        def _send(self, body: str):
            data = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            from urllib.parse import urlparse, parse_qs
            u = urlparse(self.path)
            q = parse_qs(u.query)
            if u.path == "/__ui_check__.html":
                cfg = dict(config, mode=q.get("mode", ["full"])[0])
                self._send(TEST_PAGE.replace("__CONFIG__", json.dumps(cfg)))
            elif u.path == "/__ui_shot__.html":
                body = (SHOT_PAGE.replace("__W__", q["w"][0]).replace("__H__", q["h"][0])
                        .replace("__SRC__", html.escape(q["src"][0])))
                self._send(body)
            else:
                super().do_GET()

    return Handler


def chrome_args(chrome: str, profile: str, dark: bool) -> list[str]:
    return [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
            "--no-first-run", "--no-default-browser-check", "--disable-extensions",
            f"--user-data-dir={profile}",
            f"--blink-settings=preferredColorScheme={0 if dark else 1}"]


def run_dump(chrome: str, port: int, mode: str, dark: bool, budget_ms: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="ui_check_") as profile:
        cmd = chrome_args(chrome, profile, dark) + [
            f"--virtual-time-budget={budget_ms}", "--dump-dom", "--window-size=1400,900",
            f"http://127.0.0.1:{port}/__ui_check__.html?mode={mode}"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            return {"error": "Chrome timed out"}
    m = re.search(r'<pre id="out">(.*?)</pre>', res.stdout, re.S)
    if not m:
        return {"error": "no output from Chrome (exit %s)" % res.returncode}
    try:
        data = json.loads(html.unescape(m.group(1)))
    except ValueError:
        return {"error": "unreadable output from Chrome"}
    if not data.get("done") and "error" not in data:
        data["error"] = "test page did not finish within the virtual time budget"
    return data


# The component gallery (docs/project/components.md) is shot at full length,
# so one light/dark pair per width reviews every component; other pages show
# their first screen only.
GALLERY = "project/components.html"
GALLERY_HEIGHT = 7600   # the page is about 7000 px long at 390 px wide


def take_shot(chrome: str, port: int, page: str, width: int, dark: bool, dest: Path) -> str | None:
    with tempfile.TemporaryDirectory(prefix="ui_shot_") as profile:
        if width <= 600:
            win_w = 600
            h = GALLERY_HEIGHT if page == GALLERY else 1000
            src = f"http://127.0.0.1:{port}/__ui_shot__.html?w={width}&h={h}&src=/{page}"
            win = f"{win_w},{h}"
        else:
            h = GALLERY_HEIGHT if page == GALLERY else 1000
            src = f"http://127.0.0.1:{port}/{page}"
            win = f"{width},{h}"
        tmp = dest.with_suffix(".tmp.png")
        cmd = chrome_args(chrome, profile, dark) + [
            "--virtual-time-budget=4000", f"--window-size={win}", f"--screenshot={tmp}", src]
        try:
            subprocess.run(cmd, capture_output=True, timeout=90)
        except subprocess.TimeoutExpired:
            return f"{page} {width}: screenshot timed out"
    if not tmp.exists():
        return f"{page} {width}: no screenshot produced"
    if width <= 600 and shutil.which("sips"):
        subprocess.run(["sips", "-c", str(h), str(width), str(tmp), "--out", str(dest)],
                       capture_output=True)
        tmp.unlink(missing_ok=True)
    else:
        tmp.replace(dest)
    return None


def png_data(path: Path) -> bytes:
    """Inflated pixel stream (filtered scanlines) of a PNG, else the raw bytes."""
    raw = path.read_bytes()
    try:
        pos, idat = 8, []
        while pos < len(raw):
            n = int.from_bytes(raw[pos:pos + 4], "big")
            if raw[pos + 4:pos + 8] == b"IDAT":
                idat.append(raw[pos + 8:pos + 8 + n])
            pos += 12 + n
        return zlib.decompress(b"".join(idat))
    except (zlib.error, ValueError):
        return raw


def save_baseline(shots: Path, base: Path, errors: list[str]) -> bool:
    """Make shots the baseline only when every shot was taken; else keep the old one."""
    if errors or not any(shots.glob("*.png")):
        return False
    fresh = base.with_name(".baseline-new")
    old = base.with_name(".baseline-old")
    for leftover in (fresh, old):
        shutil.rmtree(leftover, ignore_errors=True)
    shutil.copytree(shots, fresh)
    if base.exists():
        base.rename(old)
    fresh.rename(base)
    shutil.rmtree(old, ignore_errors=True)
    return True


def compare_shots(new: Path, base: Path) -> list[str]:
    changed = []
    for png in sorted(new.glob("*.png")):
        old = base / png.name
        if not old.exists():
            changed.append(f"{png.stem}: new (no baseline)")
        elif png_data(png) != png_data(old):
            changed.append(f"{png.stem}: changed")
    for old in sorted(base.glob("*.png")):
        if not (new / old.name).exists():
            changed.append(f"{old.stem}: missing now")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description="Visual/layout checks for the generated site.")
    ap.add_argument("--site", default="dist/site", help="built site folder (default dist/site)")
    ap.add_argument("--shots", action="store_true", help="save screenshots under _local/shots/")
    ap.add_argument("--baseline", choices=["save", "compare"],
                    help="save: keep this shots set as _local/shots/baseline/; "
                         "compare: list shots that differ from it")
    ap.add_argument("--pages", nargs="+", metavar="PAT",
                    help="only pages whose path matches (glob or substring)")
    ap.add_argument("--quick", action="store_true", help="only widths 390 and 1280")
    args = ap.parse_args()
    if args.baseline:
        args.shots = True
    baseline_dir = ROOT / "_local" / "shots" / "baseline"
    if args.baseline == "compare" and not any(baseline_dir.glob("*.png")):
        print("ui_check: no baseline; run with --baseline save first", file=sys.stderr)
        return 1

    chrome = find_chrome()
    if not chrome:
        print("SKIP ui_check: no Chrome found")
        return 0
    site = Path(args.site)
    if not site.is_absolute():
        site = ROOT / site
    if not (site / "index.html").is_file():
        print(f"ui_check: {site} not found or empty; run build_site.py first", file=sys.stderr)
        return 1
    pages = discover_pages(site, args.pages)
    if not pages:
        print("ui_check: no pages matched", file=sys.stderr)
        return 1
    widths = QUICK_WIDTHS if args.quick else FULL_WIDTHS

    start = time.time()
    config = {"pages": pages, "widths": widths}
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    class Server(http.server.ThreadingHTTPServer):
        request_queue_size = 128
        daemon_threads = True

        def handle_error(self, request, client_address):  # Chrome drops connections
            pass

    server = Server(("127.0.0.1", port), make_handler(site, config))
    threading.Thread(target=server.serve_forever, daemon=True).start()

    problems: list[dict] = []
    errors: list[str] = []
    try:
        budget = 120000
        with ThreadPoolExecutor(max_workers=2) as pool:
            f_light = pool.submit(run_dump, chrome, port, "full", False, budget)
            f_dark = pool.submit(run_dump, chrome, port, "img", True, budget)
            for label, fut in (("light", f_light), ("dark", f_dark)):
                data = fut.result()
                if "error" in data:
                    errors.append(f"{label} run: {data['error']}")
                problems += data.get("problems", [])

        shot_dir = None
        if args.shots:
            shot_dir = ROOT / "_local" / "shots" / time.strftime("%Y%m%d-%H%M%S")
            shot_dir.mkdir(parents=True, exist_ok=True)
            jobs = []
            for page in pages:
                stem = page.replace("/", "_").removesuffix(".html")
                for w in (390, 1280):
                    for dark in (False, True):
                        dest = shot_dir / f"{stem}-{w}-{'dark' if dark else 'light'}.png"
                        jobs.append((page, w, dark, dest))
            with ThreadPoolExecutor(max_workers=6) as pool:
                for err in pool.map(lambda j: take_shot(chrome, port, *j), jobs):
                    if err:
                        errors.append(err)
    finally:
        server.shutdown()

    seen = set()
    unique = []
    for p in problems:
        key = (p["page"], p["width"], p["issue"])
        if key not in seen:
            seen.add(key)
            unique.append(p)
    unique.sort(key=lambda p: (p["page"], p["width"], p["issue"]))
    for p in unique:
        print(f"FAIL {p['page']} {p['width']}: {p['issue']}")
    for e in errors:
        print(f"FAIL ui_check: {e}")
    secs = time.time() - start
    total = len(unique) + len(errors)
    print(f"ui_check: {len(pages)} pages x {len(widths)} widths, {total} problems ({secs:.0f}s)")
    if args.shots and shot_dir:
        print(f"screenshots: {shot_dir.relative_to(ROOT)}")
        if args.baseline == "save":
            if save_baseline(shot_dir, baseline_dir, errors):
                print(f"baseline saved: {baseline_dir.relative_to(ROOT)}")
            else:
                print("baseline NOT saved: some screenshots failed; the old baseline is kept")
        elif args.baseline == "compare":
            diffs = compare_shots(shot_dir, baseline_dir)
            for d in diffs:
                print(f"CHANGED {d}")
            print(f"baseline: {len(diffs)} of {len(list(shot_dir.glob('*.png')))} shots differ")

    out = ROOT / "build" / "verify" / "ui_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"site": str(args.site), "pages": pages, "widths": widths,
                               "problems": unique, "errors": errors,
                               "seconds": round(secs, 1)}, indent=2) + "\n", encoding="utf-8")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
