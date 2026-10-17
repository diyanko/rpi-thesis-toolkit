// Loaded as a deferred classic script by the guide template.
(async function () {
const script = document.currentScript;
if (!script) return;
const {checkReferences, RULES} = await import(new URL('core.js', script.src));

const root = document.querySelector('[data-bibcheck]');
if (root) {
  const bib = root.querySelector('[data-bib]');
  const preamble = root.querySelector('[data-preamble]');
  const tex = root.querySelector('[data-tex]');
  const files = root.querySelector('input[type=file]');
  const status = root.querySelector('[role=status]');
  const results = root.querySelector('[data-results]');
  const names = root.querySelector('[data-file-names]');
  let chapters = [], revision = 0;
  const maxBytes = 5 * 1024 * 1024;
  function node(tag, text, parent) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (parent) parent.append(element);
    return element;
  }
  function clearResults() { results.replaceChildren(); }
  function clear() {
    revision++;
    bib.value = ''; preamble.value = ''; tex.value = '';
    files.value = ''; chapters = [];
    if (names) names.textContent = '';
    root.querySelector('[data-unused]').checked = false;
    status.textContent = 'Cleared. No files or text are saved by this checker.';
    clearResults();
    bib.focus();
  }
  async function read(chosen) {
    const version = ++revision;
    clearResults();
    const list = Array.from(chosen);
    if (!list.length) return;
    if (names) names.textContent = 'Chosen: ' + list.map(file => file.name).join(', ');
    if (list.reduce((sum, file) => sum + file.size, 0) > maxBytes) {
      status.textContent = 'Choose files totaling less than 5 MB, or paste a smaller set of references.';
      return;
    }
    if (list.some(file => !/\.(bib|tex)$/i.test(file.name))) {
      status.textContent = 'Choose .bib and .tex files. Other file types cannot be read here.';
      return;
    }
    if (list.filter(file => /^preamble\.tex$/i.test(file.name)).length > 1) {
      status.textContent = 'Choose one preamble.tex so the citation style is unambiguous.';
      return;
    }
    status.textContent = 'Reading files on your computer…';
    try {
      const loaded = await Promise.all(list.map(async file => ({name: file.name, text: await file.text()})));
      if (version !== revision) return;
      const bibs = loaded.filter(file => /\.bib$/i.test(file.name));
      const setup = loaded.find(file => /^preamble\.tex$/i.test(file.name));
      const sources = loaded.filter(file => /\.tex$/i.test(file.name) && file !== setup);
      if (bibs.length) bib.value = bibs.map(file => file.text).join('\n');
      if (setup) preamble.value = setup.text;
      if (sources.length) chapters = sources;
      status.textContent = 'Read ' + loaded.map(file => file.name).join(', ') + '. Choose Check references when ready.';
    } catch {
      if (version === revision) status.textContent = 'A file could not be read. Open it in your editor and paste the text below.';
    }
  }
  function run() {
    revision++;
    clearResults();
    if (!bib.value.trim()) {
      status.textContent = 'Paste references.bib or choose a .bib file first.';
      bib.focus();
      return;
    }
    if (bib.value.length + preamble.value.length + tex.value.length > maxBytes) {
      status.textContent = 'Paste less than 5 MB of text for one check.';
      return;
    }
    const report = checkReferences({bib: bib.value, preamble: preamble.value,
      tex: [...chapters, ...(tex.value.trim() ? [{name: 'pasted .tex', text: tex.value}] : [])],
      unused: root.querySelector('[data-unused]').checked});
    const heading = node('h3', 'Reference check results', results);
    heading.tabIndex = -1;
    node('p', report.entries + ' entries; style: ' + report.style + '. ' + report.coverage, results);
    if (!preamble.value.trim()) node('p', 'No preamble.tex supplied. Using the starter’s numeric style for field advice.', results);
    if (!report.findings.length) node('p', 'Looks fine: these checks found no problems. Still compare the references in your PDF with your style guide.', results);
    for (const [severity, label] of Object.entries(RULES.severities)) {
      const findings = report.findings.filter(item => item.severity === severity);
      if (!findings.length) continue;
      node('h4', label + ' (' + findings.length + ')', results);
      const list = node('ul', undefined, results);
      for (const item of findings) {
        const li = node('li', undefined, list);
        node('strong', item.key + ' — ' + item.field + ': ', li);
        node('span', item.fix + ' ', li);
        const link = node('a', 'Citations guide', li);
        link.href = item.href;
      }
    }
    const count = report.findings.length;
    status.textContent = (count ? count + (count === 1 ? ' point' : ' points') + ' to review.' : 'Looks fine.') + ' Nothing was uploaded.';
    heading.focus();
  }
  files.addEventListener('change', () => read(files.files));
  const drop = root.querySelector('[data-drop]');
  drop.addEventListener('dragover', event => { event.preventDefault(); drop.classList.add('is-over'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('is-over'));
  drop.addEventListener('drop', event => {
    event.preventDefault(); drop.classList.remove('is-over'); read(event.dataTransfer.files);
  });
  root.querySelector('[data-run]').addEventListener('click', run);
  root.querySelector('[data-clear]').addEventListener('click', clear);
  for (const input of [bib, preamble, tex, root.querySelector('[data-unused]')]) {
    input.addEventListener('input', () => { revision++; clearResults(); status.textContent = 'Input changed. Check references again to update results.'; });
  }
  root.hidden = false;
  const nojs = document.querySelector('[data-bibcheck-nojs]');
  if (nojs) nojs.hidden = true;
}

})().catch(() => { /* Keep the checklist visible if the optional checker cannot load. */ });
