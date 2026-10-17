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
  const run_button = root.querySelector('[data-run]');
  // The shared states (ToolState in tools-highlight.js); plain text without it.
  const State = window.ToolState || {set: (r, s, state, c) => {
    s.textContent = typeof c === 'string' ? c : c ? c.title + '. ' + c.text : ''; }};
  const say = (text, state = '') => State.set(root, status, state, text, run_button);
  const fail = (title, text, href, link) => State.set(root, status, 'error', {title, text, href, link});
  const ZOTERO = 'citations.html#step-2-collect-and-cite-sources-with-zotero';
  const BY_HAND = 'citations.html#if-you-cant-use-zotero-paste-an-entry-by-hand';
  function clearResults() { results.replaceChildren(); }
  function clear() {
    revision++;
    bib.value = ''; preamble.value = ''; tex.value = '';
    files.value = ''; chapters = [];
    if (names) names.textContent = '';
    root.querySelector('[data-unused]').checked = false;
    say('Cleared. Nothing was saved.');
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
      fail('Too much to check at once', 'These files total more than 5 MB. Choose references.bib on its own, or fewer chapter files.');
      return;
    }
    const other = list.find(file => !/\.(bib|tex)$/i.test(file.name));
    if (other) {
      fail('Choose .bib and .tex files', other.name + ' cannot be read here; other file types are not checked. Export your references as a .bib file from your reference manager:',
           ZOTERO, 'Collect and cite sources with Zotero');
      return;
    }
    if (list.filter(file => /^preamble\.tex$/i.test(file.name)).length > 1) {
      fail('Two preamble.tex files', 'The citation style is set in one preamble.tex. Choose just one, from the thesis you are checking.');
      return;
    }
    say('Reading files on your computer…', 'working');
    try {
      const loaded = await Promise.all(list.map(async file => ({name: file.name, text: await file.text()})));
      if (version !== revision) return;
      const bibs = loaded.filter(file => /\.bib$/i.test(file.name));
      const setup = loaded.find(file => /^preamble\.tex$/i.test(file.name));
      const sources = loaded.filter(file => /\.tex$/i.test(file.name) && file !== setup);
      if (bibs.length) bib.value = bibs.map(file => file.text).join('\n');
      if (setup) preamble.value = setup.text;
      if (sources.length) chapters = sources;
      say('Read ' + loaded.map(file => file.name).join(', ') + '. Choose Check references when ready.');
    } catch {
      if (version === revision) fail('A file could not be read', 'Open it in your editor, copy all of its text, and paste it in the box below.');
    }
  }
  function run() {
    if (State.busy && State.busy(run_button)) return;
    revision++;
    clearResults();
    if (!bib.value.trim()) {
      fail('Nothing to check yet', 'Paste references.bib in the box, or choose your .bib file above, then choose Check references.');
      bib.focus();
      return;
    }
    if (bib.value.length + preamble.value.length + tex.value.length > maxBytes) {
      fail('Too much to check at once', 'Paste less than 5 MB of text for one check: references.bib on its own, or fewer chapters.');
      return;
    }
    // A large file can take a moment: show the working state, then check.
    say('Checking references…', 'working');
    const version = revision;
    setTimeout(() => { if (version === revision) check(); }, 30);
  }
  function check() {
    const report = checkReferences({bib: bib.value, preamble: preamble.value,
      tex: [...chapters, ...(tex.value.trim() ? [{name: 'pasted .tex', text: tex.value}] : [])],
      unused: root.querySelector('[data-unused]').checked});
    if (!report.entries) {
      fail('No entries found', 'The text has no entries that start with @, such as @book{key, ...}. Paste the whole references.bib file. How an entry looks:',
           BY_HAND, 'Paste an entry by hand');
      bib.focus();
      return;
    }
    const heading = node('h3', 'Reference check results', results);
    heading.tabIndex = -1;
    node('p', report.entries + (report.entries === 1 ? ' entry' : ' entries') + '; style: ' + report.style + '. ' + report.coverage, results);
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
    say((count ? count + (count === 1 ? ' point' : ' points') + ' to review' : 'No problems found') +
        ' in ' + report.entries + (report.entries === 1 ? ' entry.' : ' entries.') + ' Nothing was uploaded.', 'done');
    heading.focus();
  }
  files.addEventListener('change', () => read(files.files));
  const drop = root.querySelector('[data-drop]');
  if (State.dropZone) State.dropZone(drop, event => read(event.dataTransfer.files));
  else drop.addEventListener('drop', event => { event.preventDefault(); read(event.dataTransfer.files); });
  run_button.addEventListener('click', run);
  root.querySelector('[data-clear]').addEventListener('click', clear);
  for (const input of [bib, preamble, tex, root.querySelector('[data-unused]')]) {
    input.addEventListener('input', () => { revision++; clearResults(); say('Input changed. Choose Check references again to update the results.'); });
  }
  root.hidden = false;
  const nojs = document.querySelector('[data-bibcheck-nojs]');
  if (nojs) nojs.hidden = true;
}

})().catch(() => { /* Keep the checklist visible if the optional checker cannot load. */ });
