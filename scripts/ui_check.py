#!/usr/bin/env python3
"""Maintainer-only visual and layout checks for the generated static site.

Usage:
    python3 scripts/ui_check.py [--site dist/site] [--shots [--full]] [--pages PAT ...] [--quick]
    python3 scripts/ui_check.py --pdf-result [PDF]

What it does:
  * Finds Chrome or Chromium (or $CHROME). If none is found it prints
    "SKIP ui_check: no Chrome found" and exits 0.
  * Serves the site folder on a free localhost port with the standard library.
    A synthetic test page (/__ui_check__.html) is generated in memory, so the
    site folder is never modified. Chrome is driven through its DevTools
    protocol (scripts/chrome.py).
  * Loads every page in iframes at several widths and measures layout
    problems: horizontal overflow, elements past the viewport outside
    intentional scroll boxes, images that failed to load, tables that scroll on
    wide screens, clipped code at phone widths, duplicate ids, and a 200% root
    font size pass at 390 px. Image loading is checked in light and dark mode.
    It also catches the small things a screenshot shows: text cut off in a
    menu, field or button; an edge or shadow cut by its container; fields side
    by side in a form that do not line up; and one component (STYLED: buttons,
    file pickers, tags, tool parts, callouts) measuring differently on two
    pages at 1280 px.
  * With --shots, saves PNG screenshots (390 and 1280 px, light and dark; the
    pages in WIDE_SHOTS also at 820, 2560 and 3840 px) to
    _local/shots/<timestamp>/ of the main checkout (ignored by git; worktrees
    share it). Each shot is the first screen, except the component gallery
    (project/components.html), shot at full length; --full shoots every page
    at full length.
  * With --baseline save, also copies that set to _local/shots/baseline/.
    With --baseline compare, takes shots and lists the pages, widths and
    themes whose image differs from the baseline (informational; exit status
    is not affected). Images are compared by inflated PNG data, so a changed
    compression level does not count as a change.
  * --pdf-result runs no sweep: it drops a PDF (default build/main.pdf) on
    the built "Check your PDF" page (guide/check-pdf.html) and saves the
    result at 390 and 1280 px in light and dark, the end of the result, and
    the printout as a PDF, to _local/shots/pdf-check-<timestamp>/.

Output: one "FAIL page width: issue" line per problem, a summary line, and
JSON details in build/verify/ui_check.json. Exit status is 1 on any problem.
Python standard library only; requires Chrome, not installed by this project.
"""

from __future__ import annotations

import argparse
import base64
import fnmatch
import json
import os
import shutil
import sys
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from chrome import Chrome, LocalServer
from common import ROOT, find_chrome, main_checkout, site_config

# Phones, tablets in portrait and landscape (768, 820, 1024, 1180), laptops and
# monitors (1280, 1366, 1440, 1536, 1680, 1920), and large, ultrawide and 4K
# monitors at 1x (2560, 3440, 3840).
FULL_WIDTHS = [320, 390, 768, 820, 1024, 1180, 1280, 1366, 1440, 1536, 1680, 1920, 2560, 3440, 3840]
QUICK_WIDTHS = [390, 1280]

# The in-page script. CONFIG is substituted by the server per request.
TEST_PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>ui_check</title>
<style>body{margin:0}iframe{border:0;display:block;height:900px}</style></head>
<body><pre id="out">pending</pre><div id="host"></div>
<script>
const CONFIG = __CONFIG__;
const EXEMPT = ".table-wrap, figure.shot, pre, dialog, .visually-hidden, .skip-link, .class-demo";
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
// The offsets a box-shadow adds on each side: "3px 3px 0 color, ...".
function shadowExtent(value) {
  const out = { l: 0, r: 0, t: 0, b: 0 };
  if (!value || value === "none") return out;
  for (const part of value.split(/,(?![^(]*\))/)) {
    if (/inset/.test(part)) continue;
    const n = (part.replace(/rgba?\([^)]*\)|#[0-9a-f]+|[a-z-]+\([^)]*\)/gi, "").match(/-?[\d.]+px/g) || []).map(parseFloat);
    const [x = 0, y = 0, blur = 0, spread = 0] = n;
    out.r = Math.max(out.r, x + blur + spread); out.l = Math.max(out.l, -x + blur + spread);
    out.b = Math.max(out.b, y + blur + spread); out.t = Math.max(out.t, -y + blur + spread);
  }
  return out;
}
// The small things a screenshot shows and a overflow check misses: text cut off
// inside controls and buttons, edges and shadows cut by a container, and two
// fields in one form row whose boxes do not line up.
function details(win, doc, add) {
  const ctx = doc.createElement("canvas").getContext("2d");
  const found = [];
  const note = (m) => { if (found.length < 4) found.push(m); else found.push(null); };
  const shown = (el, cs) => cs.display !== "none" && cs.visibility !== "hidden" && !el.closest("[hidden], .visually-hidden, dialog:not([open])");
  for (const el of doc.querySelectorAll("button, .button, input, select, textarea, .pager a, .tag, summary")) {
    const cs = win.getComputedStyle(el);
    if (!shown(el, cs)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    // At 200% text a phone has room for about 15 characters in a box; long
    // values and choices are cut there in every browser, so only report them at 100%.
    const big = doc.documentElement.style.fontSize === "200%";
    if (el.tagName === "SELECT") {
      if (big) continue;
      const text = (el.options[el.selectedIndex] || {}).text || "";
      ctx.font = cs.font;
      const room = el.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      if (ctx.measureText(text).width > room + 1) note("select text cut off: " + describe(el) + ' "' + text + '"');
    } else if (el.tagName === "INPUT" && /^(text|search|email|url|)$/.test(el.type) && el.value) {
      if (big) continue;
      if (el.scrollWidth > el.clientWidth + 1) note("input text cut off: " + describe(el));
    } else if (!/^(INPUT|TEXTAREA)$/.test(el.tagName) && el.scrollWidth > el.clientWidth + 1 && cs.overflowX !== "visible") {
      note("text cut off: " + describe(el));
    }
    // The edge and shadow must fit inside the nearest container that clips,
    // unless that container scrolls (its content is meant to move).
    const sh = shadowExtent(cs.boxShadow);
    for (let p = el.parentElement; p && p !== doc.body; p = p.parentElement) {
      const pc = win.getComputedStyle(p);
      if (pc.overflowX === "visible" && pc.overflowY === "visible") continue;
      if (p.scrollWidth > p.clientWidth + 1 || p.scrollHeight > p.clientHeight + 1) break;
      const pr = p.getBoundingClientRect();
      const inner = { l: pr.left + p.clientLeft, t: pr.top + p.clientTop };
      inner.r = inner.l + p.clientWidth; inner.b = inner.t + p.clientHeight;
      if (r.left - sh.l < inner.l - 0.5 || r.right + sh.r > inner.r + 0.5 ||
          r.top - sh.t < inner.t - 0.5 || r.bottom + sh.b > inner.b + 0.5) {
        note("edge or shadow clipped by " + describe(p) + ": " + describe(el));
      }
      break;
    }
  }
  // Fields side by side in a form grid: their boxes start at the same height.
  for (const grid of doc.querySelectorAll("form *")) {
    const cs = win.getComputedStyle(grid);
    if (cs.display !== "grid" || !shown(grid, cs)) continue;
    // One row: cells whose boxes overlap vertically (cells may be aligned to the top or bottom).
    const cells = [];
    for (const cell of grid.children) {
      const control = cell.querySelector(":scope > :is(input:not([type=checkbox]):not([type=radio]):not([type=file]), select, textarea)");
      if (control && control.getBoundingClientRect().width) cells.push([cell.getBoundingClientRect(), control]);
    }
    cells.sort((a, b) => a[0].top - b[0].top);
    const rows = [];
    for (const [box, control] of cells) {
      const row = rows[rows.length - 1];
      if (row && box.top < row.bottom - 1) { row.controls.push(control); row.bottom = Math.max(row.bottom, box.bottom); }
      else rows.push({ bottom: box.bottom, controls: [control] });
    }
    for (const { controls } of rows) {
      const tops = controls.map((c) => c.getBoundingClientRect().top);
      if (Math.max(...tops) - Math.min(...tops) > 2) note("fields in one row do not line up: " + controls.map(describe).join(" / "));
    }
  }
  const extra = found.filter((m) => m === null).length;
  for (const m of found.filter(Boolean)) add(m);
  if (extra) add("... and " + extra + " more detail problem(s)");
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
    if (el.closest("details:not([open])") && !el.closest("summary")) continue;   // hidden until opened
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
  details(win, doc, add);
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
// Components that must look the same wherever they appear (measured at one width).
const STYLE_WIDTH = 1280;
const STYLED = [".button:not(.button-small)", ".button-small", ".tool-file", ".tool-file-button", ".tool-status",
  ".tool-privacy", ".tool-results", ".tool-hint", ".tool-label", ".tool-switch", ".tool select",
  ".tool :is(input[type=text], textarea.settings-grow)", ".tool textarea:not(.tool-drop, .settings-grow)", ".tool textarea.tool-drop", ".tool-output", ".tag:not(.tag-optional)", ".tag-optional",
  ".pager a", ".guide-content > h2", ".guide-content > h3", ".action-rows .help-card", ".button-quiet", ".nav-menu-list a:not([aria-current])", ".release-pdf", ".table-wrap", ".tip", ".note", ".warning", ".important"];
// Measured on each; height is left out because boxes for text are sized to their purpose.
const LOOK = ["paddingTop", "paddingRight", "paddingBottom", "paddingLeft", "fontSize", "fontWeight",
  "borderTopWidth", "borderTopStyle", "lineHeight"];
const styleSeen = {};
function recordStyles(win, doc, page) {
  for (const selector of STYLED) {
    for (const el of doc.querySelectorAll(selector)) {
      if (el.closest("[hidden], .visually-hidden, dialog:not([open]), .component-variant")) continue;
      const cs = win.getComputedStyle(el);
      if (cs.display === "none" || !el.getBoundingClientRect().width) continue;
      const look = LOOK.map((k) => cs[k]).join(" ");
      ((styleSeen[selector] = styleSeen[selector] || new Map()).get(look) ||
        styleSeen[selector].set(look, new Set()).get(look)).add(page);
    }
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
        // Tool pages: wait for their scripts to show the tool.
        for (let i = 0; i < 40 && doc.querySelector(".tool[hidden]"); i++) await sleep(50);
        if (CONFIG.mode === "full") {
          if (w === STYLE_WIDTH) recordStyles(win, doc, page);
          measure(win, doc, w, { code: true }, add);
          // The header menus, each opened in turn, must fit the screen too.
          for (const menu of doc.querySelectorAll(".nav-menu")) {
            menu.open = true;
            await sleep(20);
            measure(win, doc, w, { code: false }, (m) => add("with the " + menu.querySelector("summary").textContent + " menu open: " + m));
            menu.open = false;
          }
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
  // One component, one look: the same selector must measure the same on every page.
  for (const [selector, looks] of Object.entries(styleSeen)) {
    if (looks.size < 2) continue;
    const parts = [...looks.entries()].map(([look, pages]) => look + " on " + [...pages].slice(0, 2).join(", "));
    out.problems.push({ page: "all", width: String(STYLE_WIDTH), issue: "\"" + selector + "\" differs between pages: " + parts.join(" | ") });
  }
  out.done = true;
  document.getElementById("out").textContent = JSON.stringify(out).replace(/</g, "\\u003c");
}
main().catch((e) => { document.getElementById("out").textContent = JSON.stringify({ error: String(e) }); });
</script></body></html>
"""

def discover_pages(site: Path, patterns: list[str] | None) -> list[str]:
    pages = []
    for front in ("index.html", "404.html"):
        if (site / front).is_file():
            pages.append(front)
    for sub in ("guide", "project"):
        pages += sorted(p.relative_to(site).as_posix() for p in (site / sub).glob("*.html"))
    if patterns:
        pages = [p for p in pages
                 if any(fnmatch.fnmatch(p, pat) or pat in p for pat in patterns)]
    return pages


def routes(site: Path, config: dict, pdf: Path | None = None):
    """The pages the server makes up: the test page, the local 404 page, and
    the PDF for --pdf-result."""
    def dynamic(path: str, query: dict):
        if path == "/__ui_check__.html":
            cfg = dict(config, mode=query.get("mode", ["full"])[0])
            return TEST_PAGE.replace("__CONFIG__", json.dumps(cfg)).encode("utf-8"), "text/html; charset=utf-8"
        if path == "/404.html":
            # GitHub Pages serves this document at arbitrary missing URLs,
            # so its production links are absolute. Test the current build's
            # assets locally instead of silently loading the live website.
            site_url = site_config(ROOT)["site_url"]
            text = (site / "404.html").read_text(encoding="utf-8").replace(site_url.rstrip("/") + "/", "/")
            return text.encode("utf-8"), "text/html; charset=utf-8"
        if pdf and path == "/__pdf__/0":
            return pdf.read_bytes(), "application/pdf"
        return None
    return dynamic


def run_sweep(chrome: str, url: str, mode: str, dark: bool, timeout: int = 300) -> dict:
    """Open the test page in a fresh browser and wait for its JSON result."""
    try:
        with Chrome(chrome, dark=dark) as browser:
            browser.viewport(1400, 900)
            browser.open(f"{url}/__ui_check__.html?mode={mode}")
            text = browser.evaluate("""(async () => {
              const out = document.getElementById("out");
              for (let i = 0; i < %d && out.textContent === "pending"; i++) await new Promise(r => setTimeout(r, 100));
              return out.textContent;
            })()""" % (timeout * 10))
    except (OSError, RuntimeError) as error:
        return {"error": f"Chrome failed: {error}"}
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return {"error": "the test page did not finish within %d s" % timeout}
    if not data.get("done") and "error" not in data:
        data["error"] = "the test page did not finish"
    return data


# The component gallery (docs/project/components.md) is shot at full length,
# so one light/dark pair per width reviews every component; other pages show
# their first screen only.
GALLERY = "project/components.html"
GALLERY_HEIGHT = 7600   # the page is about 7000 px long at 390 px wide
# Wait for web fonts and for the images already on screen (at most 5 s).
SETTLE = """Promise.race([new Promise(r => setTimeout(r, 5000)), Promise.all([document.fonts.ready,
  ...Array.from(document.images).filter(i => !i.complete && i.loading !== "lazy")
     .map(i => new Promise(r => { i.addEventListener("load", r); i.addEventListener("error", r); }))])
]).then(() => new Promise(r => requestAnimationFrame(() => setTimeout(r, 100)))).then(() => true)"""


FULL_MAX = 16000  # px; longer pages are cut off at this height
# A tablet in portrait, an ultrawide and a 4K monitor: one home page, guide page and
# tool page, so the layouts between phone and laptop, and above, stay reviewed.
WIDE_SHOTS = {"index.html", "guide/writing.html", "guide/bring-your-work-in.html"}
SHOTS = main_checkout(ROOT) / "_local" / "shots"


def take_shot(browser, url: str, page: str, width: int, dest: Path, full: bool = False) -> str | None:
    """Save one screenshot of page at this width (full length with full);
    return an error or None."""
    height = GALLERY_HEIGHT if page == GALLERY else 1000
    try:
        browser.viewport(width, height)
        browser.open(f"{url}/{page}")
        browser.evaluate(SETTLE)
        if full and page != GALLERY:
            length = browser.evaluate("document.documentElement.scrollHeight")
            if isinstance(length, int) and length > height:
                browser.viewport(width, min(length, FULL_MAX))
                browser.evaluate(SETTLE)
        data = browser.screenshot()
    except (OSError, RuntimeError) as error:
        return f"{page} {width}: Chrome screenshot failed ({error})"
    if not data.startswith(b"\x89PNG"):
        return f"{page} {width}: no screenshot produced"
    dest.write_bytes(data)
    return None


def shoot(chrome: str, url: str, jobs: list, dark: bool, full: bool = False) -> list[str]:
    """Take the shots for one color scheme in one browser; return errors."""
    try:
        with Chrome(chrome, dark=dark) as browser:
            browser.scheme(dark)
            return [error for page, width, dest in jobs
                    if (error := take_shot(browser, url, page, width, dest, full))]
    except (OSError, RuntimeError) as error:
        return [f"{'dark' if dark else 'light'} shots: Chrome failed ({error})"]


# The result of a dropped PDF, for --pdf-result.
DROP = """(async function () {
  const bytes = await (await fetch("/__pdf__/0")).blob();
  const transfer = new DataTransfer();
  transfer.items.add(new File([bytes], %s, { type: "application/pdf" }));
  const zone = document.querySelector(".pdf-check-drop");
  zone.dispatchEvent(new DragEvent("drop", { dataTransfer: transfer, bubbles: true, cancelable: true }));
  for (let i = 0; i < 600 && !document.querySelector(".pdf-check-results h3"); i++) await new Promise(r => setTimeout(r, 100));
  const heading = document.querySelector(".pdf-check-results h3");
  if (!heading) throw new Error(document.querySelector(".pdf-check-status").textContent || "no result");
  window.scrollTo({ top: heading.getBoundingClientRect().top + scrollY - 16, behavior: "instant" });
  return document.querySelectorAll(".pdf-check-item").length;
})()"""


def pdf_result_shots(chrome: str, site: Path, pdf: Path) -> Path:
    """Screenshots of the Check your PDF page with a result, and its printout."""
    if not (site / "guide" / "check-pdf.html").is_file():
        raise SystemExit("ui_check.py --pdf-result: guide/check-pdf.html not found; run build_site.py first.")
    dest = SHOTS / ("pdf-check-" + time.strftime("%Y%m%d-%H%M%S"))
    dest.mkdir(parents=True, exist_ok=True)
    with LocalServer(site, routes(site, {}, pdf)) as server, Chrome(chrome) as browser:
        for width in (390, 1280):
            for dark in (False, True):
                browser.viewport(width, 1000, mobile=width < 600)
                browser.scheme(dark)
                browser.open(server.url + "/guide/check-pdf.html")
                browser.evaluate(DROP % json.dumps(pdf.name))
                time.sleep(0.3)
                name = f"check-pdf-result-{width}-{'dark' if dark else 'light'}"
                (dest / f"{name}.png").write_bytes(browser.screenshot())
                browser.evaluate("window.scrollTo({behavior: \"instant\", top: document.querySelector('.pdf-check-results button')"
                                 ".getBoundingClientRect().bottom + scrollY - 980}); true")
                time.sleep(0.2)
                (dest / f"{name}-end.png").write_bytes(browser.screenshot())
        # The printout: press the button with printing stubbed, then print to PDF.
        browser.evaluate("window.print = function () {}; document.querySelector('.pdf-check-results button').click(); true")
        printed = browser.call("Page.printToPDF", printBackground=False, paperWidth=8.5, paperHeight=11)
        (dest / "check-pdf-printout.pdf").write_bytes(base64.b64decode(printed["data"]))
    return dest


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
    ap.add_argument("--full", action="store_true", help="with --shots, shoot whole pages, not the first screen")
    ap.add_argument("--baseline", choices=["save", "compare"],
                    help="save: keep this shots set as _local/shots/baseline/; "
                         "compare: list shots that differ from it")
    ap.add_argument("--pages", nargs="+", metavar="PAT",
                    help="only pages whose path matches (glob or substring)")
    ap.add_argument("--quick", action="store_true", help="only widths 390 and 1280")
    ap.add_argument("--pdf-result", nargs="?", const="build/main.pdf", metavar="PDF",
                    help="only screenshots of the Check your PDF page with this PDF's result "
                         "(default build/main.pdf)")
    args = ap.parse_args()
    if args.baseline:
        args.shots = True
    baseline_dir = SHOTS / "baseline"
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
    if args.pdf_result:
        pdf = Path(args.pdf_result)
        pdf = (pdf if pdf.is_absolute() else Path.cwd() / pdf).resolve()
        if not pdf.is_file():
            print(f"ui_check.py --pdf-result: {pdf} not found; compile the starter first (scripts/build.py).",
                  file=sys.stderr)
            return 1
        print(f"screenshots: {pdf_result_shots(chrome, site, pdf).relative_to(SHOTS.parent.parent)}")
        return 0
    pages = discover_pages(site, args.pages)
    if not pages:
        print("ui_check: no pages matched", file=sys.stderr)
        return 1
    widths = QUICK_WIDTHS if args.quick else FULL_WIDTHS

    start = time.time()
    problems: list[dict] = []
    errors: list[str] = []
    shot_dir = None
    with LocalServer(site, routes(site, {"pages": pages, "widths": widths})) as server:
        with ThreadPoolExecutor(max_workers=2) as pool:
            f_light = pool.submit(run_sweep, chrome, server.url, "full", False)
            f_dark = pool.submit(run_sweep, chrome, server.url, "img", True)
            for label, fut in (("light", f_light), ("dark", f_dark)):
                data = fut.result()
                if "error" in data:
                    errors.append(f"{label} run: {data['error']}")
                problems += data.get("problems", [])

        if args.shots:
            shot_dir = SHOTS / f"{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"   # unique per run
            shot_dir.mkdir(parents=True)
            jobs = {False: [], True: []}
            for page in pages:
                stem = page.replace("/", "_").removesuffix(".html")
                for w in (390, 1280) + ((820, 2560, 3840) if page in WIDE_SHOTS else ()):
                    for dark in (False, True):
                        jobs[dark].append((page, w, shot_dir / f"{stem}-{w}-{'dark' if dark else 'light'}.png"))
            with ThreadPoolExecutor(max_workers=2) as pool:
                for found in pool.map(lambda dark: shoot(chrome, server.url, jobs[dark], dark, args.full), (False, True)):
                    errors += found

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
        print(f"screenshots: {shot_dir.relative_to(SHOTS.parent.parent)}")
        if args.baseline == "save":
            if save_baseline(shot_dir, baseline_dir, errors):
                print(f"baseline saved: {baseline_dir.relative_to(SHOTS.parent.parent)}")
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
