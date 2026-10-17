#!/usr/bin/env python3
"""Settings schema drift, browser behavior, and generated starter compilation.

    python3 -B scripts/tests/test_settings.py

Uses the existing stdlib Chrome driver. TeX and browser cases skip if their
runtimes are absent; generation and reference-table checks still run.
"""
import base64
import itertools
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_site
from chrome import Chrome, LocalServer
from common import ROOT, find_chrome
import settings
import regressions

VALID = {"title": "A study of communities", "author": "Your full name",
         "degree": "doctoral", "department": "Department of Physics, Applied Physics and Astronomy",
         "graduation-month": "May", "graduation-year": "2027"}
COMMITTEE = [{"name": "Your committee chair", "role": "Chair"},
             {"name": "Committee member two", "role": ""}]


# A synthetic 2 by 2 pixel image; this is not RPI artwork.
JPEG = base64.b64decode(
    '/9j/4AAQSkZJRgABAQAASABIAAD/4QBMRXhpZgAATU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAAqADAAQAAAABAAAAAgAAAAD/7QA4UGhvdG9zaG9wIDMuMAA4QklNBAQAAAAAAAA4QklNBCUAAAAAABDUHYzZjwCyBOmACZjs+EJ+/8AAEQgAAgACAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/bAEMAAgICAgICAwICAwUDAwMFBgUFBQUGCAYGBgYGCAoICAgICAgKCgoKCgoKCgwMDAwMDA4ODg4ODw8PDw8PDw8PD//bAEMBAgICBAQEBwQEBxALCQsQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEP/dAAQAAf/aAAwDAQACEQMRAD8AKKKKAP/Z'
)

def png_fixture():
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    pixels = (b"\x00" + b"\x80\x80\x80" * 2) * 2
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))


class Schema(unittest.TestCase):
    def test_guide_table_and_class_share_schema(self):
        data = settings.load()
        self.assertEqual(len(data["keys"]), 11)
        self.assertEqual(data["chairRoles"], ["Chair", "Co-Chair"])
        self.assertIn("| `degree-name` |", data["table"])
        self.assertEqual(json.loads(settings.javascript(data).split("export default ")[1][:-2]), data)

    def test_drift_stops_generation(self):
        for filename, before, after in (
            ("docs/going-further.md", "`engineering-doctorate` |", "`engineering` |"),
            ("docs/going-further.md", "`false` (default)", "`true` (default)"),
            ("rpi-thesis.cls", "[0-9]{4}", "[0-9]{5}"),
            ("rpi-thesis.cls", "department .tl_gset:N", "field .tl_gset:N"),
        ):
            with self.subTest(filename=filename, before=before), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                (folder / "docs").mkdir()
                for source in ("rpi-thesis.cls", "docs/going-further.md"):
                    text = (ROOT / source).read_text(encoding="utf-8")
                    if source == filename:
                        self.assertIn(before, text)
                        text = text.replace(before, after)
                    (folder / source).write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    settings.load(folder)

    @unittest.skipUnless(shutil.which("pandoc"), "no Pandoc")
    def test_reference_table_online_and_offline(self):
        for offline in (False, True):
            with self.subTest(offline=offline):
                site = build_site.Site(offline=offline)
                html = site.render("docs/settings-builder.md")
                self.assertNotIn("{{settings-table}}", html)
                self.assertIn("engineering-doctorate", html)
                self.assertIn("data-settings-nojs", html)
                self.assertIn('data-settings-builder hidden', html)
                self.assertEqual("settings/ui.js" in html, not offline)


@unittest.skipUnless(find_chrome(), "no Chrome or Chromium found")
class Browser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="test_settings_")
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.folder = Path(cls.tmp.name)
        (cls.folder / "settings").mkdir()
        (cls.folder / "guide").mkdir()
        for name in ("core", "ui"):
            shutil.copyfile(ROOT / f"site/settings/{name}.js", cls.folder / f"settings/{name}.js")
        (cls.folder / "settings/data.js").write_text(settings.javascript(settings.load()), encoding="utf-8")
        if shutil.which("pandoc"):
            html = build_site.Site(offline=False).render("docs/settings-builder.md")
        else:
            doc = (ROOT / "docs/settings-builder.md").read_text(encoding="utf-8")
            form = doc[doc.index('<div class="tool settings-builder"'):doc.index("## Settings reference")]
            html = '<!doctype html><meta charset="utf-8">' + form + '<script src="../settings/ui.js" defer></script>'
        (cls.folder / "guide/settings-builder.html").write_text(html, encoding="utf-8")
        cls.server = LocalServer(cls.folder)
        cls.addClassCleanup(cls.server.close)
        cls.browser = Chrome(find_chrome())
        cls.addClassCleanup(cls.browser.close)
        cls.browser.open(cls.server.url + "/guide/settings-builder.html")
        cls.wait_for_form()

    @classmethod
    def wait_for_form(cls):
        cls.browser.evaluate("""(async () => {
          const deadline = Date.now()+5000;
          while (document.querySelector('[data-settings-builder]').hidden) {
            if (Date.now()>deadline) throw Error('Settings page script did not initialize');
            await new Promise(resolve => setTimeout(resolve,20));
          }
        })()""")

    def generate(self, values=None, committee=None):
        return self.browser.evaluate(f"(async () => (await import('../settings/core.js')).generate({json.dumps(VALID if values is None else values)},"
                                     f"{json.dumps(COMMITTEE if committee is None else committee)},(await import('../settings/data.js')).default))()")

    def test_all_degree_month_and_boolean_choices(self):
        data = settings.load()
        for degree, month in itertools.product(data["keys"]["degree"]["choices"], data["keys"]["graduation-month"]["choices"]):
            self.assertFalse(self.generate({**VALID, "degree": degree, "graduation-month": month})["errors"])
        for key, spec in data["keys"].items():
            if spec["type"] == "boolean":
                for value in spec["choices"]:
                    self.assertFalse(self.generate({**VALID, key: value})["errors"])
                self.assertIn("accepts boolean values only.", self.generate({**VALID, key: "True"})["errors"][0])

    def test_rejections(self):
        for key, value, fragment in (("degree", "Doctoral", 'Unknown degree choice "Doctoral"'),
                                     ("degree", "unknown", 'Unknown degree choice "unknown"'),
                                     ("graduation-month", "may", 'Unknown graduation month "may"'),
                                     ("graduation-month", "January", 'Unknown graduation month "January"'),
                                     ("graduation-year", "２０２７", "Graduation year must have four digits"),
                                     ("graduation-year", "2027 ", "Graduation year must have four digits"),
                                     ("graduation-year", "202", "Graduation year must have four digits"),
                                     ("degree-name", " ", "Missing degree in metadata.tex"),
                                     ("Title", "a title", 'Unknown setting "Title"'),
                                     ("toString", "value", 'Unknown setting "toString"')):
            with self.subTest(key=key, value=value):
                result = self.generate({**VALID, key: value})
                self.assertEqual(result["text"], "")
                self.assertTrue(any(fragment in error for error in result["errors"]), result)
        for key in ("title", "author", "department", "graduation-month", "graduation-year"):
            values = dict(VALID)
            del values[key]
            self.assertIn(f"Missing {key} in metadata.tex", self.generate(values)["errors"])
        for key in ("title", "author", "department"):
            self.assertIn(f"Missing {key} in metadata.tex", self.generate({**VALID, key: " \n\t"})["errors"])
        self.assertFalse(self.generate({key: val for key, val in VALID.items() if key != "degree"})["errors"])

    def test_committee_validation_and_order(self):
        self.assertIn("No committee members in metadata.tex", self.generate(committee=[])["errors"])
        self.assertIn("Blank committee member name in metadata.tex", self.generate(committee=[{"name": " ", "role": "Chair"}])["errors"])
        errors = self.generate(committee=[{"name": "Member", "role": "chair"}])["errors"]
        self.assertEqual(errors, ["Committee chair is missing: roles given in metadata.tex were [chair], but the role must be written [Chair] or [Co-Chair]"])
        self.assertEqual(self.generate(committee=[{"name": "Member", "role": ""}])["errors"], ["Committee chair is missing"])
        committee = [{"name": "Other", "role": "Reader"}, {"name": "First chair", "role": "Co-Chair"},
                     {"name": "Second chair", "role": "Chair"}] + [{"name": f"Member {i}", "role": ""} for i in range(20)]
        result = self.generate(committee=committee)
        self.assertFalse(result["errors"])
        self.assertLess(result["text"].index("First chair"), result["text"].index("Second chair"))
        self.assertLess(result["text"].index("Second chair"), result["text"].index("Other"))

    def test_seal_names_are_readable_and_windows_separators_work(self):
        for path in ("assets/my_seal.jpg", "assets/RPI seal (1).jpeg", "assets/Seal.PNG"):
            result = self.generate({**VALID, "seal-file": path})
            self.assertIn(f"seal-file = {{{path}}}", result["text"])
            self.assertNotIn("char_generate", result["text"])
        result = self.generate({**VALID, "seal-file": r"assets\RPI seal (1).jpeg"})
        self.assertIn("seal-file = {assets/RPI seal (1).jpeg}", result["text"])

    def test_select_seal_filename_without_reading_or_uploading(self):
        self.browser.open(self.server.url + "/guide/settings-builder.html?seal")
        self.wait_for_form()
        selected = self.browser.evaluate("""(() => {
          const input = document.getElementById('settings-seal-filename');
          const data = new DataTransfer();
          const file = new File(['not image data'], 'RPI seal (1).JPEG');
          file.text = file.arrayBuffer = file.stream = () => {throw Error('Image must not be read')};
          data.items.add(file); input.files = data.files;
          input.dispatchEvent(new Event('change', {bubbles:true}));
          return {path: document.getElementById('setting-seal-file').value, files: input.files.length};
        })()""")
        self.assertEqual(selected, {"path": "assets/RPI seal (1).JPEG", "files": 0})
        self.assertIn("assets folder", self.browser.evaluate("document.getElementById('seal-file-help').textContent"))

    @unittest.skipUnless(shutil.which("pdflatex"), "no TeX Live (pdflatex)")
    @unittest.skipUnless(regressions.PdfReader or shutil.which("pdftotext"), "no PDF text reader")
    def test_seal_filenames_missing_and_present(self):
        cases = ["my_seal.jpg", "RPI seal (1).jpeg", "seal.png", "seal.PNG", "seal.JPG", "seal.JPEG",
                 "seal #1%{draft}^~.png", "seal & $1.png"]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shutil.copyfile(ROOT / "rpi-thesis.cls", folder / "rpi-thesis.cls")
            (folder / "assets").mkdir()
            for index, name in enumerate(cases):
                with self.subTest(filename=name):
                    path = "assets/" + name
                    metadata = self.generate({**VALID, "seal-file": path})["text"]
                    (folder / "test.tex").write_text("\\documentclass{rpi-thesis}\n" + metadata + "\n\\begin{document}\\maketitle\\end{document}", encoding="utf-8")
                    for exists in (False, True):
                        if exists:
                            (folder / path).write_bytes(png_fixture() if name.lower().endswith(".png") else JPEG)
                        run = subprocess.run(["pdflatex", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", "test.tex"], cwd=folder, capture_output=True, text=True)
                        self.assertEqual(run.returncode, 0, run.stdout[-2000:])
                        text = regressions.pdf_text(folder / "test.pdf")
                        log = (folder / "test.log").read_text(encoding="utf-8", errors="replace")
                        if exists:
                            self.assertNotIn("RPI seal:", text)
                            self.assertNotIn("RPI seal not found", " ".join(log.split()))
                        else:
                            self.assertIn(path, text)
                            self.assertNotIn("char_generate", text)
                            self.assertNotIn("csname", text)
                            self.assertIn("No file " + path + ".", log.replace("\n", ""))
                    (folder / path).unlink()

    def test_override_escaping_and_text_safety(self):
        result = self.generate({**VALID, "degree-name": "A custom degree", "title": r"100% of A&B_#1 {x} $y$ ~ ^ \input"})
        self.assertLess(result["text"].index("degree ="), result["text"].index("degree-name ="))
        self.assertIn(r"100\% of A\&B\_\#1 \{x\} \$y\$ \textasciitilde{} \textasciicircum{} \textbackslash{}input", result["text"])
        self.assertFalse(result["errors"])

    @unittest.skipUnless(shutil.which("pandoc"), "no Pandoc")
    def test_rendered_page_without_javascript(self):
        self.browser.call("Emulation.setScriptExecutionDisabled", value=True)
        try:
            self.browser.open(self.server.url + "/guide/settings-builder.html?nojs")
            self.assertTrue(self.browser.evaluate("document.querySelector('[data-settings-builder]').hidden"))
            self.assertFalse(self.browser.evaluate("document.querySelector('[data-settings-nojs]').hidden"))
            self.assertIn("engineering-doctorate", self.browser.evaluate("document.querySelector('table').textContent"))
            self.assertEqual(self.browser.evaluate("document.querySelector('table').rows.length"), 12)
        finally:
            self.browser.call("Emulation.setScriptExecutionDisabled", value=False)
            self.browser.open(self.server.url + "/guide/settings-builder.html?js")
            self.wait_for_form()

    def test_form_updates_removal_and_copy_fallback(self):
        self.browser.open(self.server.url + "/guide/settings-builder.html?ui")
        self.wait_for_form()
        self.assertFalse(self.browser.evaluate("document.querySelector('[data-settings-builder]').hidden"))
        self.assertTrue(self.browser.evaluate("document.querySelector('[data-settings-copy]').disabled"))
        values = {**VALID, "title": '<script>alert("text")</script>'}
        result = self.browser.evaluate(f"""(() => {{
          const values = {json.dumps(values)};
          for (const [key,value] of Object.entries(values)) document.getElementById('setting-'+key).value=value;
          document.querySelector('[data-member-name]').value='Your committee chair';
          document.querySelector('form').dispatchEvent(new Event('input'));
          return {{output:document.querySelector('[data-settings-output]').textContent, disabled:document.querySelector('[data-settings-copy]').disabled}};
        }})()""")
        self.assertFalse(result["disabled"])
        self.assertIn('<script>', result["output"])
        self.assertFalse(self.browser.evaluate("!!window.alerted"))
        self.browser.evaluate("Object.defineProperty(navigator, 'clipboard', {value:{writeText:async()=>{throw Error('denied')}}}); document.querySelector('[data-settings-copy]').click()")
        self.assertEqual(self.browser.evaluate("document.querySelector('[data-settings-status]').textContent"), "Select and copy the block below.")
        self.browser.evaluate("document.querySelector('[data-settings-add]').click()")
        self.assertTrue(self.browser.evaluate("document.querySelector('[data-settings-copy]').disabled"))
        self.assertEqual(self.browser.evaluate("document.querySelector('[data-settings-output]').textContent"), "")
        self.browser.evaluate("document.querySelectorAll('[data-settings-members] button')[1].click()")
        self.assertFalse(self.browser.evaluate("document.querySelector('[data-settings-copy]').disabled"))
        self.browser.evaluate("document.getElementById('setting-graduation-year').value='27'; document.querySelector('form').dispatchEvent(new Event('input'))")
        self.assertTrue(self.browser.evaluate("document.querySelector('[data-settings-copy]').disabled"))
        self.assertEqual(self.browser.evaluate("document.querySelector('[data-settings-output]').textContent"), "")
        self.assertEqual(self.browser.evaluate("[localStorage.length,sessionStorage.length]"), [0, 0])
        self.browser.open(self.server.url + "/guide/settings-builder.html?reload")
        self.wait_for_form()
        self.assertEqual(self.browser.evaluate("document.getElementById('setting-title').value"), "")

    @unittest.skipUnless(shutil.which("pdflatex"), "no TeX Live (pdflatex)")
    def test_messages_match_class_errors(self):
        cases = [({**VALID, "degree": "Doctoral"}, COMMITTEE),
                 ({**VALID, "graduation-month": "may"}, COMMITTEE),
                 ({**VALID, "title": ""}, COMMITTEE),
                 ({**VALID, "degree-name": " "}, COMMITTEE),
                 ({**VALID, "graduation-year": "202"}, COMMITTEE),
                 ({**VALID, "list-of-tables": "True"}, COMMITTEE),
                 ({**VALID, "wrong-key": "true"}, COMMITTEE),
                 (VALID, []), (VALID, [{"name": "", "role": "Chair"}]),
                 (VALID, [{"name": "Member", "role": "chair"}])]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shutil.copyfile(ROOT / "rpi-thesis.cls", folder / "rpi-thesis.cls")
            for values, committee in cases:
                with self.subTest(values=values, committee=committee):
                    # Deliberately invalid metadata: bypass the generator's rejection.
                    block = "\\thesissetup{\n" + "\n".join(f"{key} = {{{value}}}," for key, value in values.items()) + "\n}\n"
                    block += "\n".join(f"\\committeemember[{member['role']}]{{{member['name']}}}" for member in committee)
                    (folder / "test.tex").write_text("\\documentclass{rpi-thesis}\n" + block + "\n\\begin{document}\\maketitle\\end{document}", encoding="utf-8")
                    run = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape", "test.tex"], cwd=folder, capture_output=True, text=True)
                    self.assertNotEqual(run.returncode, 0)
                    log = (folder / "test.log").read_text(encoding="utf-8", errors="replace")
                    # TeX wraps at max_print_line and inserts indentation in errors.
                    log = re.sub(r"\s+", " ", log)
                    first = self.generate(values, committee)["errors"][0]
                    self.assertTrue(re.sub(r"\s+", "", first) in re.sub(r"\s+", "", log), f"{first}\n{run.stdout[-1800:]}")

    @unittest.skipUnless(all(shutil.which(tool) for tool in ("latexmk", "pdflatex", "biber")), "no TeX Live (latexmk, pdflatex, biber)")
    def test_generated_metadata_compiles_in_starter(self):
        values = {**VALID, "degree": "masters", "degree-name": "Master of Science", "graduation-month": "December",
                  "title": r"A study of 100% of A&B_#1 {x} $y$ ~ ^ \text", "author": "Your full name",
                  "copyright-page": "true", "list-of-tables": "true", "list-of-figures": "true",
                  "seal-file": "assets/missing_seal%file.jpg"}
        result = self.generate(values, [{"name": "Member, Two", "role": "Reader]"},
                                        {"name": "Member three", "role": "Reader [external]"}, *COMMITTEE])
        self.assertFalse(result["errors"])
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for name in ("main.tex", "preamble.tex", "rpi-thesis.cls", "references.bib", "latexmkrc"):
                shutil.copyfile(ROOT / name, folder / name)
            for name in ("chapters", "frontmatter", "appendices", "figures"):
                shutil.copytree(ROOT / name, folder / name)
            (folder / "assets").mkdir()
            (folder / "metadata.tex").write_text(result["text"], encoding="utf-8")
            run = subprocess.run(["latexmk", "-norc", "-r", "latexmkrc", "-pdf", "-outdir=build", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=folder, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout[-6000:])
            self.assertTrue((folder / "build/main.pdf").is_file())
            log = (folder / "build/main.log").read_text(encoding="utf-8", errors="replace")
            self.assertNotIn("Missing character:", log)
            self.assertIn("char_generate:nn", result["text"])
            self.assertIn(r"\committeemember[Reader {[}external{]}]", result["text"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
