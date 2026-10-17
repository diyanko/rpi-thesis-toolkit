/* Pure reference checks. No DOM, storage, network, or file access.
 * Tune policy here: profiles, field expectations, patterns, severity, and fixes
 * all live in RULES. Algorithms below only parse or evaluate this table.
 * Field expectations: biblatex manual §2.1 (not unconditional Biber errors).
 * Sentence case: biblatex-apa manual and biblatex-ieee title macro. Heuristics always ask for review.
 */
export const RULES = {
  severities: {break: 'May stop citations', wrong: 'May print wrong', advice: 'Style advice', tidy: 'Tidy-ups'},
  profiles: [
    {id: 'numeric', match: '^numeric(?:-comp|-verb)?$'},
    {id: 'authoryear', match: '^authoryear(?:-comp|-ibid|-icomp)?$'},
    {id: 'ieee', match: '^ieee$', sentenceCase: true,
      languages: ['english', 'american', 'british', 'australian', 'canadian', 'newzealand'],
      sentenceTypes: ['article', 'inbook', 'incollection', 'inproceedings', 'online', 'report', 'thesis', 'misc', 'unpublished'],
      sentenceFields: ['title', 'subtitle']},
    {id: 'apa', match: '^apa$', sentenceCase: true, languages: ['english', 'american', 'british', 'australian', 'canadian', 'newzealand'],
      recommend: {article: ['doi|url'], book: ['doi|url'], online: ['date|year']}},
    {id: 'mla', match: '^mla(?:-strict|7)?$', recommend: {article: ['pages'], online: ['date|year', 'organization|publisher']}},
    {id: 'chicago', match: '^chicago(?:-authordate|-notes)?$', recommend: {book: ['location'], online: ['date|year']}},
    {id: 'chem-acs', match: '^chem-acs$', recommend: {article: ['doi', 'pages']}}
  ],
  types: {
    article: {required: ['author', 'title', 'journaltitle|journal', 'date|year'], recommended: ['volume', 'pages|eid']},
    book: {required: ['author|editor', 'title', 'date|year'], recommended: ['publisher']},
    collection: {required: ['editor', 'title', 'date|year'], recommended: ['publisher']},
    inbook: {required: ['author', 'title', 'booktitle', 'date|year'], recommended: ['publisher', 'pages']},
    incollection: {required: ['author', 'title', 'booktitle', 'date|year'], recommended: ['editor', 'publisher', 'pages']},
    inproceedings: {required: ['author', 'title', 'booktitle', 'date|year'], recommended: ['pages', 'doi|url']},
    proceedings: {required: ['title', 'date|year'], recommended: ['editor', 'publisher']},
    online: {required: ['title', 'url'], recommended: ['author|editor|organization']},
    report: {required: ['author', 'title', 'institution', 'date|year'], recommended: ['type', 'number']},
    thesis: {required: ['author', 'title', 'type', 'institution|school', 'date|year'], recommended: []},
    misc: {required: ['title'], recommended: ['author|editor|organization', 'date|year']},
    software: {required: ['title'], recommended: ['author|organization', 'date|year', 'version', 'doi|url']},
    dataset: {required: ['title'], recommended: ['author|organization', 'date|year', 'doi|url']},
    unpublished: {required: ['author', 'title', 'date|year'], recommended: ['note']}
  },
  aliases: {conference: 'inproceedings', techreport: 'report', phdthesis: 'thesis', mastersthesis: 'thesis', www: 'online'},
  months: ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'],
  nameFields: ['author', 'editor', 'translator'],
  citationSignatures: {command: '\\\\([A-Za-z]*cite[A-Za-z]*|nocite)\\*?', multi: 'cites$', volume: 'volcites?$'},
  mathPairs: [['$$', '$$'], ['$', '$'], ['\\(', '\\)'], ['\\[', '\\]']],
  visibilityFields: ['doi', 'url', 'isbn'],
  titleFields: ['title', 'subtitle', 'booktitle'],
  verbatimFields: ['url', 'doi', 'file', 'eprint'],
  ignoredFields: ['abstract', 'keywords', 'file', 'annote'],
  checks: {
    syntax: {severity: 'break', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', fix: 'Check commas, quotes, and balanced braces in references.bib. Details: {detail}.'},
    empty: {severity: 'break', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', fix: 'Paste at least one complete entry from references.bib.'},
    duplicate: {severity: 'break', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', fix: 'Give each entry a unique key; this key appears more than once.'},
    keyCase: {severity: 'wrong', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', fix: 'Use clearly distinct keys; this differs only in capitalization from {detail}.'},
    key: {severity: 'advice', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', pattern: '^[A-Za-z0-9][A-Za-z0-9:._/+~-]*$', fix: 'Use a key with letters, digits, and simple punctuation, without spaces; update its citations too.'},
    missing: {severity: 'break', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', fix: 'Add this cited entry to references.bib, or correct its key in {detail}.'},
    unused: {severity: 'tidy', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', fix: 'No citation was found in the supplied .tex files. Keep it if another chapter uses it.'},
    required: {severity: 'wrong', section: 'check-the-output-yourself', fix: 'This entry type normally needs {detail}. Check the source and add it if available; missing data can be legitimate.'},
    recommended: {severity: 'advice', section: 'check-the-output-yourself', fix: 'Check the source for {detail}; include it when available for this style.'},
    access: {severity: 'wrong', section: 'web-sources-need-an-access-date', fix: 'Add urldate = {YYYY-MM-DD}, the date you read this URL. Check that it prints in the PDF (OGE manual §3.4 p. 34).'},
    date: {severity: 'wrong', section: 'web-sources-need-an-access-date', fix: 'Use a real ISO date: YYYY, YYYY-MM, or YYYY-MM-DD; urldate needs YYYY-MM-DD. Publication dates may use an ISO interval, such as 2020/2021.'},
    year: {severity: 'wrong', section: 'check-the-output-yourself', pattern: '^\\d{4}$', fix: 'Use a four-digit year, or move a fuller ISO date into date.'},
    month: {severity: 'wrong', section: 'check-the-output-yourself', pattern: '^(?:0?[1-9]|1[0-2]|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)$', fix: 'Use a month number (1–12), a three-letter month macro, or an ISO date in date.'},
    dateOverrides: {severity: 'advice', section: 'check-the-output-yourself', fix: 'date takes precedence over year/month in biblatex. Check these values agree, then keep one date representation.'},
    doi: {severity: 'wrong', section: 'check-the-output-yourself', pattern: '^10\\.\\d{4,9}/[^\\s<>]+$', fix: 'Use the bare DOI, for example 10.1234/example, without doi: or https://doi.org/. Verify it against the source.'},
    isbn: {severity: 'advice', section: 'check-the-output-yourself', fix: 'Check the ISBN against the book: its length or check digit does not match an ISBN-10 or ISBN-13.'},
    doiUrl: {severity: 'tidy', section: 'web-sources-need-an-access-date', pattern: '^https?://(?:dx\\.)?doi\\.org/', fix: 'The URL repeats the DOI. Usually keep the bare doi field and remove this duplicate URL; retain a separate source URL if needed.'},
    http: {severity: 'tidy', section: 'check-the-output-yourself', pattern: '^http://', fix: 'Check whether this source offers an https:// address before replacing http://. The checker does not visit links.'},
    url: {severity: 'advice', section: 'check-the-output-yourself', pattern: '^https?://[^\\s/]+(?:/[^\\s]*)?$', fix: 'Check the full URL, including https:// and the host, against the source.'},
    organization: {severity: 'wrong', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', pattern: '\\b(?:institute|university|foundation|association|society|department|organization|organisation|corporation|committee|council|agency|inc|ltd)\\b', fix: 'If this is an organization, wrap the whole name in an extra pair of braces: author = {{Example Research Institute}}.'},
    separators: {severity: 'wrong', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', pattern: ';| & |\\\\&', fix: 'Separate people with the literal word and, such as Alice Smith and Bob Jones. Brace an organization containing and.'},
    commas: {severity: 'advice', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', fix: 'Check name commas: use Family, Given, or Family, Jr., Given. Separate people with and.'},
    particle: {severity: 'advice', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', pattern: '\\b(?:van|von|de|del|der|di|da|du)\\b', fix: 'Check the family-name particle in the PDF; Family, Given form can make the intended family name clearer.'},
    suffix: {severity: 'advice', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', pattern: '\\b(?:Jr|Sr)\\.?$|\\b(?:II|III|IV)$', fix: 'For a suffix, use Family, Jr., Given so biblatex separates the suffix from the family name.'},
    nameForms: {severity: 'advice', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', fix: 'Possibly the same person as {detail}. Compare with the sources and use a consistent form only if they are the same person.'},
    capitals: {severity: 'advice', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', firstWordPattern: '[A-Z]{2,}|[A-Z][a-z]+[A-Z]', pattern: '\\b(?:[A-Z]{2,}[A-Za-z0-9]*|[A-Z][a-z]+[A-Z][A-Za-z]*|[A-Z][a-z]+)\\b', fix: 'This style may change English title case. Protect only proper names or acronyms that need capitals, for example {NASA} or {Python}; review: {detail}.'},
    special: {severity: 'wrong', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', pattern: '[&%_#]', fix: 'Escape literal special characters in text, for example \\&, \\%, \\_, or \\#. URL and DOI fields are handled separately.'},
    encoding: {severity: 'wrong', section: 'if-you-cant-use-zotero-paste-an-entry-by-hand', pattern: '\uFFFD|Ã[\u0080-\u00BF]|Â[\u0080-\u00BF]|â€', fix: 'Re-export references.bib as UTF-8, then check accented names against the source. Valid Unicode accents need no replacement.'},
    ignored: {severity: 'advice', section: 'change-the-citation-style', fix: 'This library metadata normally does not print in these styles. Check the style manual before expecting it in the reference list.'},
    disabled: {severity: 'advice', section: 'change-the-citation-style', fix: 'preamble.tex sets {detail}=false, so this field may be hidden. Check the PDF; URL access dates still need to print.'},
    miscArticle: {severity: 'advice', section: 'check-the-output-yourself', fix: 'This looks like a journal article. Check whether @article with journaltitle would describe it better than @misc.'},
    type: {severity: 'advice', section: 'check-the-output-yourself', fix: 'No field profile is available for @{detail}. Check its entry-type support in your style manual.'},
    duplicateEntry: {severity: 'tidy', section: 'check-the-output-yourself', fix: 'Possibly the same source as {detail} (matching DOI or normalized title). Compare the records before merging them.'},
    unsupported: {severity: 'advice', section: 'check-the-output-yourself', fix: 'The browser checker does not resolve {detail}. Check inherited fields and citations with Biber and the PDF; this is a partial check.'},
    style: {severity: 'advice', section: 'change-the-citation-style', fix: 'No known style was detected ({detail}). Only general biblatex checks ran. Supply preamble.tex and check the style manual.'}
  }
};

function escaped(text, i) {
  let n = 0;
  while (i > 0 && text[--i] === '\\') n++;
  return n % 2 === 1;
}

export function stripComments(text) {
  return text.split('\n').map(line => {
    for (let i = 0; i < line.length; i++) {
      if (line[i] === '%' && !escaped(line, i)) return line.slice(0, i);
    }
    return line;
  }).join('\n');
}

// Split only outside braces/quotes, preserving nested name and title protection.
function splitTop(text, delimiter) {
  const parts = [];
  let depth = 0, quote = false, start = 0;
  for (let i = 0; i < text.length; i++) {
    if (escaped(text, i)) continue;
    if (text[i] === '{') depth++;
    if (text[i] === '}') depth--;
    if (text[i] === '"' && depth === 0) quote = !quote;
    const length = delimiter === ' and ' && /\s/.test(text[i])
      ? (/^\s+and\s+/i.exec(text.slice(i))?.[0].length || 0)
      : (text.startsWith(delimiter, i) ? delimiter.length : 0);
    if (!depth && !quote && length) {
      parts.push(text.slice(start, i));
      start = i + length;
      i += length - 1;
    }
  }
  parts.push(text.slice(start));
  return parts;
}

export function parseBib(text) {
  const entries = [], errors = [];
  const macros = Object.fromEntries(RULES.months.map(m => [m, m]));
  // Percent signs inside values are data (and may themselves be a problem).
  let i = 0;
  const skip = () => {
    while (i < text.length) {
      if (/\s/.test(text[i])) { i++; continue; }
      if (text[i] === '%') { while (i < text.length && text[i] !== '\n') i++; continue; }
      break;
    }
  };
  const value = (raw, key, field) => splitTop(raw, '#').map(part => {
    const s = part.trim();
    if ((s.startsWith('{') && s.endsWith('}')) || (s.startsWith('"') && s.endsWith('"'))) return s.slice(1, -1);
    if (/^\d+$/.test(s)) return s;
    if (Object.hasOwn(macros, s.toLowerCase())) return macros[s.toLowerCase()];
    errors.push({id: 'unsupported', key, field, detail: 'the string macro ' + s});
    return s;
  }).join('');
  while (i < text.length) {
    skip();
    if (i >= text.length) break;
    // BibTeX permits arbitrary text outside entries.
    if (text[i] !== '@') { i++; continue; }
    const match = /^@(\w+)\s*([{(])/.exec(text.slice(i));
    if (!match) { errors.push({id: 'syntax', key: '(file)', field: 'entry', detail: 'unreadable @entry'}); i++; continue; }
    const type = match[1].toLowerCase(), close = match[2] === '{' ? '}' : ')';
    i += match[0].length;
    const start = i;
    let depth = 0, quote = false;
    for (; i < text.length; i++) {
      const c = text[i];
      if (escaped(text, i)) continue;
      if (c === '"' && !depth) quote = !quote;
      if (!depth && !quote && c === close) break;
      if (c === '{') depth++;
      if (c === '}') depth--;
      // Comments outside a field value are ignored without damaging raw % in it.
      if (c === '%' && !depth && !quote) {
        const end = text.indexOf('\n', i);
        const stop = end < 0 ? text.length : end;
        text = text.slice(0, i) + ' '.repeat(stop - i) + text.slice(stop);
        i = stop - 1;
      }
    }
    const body = text.slice(start, i);
    if (i === text.length) errors.push({id: 'syntax', key: body.split(',')[0].trim() || '(file)', field: 'entry', detail: 'unclosed entry or value'});
    i++;
    if (type === 'comment' || type === 'preamble') continue;
    const pieces = splitTop(body, ',');
    const key = type === 'string' ? '(string)' : pieces.shift().trim();
    const fields = Object.create(null);
    for (const piece of pieces) {
      if (!piece.trim()) continue;
      const field = /^\s*([\w-]+)\s*=\s*([\s\S]+)$/.exec(piece);
      if (!field) { errors.push({id: 'syntax', key, field: 'entry', detail: 'expected field = {value}'}); continue; }
      const name = field[1].toLowerCase(), raw = field[2].trim();
      if (Object.hasOwn(fields, name)) errors.push({id: 'syntax', key, field: name, detail: 'repeated field'});
      // An assignment outside braces in the value usually means a missing comma.
      if (splitTop(raw, '=').length > 1 || /^{[\s\S]*}\s+\w+\s*=/.test(raw)) {
        errors.push({id: 'syntax', key, field: name, detail: 'possible missing comma before another field'});
      }
      fields[name] = value(raw, key, name);
    }
    if (type === 'string') Object.assign(macros, fields);
    else entries.push({key, type, fields});
  }
  return {entries, errors};
}

export function detectStyle(preamble = '') {
  const text = stripComments(preamble);
  let style = preamble.trim() ? '' : 'numeric', options = '';
  const packages = /\\usepackage\s*(?:\[([^\]]*)\])?\s*{([^}]+)}/g;
  for (const m of text.matchAll(packages)) {
    if (m[2].split(',').map(s => s.trim()).includes('biblatex-chicago')) {
      style = 'chicago'; options = m[1] || '';
    } else if (m[2].split(',').map(s => s.trim()).includes('biblatex')) {
      options = m[1] || '';
      style = /(?:^|,)\s*style\s*=\s*{?([\w-]+)/.exec(options)?.[1] || '';
    }
  }
  // Later options can change a package-level style or visibility choice.
  for (const m of text.matchAll(/\\ExecuteBibliographyOptions\s*{((?:[^{}]|{[^{}]*})*)}/g)) {
    options += ',' + m[1];
    style = /(?:^|,)\s*style\s*=\s*([\w-]+)/.exec(m[1])?.[1] || style;
  }
  const values = Object.create(null);
  for (const option of splitTop(options, ',')) {
    const setting = /^\s*([\w-]+)\s*=\s*(.*?)\s*$/.exec(option);
    if (setting) {
      const value = setting[2].replace(/^{(.*)}$/, '$1').trim();
      values[setting[1]] = value;
      if (setting[1] === 'style' || setting[1] === 'bibstyle') style = value;
    }
  }
  const profile = RULES.profiles.find(p => new RegExp(p.match).test(style));
  const disabled = RULES.visibilityFields.filter(field => values[field] === 'false');
  return {style: style || 'unknown', profile: profile || null, disabled};
}

function validDate(value, full) {
  const part = s => {
    const m = /^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$/.exec(s);
    if (!m || (full && !m[3])) return false;
    const y = Number(m[1]), month = Number(m[2]), day = Number(m[3]);
    if (m[2] && (month < 1 || month > 12)) return false;
    if (m[3]) {
      const leap = y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
      const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
      if (day < 1 || day > days[month - 1]) return false;
    }
    return true;
  };
  const parts = value.split('/');
  return parts.length <= (full ? 1 : 2) && parts.every(s => !s ? !full && parts.length === 2 : part(s)) && parts.some(Boolean);
}

function validISBN(text) {
  const s = text.replace(/[-\s]/g, '').toUpperCase();
  if (/^\d{9}[\dX]$/.test(s)) return [...s].reduce((sum, c, i) => sum + (c === 'X' ? 10 : +c) * (10 - i), 0) % 11 === 0;
  if (/^97[89]\d{10}$/.test(s)) return [...s].reduce((sum, c, i) => sum + +c * (i % 2 ? 3 : 1), 0) % 10 === 0;
  return false;
}

function unprotected(text) {
  let out = '', depth = 0;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (escaped(text, i)) { out += ' '; continue; }
    if (c === '{') depth++;
    else if (c === '}') depth--;
    else out += depth ? ' ' : c;
  }
  return out;
}

// Hide mathematical expressions before checking literal text. Preserve offsets
// so escape detection still counts the original backslashes correctly.
function literalText(text) {
  let out = '', close = '';
  for (let i = 0; i < text.length; i++) {
    if (!escaped(text, i)) {
      if (close && text.startsWith(close, i)) {
        out += ' '.repeat(close.length); i += close.length - 1; close = ''; continue;
      }
      const pair = !close && RULES.mathPairs.find(([open]) => text.startsWith(open, i));
      if (pair) {
        close = pair[1]; out += ' '.repeat(pair[0].length); i += pair[0].length - 1; continue;
      }
    }
    out += close ? ' ' : text[i];
  }
  return out;
}

export function citedKeys(files = []) {
  const found = new Map();
  let all = false;
  for (const file of files) {
    const text = stripComments(file.text).replace(/\\begin{(?:verbatim\*?|lstlisting|minted)}[\s\S]*?\\end{(?:verbatim\*?|lstlisting|minted)}/g, '');
    // Only multicite commands consume another braced group. Ordinary
    // citations can be followed by grouped prose, which is not another key.
    const commands = new RegExp(RULES.citationSignatures.command, 'gi');
    for (const m of text.matchAll(commands)) {
      let rest = text.slice(m.index + m[0].length);
      const multi = new RegExp(RULES.citationSignatures.multi, 'i').test(m[1]);
      const volume = new RegExp(RULES.citationSignatures.volume, 'i').test(m[1]);
      if (multi) rest = rest.replace(/^\s*(?:\([^)]*\)\s*){0,2}/, '');
      do {
        rest = rest.replace(/^\s*(?:\[[^\]]*\]\s*){0,2}/, '');
        if (volume) {
          const number = /^{([^{}]*)}/.exec(rest);
          if (!number) break;
          rest = rest.slice(number[0].length).replace(/^\s*(?:\[[^\]]*\]\s*){0,2}/, '');
        }
        const group = /^{([^{}]*)}/.exec(rest);
        if (!group) break;
        for (const key of group[1].split(',').map(k => k.trim()).filter(Boolean)) {
          if (key === '*' && m[1].toLowerCase() === 'nocite') all = true;
          else found.set(key, file.name || '.tex file');
        }
        rest = rest.slice(group[0].length);
      } while (multi);
    }
  }
  return {found, all};
}

export function checkReferences({bib = '', preamble = '', tex = [], unused = false} = {}, rules = RULES) {
  const parsed = parseBib(bib), style = detectStyle(preamble), findings = [];
  const add = (id, key, field, detail = '') => {
    const rule = rules.checks[id];
    findings.push({id, severity: rule.severity, key, field,
      fix: rule.fix.replaceAll('{detail}', detail), href: 'citations.html#' + rule.section});
  };
  const matches = (id, value) => new RegExp(rules.checks[id].pattern, 'i').test(value);
  for (const e of parsed.errors) add(e.id, e.key, e.field, e.detail);
  if (!parsed.entries.length) add('empty', '(file)', 'entry');
  if (!style.profile) add('style', '(preamble.tex)', 'style', style.style);
  const keys = new Map(), folded = new Map(), sources = new Map(), people = new Map();
  const citations = citedKeys(tex);
  for (const entry of parsed.entries) {
    const {key, fields: f} = entry;
    const type = rules.aliases[entry.type] || entry.type;
    if (keys.has(key)) add('duplicate', key, 'key');
    else keys.set(key, entry);
    if (folded.has(key.toLowerCase()) && folded.get(key.toLowerCase()) !== key) add('keyCase', key, 'key', folded.get(key.toLowerCase()));
    folded.set(key.toLowerCase(), key);
    if (!matches('key', key)) add('key', key, 'key');
    if (type === 'xdata') { add('unsupported', key, 'entry', '@xdata inheritance'); continue; }
    const inherited = f.crossref || f.xdata;
    if (inherited) add('unsupported', key, f.crossref ? 'crossref' : 'xdata', 'inherited fields from ' + inherited);
    const expectations = rules.types[type];
    if (!expectations) add('type', key, 'entry type', type);
    // No missing-field claims when inheritance may supply them.
    if (expectations && !inherited) {
      for (const [kind, groups] of [['required', expectations.required],
        ['recommended', [...expectations.recommended, ...(style.profile?.recommend?.[type] || [])]]]) {
        for (const group of new Set(groups)) {
          if (!group.split('|').some(field => f[field]?.trim()) &&
              !(group === 'type' && ['phdthesis', 'mastersthesis'].includes(entry.type))) add(kind, key, group, group.replaceAll('|', ' or '));
        }
      }
    }
    if (f.url && !f.urldate) add('access', key, 'urldate');
    for (const field of ['date', 'urldate', 'origdate', 'eventdate']) {
      if (f[field] && !validDate(f[field], field === 'urldate')) add('date', key, field);
    }
    for (const field of ['year', 'month', 'doi']) if (f[field] && !matches(field, f[field])) add(field, key, field);
    if (f.date && (f.year || f.month)) add('dateOverrides', key, 'date');
    if (f.isbn && !validISBN(f.isbn)) add('isbn', key, 'isbn');
    if (f.url) {
      if (!matches('url', f.url)) add('url', key, 'url');
      if (matches('http', f.url)) add('http', key, 'url');
      if (f.doi && matches('doiUrl', f.url) && f.url.replace(new RegExp(rules.checks.doiUrl.pattern, 'i'), '').toLowerCase() === f.doi.toLowerCase()) add('doiUrl', key, 'url');
    }
    for (const field of rules.ignoredFields) if (f[field]) add('ignored', key, field);
    for (const field of style.disabled) if (f[field]) add('disabled', key, field, field);
    if (type === 'misc' && (f.journal || f.journaltitle)) add('miscArticle', key, 'entry type');
    for (const field of rules.nameFields) {
      if (!f[field]) continue;
      for (const name of splitTop(f[field], ' and ').map(s => s.trim())) {
        if (name.startsWith('{') && name.endsWith('}')) continue;
        for (const id of ['organization', 'separators', 'particle']) if (matches(id, name)) add(id, key, field);
        const parts = splitTop(name, ',').map(s => s.trim());
        if (parts.length > 3 || (parts.length === 2 && parts[0].split(/\s+/).length > 1 && parts[1].split(/\s+/).length > 1)) add('commas', key, field);
        if (parts.length < 3 && matches('suffix', name)) add('suffix', key, field);
        const words = name.split(/\s+/), family = (parts.length > 1 ? parts[0] : words.at(-1)).toLowerCase();
        const given = parts.length > 1 ? parts.at(-1) : words.slice(0, -1).join(' ');
        const identity = family + ':' + (given.match(/[A-Za-z]/)?.[0] || '').toLowerCase();
        const form = family + ':' + given.replace(/[.\s{}]/g, '').toLowerCase();
        if (given && people.has(identity) && people.get(identity).form !== form) add('nameForms', key, field, people.get(identity).name + ' (' + people.get(identity).key + ')');
        else if (given) people.set(identity, {form, name, key});
      }
    }
    if (style.profile?.sentenceCase && (!f.langid || style.profile.languages.includes(f.langid.toLowerCase())) &&
        (!style.profile.sentenceTypes || style.profile.sentenceTypes.includes(type))) {
      for (const field of style.profile.sentenceFields || rules.titleFields) {
        if (!f[field]) continue;
        const raw = unprotected(literalText(f[field]));
        const words = [...raw.matchAll(new RegExp(rules.checks.capitals.pattern, 'g'))]
          .filter(m => raw.slice(0, m.index).trim() || new RegExp(rules.checks.capitals.firstWordPattern).test(m[0])).map(m => m[0]);
        if (words.length) add('capitals', key, field, [...new Set(words)].join(', '));
      }
    }
    for (const [field, value] of Object.entries(f)) {
      if (matches('encoding', value)) add('encoding', key, field);
      if (!rules.verbatimFields.includes(field)) {
        const literal = literalText(value);
        const chars = [...literal.matchAll(new RegExp(rules.checks.special.pattern, 'g'))];
        if (chars.some(m => !escaped(literal, m.index))) add('special', key, field);
      }
    }
    const ids = [f.doi && 'doi:' + f.doi.toLowerCase(), f.title && 'title:' + f.title.normalize('NFKD').replace(/[^\p{L}\p{N}]/gu, '').toLowerCase()].filter(Boolean);
    const duplicate = ids.map(id => sources.get(id)).find(Boolean);
    if (duplicate && duplicate !== key) add('duplicateEntry', key, 'doi/title', duplicate);
    for (const id of ids) sources.set(id, key);
    if (unused && tex.length && !citations.all && !citations.found.has(key)) add('unused', key, 'key');
  }
  for (const [key, file] of citations.found) if (!keys.has(key)) add('missing', key, 'citation', file);
  const order = Object.keys(rules.severities);
  findings.sort((a, b) => order.indexOf(a.severity) - order.indexOf(b.severity));
  return {style: style.style, entries: parsed.entries.length, findings,
    coverage: tex.length ? 'Only the supplied .tex files were checked for citations.' : 'No .tex files supplied; citation coverage was not checked.'};
}
