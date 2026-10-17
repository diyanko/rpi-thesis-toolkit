#!/usr/bin/env python3
"""Tests for how package.py rewrites and checks links in shipped Markdown.
Needs Pandoc, as package.py does.

    python3 scripts/test_package.py
"""
import io
from pathlib import Path
import sys
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import package

SHIPPED = {"README.md", "docs/a.md"}
REPO = package.repository_url() + "/blob/v1.2.3/CREDITS.md"


def ship(text):
    return package.shipped_markdown("README.md", text, SHIPPED, "1.2.3")


def broken_in(text):
    """The message check_links raises for a ZIP holding README.md and docs/a.md, or ''."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr("README.md", text)
        z.writestr("docs/a.md", "x")
    with zipfile.ZipFile(buffer) as z:
        try:
            package.check_links("test ZIP", z)
        except SystemExit as error:
            return str(error)
    return ""


class Rewrite(unittest.TestCase):
    def test_outside_files_become_repository_links(self):
        self.assertEqual(ship("[c](CREDITS.md)"), f"[c]({REPO})")
        self.assertEqual(ship("[c](CREDITS.md#top)"), f"[c]({REPO}#top)")

    def test_shipped_absolute_and_fragment_links_stay(self):
        text = "[a](docs/a.md) [b](https://example.org/x) [c](#here) [d](mailto:a@b.c)"
        self.assertEqual(ship(text), text)

    def test_title(self):
        self.assertEqual(ship('[c](CREDITS.md "Credits")'), f'[c]({REPO} "Credits")')
        self.assertEqual(ship("[c](CREDITS.md 'Credits')"), f"[c]({REPO} 'Credits')")

    def test_angle_brackets(self):
        self.assertEqual(ship("[c](<CREDITS.md>)"), f"[c](<{REPO}>)")

    def test_reference_definition(self):
        self.assertEqual(ship("[c][id]\n\n[id]: CREDITS.md\n"), f"[c][id]\n\n[id]: {REPO}\n")

    def test_image(self):
        self.assertEqual(ship("![alt](CREDITS.md)"), f"![alt]({REPO})")

    def test_code_span_is_left_alone(self):
        text = "Write `[text](notes.md)` and ``[t](CREDITS.md)`` like that."
        self.assertEqual(ship(text), text)

    def test_escaped_backtick_opens_no_span(self):
        self.assertEqual(ship("\\` [c](CREDITS.md) ` and `x`"), f"\\` [c]({REPO}) ` and `x`")

    def test_definition_on_next_line(self):
        self.assertEqual(ship('[c][id]\n\n[id]:\n  CREDITS.md "Credits"\n'), f'[c][id]\n\n[id]:\n  {REPO} "Credits"\n')

    def test_title_with_escaped_quotes(self):
        self.assertEqual(ship('[c](CREDITS.md "Read \\"credits\\"")'), f'[c]({REPO} "Read \\"credits\\"")')

    def test_fenced_block_is_left_alone(self):
        for fence in ("```", "~~~", "`````"):
            text = f"{fence}md\n[text](notes.md)\n{fence}\n[c](CREDITS.md)"
            self.assertEqual(ship(text), f"{fence}md\n[text](notes.md)\n{fence}\n[c]({REPO})")

    def test_indented_code_and_escaped_brackets_stay_literal(self):
        # Audit: the old scanner rewrote (or refused) links that are not links.
        for text in ("Text.\n\n    [example](missing.md)\n", "\\[literal](missing.md)\n"):
            self.assertEqual(ship(text), text)

    def test_balanced_parentheses_and_escaped_destinations(self):
        text = "[a](docs/a(v2).md) ![b](docs/a\\(v2\\).md)"
        self.assertEqual(package.shipped_markdown("README.md", text, SHIPPED | {"docs/a(v2).md"}, "1.2.3"), text)

    def test_only_the_link_is_rewritten_not_the_same_words_in_code(self):
        text = "`CREDITS.md` and [c](CREDITS.md) and\n\n```\n[c](CREDITS.md)\n```\n"
        self.assertEqual(ship(text), f"`CREDITS.md` and [c]({REPO}) and\n\n```\n[c](CREDITS.md)\n```\n")

    def test_a_link_written_another_way_stops_the_build(self):
        # Pandoc reads CREDITS&#46;md as CREDITS.md; rather than guess where it is written, refuse.
        with self.assertRaisesRegex(SystemExit, "could not find"):
            ship("[c](CREDITS&#46;md)")

    def test_missing_target_is_an_error(self):
        with self.assertRaises(SystemExit):
            ship("[x](no-such-file.md)")


class Check(unittest.TestCase):
    def test_good_links_pass(self):
        text = "[a](docs/a.md) [b](https://example.org) [c](#x)\n\n[id]: docs/a.md\n"
        self.assertEqual(broken_in(text), "")

    def test_each_form_is_reported(self):
        for text in ('[t](gone.md "title")', "[t](<gone.md>)", "[t][id]\n\n[id]: gone.md", "![a](gone.md)", "[t](gone.md)"):
            self.assertIn("gone.md", broken_in(text), text)

    def test_code_is_not_reported(self):
        self.assertEqual(broken_in("`[t](gone.md)`\n\n```\n[t](gone.md)\n```\n"), "")
        self.assertEqual(broken_in("Text.\n\n    [t](gone.md)\n\n\\[literal](gone.md)\n"), "")

    def test_unused_reference_definition_is_not_a_rendered_link(self):
        self.assertEqual(broken_in("[unused]: gone.md\n"), "")


if __name__ == "__main__":
    unittest.main()
