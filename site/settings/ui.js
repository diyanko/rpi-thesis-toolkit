// The site template loads a classic script. Resolve modules from this script,
// rather than from the guide page's URL. Keep the reference table on failure.
(async function () {
  const root = document.querySelector("[data-settings-builder]");
  const script = document.currentScript;
  if (!root || !script) return;
  const base = new URL(".", script.src);
  try {
    const [{default: schema}, {generate, readMetadata, metadataFile}] = await Promise.all([
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
      "degree-name": "Other degree name (optional)", department: "Full department name",
      "graduation-month": "Graduation month", "graduation-year": "Graduation year",
      "seal-file": "Seal file in your project", "copyright-page": "Copyright page",
      "list-of-tables": "List of tables", "list-of-figures": "List of figures"};
    // The core uses the class's own messages, which name metadata.tex; on the form, name the field.
    const formMessage = text => text
      .replace(/^Missing ([\w-]+) in metadata\.tex$/, (_, key) => `${labels[key] || key}: still empty`)
      .replace(/^Blank committee member name in metadata\.tex$/, "A committee member has no name")
      .replace(/ in metadata\.tex/g, "");
    const controls = new Map();
    let held = new Set();   // optional settings an import could not read (see fill)
    // A short hint under the field it is about, instead of notes above the form.
    const link = (text, href) => { const a = document.createElement("a"); a.textContent = text; a.href = href; return a; };
    const HINTS = {
      title: () => ["In normal capitalization; the title page prints capitals. Math in a title: edit the copied block (",
                    link("example", "going-further.html#all-thesis-settings"), ")."],
      "degree-name": () => ["Only if your degree's name is not in the menu."],
      "graduation-month": () => ["The month you graduate, not the month you submit."],
    };
    // Browsers without field-sizing: grow a text box to its content.
    function fit(box) {
      if (CSS.supports && CSS.supports("field-sizing", "content")) return;
      box.style.height = "auto";
      box.style.height = box.scrollHeight + (box.offsetHeight - box.clientHeight) + "px";
    }
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
      // Long text grows with what you type (title, department); Enter adds no line break.
      const grows = key === "title" || key === "department";
      const control = element(spec.choices ? "select" : grows ? "textarea" : "input", "", container);
      control.id = label.htmlFor;
      control.name = key;
      if (grows) {
        control.rows = 1;
        control.className = "settings-grow";
        control.addEventListener("keydown", event => { if (event.key === "Enter") event.preventDefault(); });
        control.addEventListener("input", () => fit(control));
      }
      if (spec.choices) {
        if (!("default" in spec)) {  // no default: ask, rather than show an empty box
          const prompt = element("option", "Choose…", control);
          prompt.value = "";
          prompt.disabled = true;
        }
        for (const value of spec.choices) {
          // The name the title page prints; the copied block uses the value.
          const option = element("option", (spec.names && spec.names[value]) || value, control);
          option.value = value;
        }
      } else if (!grows) control.type = "text";
      control.value = spec.default ?? "";
      if (key === "graduation-year") control.inputMode = "numeric";
      controls.set(key, control);
      const hint = HINTS[key];
      if (hint) {
        const help = element("p", "", container);
        help.className = "tool-hint";
        help.id = `setting-${key}-help`;
        help.append(...hint());
        control.setAttribute("aria-describedby", help.id);
      }
      if (key === "seal-file") {
        const help = element("p", "Put the downloaded seal in your project's assets folder and keep its filename (.jpg, .jpeg, or .png).", container);
        help.id = "seal-file-help";
        help.className = "tool-hint";
        control.setAttribute("aria-describedby", help.id);
        // The shared file picker (components gallery, "Tool pages"): only the name is used.
        const pick = element("label", "", container);
        pick.className = "tool-drop tool-file settings-seal-pick";
        pick.htmlFor = "settings-seal-filename";
        const pickButton = element("span", "Use the seal's filename", pick);
        pickButton.className = "tool-file-button";
        pickButton.dataset.icon = "file";
        element("span", "or drop it here. Only the name is used; the image is not read.", pick).className = "tool-file-or";
        const file = element("input", "", container);
        file.id = pick.htmlFor;
        file.type = "file";
        file.className = "visually-hidden";
        file.accept = ".jpg,.jpeg,.png,.pdf";
        const useName = chosen => {
          if (chosen && chosen[0]) {
            control.value = "assets/" + chosen[0].name;
            held.delete(key);
            update();
          }
        };
        file.addEventListener("change", () => {
          useName(file.files);
          file.value = ""; // Keep only the filename; the image is never read.
        });
        if (window.ToolState && window.ToolState.dropZone) window.ToolState.dropZone(pick, event => useName(event.dataTransfer.files));
      }
    }
    // The title page sketch: the class's \maketitle lines and gaps, scaled to the box
    // (site.css, "Settings builder"). Plain text only; the PDF is the real check.
    const preview = root.querySelector("[data-settings-preview]");
    const sheet = preview ? element("div", "", null) : null;
    const full = preview ? element("p", "", null) : null;
    if (preview) {
      sheet.className = "settings-page";
      sheet.setAttribute("aria-hidden", "true");
      const toggle = preview.querySelector(".tool-switch");
      if (toggle) toggle.after(sheet); else preview.prepend(sheet);
      full.className = "tool-hint settings-page-full";
      full.hidden = true;
      preview.append(full);
    }
    function sketch(settings, committee) {
      if (!preview || sheet.hidden) return;
      const [submitted, degreeOf, approved, institute, town] = schema.titlePage;
      const line = (text, className, fallback) => {
        const node = element("p", text.trim() || fallback, sheet);
        node.className = className + (text.trim() ? "" : " is-empty");
      };
      const degree = settings["degree-name"] ?? schema.keys.degree.names[settings.degree] ?? settings.degree;
      sheet.replaceChildren();
      line(settings.title.toUpperCase(), "tp-large", "YOUR THESIS TITLE");
      line(settings.author, "tp-large tp-gap-20", "Your full name");
      line(submitted, "tp-gap-20", "");
      line(degreeOf, "", "");
      line(degree.toUpperCase(), "tp-italic tp-gap-10", "DEGREE");
      line(approved, "tp-gap-40", "");
      for (const member of committee.length ? committee : [{name: "", role: ""}]) {
        line(member.name.trim() ? member.name + (member.role.trim() ? ", " + member.role : "") : "", "", "Committee member");
      }
      const seal = element("p", "RPI seal", sheet);
      seal.className = "tp-seal";
      line(settings.department, "tp-italic tp-gap-20", "Department of ...");
      line(institute, "", "");
      line(town, "", "");
      const date = [settings["graduation-month"], settings["graduation-year"]].filter(Boolean).join(" ");
      line(date ? `[${date}]` : "", "tp-gap-12", "[Month Year]");
      // A page taller than US letter means the PDF's title page may not fit on one page.
      full.hidden = sheet.scrollHeight <= Math.ceil(sheet.clientWidth * 11 / 8.5) + 2;
      full.textContent = "This much text may not fit on one page. Compile and check the title page; shorten the title or department if it runs over.";
    }
    // One row per member: the full name and a role menu, so Chair and Co-Chair are
    // always spelled as the class needs; "Another role" opens a text box.
    let nextMember = 0;
    const OTHER = "other";
    function roleOf(row) {  // "" is a member without a role
      const choice = row.querySelector("[data-member-role]").value;
      return choice === OTHER ? row.querySelector("[data-member-other]").value.trim() : choice;
    }
    function addMember(role = "") {
      // A quiet list: column names once (wide screens), then one line per member.
      if (!members.querySelector(".settings-member-head")) {
        const head = element("div", "", members);
        head.className = "settings-member-head";
        head.setAttribute("aria-hidden", "true");
        element("span", "Full name", head);
        element("span", "Role", head);
      }
      const number = ++nextMember;
      const row = element("div", "", members);
      row.className = "settings-member";
      row.setAttribute("role", "group");
      row.setAttribute("aria-label", `Committee member ${number}`);
      const name = element("input", "", row);
      name.type = "text";
      name.className = "m-name";
      name.placeholder = "Full name";
      name.setAttribute("aria-label", `Full name, committee member ${number}`);
      name.dataset.memberName = "";
      const choice = element("select", "", row);
      choice.className = "m-role";
      choice.setAttribute("aria-label", `Role, committee member ${number}`);
      choice.dataset.memberRole = "";
      for (const [value, text] of [["", "Member"], ...schema.chairRoles.map(r => [r, r]), [OTHER, "Another role…"]]) {
        element("option", text, choice).value = value;
      }
      const other = element("input", "", row);
      other.type = "text";
      other.className = "m-other";
      other.placeholder = "Role, as printed after the name";
      other.setAttribute("aria-label", `Role as printed, committee member ${number}`);
      other.dataset.memberOther = "";
      const known = role === "" || schema.chairRoles.includes(role);
      choice.value = known ? role : OTHER;
      other.value = known ? "" : role;
      const showOther = () => { other.hidden = choice.value !== OTHER; };
      choice.addEventListener("change", () => { showOther(); if (!other.hidden) other.focus(); });
      showOther();
      const remove = element("button", "", row);
      remove.type = "button";
      remove.className = "button-quiet m-remove";
      remove.dataset.icon = "remove";
      remove.setAttribute("aria-label", `Remove committee member ${number}`);
      remove.title = "Remove";
      remove.addEventListener("click", () => {
        const next = row.nextElementSibling || row.previousElementSibling;
        row.remove();
        update();
        const focus = next && next.querySelector && next.querySelector(".m-name");
        (focus || root.querySelector("[data-settings-add]")).focus();
      });
      update();
      return name;
    }
    function update() {
      for (const box of fields.querySelectorAll(".settings-grow")) fit(box);
      const settings = Object.fromEntries([...controls].map(([key, control]) =>
        [key, control.type === "checkbox" ? String(control.checked) : control.value]));
      // An empty optional override uses the class's degree default.
      if (settings["degree-name"] === "") delete settings["degree-name"];
      const committee = [...members.querySelectorAll(".settings-member")].map(row => ({
        name: row.querySelector("[data-member-name]").value,
        role: roleOf(row)
      }));
      // Chairs first, as in the copied block.
      sketch(settings, [...committee.filter(m => schema.chairRoles.includes(m.role)),
                        ...committee.filter(m => !schema.chairRoles.includes(m.role))]);
      const result = generate(settings, committee, schema);
      for (const key of held) result.errors.push(`${labels[key] || key}: your file uses LaTeX here that the form cannot keep; edit that line in your file instead`);
      errors.replaceChildren();
      // An empty field gets one line, "still empty", not also a format error;
      // the empty fields share that line.
      const shown = result.errors.map(formMessage).filter(text =>
        !(text.startsWith("Unknown graduation month \"\"") ||
          (text.startsWith("Graduation year must") && !settings["graduation-year"].trim())));
      const empty = shown.filter(text => text.endsWith(": still empty")).map(text => text.slice(0, -": still empty".length));
      const items = [...(empty.length ? ["Still empty: " + empty.join(", ")] : []),
                     ...shown.filter(text => !text.endsWith(": still empty"))];
      for (const text of items) element("li", text, errors);
      block = result.text;
      if (window.ToolsHighlight) window.ToolsHighlight.render(output, block);  // colored; Copy uses the plain text
      else output.textContent = block;
      copy.disabled = Boolean(result.errors.length);
      const save = root.querySelector("[data-settings-download]");
      if (save) save.disabled = copy.disabled;
      // A year that is typed but not four digits is marked on its field, in words in the list too.
      const year = controls.get("graduation-year");
      if (year.value && !/^[0-9]{4}$/.test(year.value)) year.setAttribute("aria-invalid", "true");
      else year.removeAttribute("aria-invalid");
      status.setAttribute("data-state", result.errors.length ? "" : "done");
      status.textContent = result.errors.length
        ? "Still to fill in or fix:"
        : "Looks fine: your block is ready to copy.";
    }
    root.querySelector("[data-settings-add]").addEventListener("click", () => addMember().focus());
    // The sketch can be hidden; the form then uses the whole width.
    const sketchSwitch = root.querySelector("[data-settings-sketch]");
    if (sketchSwitch && sheet) sketchSwitch.addEventListener("change", () => {
      sheet.hidden = !sketchSwitch.checked;
      if (!sketchSwitch.checked) full.hidden = true;
      preview.classList.toggle("is-off", !sketchSwitch.checked);
      if (sketchSwitch.checked) update();
    });
    // Start from an existing metadata.tex: read here, never uploaded; plain values only.
    const load = root.querySelector("[data-settings-load]");
    const loaded = root.querySelector("[data-settings-loaded]");
    const fill = (name, text) => {
      const found = readMetadata(text, schema);
      if (!found.ok) {
        loaded.textContent = name + " has no \\thesissetup block or committee lines; nothing was filled in.";
        return;
      }
      // Start from a clean form, so nothing from earlier typing stays behind.
      for (const [key, control] of controls) {
        const spec = schema.keys[key];
        if (control.type === "checkbox") control.checked = spec.default === "true";
        else control.value = spec.default ?? "";
      }
      for (const [key, value] of Object.entries(found.settings)) {
        const control = controls.get(key);
        if (!control) continue;
        if (control.type === "checkbox") control.checked = value === "true";
        else control.value = value;
      }
      // The committee always comes from the file: with no lines there, one empty chair row.
      members.querySelectorAll(".settings-member").forEach(row => row.remove());
      for (const member of found.committee) addMember(member.role).value = member.name;
      if (!found.committee.length) addMember(schema.chairRoles[0]);
      // An optional setting the form could not read would vanish from the block: hold the copy back.
      held = new Set(found.skipped.filter(key => controls.has(key) && !schema.required.includes(key)));
      update();
      const count = Object.keys(found.settings).length;
      const parts = ["Filled in from " + name + ": " + count + (count === 1 ? " setting" : " settings") + " and " +
        found.committee.length + (found.committee.length === 1 ? " committee member." : " committee members.")];
      if (found.skipped.length) parts.push("Left empty, because they use LaTeX the form cannot keep: " +
        [...new Set(found.skipped)].join(", ") + ". Fill them in here, or edit those lines in your file instead of copying this block.");
      if (found.unknown.length) parts.push("Not settings of this class: " + found.unknown.join(", ") + ".");
      loaded.textContent = parts.join(" ");
    };
    const readFile = async chosen => {
      const file = chosen && chosen[0];
      if (!file) return;
      if (file.size > 200000) { loaded.textContent = file.name + " is too large to be metadata.tex."; return; }
      try { fill(file.name, await file.text()); } catch { loaded.textContent = file.name + " could not be read."; }
    };
    if (load) {
      load.addEventListener("change", () => { readFile(load.files); load.value = ""; });
      const zone = root.querySelector(".settings-load");
      if (window.ToolState && window.ToolState.dropZone) window.ToolState.dropZone(zone, event => readFile(event.dataTransfer.files));
    }
    // Download a whole metadata.tex with the current block.
    const download = root.querySelector("[data-settings-download]");
    if (download) download.addEventListener("click", () => {
      if (!block) return;
      const url = URL.createObjectURL(new Blob([metadataFile(block)], {type: "text/plain"}));
      const link = element("a", "", document.body);
      link.href = url;
      link.download = "metadata.tex";
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      status.textContent = "Downloaded metadata.tex. Put it in your thesis folder in place of the old one.";
    });
    form.addEventListener("submit", event => event.preventDefault());
    form.addEventListener("input", event => { for (const [key, control] of controls) if (control === event.target) held.delete(key); update(); });
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
