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
  return text.replace(/[\\{}%#$&_^~]/g, char =>
    `\\csname char_generate:nn\\endcsname{${char.codePointAt(0)}}{12}`).replace(/[\r\n\t]/g, " ");
}

export function generate(settings, committee, schema) {
  const errors = validate(settings, committee, schema);
  if (errors.length) return {errors, text: ""};
  const lines = Object.keys(schema.keys).filter(key => key in settings).map(key => {
    // Paths are literal filenames rather than printed text.
    const value = key === "seal-file" ? escapePath(settings[key]) : escapeText(settings[key]);
    return `  ${key} = {${value}},`;
  });
  const chairs = committee.filter(member => schema.chairRoles.includes(member.role));
  const others = committee.filter(member => !schema.chairRoles.includes(member.role));
  const members = [...chairs, ...others].map(member =>
    `\\committeemember${member.role ? `[${escapeText(member.role).replace(/[\[\]]/g, char => `{${char}}`)}]` : ""}{${escapeText(member.name)}}`);
  return {errors: [], text: `\\thesissetup{\n${lines.join("\n")}\n}\n\n${members.join("\n")}\n`};
}
