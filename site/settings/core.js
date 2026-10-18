/* Pure metadata validation and generation. No browser APIs or stored state.
   The schema is generated from the class and guide by scripts/settings.py. */
const blank = value => /^[ \t\r\n]*$/.test(value);
const message = (schema, id, values = {}) => schema.errors[id].replace(/\{(\w+)\}/g, (_, key) => values[key]);

export function validate(settings, committee, schema) {
  const errors = [];
  const effective = Object.fromEntries(Object.entries(schema.keys)
    .filter(([, spec]) => "default" in spec).map(([key, spec]) => [key, spec.default]));
  for (const [key, value] of Object.entries(settings)) {
    const spec = Object.hasOwn(schema.keys, key) ? schema.keys[key] : null;
    if (!spec) {
      errors.push(message(schema, "unknown", {key}));
      continue;
    }
    if (spec.choices && !spec.choices.includes(value)) {
      // l3keys supplies the boolean error; the class supplies choice errors.
      errors.push(spec.type === "boolean"
        ? `Key 'rpi/thesis/${key}' accepts boolean values only.`
        : message(schema, key, {value}));
      continue;
    }
    effective[key] = value;
  }
  // degree-name is applied after degree in the generated block, as the guide asks.
  if ("degree-name" in effective) effective.degree = effective["degree-name"];
  for (const key of schema.required) {
    if (blank(effective[key] ?? "")) errors.push(message(schema, "required", {key}));
  }
  if (!/^[0-9]{4}$/.test(effective["graduation-year"] ?? "")) errors.push(message(schema, "year"));
  for (const member of committee) {
    if (blank(member.name)) errors.push(message(schema, "blank-member"));
  }
  if (!committee.length) errors.push(message(schema, "committee"));
  if (!committee.some(member => schema.chairRoles.includes(member.role))) {
    const roles = committee.filter(member => member.role !== "").map(member => ` [${member.role}]`).join("");
    errors.push(message(schema, "chair") + (roles ? message(schema, "roles", {roles}) : ""));
  }
  return errors;
}

// The form takes plain text, so punctuation cannot turn into TeX syntax.
// Escape in one pass: newly inserted command braces must not be escaped again.
export function escapeText(text) {
  const escapes = {"\\": "\\textbackslash{}", "{": "\\{", "}": "\\}", "%": "\\%", "#": "\\#",
    "$": "\\$", "&": "\\&", "_": "\\_", "^": "\\textasciicircum{}", "~": "\\textasciitilde{}"};
  return text.replace(/[\\{}%#$&_^~]/g, char => escapes[char]).replace(/[\r\n\t]/g, " ");
}

function escapePath(text) {
  return text.replace(/[{}%#^~]/g, char =>
    `\\csname char_generate:nn\\endcsname{${char.codePointAt(0)}}{12}`).replace(/[\r\n\t]/g, " ");
}

export function generate(settings, committee, schema) {
  const errors = validate(settings, committee, schema);
  if (errors.length) return {errors, text: ""};
  const path = settings["seal-file"]?.replace(/\\/g, "/");
  const encodedPath = path === undefined ? undefined : escapePath(path);
  const expandPath = path !== encodedPath;
  const lines = Object.keys(schema.keys).filter(key => key in settings).map(key => {
    const value = key === "seal-file" ? encodedPath : escapeText(settings[key]);
    return [key, `  ${key} = {${value}},`];
  });
  let setup;
  if (expandPath) {
    // Expand only filename character escapes before the class stores the path.
    // Keep printed text untouched. The missing-file box then sees the actual
    // filename too, rather than the commands used to produce its characters.
    const text = lines.filter(([key]) => key !== "seal-file").map(([, line]) => line).join("\n");
    const seal = lines.find(([key]) => key === "seal-file")[1];
    setup = `\\expanded{\\noexpand\\thesissetup{\n\\unexpanded{\n${text}\n}\n${seal}\n}}`;
  } else {
    setup = `\\thesissetup{\n${lines.map(([, line]) => line).join("\n")}\n}`;
  }
  const chairs = committee.filter(member => schema.chairRoles.includes(member.role));
  const others = committee.filter(member => !schema.chairRoles.includes(member.role));
  const members = [...chairs, ...others].map(member =>
    `\\committeemember${member.role ? `[${escapeText(member.role).replace(/[\[\]]/g, char => `{${char}}`)}]` : ""}{${escapeText(member.name)}}`);
  return {errors: [], text: `${setup}\n\n${members.join("\n")}\n`};
}

// Reading an existing metadata.tex back into the form. Only plain values are
// taken: a value that still holds a LaTeX command after the form's own escapes
// are undone (math in a title, for example) is left out and named, because the
// form would print its backslashes as text.
const UNESCAPE = [["\\textbackslash{}", "\\"], ["\\textasciitilde{}", "~"], ["\\textasciicircum{}", "^"],
  ["\\&", "&"], ["\\%", "%"], ["\\_", "_"], ["\\#", "#"], ["\\$", "$"], ["\\{", "{"], ["\\}", "}"]];

function stripComments(text) {
  return text.split(/\r?\n/).map(line => {
    for (let i = 0; i < line.length; i++) {
      if (line[i] === "\\") { i++; continue; }
      if (line[i] === "%") return line.slice(0, i);
    }
    return line;
  }).join("\n");
}

// The text of the brace group that starts at text[start], and the offset after it.
function braceGroup(text, start) {
  if (text[start] !== "{") return null;
  let depth = 0;
  for (let i = start; i < text.length; i++) {
    if (text[i] === "\\") { i++; continue; }
    if (text[i] === "{") depth++;
    else if (text[i] === "}" && --depth === 0) return [text.slice(start + 1, i), i + 1];
  }
  return null;
}

function plainValue(value) {
  let text = value.trim();
  while (text.startsWith("{") && braceGroup(text, 0)?.[1] === text.length) text = text.slice(1, -1).trim();
  // The form's own escapes become characters; any other command means "not plain".
  const marks = ["\u0001", "\u0002", "\u0003"];
  ["\\textbackslash{}", "\\textasciitilde{}", "\\textasciicircum{}"].forEach((code, i) => { text = text.split(code).join(marks[i]); });
  if (/\\[A-Za-z@]/.test(text)) return null;
  text = text.replace(/(^|[^\\])[{}]+/g, "$1").replace(/~/g, " ");  // protective braces, as in {Doe}; ~ is a space
  for (const [code, char] of UNESCAPE.slice(3)) text = text.split(code).join(char);
  ["\\", "~", "^"].forEach((char, i) => { text = text.split(marks[i]).join(char); });
  return text.replace(/\s+/g, " ");
}

export function readMetadata(source, schema) {
  const text = stripComments(String(source || ""));
  const found = {settings: {}, committee: [], skipped: [], unknown: []};
  const at = text.indexOf("\\thesissetup");
  const group = at < 0 ? null : braceGroup(text, text.indexOf("{", at));
  if (group) {
    // Split at commas outside braces.
    const parts = [];
    let depth = 0, from = 0;
    const body = group[0];
    for (let i = 0; i < body.length; i++) {
      if (body[i] === "\\") { i++; continue; }
      if (body[i] === "{") depth++;
      else if (body[i] === "}") depth--;
      else if (body[i] === "," && depth === 0) { parts.push(body.slice(from, i)); from = i + 1; }
    }
    parts.push(body.slice(from));
    for (const part of parts) {
      const eq = part.indexOf("=");
      if (eq < 0) continue;
      const key = part.slice(0, eq).trim();
      if (!key) continue;
      if (!Object.hasOwn(schema.keys, key)) { found.unknown.push(key); continue; }
      const value = plainValue(part.slice(eq + 1));
      if (value === null) found.skipped.push(key);
      else found.settings[key] = value;
    }
  }
  const member = /\\committeemember\s*(?:\[([^\]]*)\])?\s*/g;
  let match;
  while ((match = member.exec(text))) {
    const name = braceGroup(text, member.lastIndex);
    if (!name) continue;
    const plainName = plainValue("{" + name[0] + "}"), plainRole = plainValue(match[1] || "");
    if (plainName === null || plainRole === null) found.skipped.push("committee member");
    else found.committee.push({name: plainName, role: plainRole});
    member.lastIndex = name[1];
  }
  found.ok = Boolean(group) || found.committee.length > 0;
  return found;
}

// A whole metadata.tex for download: a short header, then the block.
export function metadataFile(block) {
  return "% !TEX root = main.tex\n% Your details for the title page, written by the Settings builder.\n" +
    "% Every setting: the guide, Going further, \"All thesis settings\".\n" + block;
}
