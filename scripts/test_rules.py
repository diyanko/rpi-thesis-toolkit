#!/usr/bin/env python3
"""Tests for scripts/rules.py: rule ids in the requirements map and the
{{rule:...}} / {{cite:...}} references that guide pages use. Stdlib only.

    python3 scripts/test_rules.py
"""
import json
import re
import unittest
from pathlib import Path

import rules

ROOT = Path(__file__).resolve().parent.parent
MAP = """# Map

### Page numbers

| Rule | Manual | Where | Checked by |
| --- | --- | --- | --- |
| `body-arabic` Body Arabic from 1 | §2.2 p. 16 | cls | check |
| `number-place` Numbers 0.75 in from the edge | §2.2 pp. 16-17; FC | cls | check |

### Fonts

| Rule | Manual | Where | Checked by |
| --- | --- | --- | --- |
| `black-text` All text black | §2.1 p. 16; FC | cls | visual |

### Measurements

| Measure | pt | Rule |
| --- | --- | --- |
| `edge` Edge distance | 54 | `number-place` |
"""


class Parse(unittest.TestCase):
    def test_rows_sections_and_measures(self):
        found, measures = rules.parse(MAP)
        self.assertEqual(found["number-place"]["cite"], "§2.2 pp. 16-17; FC")
        self.assertEqual(found["black-text"]["section"], "fonts")
        self.assertEqual(measures["edge"], {"measure": "Edge distance", "pt": 54, "rule": "number-place"})

    def test_repeated_or_missing_id_stops(self):
        with self.assertRaisesRegex(SystemExit, "used twice"):
            rules.parse(MAP.replace("`black-text`", "`body-arabic`"))
        with self.assertRaisesRegex(SystemExit, "start the Rule cell with an id"):
            rules.parse(MAP.replace("`black-text` ", ""))

    def test_measure_needs_a_known_rule(self):
        with self.assertRaisesRegex(SystemExit, "has no row"):
            rules.parse(MAP.replace("54 | `number-place`", "54 | `nowhere`"))


class Expand(unittest.TestCase):
    found = rules.parse(MAP)[0]

    def expand(self, text):
        return rules.expand(text, "docs/page.md", self.found)

    def test_rule_and_cite(self):
        text, problems, used = self.expand("{{rule:black-text}} ({{cite:black-text}}).")
        self.assertEqual(problems, [])
        self.assertEqual(used, ["black-text", "black-text"])
        self.assertEqual(text, "All text black ([§2.1 p. 16; FC](project/requirements.md#fonts)).")

    def test_several_cites_show_each_piece_once_and_share_a_section_link(self):
        text, _, _ = self.expand("{{cite:body-arabic,number-place,black-text}}")
        self.assertEqual(text, "[§2.2 p. 16; §2.2 pp. 16-17; FC](project/requirements.md#page-numbers); "
                               "[§2.1 p. 16](project/requirements.md#fonts)")

    def test_unknown_id_is_a_problem(self):
        _, problems, _ = self.expand("{{cite:no-such-rule}} {{rule:black-text,body-arabic}}")
        self.assertEqual(len(problems), 2)
        self.assertIn("names no rule (no-such-rule)", problems[0])
        self.assertIn("takes exactly one id", problems[1])

    def test_code_is_left_alone(self):
        source = "`{{cite:black-text}}`\n\n```\n{{rule:nothing}}\n```\n"
        self.assertEqual(self.expand(source), (source, [], []))

    def test_link_is_relative_to_the_page(self):
        text, _, _ = rules.expand("{{cite:black-text}}", "README.md", self.found)
        self.assertIn("(docs/project/requirements.md#fonts)", text)


class RealMap(unittest.TestCase):
    def test_every_guide_reference_names_a_rule(self):
        for path in sorted((ROOT / "docs").glob("*.md")):
            _, problems, _ = rules.expand(path.read_text(encoding="utf-8"), f"docs/{path.name}")
            self.assertEqual(problems, [], path.name)

    def test_every_table_in_the_map_is_read(self):
        # A new table with other headings would silently hold rules without ids.
        text = (ROOT / rules.SOURCE).read_text(encoding="utf-8")
        start = text.index("## Requirements map")
        mapped = text[start:text.index("\n## ", start)]
        headers = {line.split(" | ")[0][2:] for line, after in zip(mapped.splitlines(), mapped.splitlines()[1:])
                   if line.startswith("| ") and after.startswith("| ---")}
        self.assertEqual(headers, {"Rule", "Measure", "Status"})
        rows = len(re.findall(r"(?m)^\| `[a-z0-9-]+` ", mapped))
        self.assertEqual(rows, len(rules.load()[0]) + len(rules.load()[1]))

    def test_checker_citations_match_rules(self):
        # site/pdf-check.js cites must stay identical to a row's Manual cell.
        cites = {row["cite"] for row in rules.load()[0].values()}
        script = (ROOT / "site/pdf-check.js").read_text(encoding="utf-8")
        for cite in re.findall(r'\bcite2?: "([^"]+)"', script):
            self.assertTrue(any(cite in full for full in cites), cite)

    def test_embedded_json_is_inert_and_parses(self):
        block = rules.embed()
        self.assertNotIn("</", block[block.index(">") + 1:block.rindex("</script>")])
        payload = json.loads(block[block.index(">") + 1:block.rindex("</script>")])
        self.assertEqual(payload["measures"]["paper-width"]["pt"], 612)
        self.assertEqual(payload["rules"]["page-size"]["cite"], "§2.2 p. 16; FC")


if __name__ == "__main__":
    unittest.main()
