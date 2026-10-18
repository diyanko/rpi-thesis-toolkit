// Loaded as a deferred classic script by the guide template.
// Everything stays in this page: no upload, no storage. Fixes change only the
// text in the box; the student downloads the corrected file.
(async function () {
const script = document.currentScript;
if (!script) return;
const {checkReferences, applyFixes, joinSources, splitSources, sourceLine, RULES} = await import(new URL('core.js', script.src));

const root = document.querySelector('[data-bibcheck]');
if (root) {
  const bib = root.querySelector('[data-bib]');
  const preamble = root.querySelector('[data-preamble]');
  const tex = root.querySelector('[data-tex]');
  const files = root.querySelector('input[type=file]');
  const status = root.querySelector('[role=status]');
  const results = root.querySelector('[data-results]');
  const names = root.querySelector('[data-file-names]');
  const unusedBox = root.querySelector('[data-unused]');
  // loaded: the .bib files read from disk, for download names. checked: the
  // box text the shown results describe. undo: the text before the first fix.
  let chapters = [], loaded = [], revision = 0, report = null, checked = null;
  let undo = null, fixed = false, view = 'severity';
  const maxBytes = 5 * 1024 * 1024;
  function node(tag, text, parent, className) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
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
  const AUTO_EXPORT = 'citations.html#set-it-and-forget-it';
  const plural = (n, one, many) => n + ' ' + (n === 1 ? one : many);
  function clearResults() { results.replaceChildren(); report = null; checked = null; }
  function clear() {
    revision++;
    bib.value = ''; preamble.value = ''; tex.value = '';
    files.value = ''; chapters = []; loaded = []; undo = null; fixed = false;
    if (names) names.textContent = '';
    unusedBox.checked = false;
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
      const read = await Promise.all(list.map(async file => ({name: file.name, text: await file.text()})));
      if (version !== revision) return;
      const bibs = read.filter(file => /\.bib$/i.test(file.name));
      const setup = read.find(file => /^preamble\.tex$/i.test(file.name));
      const sources = read.filter(file => /\.tex$/i.test(file.name) && file !== setup);
      // Several .bib files share the box, each after a "% From the file" line.
      if (bibs.length) { bib.value = joinSources(bibs); loaded = bibs; undo = null; fixed = false; }
      if (setup) preamble.value = setup.text;
      if (sources.length) chapters = sources;
      say('Read ' + read.map(file => file.name).join(', ') + '. Choose Check references when ready.');
    } catch {
      if (version === revision) fail('A file could not be read', 'Open it in your editor, copy all of its text, and paste it in the box below.');
    }
  }
  function run() {
    if (State.busy && State.busy(run_button)) return;
    revision++;
    clearResults();
    if (!bib.value.trim()) {
      State.set(root, status, '', 'Paste references.bib in the box or choose your .bib file first.');
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
  function compute() {
    return checkReferences({bib: bib.value, preamble: preamble.value,
      tex: [...chapters, ...(tex.value.trim() ? [{name: 'pasted chapter text', text: tex.value}] : [])],
      unused: unusedBox.checked});
  }
  function summary(prefix = '') {
    const count = report.findings.length;
    return prefix + (count ? plural(count, 'point', 'points') + ' to review' : 'No problems found') +
      ' in ' + plural(report.entries, 'entry.', 'entries.') + ' Nothing was uploaded.';
  }
  // focus: where focus goes after the results are drawn (the heading by default).
  function check(prefix = '', focus) {
    report = compute();
    checked = bib.value;
    // No entries and nothing else to say: explain the format. Syntax or
    // citation findings still show below when there are any.
    if (!report.entries && report.findings.every(f => f.id === 'empty')) {
      report = null;
      fail('No entries found', 'The text has no entries that start with @, such as @book{key, ...}. Paste the whole references.bib file. How an entry looks:',
           BY_HAND, 'Paste an entry by hand');
      bib.focus();
      return;
    }
    draw();
    say(summary(prefix), 'done');
    (focus && focus() || results.querySelector('h3')).focus();
  }

  // Where a finding is, in words: "line 12", or "library.bib, line 3" when
  // several files share the box.
  function where(loc) {
    if (loc.file) return loc.file + ', line ' + loc.line;
    const source = sourceLine(checked, loc.line);
    return (source.name ? source.name + ', line ' : 'line ') + source.line;
  }
  // A control that selects the place in the box, so the student sees it.
  function jumpButton(loc, parent, text) {
    const button = node('button', text || where(loc), parent, 'bibcheck-line');
    button.type = 'button';
    button.setAttribute('aria-label', 'Show ' + where(loc) + ' in the box');
    button.addEventListener('click', () => jump(loc));
    return button;
  }
  function jump(loc) {
    if (bib.value !== checked) { say('The text changed. Choose Check references again to update the results.'); return; }
    // Put the start of the place near the top of the box, then select it.
    bib.focus({preventScroll: true});
    bib.setSelectionRange(loc.start, loc.start);
    bib.scrollTop = Math.max(0, offsetTop(loc.start) - bib.clientHeight / 4);
    bib.setSelectionRange(loc.start, loc.end, 'backward');
    bib.scrollIntoView({block: 'nearest'});
  }
  // The height of the text before offset, as the box wraps it: a hidden copy
  // with the same width and font.
  function offsetTop(offset) {
    const style = getComputedStyle(bib), copy = document.createElement('div');
    for (const name of ['font', 'letterSpacing', 'lineHeight', 'tabSize', 'paddingTop', 'paddingRight', 'paddingLeft', 'borderLeftWidth', 'borderRightWidth', 'boxSizing'])
      copy.style[name] = style[name];
    Object.assign(copy.style, {position: 'absolute', visibility: 'hidden', whiteSpace: 'pre-wrap', overflowWrap: 'break-word', width: bib.clientWidth + 'px', borderStyle: 'solid', borderColor: 'transparent'});
    copy.textContent = bib.value.slice(0, offset) + '​';
    document.body.append(copy);
    // The last line is the one the place starts on; "normal" line height has no number.
    const height = copy.scrollHeight - (parseFloat(style.lineHeight) || parseFloat(style.fontSize) * 1.2);
    copy.remove();
    return height;
  }

  // One point: what and where, the fix with its guide section, and, when the
  // checker can make the change safely, the change itself with a button.
  function item(f, list, byEntry) {
    const li = node('li', undefined, list, 'bibcheck-item');
    const head = byEntry ? RULES.severities[f.severity] + ' — ' + f.field.replaceAll('|', ' or ')
                         : f.key + ' — ' + f.field.replaceAll('|', ' or ');   // journaltitle|journal reads as "journaltitle or journal"
    node('strong', head, li);
    if (f.line && !(byEntry && f.line === f.entry?.line && f.start === f.entry?.start)) {
      li.append(' (');
      if (f.file) li.append(where(f)); else jumpButton(f, li);
      li.append(')');
    }
    li.append(': ');
    node('span', f.fix + ' ', li);
    if (f.related) {
      li.append('Other entry: ');
      jumpButton(f.related, li);
      li.append('. ');
    }
    const link = node('a', f.guide, li);
    link.href = f.href;
    li.append('.');
    if (f.edit) {
      const change = node('div', undefined, li, 'bibcheck-change');
      const now = node('p', undefined, change);
      node('span', 'Now', now, 'bibcheck-change-label');
      node('code', f.edit.before, now);
      const after = node('p', undefined, change);
      node('span', 'After the fix', after, 'bibcheck-change-label');
      node('code', f.edit.after, after);
      const button = node('button', f.edit.label, change, 'button button-secondary button-small');
      button.dataset.icon = 'check';
      button.type = 'button';
      button.setAttribute('data-fix', '');
      button.setAttribute('aria-label', f.edit.label + ': ' + f.key + ', ' + f.field);
      button.addEventListener('click', () => fixOne(f, button));
    }
  }

  function draw() {
    results.replaceChildren();
    const heading = node('h3', 'Reference check results', results);
    heading.tabIndex = -1;
    node('p', plural(report.entries, 'entry', 'entries') + '; style: ' + report.style + '. ' + report.coverage, results);
    if (!preamble.value.trim()) node('p', 'No preamble.tex supplied. Using the starter’s numeric style for field advice.', results);
    if (!report.findings.length) node('p', 'Looks fine: these checks found no problems. Still compare the references in your PDF with your style guide.', results);
    const fixes = report.findings.filter(f => f.edit);
    if (fixes.length || fixed) {
      const bar = node('div', undefined, results, 'bibcheck-fixbar');
      if (fixes.length) {
        node('p', plural(fixes.length, 'point has a safe fix', 'points have a safe fix') +
          ', shown under the point. A fix changes only the text in the box, never the meaning or a key.', bar);
      }
      if (fixed) {
        const text = node('p', 'Your fixes are in the box. Download the corrected file and use it in place of the old one. If Zotero or another reference manager exports this file, make the same corrections there too, or the next export replaces them: ', bar);
        node('a', 'auto-export cautions', text).href = AUTO_EXPORT;
        text.append('.');
      }
      const actions = node('p', undefined, bar, 'tool-actions');
      if (fixes.length) {
        const all = node('button', fixes.length === 1 ? 'Apply the fix' : 'Apply all ' + fixes.length + ' fixes', actions, 'button button-secondary');
        all.dataset.icon = 'check';
        all.type = 'button';
        all.setAttribute('data-fix-all', '');
        all.addEventListener('click', fixAll);
      }
      if (fixed) {
        for (const file of downloads()) {
          const save = node('button', 'Download ' + file.name, actions, 'button button-secondary');
          save.dataset.icon = 'download';
          save.type = 'button';
          save.setAttribute('data-download', '');
          save.addEventListener('click', () => download(file));
        }
        if (undo !== null) {
          const back = node('button', 'Undo the fixes', actions, 'button button-secondary');
          back.dataset.icon = 'undo';
          back.type = 'button';
          back.setAttribute('data-undo', '');
          back.addEventListener('click', undoFixes);
        }
      }
    }
    if (report.findings.length > 1) {
      // Two ways to read the same points: by how serious, or entry by entry.
      const choice = node('fieldset', undefined, results, 'convert-options bibcheck-view');
      node('legend', 'Group the points', choice);
      for (const [value, text] of [['severity', 'By how serious'], ['entry', 'By entry']]) {
        const label = node('label', undefined, choice);
        const radio = node('input', undefined, label);
        radio.type = 'radio'; radio.name = 'bibcheck-view'; radio.value = value;
        radio.checked = view === value;
        radio.addEventListener('change', () => { view = value; groups(); });
        node('span', text, label);
      }
    }
    node('div', undefined, results).setAttribute('data-groups', '');
    groups();
  }
  function groups() {
    const box = results.querySelector('[data-groups]');
    box.replaceChildren();
    if (view === 'entry' && report.findings.length > 1) {
      const entries = new Map(), loose = [];
      for (const f of report.findings) {
        if (!f.entry) { loose.push(f); continue; }
        if (!entries.has(f.entry.start)) entries.set(f.entry.start, {entry: f.entry, key: f.key, findings: []});
        entries.get(f.entry.start).findings.push(f);
      }
      for (const group of [...entries.values()].sort((a, b) => a.entry.start - b.entry.start)) {
        const h = node('h4', group.key + ' ', box);
        h.append('(');
        jumpButton(group.entry, h);
        h.append(')');
        const list = node('ul', undefined, box);
        for (const f of group.findings) item(f, list, true);
      }
      if (loose.length) {
        node('h4', 'Not tied to one entry', box);
        const list = node('ul', undefined, box);
        for (const f of loose) item(f, list, false);
      }
      return;
    }
    for (const [severity, label] of Object.entries(RULES.severities)) {
      const findings = report.findings.filter(item => item.severity === severity);
      if (!findings.length) continue;
      node('h4', label + ' (' + findings.length + ')', box);
      const list = node('ul', undefined, box);
      for (const f of findings) item(f, list, false);
    }
  }

  // Fixes: apply to the box, then check again, since every later offset moves.
  function stale() {
    if (bib.value === checked) return false;
    say('The text changed. Choose Check references again before applying fixes.');
    return true;
  }
  function fixOne(f, button) {
    if (stale()) return;
    const index = [...results.querySelectorAll('[data-fix]')].indexOf(button);
    if (undo === null) undo = bib.value;
    bib.value = applyFixes(bib.value, [f.edit]).text;
    fixed = true;
    // Keep the student's place: the next fix button, else the fix bar.
    check('Fixed in ' + f.key + ': ' + f.edit.label.toLowerCase() + '. ', () => {
      const next = results.querySelectorAll('[data-fix]');
      return next[Math.min(index, next.length - 1)] || results.querySelector('[data-download]');
    });
  }
  function fixAll() {
    if (stale()) return;
    if (undo === null) undo = bib.value;
    let total = 0, current = report;
    // Overlapping fixes in one field wait for the next pass.
    for (let pass = 0; pass < 5; pass++) {
      const result = applyFixes(bib.value, current.findings.filter(f => f.edit).map(f => f.edit));
      if (!result.applied) break;
      bib.value = result.text;
      total += result.applied;
      current = compute();
    }
    fixed = true;
    check('Applied ' + plural(total, 'fix', 'fixes') + '. ', () => results.querySelector('[data-download]'));
  }
  function undoFixes() {
    if (undo === null) return;
    bib.value = undo;
    undo = null; fixed = false;
    check('Restored the text from before the fixes. ');
  }
  // One download per file: the box split at its "% From the file" lines, or
  // the one file read (references.bib when the text was pasted).
  function downloads() {
    const parts = splitSources(bib.value);
    if (parts.some(part => part.name)) {
      const original = name => loaded.find(file => file.name === name)?.text.replace(/\r\n?/g, '\n').replace(/\n*$/, '\n');
      return parts.filter(part => part.name && part.text !== original(part.name)).map(part => ({name: part.name, text: part.text}));
    }
    return [{name: loaded.length === 1 ? loaded[0].name : 'references.bib', text: bib.value}];
  }
  function download(file) {
    try {
      const url = URL.createObjectURL(new Blob([file.text], {type: 'text/plain;charset=utf-8'}));
      const link = node('a', undefined, document.body);
      link.href = url; link.download = file.name; link.hidden = true;
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 10000);
      say('Your browser is saving ' + file.name + ', usually to Downloads. Use it in place of the old file, then compile and check the PDF.', 'done');
    } catch {
      fail('The download did not start', 'Copy all of the text in the box instead and paste it into ' + file.name + ' in your editor.');
    }
  }

  files.addEventListener('change', () => read(files.files));
  const drop = root.querySelector('[data-drop]');
  if (State.dropZone) State.dropZone(drop, event => read(event.dataTransfer.files));
  else drop.addEventListener('drop', event => { event.preventDefault(); read(event.dataTransfer.files); });
  run_button.addEventListener('click', run);
  root.querySelector('[data-clear]').addEventListener('click', clear);
  for (const input of [bib, preamble, tex, unusedBox]) {
    input.addEventListener('input', () => {
      revision++;
      // Typing makes the undo point stale; the download stays available.
      if (input === bib) undo = null;
      clearResults();
      say('Input changed. Choose Check references again to update the results.');
    });
  }
  root.hidden = false;
  const nojs = document.querySelector('[data-bibcheck-nojs]');
  if (nojs) nojs.hidden = true;
}

})().catch(() => { /* Keep the checklist visible if the optional checker cannot load. */ });
