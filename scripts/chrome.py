"""Headless Chrome through its DevTools protocol, and a localhost file server.

Used by ui_check.py (layout sweep and screenshots) and check_pdfs.py (the
"Check your PDF" checks). Python standard library only: a minimal WebSocket
client speaks the DevTools protocol, and http.server serves the files, so
nothing leaves this computer. Maintainer tooling only.
"""
import base64
import errno
import http.server
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen


class WebSocket:
    """Just enough of RFC 6455 for DevTools: text frames, pings, close."""

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
    """Headless Chrome with one tab, driven by DevTools commands. dark=True
    starts it with the dark color scheme preferred, for every frame."""

    def __init__(self, chrome, dark=False):
        self.profile = tempfile.TemporaryDirectory(prefix="chrome_")
        self.process = subprocess.Popen(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
             "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
             f"--blink-settings=preferredColorScheme={0 if dark else 1}",
             f"--user-data-dir={self.profile.name}", "--remote-debugging-port=0", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        port_file = Path(self.profile.name) / "DevToolsActivePort"
        deadline = time.time() + 30
        while not (port_file.exists() and port_file.read_text(encoding="utf-8").count("\n") >= 1):
            if time.time() > deadline or self.process.poll() is not None:
                self.close()
                raise RuntimeError("Chrome did not start its DevTools port")
            time.sleep(0.1)
        port = int(port_file.read_text(encoding="utf-8").split()[0])
        with urlopen(Request(f"http://127.0.0.1:{port}/json/new?about:blank", method="PUT"), timeout=30) as reply:
            target = json.load(reply)
        self.socket = WebSocket(target["webSocketDebuggerUrl"])
        self.next_id = 0
        self.call("Page.enable")
        self.call("Runtime.enable")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

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

    def open(self, url, timeout=60):
        self.call("Page.navigate", url=url)
        deadline = time.time() + timeout
        while self.evaluate("document.readyState") != "complete" or self.evaluate("location.href") != url:
            if time.time() > deadline:
                raise RuntimeError(f"{url} did not finish loading")
            time.sleep(0.05)

    def viewport(self, width, height, mobile=False):
        self.call("Emulation.setDeviceMetricsOverride", width=width, height=height,
                  deviceScaleFactor=1, mobile=mobile)

    def scheme(self, dark):
        """Emulate prefers-color-scheme for the page itself."""
        self.call("Emulation.setEmulatedMedia", media="",
                  features=[{"name": "prefers-color-scheme", "value": "dark" if dark else "light"}])

    def screenshot(self):
        """The viewport as PNG bytes."""
        return base64.b64decode(self.call("Page.captureScreenshot", format="png")["data"])

    def close(self):
        socket = getattr(self, "socket", None)
        if socket and self.process.poll() is None:
            try:
                self.call("Browser.close")
            except (OSError, ConnectionError, RuntimeError):
                pass  # Chrome may close DevTools before acknowledging shutdown.
        if socket:
            socket.sock.close()
        if self.process.poll() is None:
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=10)
        # Chromium helpers may finish profile writes just after its main process.
        for attempt in range(20):
            try:
                self.profile.cleanup()
                break
            except OSError as error:
                if error.errno != errno.ENOTEMPTY or attempt == 19:
                    raise
                time.sleep(0.05)


class LocalServer:
    """Serves a folder on a free 127.0.0.1 port, without touching the folder.
    dynamic(path, query) may answer a request itself with (bytes, content
    type); None falls through to the folder's files."""

    def __init__(self, folder, dynamic=None):
        class Handler(http.server.SimpleHTTPRequestHandler):
            extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                              ".mjs": "text/javascript", ".js": "text/javascript"}

            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(folder), **kwargs)

            def log_message(self, *args):
                pass

            def do_GET(self):
                address = urlsplit(self.path)
                answer = dynamic(address.path, parse_qs(address.query)) if dynamic else None
                if answer is None:
                    return super().do_GET()
                body, kind = answer
                self.send_response(200)
                self.send_header("Content-Type", kind)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        class Threading(http.server.ThreadingHTTPServer):
            request_queue_size = 128
            daemon_threads = True

            def handle_error(self, request, client_address):  # Chrome drops connections
                pass

        self.httpd = Threading(("127.0.0.1", 0), Handler)
        self.port = self.httpd.server_address[1]
        self.url = f"http://127.0.0.1:{self.port}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()
