"""Generate settings/data.js from the class and the guide; never hand-edit data.

build_site.py calls load() on every build. Unsupported class syntax or a guide
key/choice/default mismatch stops the build rather than serving stale choices.
The guide's table also supplies the builder's no-JavaScript reference table.
"""
import json
import re

from common import ROOT


def group(text, start):
    """Read one balanced TeX brace group, returning (content, next offset)."""
    if text[start] != "{":
        raise ValueError("settings: expected a TeX brace group")
    depth = 1
    for end in range(start + 1, len(text)):
        if text[end] == "{":
            depth += 1
        elif text[end] == "}":
            depth -= 1
        if not depth:
            return text[start + 1:end], end + 1
    raise ValueError("settings: unfinished TeX brace group")


def plain(text):
    # Under ExplSyntaxOn, source whitespace disappears; ~ is an explicit space.
    text = re.sub(r"\s+", "", text).replace("~", " ")
    if "\\" in text:
        raise ValueError("settings: unhandled TeX in a validation message: " + text)
    return text


def load(root=ROOT):
    cls = (root / "rpi-thesis.cls").read_text(encoding="utf-8")
    cls = re.sub(r"(?m)%.*$", "", cls)
    start = cls.index(r"\keys_define:nn { rpi/thesis }")
    block, _ = group(cls, cls.index("{", cls.index("}", start) + 1))
    entries = re.findall(r"(?m)^    ([a-z-]+) \.(tl_gset:N|bool_gset:N|choice:)", block)
    defaults_block = re.search(r"\\keys_set:nn \{ rpi/thesis \}\s*\{([^}]+)\}", cls)[1]
    defaults = dict(re.findall(r"([a-z-]+)\s*=\s*([^,\s}]+)", defaults_block))
    section = (root / "docs/going-further.md").read_text(encoding="utf-8").split("## All thesis settings\n", 1)[1]
    table = "\n".join(line for line in section.splitlines() if line.startswith("|"))
    rows = {}
    for line in table.splitlines()[2:]:
        key, values, notes = [s.strip() for s in line.strip("|").split("|")]
        rows[key.strip("`")] = {"values": values, "notes": notes}
    if set(rows) != {key for key, _ in entries}:
        raise ValueError("settings: class keys and Going further's settings table differ")
    keys = {}
    for key, kind in entries:
        row = rows[key]
        item = {"type": {"tl_gset:N": "text", "bool_gset:N": "boolean", "choice:": "choice"}[kind], **row}
        if kind == "choice:":
            item["choices"] = re.findall(rf"{key} / ([\w-]+) \.code:n", block)
            item["choices"].remove("unknown")
            # What the title page prints for each choice, for the builder's preview.
            item["names"] = {choice: plain(name) for choice, name in re.findall(
                rf"{key} / ([\w-]+) \.code:n =\s*\{{ \\tl_gset:Nn \\g_rpi_\w+_tl \{{([^{{}}]+)\}} \}}", block)}
            if set(item["names"]) != set(item["choices"]):
                raise ValueError(f"settings: could not read the printed name of every {key} choice")
        if kind == "bool_gset:N":
            item["choices"] = ["true", "false"]
        if "choices" in item and set(re.findall(r"`([^`]+)`", row["values"])) != set(item["choices"]):
            raise ValueError(f"settings: {key} choices differ between class and guide")
        if key in defaults:
            item["default"] = defaults[key]
            if kind == "tl_gset:N":
                documented = re.search(r"default: `([^`]+)`", row["values"])
                same = documented and documented[1] == defaults[key]
            else:
                same = f"`{defaults[key]}` (default)" in row["values"]
            if not same:
                raise ValueError(f"settings: {key} default differs between class and guide")
        keys[key] = item
    required = re.findall(r"\\rpi_require:Nn \\g_rpi_\w+_tl \{([^}]+)\}", cls)
    for key in required:
        if key != "degree" and "required" not in rows[key]["values"]:
            raise ValueError(f"settings: {key} is required in the class but not the guide")
    errors = {}
    messages = cls[start:cls.index(r"\tl_const:Nn \c_rpi_seal_png_tl")]
    for match in re.finditer(r"\\ClassError\{rpi-thesis\}", messages):
        message, _ = group(messages, match.end())
        message = message.replace(r"\tl_to_str:N \l_keys_value_tl", "{value}")
        message = message.replace(r"\l_keys_key_str", "{key}").replace("#2", "{key}")
        if message.startswith("Committee~chair"):
            prefix, rest = message.split(r"\tl_if_empty:NF \g_rpi_roles_tl", 1)
            detail, _ = group(rest, rest.index("{"))
            errors["chair"] = plain(prefix)
            errors["roles"] = plain(detail.replace(r"\g_rpi_roles_tl", "{roles}"))
        else:
            message = plain(message)
            for label, beginning in (("degree", "Unknown degree"), ("graduation-month", "Unknown graduation"),
                                     ("unknown", "Unknown setting"), ("blank-member", "Blank committee"),
                                     ("required", "Missing "), ("year", "Graduation year"),
                                     ("committee", "No committee")):
                if message.startswith(beginning):
                    errors[label] = message
                    break
            else:
                raise ValueError("settings: unhandled class validation message: " + message)
    expected = {"degree", "graduation-month", "unknown", "blank-member", "required", "year", "committee", "chair", "roles"}
    if set(errors) != expected:
        raise ValueError("settings: class validation messages changed; update the generator")
    year = re.search(r"\\regex_match:nnF \{([^\n]+)\} \\g_rpi_year_tl", cls)[1]
    if year != r"\A[0-9]{4}\Z":
        raise ValueError("settings: class year validation changed; update the browser validator")
    role_block = cls.split(r"\str_case:nnF {#1}", 1)[1].split(r"\cs_new_protected:Npn", 1)[0]
    roles = re.findall(r"\{([^{}]+)\} \{ \\int_gincr:N \\g_rpi_chairs_int \}", role_block)
    if not roles:
        raise ValueError("settings: could not read chair roles from the class")
    # The title page's fixed lines, for the builder's preview; stop if the class changes them.
    title_page = cls.split(r"\RenewDocumentCommand \maketitle", 1)[1].split(r"\clearpage", 1)[0]
    fixed = ["Submitted in Partial Fulfillment of the Requirements", "for the Degree of", "Approved by:",
             "Rensselaer Polytechnic Institute", "Troy, New York"]
    for line in fixed:
        if line.replace(" ", "~") not in title_page:
            raise ValueError(f"settings: the title page no longer says \"{line}\"; update the builder's preview")
    return {"keys": keys, "required": required, "errors": errors, "chairRoles": roles, "titlePage": fixed,
            "table": table}


def javascript(data):
    return "// Generated by scripts/settings.py from rpi-thesis.cls and docs/going-further.md.\nexport default " + json.dumps(data, ensure_ascii=True, indent=2) + ";\n"
