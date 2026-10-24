#!/usr/bin/env python3
"""Indexing regressions: inspect built HTML and discovery files. Stdlib only."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_checks import validate_search
from build_site import write_llms
from types import SimpleNamespace


class SearchDiscovery(unittest.TestCase):
    url = "https://example.org/toolkit"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "guide").mkdir()
        self.indexed = {"index.html": ("Home", "Start here"),
                        "guide/write.html": ("Write", "Writing &amp; citations")}
        self.addresses = [self.url + "/", self.url + "/guide/write.html"]
        for page, address in zip(self.indexed, self.addresses):
            (self.root / page).write_text(f'<link rel="canonical" href="{address}">')
        (self.root / "404.html").write_text('<meta name="robots" content="noindex">')
        self.sitemap(self.addresses)
        self.robots("User-agent: *\nAllow: /\n")

    def sitemap(self, addresses):
        (self.root / "sitemap.xml").write_text(
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join(f"<url><loc>{address}</loc></url>" for address in addresses) + "</urlset>")

    def robots(self, text):
        (self.root / "robots.txt").write_text(text + f"\nSitemap: {self.url}/sitemap.xml\n")

    def check(self):
        return validate_search(self.root, self.url, self.indexed)

    def test_project_path_and_noindex_404_are_valid(self):
        self.assertEqual(self.check(), [])

    def test_missing_duplicate_and_redirect_sitemap_entries_fail(self):
        for addresses in (self.addresses[:1], self.addresses * 2,
                          self.addresses + [self.url + "/guide/old.html"]):
            with self.subTest(addresses=addresses):
                self.sitemap(addresses)
                self.assertTrue(any("sitemap.xml:" in error for error in self.check()))

    def test_relative_or_duplicate_canonical_fails(self):
        for html in ('<link rel="canonical" href="/">',
                     f'<link rel="canonical" href="{self.url}/">' * 2):
            with self.subTest(html=html):
                (self.root / "index.html").write_text(html)
                self.assertTrue(any("canonical URL" in error for error in self.check()))

    def test_googlebot_specific_and_general_indexing_blocks_fail(self):
        for name, content in (("Googlebot", "NOINDEX, follow"), ("robots", "none")):
            with self.subTest(name=name):
                (self.root / "index.html").write_text(
                    f'<link rel="canonical" href="{self.url}/">'
                    f'<meta name="{name}" content="{content}">')
                self.assertTrue(any("indexing block" in error for error in self.check()))

    def test_agent_specific_crawl_block_fails(self):
        self.robots("User-agent: *\nAllow: /\nUser-agent: OAI-SearchBot\nDisallow: /toolkit/\n")
        self.assertTrue(any("OAI-SearchBot is blocked" in error for error in self.check()))

    def test_llms_lists_current_content_and_history_without_html_entities(self):
        site = SimpleNamespace(url=self.url, meta=self.indexed, repo="https://github.com/example/toolkit")
        write_llms(site, self.root)
        text = (self.root / "llms.txt").read_text()
        self.assertIn(f"({self.url}/guide/write.html)", text)
        self.assertIn("Writing & citations", text)
        self.assertIn("/releases)", text)
        self.assertIn("/commits/main/)", text)
        self.assertNotIn("404.html", text)
        self.assertIn("superseded advice", text)


if __name__ == "__main__":
    unittest.main()
