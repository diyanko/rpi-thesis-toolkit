#!/usr/bin/env python3
"""Optional controls must not move content when their scripts initialize."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chrome import Chrome, LocalServer
from common import find_chrome

ROOT = Path(__file__).resolve().parents[2]
CHROME = find_chrome()


@unittest.skipUnless(CHROME, 'no Chrome or Chromium')
class HeaderLayout(unittest.TestCase):
    def test_revealing_each_header_control_preserves_geometry(self):
        page = b'''<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
          <link rel="stylesheet" href="/site/site.css">
          <header class="site-header"><div class="brand"><a class="wordmark">RPI Thesis Toolkit</a><span>Unofficial</span></div>
          <div class="header-tools"><button class="search-open search-header" hidden><svg class="search-icon"></svg><span>Search</span></button>
          <div class="appearance" hidden><button class="appearance-toggle">A</button></div></div></header>
          <main>Content must stay in place as optional controls appear.</main>'''
        with LocalServer(ROOT, lambda path, query: (page, 'text/html') if path == '/fixture' else None) as server, Chrome(CHROME) as browser:
            for width in (390, 412, 1280):
                with self.subTest(width=width):
                    browser.viewport(width, 823)
                    browser.open(server.url + '/fixture')
                    browser.evaluate('document.fonts.ready')
                    geometry = "JSON.stringify(['header','.brand','main'].map(s=>document.querySelector(s).getBoundingClientRect().toJSON()))"
                    before = browser.evaluate(geometry)
                    for selector in ('.search-header', '.appearance'):
                        self.assertEqual(browser.evaluate(f"getComputedStyle(document.querySelector('{selector}')).visibility"), 'hidden')
                        browser.evaluate(f"document.querySelector('{selector}').hidden=false")
                        self.assertEqual(browser.evaluate(geometry), before)


if __name__ == '__main__':
    unittest.main()
