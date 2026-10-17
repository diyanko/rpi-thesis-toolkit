#!/usr/bin/env python3
"""OGE rules, written once in docs/project/requirements.md, for the rest of the toolkit.

    python3 scripts/rules.py     check the map and list each rule id with the
                                 guide pages that use it

Every rule row in the requirements map starts its Rule cell with an id in
code, such as `page-size`. Guide pages refer to a rule instead of restating it, and
scripts/build_site.py fills the references in before Pandoc runs:

    {{rule:page-size}}           the rest of the row's Rule cell, as written
    {{cite:page-size}}           the row's Manual cell, linked to its section
    {{cite:page-size,lists}}     several rows' citations, each piece once

References inside `code` or fenced code blocks are left alone. An unknown id
stops the build. The rows of the **Measurements** table give the numbers a PDF
check compares with; embed() hands rules and measurements to a page script as
JSON (see the docstring there). Python standard library only.
"""

from functools import lru_cache
import json
import posixpath
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "docs/project/requirements.md"
LABELLED = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)*)` +(\S.*)")  # `page-size` US letter, ...
KINDS = {"Rule": "Manual", "Measure": "pt"}  # first column -> the column that marks the table
# Code first, so a reference written inside `code` or a fence is shown as is.
REFERENCE = re.compile(r"(?P<code>^```.*?^```[^\n]*$|`[^`\n]+`)|\{\{(?P<kind>rule|cite):(?P<ids>[^{}]*)\}\}",
                       re.S | re.M)


def slug(heading):
    """The anchor Pandoc and GitHub give a heading such as 'Captions, tables and figures'."""
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", heading.strip().lower()))


def plain(markdown):
    """Markdown cell text -> plain text: no backticks, emphasis, or link targets."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", markdown)
    return " ".join(re.sub(r"[`*]", "", text).split())


def cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse(text, source=SOURCE):
    """Return (rules, measures) from the map's Markdown.

    rules:    id -> {"rule", "cite", "where", "checked", "section"} (Markdown cells;
              section is the anchor of the ### heading above the table)
    measures: id -> {"measure", "pt", "rule"}
    Raises SystemExit naming the line for a missing, malformed, or repeated id."""
    rules, measures, section, header = {}, {}, "", None
    for number, line in enumerate(text.splitlines(), 1):
        where = f"{source}:{number}"
        if line.startswith("#"):
            section, header = slug(line.lstrip("#")), None
            continue
        if not line.startswith("|"):
            header = None
            continue
        row = cells(line)
        if header is None:
            header = row
            continue
        if set("".join(row)) <= set("-: ") or KINDS.get(header[0]) not in header[1:]:
            continue
        if len(row) != len(header):
            raise SystemExit(f"{where}: this row has {len(row)} cells but the table has {len(header)} columns.")
        values = dict(zip(header, row))
        label = LABELLED.fullmatch(row[0])
        if not label:
            raise SystemExit(f"{where}: start the {header[0]} cell with an id in code, such as "
                             "`page-size` (lowercase letters, digits, hyphens), then the text.")
        key, values[header[0]] = label[1], label[2]
        if key in rules or key in measures:
            raise SystemExit(f"{where}: the id `{key}` is used twice; give each row its own.")
        if header[0] == "Rule":
            if not values["Manual"]:
                raise SystemExit(f"{where}: the rule `{key}` needs its Manual cell.")
            rules[key] = {"rule": values["Rule"], "cite": values["Manual"], "where": values.get("Where", ""),
                          "checked": values.get("Checked by", ""), "section": section}
        else:
            try:
                points = float(values["pt"])
            except ValueError:
                raise SystemExit(f"{where}: the pt cell of `{key}` must be a number.") from None
            measures[key] = {"measure": values["Measure"], "pt": int(points) if points.is_integer() else points,
                             "rule": values["Rule"].strip("`")}
    for key, measure in measures.items():
        if measure["rule"] not in rules:
            raise SystemExit(f"{source}: the measurement `{key}` names the rule `{measure['rule']}`, "
                             "which has no row; use a rule id from the requirements map.")
    return rules, measures


@lru_cache(maxsize=None)
def load():
    return parse((ROOT / SOURCE).read_text(encoding="utf-8"))


def cite(keys, rules, link):
    """Linked citations for several rules; a piece such as 'FC' is shown once."""
    shown, groups = set(), []  # [section, pieces]; rules from one section share a link
    for key in keys:
        pieces = [piece for piece in rules[key]["cite"].split("; ") if piece not in shown]
        shown.update(pieces)
        if pieces and groups and groups[-1][0] == rules[key]["section"]:
            groups[-1][1].extend(pieces)
        elif pieces:
            groups.append([rules[key]["section"], pieces])
    return "; ".join(f"[{'; '.join(pieces)}]({link}#{section})" for section, pieces in groups)


def expand(text, source, rules=None):
    """Fill in {{rule:...}} and {{cite:...}} in the Markdown of `source` (a path
    such as docs/reviewer-checklist.md). Returns (text, problems, ids used)."""
    rules = load()[0] if rules is None else rules
    link = posixpath.relpath(SOURCE, posixpath.dirname(source) or ".")
    problems, used = [], []

    def replace(match):
        if match["code"]:
            return match[0]
        keys = [key.strip() for key in match["ids"].split(",")]
        unknown = [key for key in keys if key not in rules]
        if unknown or (match["kind"] == "rule" and len(keys) != 1):
            problems.append(
                f"{source}: {match[0]} " + (f"names no rule ({', '.join(unknown)})" if unknown
                                            else "takes exactly one id")
                + f"; use a rule id from {SOURCE}, such as {{{{{match['kind']}:page-size}}}}.")
            return match[0]
        used.extend(keys)
        return rules[keys[0]]["rule"] if match["kind"] == "rule" else cite(keys, rules, link)

    return REFERENCE.sub(replace, text), problems, used


def data():
    """The rules and measurements as plain values, for a page script."""
    rules, measures = load()
    return {"source": SOURCE,
            "rules": {key: {"rule": plain(row["rule"]), "cite": row["cite"], "section": row["section"]}
                      for key, row in rules.items()},
            "measures": measures}


def embed():
    """An inert <script type="application/json" id="oge-rules"> block for a page that
    loads a page script. A script reads it with
    JSON.parse(document.getElementById("oge-rules").textContent) and gets
    {"source": "docs/project/requirements.md",
     "rules": {id: {"rule": plain text, "cite": "§2.2 p. 16; FC", "section": anchor}},
     "measures": {id: {"measure": label, "pt": number, "rule": rule id}}}.
    It works from file: URLs and needs no extra file in the website."""
    payload = json.dumps(data(), ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return '\n<script type="application/json" id="oge-rules">' + payload.replace("<", "\\u003c") + "</script>\n"


def main():
    rules, measures = load()
    pages, failed = {}, False
    for path in sorted((ROOT / "docs").glob("*.md")):
        source = path.relative_to(ROOT).as_posix()
        _, problems, used = expand(path.read_text(encoding="utf-8"), source, rules)
        for problem in problems:
            print("ERROR: " + problem)
            failed = True
        for key in used:
            pages.setdefault(key, set()).add(path.name)
    for key in rules:
        print(f"{key:24} {rules[key]['cite']:28} {', '.join(sorted(pages.get(key, ()))) or '-'}")
    print(f"{len(rules)} rules, {len(measures)} measurements; "
          f"{len(pages)} rules used by guide pages.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
