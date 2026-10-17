#!/usr/bin/env python3
"""Run the "Check your PDF" checks on every PDF in a folder, in headless Chrome.

    python3 scripts/check_pdfs.py [FOLDER] [--details] [--json FILE]
    python3 scripts/check_pdfs.py --shots [PDF]

FOLDER defaults to _local/pdf-samples/ (ignored by Git): put PDFs there that
OGE accepted or returned, to see how the checker does on them. Never copy
those PDFs into tracked files; they are someone's thesis. Each PDF is read in
the browser exactly as the page reads it (site/pdf-check/core.js and the
vendored pdf.js, served from site/ on a localhost port); nothing leaves this
computer.

Output: one row per PDF with a letter per check (. looks right, ~ differs
from the manual's wording, X look at this, ? could not tell, i information),
then a key. --details also prints
every flagged point. --json saves the full results.

--shots builds nothing: it loads dist/site/guide/check-pdf.html (run
build_site.py first), drops the PDF (default build/main.pdf) on the page, and
saves screenshots at 390 and 1280 px in light and dark, plus the printout as
a PDF, to _local/shots/pdf-check-<time>/.

Needs Chrome or Chromium ($CHROME, as for ui_check.py). Python standard
library only; Chrome is driven through its DevTools protocol.
"""
import argparse
import base64
import http.server
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ui_check import find_chrome  # noqa: E402
import rules  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "_local" / "pdf-samples"
ORDER = ["paper", "same-size", "numbering", "position", "distance", "headings", "margins", "contents", "listed",
         "fonts", "blank", "size", "version"]
MARK = {"ok": ".", "differs": "~", "check": "X", "unknown": "?", "info": "i"}
# The harness page carries the same rules block as the guide page (scripts/rules.py);
# RULES is the expression that reads it, as ui.js does.
HARNESS = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>check_pdfs</title>
<script src="/pdf-check/core.js"></script></head><body>%s</body></html>"""
RULES = 'JSON.parse(document.getElementById("oge-rules").textContent)'
# The page part (ui.js) with the guide page's own checker markup, for
# scripts/test_pdf_check.py. It counts the pdf.js workers that are running.
UI_HARNESS = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>check_pdfs ui</title>
<script>
window.liveWorkers = 0;
window.Worker = class extends Worker {
  constructor(...args) { super(...args); this.counted = true; window.liveWorkers++; }
  terminate() { if (this.counted) { this.counted = false; window.liveWorkers--; } super.terminate(); }
};
</script></head><body><main class="guide-content">%s</main>%s<script src="/pdf-check/ui.js"></script></body></html>"""


def checker_markup():
    """The checker's markup from docs/check-pdf.md (one line starting <div class="pdf-check")."""
    found = re.search(r'(?m)^<div class="pdf-check" .*$', (ROOT / "docs/check-pdf.md").read_text(encoding="utf-8"))
    if not found:
        raise RuntimeError("docs/check-pdf.md has no <div class=\"pdf-check\" ...> line")
    return found[0].replace('data-version=""', f'data-version="{class_version()}"', 1)

RUN = """(async function () {
  const pdfjs = await import("/pdf-check/pdfjs/pdf.min.mjs");
  pdfjs.GlobalWorkerOptions.workerSrc = "/pdf-check/pdfjs/pdf.worker.min.mjs";
  if (pdfjs.version !== PdfCheckCore.PDFJS_VERSION) throw new Error("pdf.js " + pdfjs.version + " is not PDFJS_VERSION");
  const bytes = new Uint8Array(await (await fetch(%(url)s)).arrayBuffer());
  const data = await PdfCheckCore.read(pdfjs, bytes);
  return PdfCheckCore.analyse(data, { current: %(current)s, rules: %(rules)s });
})()"""


# ---------- A minimal DevTools client (WebSocket, standard library) ----------
class WebSocket:
    def __init__(self, url, timeout=300):
        address = urlsplit(url)
        self.sock = socket.create_connection((address.hostname, address.port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET {address.path} HTTP/1.1\r\nHost: {address.netloc}\r\nUpgrade: websocket\r\n"
                           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        self.buffer = bytearray()
        while b"\r\n\r\n" not in self.buffer:
            self._fill()
        head, _, rest = bytes(self.buffer).partition(b"\r\n\r\n")
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise ConnectionError("Chrome refused the DevTools connection: " + head.decode(errors="replace")[:200])
        self.buffer = bytearray(rest)

    def _fill(self):
        chunk = self.sock.recv(1 << 16)
        if not chunk:
            raise ConnectionError("Chrome closed the DevTools connection")
        self.buffer += chunk

    def _take(self, count):
        while len(self.buffer) < count:
            self._fill()
        out = bytes(self.buffer[:count])
        del self.buffer[:count]
        return out

    def _frame(self, opcode, data):
        mask = os.urandom(4)
        size = len(data)
        head = bytes([0x80 | opcode]) + (bytes([0x80 | size]) if size < 126 else
                                         bytes([0x80 | 126]) + size.to_bytes(2, "big") if size < 65536 else
                                         bytes([0x80 | 127]) + size.to_bytes(8, "big"))
        self.sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def send(self, text):
        self._frame(0x1, text.encode("utf-8"))

    def receive(self):
        message = b""
        while True:
            first, second = self._take(2)
            size = second & 0x7F
            if size == 126:
                size = int.from_bytes(self._take(2), "big")
            elif size == 127:
                size = int.from_bytes(self._take(8), "big")
            mask = self._take(4) if second & 0x80 else None
            data = self._take(size)
            if mask:
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            opcode = first & 0x0F
            if opcode == 0x8:
                raise ConnectionError("Chrome closed the DevTools connection")
            if opcode == 0x9:
                self._frame(0xA, data)
                continue
            if opcode in (0x0, 0x1, 0x2):
                message += data
                if first & 0x80:
                    return message.decode("utf-8")


class Chrome:
    """Headless Chrome with one tab, driven by DevTools commands."""

    def __init__(self, chrome):
        self.profile = tempfile.TemporaryDirectory(prefix="check_pdfs_")
        self.process = subprocess.Popen(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
             "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
             f"--user-data-dir={self.profile.name}", "--remote-debugging-port=0", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        port_file = Path(self.profile.name) / "DevToolsActivePort"
        deadline = time.time() + 30
        while not (port_file.exists() and port_file.read_text().count("\n") >= 1):
            if time.time() > deadline or self.process.poll() is not None:
                self.close()
                raise RuntimeError("Chrome did not start its DevTools port")
            time.sleep(0.1)
        port = int(port_file.read_text().split()[0])
        with urlopen(Request(f"http://127.0.0.1:{port}/json/new?about:blank", method="PUT"), timeout=30) as reply:
            target = json.load(reply)
        self.socket = WebSocket(target["webSocketDebuggerUrl"])
        self.next_id = 0
        self.call("Page.enable")
        self.call("Runtime.enable")

    def call(self, method, **params):
        self.next_id += 1
        self.socket.send(json.dumps({"id": self.next_id, "method": method, "params": params}))
        while True:
            reply = json.loads(self.socket.receive())
            if reply.get("id") == self.next_id:
                if "error" in reply:
                    raise RuntimeError(f"{method}: {reply['error'].get('message')}")
                return reply.get("result", {})

    def evaluate(self, expression):
        result = self.call("Runtime.evaluate", expression=expression, awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in result:
            details = result["exceptionDetails"]
            raise RuntimeError((details.get("exception") or {}).get("description") or details.get("text"))
        return result["result"].get("value")

    def open(self, url):
        self.call("Page.navigate", url=url)
        deadline = time.time() + 60
        while self.evaluate("document.readyState") != "complete" or self.evaluate("location.href") != url:
            if time.time() > deadline:
                raise RuntimeError(f"{url} did not finish loading")
            time.sleep(0.05)

    def close(self):
        if getattr(self, "socket", None):
            self.socket.sock.close()
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.profile.cleanup()


class Server:
    """Serves a folder on a localhost port, plus the harness page and the PDFs
    under /__pdf__/N, without touching the folder."""

    def __init__(self, folder, pdfs=()):
        pdfs = list(pdfs)

        class Handler(http.server.SimpleHTTPRequestHandler):
            extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                              ".mjs": "text/javascript", ".js": "text/javascript"}

            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(folder), **kwargs)

            def log_message(self, *args):
                pass

            def reply(self, body, kind):
                self.send_response(200)
                self.send_header("Content-Type", kind)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                path = urlsplit(self.path).path
                if path == "/__pdf_check__.html":
                    self.reply((HARNESS % rules.embed()).encode(), "text/html; charset=utf-8")
                elif path == "/__pdf_ui__.html":
                    self.reply((UI_HARNESS % (checker_markup(), rules.embed())).encode(), "text/html; charset=utf-8")
                elif path.startswith("/__pdf__/"):
                    self.reply(Path(pdfs[int(path.rsplit("/", 1)[1])]).read_bytes(), "application/pdf")
                else:
                    super().do_GET()

        class Threading(http.server.ThreadingHTTPServer):
            daemon_threads = True

            def handle_error(self, request, client_address):
                pass

        self.httpd = Threading(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def class_version():
    """The version in the \\ProvidesClass line of rpi-thesis.cls, as the website shows it."""
    match = re.search(r"\\ProvidesClass\{rpi-thesis\}\[\S+ v([\w.-]+)",
                      (ROOT / "rpi-thesis.cls").read_text(encoding="utf-8"))
    return match.group(1) if match else ""


def check(pdfs, current=None, chrome=None):
    """Results for each PDF: (path, list of checks) or (path, error text)."""
    chrome = chrome or find_chrome()
    if not chrome:
        raise RuntimeError("no Chrome found")
    current = class_version() if current is None else current
    server = Server(ROOT / "site", pdfs)
    browser = Chrome(chrome)
    out = []
    try:
        browser.open(server.url + "/__pdf_check__.html")
        for index, pdf in enumerate(pdfs):
            try:
                found = browser.evaluate(RUN % {"url": json.dumps(f"/__pdf__/{index}"), "current": json.dumps(current), "rules": RULES})
                out.append((pdf, found))
            except RuntimeError as error:
                out.append((pdf, str(error).splitlines()[0]))
    finally:
        browser.close()
        server.close()
    return out


def table(results, details=False):
    width = max([len(Path(p).name) for p, _ in results] + [4])
    lines = ["PDF".ljust(width) + "  " + " ".join(f"{k + 1:>2}" for k in range(len(ORDER)))]
    for pdf, found in results:
        name = Path(pdf).name.ljust(width)
        if isinstance(found, str):
            lines.append(f"{name}  could not be read: {found}")
            continue
        by = {f["id"]: f for f in found}
        lines.append(name + "  " + " ".join(f"{MARK.get(by[k]['state'], '-') if k in by else '-':>2}" for k in ORDER))
        if details:
            for f in found:
                if f["state"] in ("check", "differs", "unknown"):
                    lines.append(f"    {MARK[f['state']]} {f['title']}: {f['summary']}")
                    lines += [f"        {text}" for text in f["pages"][:20]]
    lines.append("Checks: " + ", ".join(f"{k + 1} {name}" for k, name in enumerate(ORDER)))
    lines.append("Key: . looks right, ~ differs from the manual's wording, X look at this, ? could not tell, i information")
    return "\n".join(lines)


def shots(pdf, chrome):
    site = ROOT / "dist" / "site"
    if not (site / "guide" / "check-pdf.html").is_file():
        raise SystemExit("check_pdfs.py --shots: dist/site/guide/check-pdf.html not found; run build_site.py first.")
    dest = ROOT / "_local" / "shots" / ("pdf-check-" + time.strftime("%Y%m%d-%H%M%S"))
    dest.mkdir(parents=True, exist_ok=True)
    server = Server(site, [pdf])
    browser = Chrome(chrome)
    drop = """(async function () {
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
    })()""" % json.dumps(Path(pdf).name)
    try:
        for width in (390, 1280):
            for dark in (False, True):
                browser.call("Emulation.setDeviceMetricsOverride", width=width, height=1000,
                             deviceScaleFactor=1, mobile=width < 600)
                browser.call("Emulation.setEmulatedMedia", media="",
                             features=[{"name": "prefers-color-scheme", "value": "dark" if dark else "light"}])
                browser.open(server.url + "/guide/check-pdf.html")
                browser.evaluate(drop)
                time.sleep(0.3)
                shot = browser.call("Page.captureScreenshot", format="png")
                name = f"check-pdf-result-{width}-{'dark' if dark else 'light'}"
                (dest / f"{name}.png").write_bytes(base64.b64decode(shot["data"]))
                browser.evaluate("window.scrollTo({behavior: \"instant\", top: document.querySelector('.pdf-check-results button')"
                                 ".getBoundingClientRect().bottom + scrollY - 980}); true")
                time.sleep(0.2)
                shot = browser.call("Page.captureScreenshot", format="png")
                (dest / f"{name}-end.png").write_bytes(base64.b64decode(shot["data"]))
        # The printout: press the button with printing stubbed, then print to PDF.
        browser.evaluate("window.print = function () {}; document.querySelector('.pdf-check-results button').click(); true")
        printed = browser.call("Page.printToPDF", printBackground=False, paperWidth=8.5, paperHeight=11)
        (dest / "check-pdf-printout.pdf").write_bytes(base64.b64decode(printed["data"]))
    finally:
        browser.close()
        server.close()
    print(f"screenshots: {dest.relative_to(ROOT)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("folder", nargs="?", help="folder of PDFs (default _local/pdf-samples/), or with --shots one PDF")
    parser.add_argument("--details", action="store_true", help="print every flagged point")
    parser.add_argument("--json", metavar="FILE", help="save the full results as JSON")
    parser.add_argument("--shots", action="store_true", help="screenshots of the page with a result")
    args = parser.parse_args()
    chrome = find_chrome()
    if not chrome:
        print("SKIP check_pdfs: no Chrome found (set $CHROME)")
        return 0
    if args.shots:
        pdf = Path(args.folder or ROOT / "build" / "main.pdf")
        if not pdf.is_file():
            raise SystemExit(f"check_pdfs.py --shots: {pdf} not found; compile the starter first (scripts/build.py).")
        shots(pdf.resolve(), chrome)
        return 0
    folder = Path(args.folder) if args.folder else SAMPLES
    pdfs = sorted(p for p in folder.glob("*.pdf") if p.is_file()) if folder.is_dir() else []
    if not pdfs:
        print(f"check_pdfs: no PDFs in {folder}; put PDFs there (never in tracked files).")
        return 1
    results = check([str(p) for p in pdfs], chrome=chrome)
    print(table(results, args.details))
    if args.json:
        Path(args.json).write_text(json.dumps([{"pdf": Path(p).name, "result": r} for p, r in results], indent=2) + "\n",
                                   encoding="utf-8")
    return 1 if any(isinstance(r, str) for _, r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
