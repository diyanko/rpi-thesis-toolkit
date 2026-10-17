// The site template loads a classic script. Resolve modules from this script,
// rather than from the guide page's URL. Keep the reference table on failure.
(async function () {
  const root = document.querySelector("[data-settings-builder]");
  const script = document.currentScript;
  if (!root || !script) return;
  const base = new URL(".", script.src);
  try {
    const [{default: schema}, {generate}] = await Promise.all([
      import(new URL("data.js", base).href), import(new URL("core.js", base).href)
    ]);
    const form = root.querySelector("form");
    const fields = root.querySelector("[data-settings-fields]");
    const members = root.querySelector("[data-settings-members]");
    const status = root.querySelector("[data-settings-status]");
    const errors = root.querySelector("[data-settings-errors]");
    const output = root.querySelector("[data-settings-output]");
    let block = "";
    function selectOutput() {
      const range = document.createRange();
      range.selectNodeContents(output);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    }
    const copy = root.querySelector("[data-settings-copy]");
    const labels = {title: "Thesis or dissertation title", author: "Your full name", degree: "Degree",
      "degree-name": "Custom degree name (optional)", department: "Full department name",
      "graduation-month": "Graduation month", "graduation-year": "Graduation year",
      "seal-file": "Seal file in your project", "copyright-page": "Copyright page",
      "list-of-tables": "List of tables", "list-of-figures": "List of figures"};
    const controls = new Map();
    function element(tag, text, parent) {
      const node = document.createElement(tag);
      if (text) node.textContent = text;
      if (parent) parent.append(node);
      return node;
    }
    const isYesNo = spec => Boolean(spec.choices) && spec.choices.length === 2 &&
      spec.choices.includes("true") && spec.choices.includes("false");
    for (const [key, spec] of Object.entries(schema.keys)) {
      if (isYesNo(spec)) {  // a yes/no setting: a native checkbox drawn as a switch, all in one row
        const row = fields.querySelector(".settings-switches") || element("div", "", fields);
        row.className = "settings-switches";
        const label = element("label", "", row);
        label.className = "tool-switch";
        const control = element("input", "", label);
        control.type = "checkbox";
        control.setAttribute("role", "switch");
        control.id = `setting-${key}`;
        control.name = key;
        control.checked = spec.default === "true";
        element("span", labels[key] || key, label);
        controls.set(key, control);
        continue;
      }
      const container = element("div", "", fields);
      const label = element("label", labels[key] || key, container);
      label.htmlFor = `setting-${key}`;
      const control = element(spec.choices ? "select" : "input", "", container);
      control.id = label.htmlFor;
      control.name = key;
      if (spec.choices) {
        for (const value of spec.choices) {
          const option = element("option", value, control);
          option.value = value;
        }
      } else control.type = "text";
      control.value = spec.default ?? "";
      if (key === "graduation-year") control.inputMode = "numeric";
      controls.set(key, control);
      if (key === "seal-file") {
        const help = element("p", "Put the downloaded seal in your project's assets folder. Keep its filename, including .jpg, .jpeg, or .png. You can select it below to fill in its name; nothing is uploaded.", container);
        help.id = "seal-file-help";
        control.setAttribute("aria-describedby", help.id);
        const fileLabel = element("label", "Use the downloaded seal's filename (optional)", container);
        fileLabel.htmlFor = "settings-seal-filename";
        const file = element("input", "", container);
        file.id = fileLabel.htmlFor;
        file.type = "file";
        file.accept = ".jpg,.jpeg,.png,.pdf";
        file.addEventListener("change", () => {
          if (file.files[0]) {
            control.value = "assets/" + file.files[0].name;
            update();
          }
          file.value = ""; // Keep only the filename; the image is never read.
        });
      }
    }
    let nextMember = 0;
    function addMember(role = "") {
      const row = element("fieldset", "", members);
      const number = ++nextMember;
      element("legend", `Committee member ${number}`, row);
      const nameLabel = element("label", "Full name", row);
      nameLabel.htmlFor = `member-${number}-name`;
      const name = element("input", "", row);
      name.id = nameLabel.htmlFor;
      name.type = "text";
      name.dataset.memberName = "";
      const roleLabel = element("label", "Role (Chair, Co-Chair, or leave empty)", row);
      roleLabel.htmlFor = `member-${number}-role`;
      const roleInput = element("input", "", row);
      roleInput.id = roleLabel.htmlFor;
      roleInput.type = "text";
      roleInput.value = role;
      roleInput.dataset.memberRole = "";
      const remove = element("button", "Remove this member", row);
      remove.type = "button";
      remove.className = "button button-secondary";
      remove.addEventListener("click", () => { row.remove(); update(); });
      update();
      return name;
    }
    function update() {
      const settings = Object.fromEntries([...controls].map(([key, control]) =>
        [key, control.type === "checkbox" ? String(control.checked) : control.value]));
      // An empty optional override uses the class's degree default.
      if (settings["degree-name"] === "") delete settings["degree-name"];
      const committee = [...members.querySelectorAll("fieldset")].map(row => ({
        name: row.querySelector("[data-member-name]").value,
        role: row.querySelector("[data-member-role]").value
      }));
      const result = generate(settings, committee, schema);
      errors.replaceChildren();
      for (const error of result.errors) element("li", error, errors);
      block = result.text;
      if (window.ToolsHighlight) window.ToolsHighlight.render(output, block);  // colored; Copy uses the plain text
      else output.textContent = block;
      copy.disabled = Boolean(result.errors.length);
      // A year that is typed but not four digits is marked on its field, in words in the list too.
      const year = controls.get("graduation-year");
      if (year.value && !/^[0-9]{4}$/.test(year.value)) year.setAttribute("aria-invalid", "true");
      else year.removeAttribute("aria-invalid");
      status.setAttribute("data-state", result.errors.length ? "" : "done");
      status.textContent = result.errors.length
        ? "Still to fill in or fix (" + result.errors.length + "):"
        : "Looks fine: your block is ready to copy.";
    }
    root.querySelector("[data-settings-add]").addEventListener("click", () => addMember().focus());
    form.addEventListener("submit", event => event.preventDefault());
    form.addEventListener("input", update);
    form.addEventListener("change", update);
    copy.addEventListener("click", async () => {
      const text = block;
      try {
        await navigator.clipboard.writeText(text);
        status.textContent = block === text ? "Copied. Replace the settings and committee lines in metadata.tex." : "Settings changed. Copy the current block again.";
      } catch {
        output.focus();
        selectOutput();
        status.textContent = "Select and copy the block below.";
      }
    });
    addMember(schema.chairRoles[0]);
    root.hidden = false;
    document.querySelector("[data-settings-nojs]").hidden = true;
  } catch {
    // The page remains usable through the settings table if modules fail.
  }
})();
