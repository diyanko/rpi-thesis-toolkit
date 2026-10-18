/* Pure reference checks. No DOM, storage, network, or file access.
 * Tune policy here: profiles, field expectations, patterns, severity, and fixes
 * all live in RULES. Algorithms below only parse or evaluate this table.
 * Field expectations: biblatex manual §2.1 (not unconditional Biber errors).
 * Sentence case: biblatex-apa manual and biblatex-ieee title macro. Heuristics always ask for review.
 * Fixes: only deterministic, meaning-preserving text edits (escaping, a bare
 * DOI, a month number, a missing comma, an ISO date moved into date). Nothing
 * invents data or changes keys; anything uncertain stays advice.
 */
export const RULES = {
  severities: {break: 'May stop citations', wrong: 'May print wrong', advice: 'Style advice', tidy: 'Tidy-ups'},
  // Guide sections a finding links to: [address relative to the guide, link text].
  guides: {
    entry: ['citations.html#if-you-cant-use-zotero-paste-an-entry-by-hand', 'How an entry looks'],
    names: ['citations.html#if-you-cant-use-zotero-paste-an-entry-by-hand', 'Names in author fields'],
    access: ['citations.html#web-sources-need-an-access-date', 'Web sources need an access date'],
    output: ['citations.html#check-the-output-yourself', 'Check the output yourself'],
    style: ['citations.html#change-the-citation-style', 'Change the citation style'],
    keys: ['check-references.html#checklist-keys', 'Checklist: keys'],
    fields: ['check-references.html#checklist-fields', 'Checklist: usual fields'],
    dates: ['check-references.html#checklist-dates', 'Checklist: dates'],
    links: ['check-references.html#checklist-links', 'Checklist: DOIs and links'],
    text: ['check-references.html#checklist-special-characters', 'Checklist: special characters'],
    capitals: ['check-references.html#checklist-capitals', 'Checklist: capitals']
  },
  monthNames: ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'],
  // A value that holds a link keeps its characters; escaping would break it.
  linkCommands: '\\\\(?:url|href|path|nolinkurl|verb|detokenize)\\b',
  // How several loaded .bib files are marked in the box (a BibTeX comment).
  sourceMarker: '% From the file ',
  // Inline code in .tex files: \\verb|...| (any delimiter) and \\lstinline|...|.
  inlineCode: '\\\\(?:verb\\*?|lstinline)([^A-Za-z\\s{\\[*])[^\\n]*?\\1',
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
  verbatimFields: ['url', 'doi', 'file', 'eprint', 'crossref', 'xref', 'xdata', 'related', 'entryset', 'ids'],
  ignoredFields: ['abstract', 'keywords', 'file', 'annote'],
  checks: {
    syntax: {severity: 'break', guide: 'entry', fix: 'Check commas, quotes, and balanced braces here. Details: {detail}.'},
    empty: {severity: 'break', guide: 'entry', fix: 'Paste at least one complete entry from references.bib.'},
    duplicate: {severity: 'break', guide: 'keys', fix: 'Give each entry a unique key; another entry already uses this one. Update the citations that mean this entry.'},
    keyCase: {severity: 'wrong', guide: 'keys', fix: 'Use clearly distinct keys; this differs only in capitalization from {detail}.'},
    key: {severity: 'advice', guide: 'keys', pattern: '^[A-Za-z0-9][A-Za-z0-9:._/+~-]*$', fix: 'Use a key with letters, digits, and simple punctuation, without spaces; update its citations too.'},
    missing: {severity: 'break', guide: 'keys', fix: 'Add this cited entry to references.bib, or correct its key in {detail}.'},
    unused: {severity: 'tidy', guide: 'keys', fix: 'No citation was found in the supplied .tex files. Keep it if another chapter uses it.'},
    required: {severity: 'wrong', guide: 'fields', fix: 'This entry type normally needs {detail}. Check the source and add it if available; missing data can be legitimate.'},
    recommended: {severity: 'advice', guide: 'fields', fix: 'Check the source for {detail}; include it when available for this style.'},
    access: {severity: 'wrong', guide: 'access', fix: 'Add urldate = {YYYY-MM-DD}, the date you read this URL. Check that it prints in the PDF (OGE manual §3.4 p. 34).'},
    date: {severity: 'wrong', guide: 'dates', fix: 'Use a real ISO date: YYYY, YYYY-MM, or YYYY-MM-DD; urldate needs YYYY-MM-DD. Publication dates may use an ISO interval, such as 2020/2021.'},
    year: {severity: 'wrong', guide: 'dates', pattern: '^\\d{4}$', fix: 'Use a four-digit year, or move a fuller ISO date into date.'},
    month: {severity: 'wrong', guide: 'dates', pattern: '^(?:0?[1-9]|1[0-2]|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)$', fix: 'Use a month number (1–12), a three-letter month macro, or an ISO date in date.'},
    dateOverrides: {severity: 'advice', guide: 'dates', fix: 'date takes precedence over year/month in biblatex. Check these values agree, then keep one date representation.'},
    doi: {severity: 'wrong', guide: 'links', pattern: '^10\\.\\d{4,9}/[^\\s<>]+$', fix: 'Use the bare DOI, for example 10.1234/example, without doi: or https://doi.org/. Verify it against the source.'},
    isbn: {severity: 'advice', guide: 'links', fix: 'Check the ISBN against the book: its length or check digit does not match an ISBN-10 or ISBN-13.'},
    doiUrl: {severity: 'tidy', guide: 'links', pattern: '^https?://(?:dx\\.)?doi\\.org/', fix: 'The URL repeats the DOI. Usually keep the bare doi field and remove this duplicate URL; retain a separate source URL if needed.'},
    http: {severity: 'tidy', guide: 'links', pattern: '^http://', fix: 'Check whether this source offers an https:// address before replacing http://. The checker does not visit links.'},
    url: {severity: 'advice', guide: 'links', pattern: '^https?://[^\\s/]+(?:/[^\\s]*)?$', fix: 'Check the full URL, including https:// and the host, against the source.'},
    organization: {severity: 'wrong', guide: 'names', pattern: '\\b(?:institute|university|foundation|association|society|department|organization|organisation|corporation|committee|council|agency|inc|ltd)\\b', fix: 'If this is an organization, wrap the whole name in an extra pair of braces: author = {{Example Research Institute}}.'},
    separators: {severity: 'wrong', guide: 'names', pattern: ';| & |\\\\&', fix: 'Separate people with the literal word and, such as Alice Smith and Bob Jones. Brace an organization containing and.'},
    commas: {severity: 'advice', guide: 'names', fix: 'Check name commas: use Family, Given, or Family, Jr., Given. Separate people with and.'},
    particle: {severity: 'advice', guide: 'names', pattern: '\\b(?:van|von|de|del|der|di|da|du)\\b', fix: 'Check the family-name particle in the PDF; Family, Given form can make the intended family name clearer.'},
    suffix: {severity: 'advice', guide: 'names', pattern: '\\b(?:Jr|Sr)\\.?$|\\b(?:II|III|IV)$', fix: 'For a suffix, use Family, Jr., Given so biblatex separates the suffix from the family name.'},
    nameForms: {severity: 'advice', guide: 'names', fix: 'Possibly the same person as {detail}. Compare with the sources and use a consistent form only if they are the same person.'},
    capitals: {severity: 'advice', guide: 'capitals', firstWordPattern: '[A-Z]{2,}|[A-Z][a-z]+[A-Z]', pattern: '\\b(?:[A-Z]{2,}[A-Za-z0-9]*|[A-Z][a-z]+[A-Z][A-Za-z]*|[A-Z][a-z]+)\\b', fix: 'This style may change English title case. Protect only proper names or acronyms that need capitals, for example {NASA} or {Python}; review: {detail}.'},
    special: {severity: 'wrong', guide: 'text', pattern: '[&%_#]', fix: 'Escape literal special characters in text, for example \\&, \\%, \\_, or \\#. URL and DOI fields are handled separately.'},
    encoding: {severity: 'wrong', guide: 'text', pattern: '\uFFFD|Ã[\u0080-\u00BF]|Â[\u0080-\u00BF]|â€', fix: 'Re-export references.bib as UTF-8, then check accented names against the source. Valid Unicode accents need no replacement.'},
    ignored: {severity: 'advice', guide: 'style', fix: 'This library metadata normally does not print in these styles. Check the style manual before expecting it in the reference list.'},
    disabled: {severity: 'advice', guide: 'style', fix: 'preamble.tex sets {detail}=false, so this field may be hidden. Check the PDF; URL access dates still need to print.'},
    miscArticle: {severity: 'advice', guide: 'fields', fix: 'This looks like a journal article. Check whether @article with journaltitle would describe it better than @misc.'},
    type: {severity: 'advice', guide: 'fields', fix: 'No field profile is available for @{detail}. Check its entry-type support in your style manual.'},
    duplicateEntry: {severity: 'tidy', guide: 'output', fix: 'Possibly the same source as {detail} (matching DOI or normalized title). Compare the records before merging them.'},
    unsupported: {severity: 'advice', guide: 'output', fix: 'The browser checker does not resolve {detail}. Check inherited fields and citations with Biber and the PDF; this is a partial check.'},
    style: {severity: 'advice', guide: 'style', fix: 'No known style was detected ({detail}). Only general biblatex checks ran. Supply preamble.tex and check the style manual.'}
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
// Each part keeps its offset in text, so findings can point at the source.
function splitSpans(text, delimiter) {
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
      parts.push({text: text.slice(start, i), start});
      start = i + length;
      i += length - 1;
    }
  }
  parts.push({text: text.slice(start), start});
  return parts;
}
const splitTop = (text, delimiter) => splitSpans(text, delimiter).map(part => part.text);

// The end of one braced or quoted value that starts at s[0], or -1.
function valueEnd(s) {
  const braced = s[0] === '{';
  let depth = braced ? 1 : 0;
  for (let j = 1; j < s.length; j++) {
    if (escaped(s, j)) continue;
    if (!braced && s[j] === '"' && depth === 0) return j;
    if (s[j] === '{') depth++;
    if (s[j] === '}') depth--;
    if (braced && depth === 0) return j;
  }
  return -1;
}

// Line numbers (1-based) for offsets in text.
function lineIndex(text) {
  const starts = [0];
  for (let i = text.indexOf('\n'); i >= 0; i = text.indexOf('\n', i + 1)) starts.push(i + 1);
  return offset => {
    let low = 0, high = starts.length - 1;
    while (low < high) {
      const mid = (low + high + 1) >> 1;
      if (starts[mid] <= offset) low = mid; else high = mid - 1;
    }
    return low + 1;
  };
}

export function parseBib(text) {
  const entries = [], errors = [], original = text, lineAt = lineIndex(text);
  const macros = Object.fromEntries(RULES.months.map(m => [m, m]));
  const at = (start, end) => ({start, end, line: lineAt(start)});
  // Percent signs inside values are data (and may themselves be a problem).
  let i = 0;
  const skip = () => {
    while (i < text.length) {
      if (/\s/.test(text[i])) { i++; continue; }
      if (text[i] === '%') { while (i < text.length && text[i] !== '\n') i++; continue; }
      break;
    }
  };
  const value = (raw, key, field, loc, quiet) => splitTop(raw, '#').map(part => {
    const s = part.trim();
    if (s.startsWith('{') || s.startsWith('"')) {
      if (valueEnd(s) === s.length - 1) return s.slice(1, -1);
      if (!quiet) errors.push({id: 'syntax', key, field, ...loc, detail: 'a value component must be one balanced braced or quoted value; join components with #'});
      return s;
    }
    if (/^\d+$/.test(s)) return s;
    if (!/^[^\s{}"#=,()]+$/.test(s)) {
      if (!quiet) errors.push({id: 'syntax', key, field, ...loc, detail: 'expected a braced value, quoted value, number, or string macro'});
      return s;
    }
    if (Object.hasOwn(macros, s.toLowerCase())) return macros[s.toLowerCase()];
    errors.push({id: 'unsupported', key, field, ...loc, detail: 'the string macro ' + s});
    return s;
  }).join('');
  // The next line that starts an entry, for recovery after an unclosed one.
  const nextEntry = from => {
    const found = /\n[ \t]*@[A-Za-z]+[ \t]*[{(]/.exec(original.slice(from));
    return found ? from + found.index + found[0].indexOf('@') : -1;
  };
  while (i < text.length) {
    skip();
    if (i >= text.length) break;
    // BibTeX permits arbitrary text outside entries.
    if (text[i] !== '@') { i++; continue; }
    const entryStart = i, mark = errors.length;
    const match = /^@(\w+)\s*([{(])/.exec(text.slice(i));
    if (!match) { errors.push({id: 'syntax', key: '(file)', field: 'entry', ...at(i, i + 1), detail: 'unreadable @entry'}); i++; continue; }
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
    let unclosed = i === text.length, resume = -1;
    if (unclosed) {
      // One missing brace would otherwise swallow every later entry. Stop at
      // the next line that starts an entry, and check the rest on its own.
      resume = nextEntry(start);
      if (resume >= 0) { i = resume; text = text.slice(0, resume) + original.slice(resume); }
    }
    const body = text.slice(start, i);
    const keyText = body.split(',')[0].trim() || '(file)';
    if (unclosed) {
      errors.push({id: 'syntax', key: keyText, field: 'entry', ...at(entryStart, i),
        detail: resume >= 0 ? 'a closing brace or quote is missing in this entry, so it runs into the next entry (line ' + lineAt(resume) + ')' : 'unclosed entry or value'});
    }
    const entryEnd = unclosed ? i : i + 1;
    if (!unclosed) i++;
    // An extra closing brace ends the entry early; the rest looks like a field.
    if (!unclosed) {
      const after = /^[ \t]*(?:\r?\n[ \t]*)?,?\s*[A-Za-z][\w-]*\s*=\s*[{"\w]/.exec(text.slice(i));
      if (after) errors.push({id: 'syntax', key: keyText, field: 'entry', ...at(entryStart, i + after[0].length),
        detail: 'text after the end of this entry looks like a field; check for an extra closing brace'});
    }
    // Every message about this entry knows where the entry is.
    const own = () => { for (const e of errors.slice(mark)) e.entry ||= at(entryStart, entryEnd); };
    if (type === 'comment' || type === 'preamble') { own(); continue; }
    const pieces = splitSpans(body, ',');
    const keyPiece = type === 'string' ? null : pieces.shift();
    const key = keyPiece ? keyPiece.text.trim() : '(string)';
    const fields = Object.create(null), spans = Object.create(null);
    let broken = unclosed;
    for (const piece of pieces) {
      if (!piece.text.trim()) continue;
      const pieceStart = start + piece.start;
      const field = /^(\s*)([\w-]+)(\s*=\s*)([\s\S]*?)\s*$/.exec(piece.text);
      if (!field || !field[4]) {
        const lead = piece.text.length - piece.text.trimStart().length;
        if (!unclosed) errors.push({id: 'syntax', key, field: 'entry', ...at(pieceStart + lead, pieceStart + piece.text.trimEnd().length), detail: 'expected field = {value}'});
        continue;
      }
      const name = field[2].toLowerCase(), raw = field[4];
      const nameStart = pieceStart + field[1].length, rawStart = nameStart + field[2].length + field[3].length;
      const span = {...at(nameStart, rawStart + raw.length), name: field[2], eq: field[3], raw};
      if (Object.hasOwn(fields, name)) errors.push({id: 'syntax', key, field: name, ...span, detail: 'repeated field'});
      // An assignment outside braces in the value usually means a missing comma.
      const comma = splitTop(raw, '=').length > 1 || /^{[\s\S]*}\s+\w+\s*=/.test(raw);
      if (comma && !unclosed) {
        errors.push({id: 'syntax', key, field: name, ...span, detail: 'possible missing comma before another field', edit: commaEdit(span)});
      }
      // One message per problem: the unclosed entry or the missing comma
      // explains the odd values that follow from it.
      broken ||= comma;
      fields[name] = value(raw, key, name, at(nameStart, rawStart + raw.length), unclosed || comma);
      if (!Object.hasOwn(spans, name)) spans[name] = span;
    }
    own();
    if (type === 'string') Object.assign(macros, fields);
    else entries.push({key, type, fields, spans, ...at(entryStart, entryEnd), broken});
  }
  return {entries, errors};
}

// Fixes. Each replaces one field assignment, source.slice(start, end), with
// text; before and after show that field with its spaces collapsed.
function fixField(span, label, raw, name = span.name) {
  const show = (n, r) => (n + ' = ' + r).replace(/\s+/g, ' ');
  return {label, start: span.start, end: span.end, text: name + span.eq + raw,
    source: span.name + span.eq + span.raw, before: show(span.name, span.raw), after: show(name, raw)};
}
// Only a value written as one braced or quoted part is edited.
function single(span) {
  const raw = span.raw;
  return /^["{]/.test(raw) && valueEnd(raw) === raw.length - 1 ? raw.slice(1, -1) : null;
}
const rewrap = (span, inner) => span.raw[0] + inner + span.raw.at(-1);
function commaEdit(span) {
  const raw = span.raw;
  const end = /^["{]/.test(raw) ? valueEnd(raw) : (/^[^\s{}"#=,()]+/.exec(raw)?.[0].length || 0) - 1;
  if (end < 0 || !/^\s+[A-Za-z][\w-]*\s*=/.test(raw.slice(end + 1))) return null;
  return fixField(span, 'Add the missing comma', raw.slice(0, end + 1) + ',' + raw.slice(end + 1));
}

// Apply fixes to text, last first so earlier offsets stay valid. Fixes that
// overlap one already applied, or whose text has changed, are skipped; check
// again to see what remains.
export function applyFixes(text, fixes) {
  let out = text, floor = Infinity, applied = 0;
  for (const fix of [...fixes].sort((a, b) => b.start - a.start)) {
    // A fix applies only to the text it was made for.
    if (fix.end > floor || text.slice(fix.start, fix.end) !== fix.source) continue;
    out = out.slice(0, fix.start) + fix.text + out.slice(fix.end);
    floor = fix.start;
    applied++;
  }
  return {text: out, applied};
}

// Several .bib files share the box, each after a marker comment. These give a
// line's file and its line in that file, and split the box back into files.
export function joinSources(files) {
  if (files.length < 2) return files.map(file => file.text).join('');
  return files.map(file => RULES.sourceMarker + file.name + '\n' + file.text.replace(/\r\n?/g, '\n').replace(/\n?$/, '\n')).join('');
}
export function splitSources(text) {
  const parts = [];
  for (const line of text.split('\n')) {
    if (line.startsWith(RULES.sourceMarker)) parts.push({name: line.slice(RULES.sourceMarker.length).trim(), lines: []});
    else if (parts.length) parts.at(-1).lines.push(line);
    else parts.push({name: null, lines: [line]});
  }
  // A file from the box ends with one line break, as joinSources wrote it.
  return parts.map(part => ({name: part.name, text: part.name ? part.lines.join('\n').replace(/\n*$/, '\n') : part.lines.join('\n')}));
}
export function sourceLine(text, line) {
  const lines = text.split('\n', line);
  for (let n = lines.length - 1; n >= 0; n--) {
    if (lines[n].startsWith(RULES.sourceMarker)) return {name: lines[n].slice(RULES.sourceMarker.length).trim(), line: line - n - 1};
  }
  return {name: null, line};
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
    // Code examples are not citations: blank them, keeping line breaks so
    // line numbers still match the file. Inline \\verb and \\lstinline go
    // first, because their text may hold a % sign.
    const blank = part => part.replace(/[^\n]/g, ' ');
    const text = stripComments(file.text.replace(/\r\n?/g, '\n').replace(new RegExp(RULES.inlineCode, 'g'), blank))
      .replace(/\\begin{(verbatim\*?|lstlisting|minted|comment)}[\s\S]*?\\end{\1}/g, blank);
    const lineAt = lineIndex(text);
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
          else if (!found.has(key)) found.set(key, {name: file.name || '.tex file', line: lineAt(m.index)});
        }
        rest = rest.slice(group[0].length);
      } while (multi);
    }
  }
  return {found, all};
}

// The safe fix for a finding, as {edit}, or {} when it needs a person.
function fixFor(id, entry, field = id) {
  const span = entry.spans[field], inner = span && single(span);
  if (inner === null || inner === undefined) return {};
  let fix = null;
  if (id === 'special' && !RULES.nameFields.includes(field) && !new RegExp(RULES.linkCommands).test(inner)) {
    // Escape only the characters the check flagged: outside math, not escaped.
    const literal = literalText(inner);
    let out = '';
    for (let i = 0; i < inner.length; i++) {
      if (/[&%_#]/.test(literal[i]) && !escaped(literal, i)) out += '\\';
      out += inner[i];
    }
    if (out !== inner) fix = fixField(span, 'Escape the special characters', rewrap(span, out));
  } else if (id === 'doi') {
    // A DOI written as a link or with doi: in front: keep only the DOI itself.
    const bare = /^\s*(?:https?:\/\/(?:dx\.)?doi\.org\/|doi:\s*)(\S+)\s*$/i.exec(inner)?.[1];
    if (bare && !bare.includes('%') && new RegExp(RULES.checks.doi.pattern, 'i').test(bare)) fix = fixField(span, 'Keep only the DOI', rewrap(span, bare));
  } else if (id === 'month') {
    const word = inner.trim().toLowerCase().replace(/\.$/, '');
    const n = RULES.monthNames.indexOf(word) + 1 || RULES.months.indexOf(word) + 1 || (word === 'sept' ? 9 : 0);
    if (n) fix = fixField(span, 'Use the month number', '{' + n + '}');
  } else if (id === 'year' && !entry.fields.date && /^\d{4}-\d{2}(?:-\d{2})?$/.test(inner.trim()) && validDate(inner.trim())) {
    // A full ISO date belongs in date; the value is unchanged.
    fix = fixField(span, 'Move this date into the date field', span.raw, 'date');
  }
  return fix ? {edit: fix} : {};
}

export function checkReferences({bib = '', preamble = '', tex = [], unused = false} = {}, rules = RULES) {
  const parsed = parseBib(bib), style = detectStyle(preamble), findings = [];
  // A finding points at the field when the entry has it, else at the entry.
  // Location: line, and start/end offsets in bib (or file and line for .tex).
  const place = (entry, field) => {
    const span = entry?.spans[field] || entry;
    return span ? {line: span.line, start: span.start, end: span.end} : {};
  };
  const add = (id, key, field, detail = '', where = {}, extra = {}) => {
    const rule = rules.checks[id], [href, guide] = rules.guides[rule.guide];
    findings.push({id, severity: rule.severity, key, field,
      fix: rule.fix.replaceAll('{detail}', detail), href, guide, ...where, ...extra});
  };
  const matches = (id, value) => new RegExp(rules.checks[id].pattern, 'i').test(value);
  for (const e of parsed.errors) {
    add(e.id, e.key, e.field, e.detail, e.line ? {line: e.line, start: e.start, end: e.end, entry: e.entry} : {}, e.edit ? {edit: e.edit} : {});
  }
  if (!parsed.entries.length) add('empty', '(file)', 'entry');
  if (!style.profile) add('style', '(preamble.tex)', 'style', style.style);
  const keys = new Map(), folded = new Map(), sources = new Map(), people = new Map();
  const citations = citedKeys(tex);
  for (const entry of parsed.entries) {
    const {key, fields: f} = entry;
    const type = rules.aliases[entry.type] || entry.type;
    // Shorthands: the finding's place, and add() for this entry.
    const here = field => place(entry, field === 'key' ? null : field);   // a key finding is about the entry, not a key field
    const note = (id, field, detail, extra) => add(id, key, field, detail, {...here(field), entry: place(entry)}, extra);
    const also = other => ({related: place(other)});
    if (keys.has(key)) note('duplicate', 'key', '', also(keys.get(key)));
    else keys.set(key, entry);
    const twin = folded.get(key.toLowerCase());
    if (twin && twin.key !== key) note('keyCase', 'key', twin.key, also(twin));
    if (!twin) folded.set(key.toLowerCase(), entry);
    if (!matches('key', key)) note('key', 'key');
    if (type === 'xdata') { note('unsupported', 'entry', '@xdata inheritance'); continue; }
    const inherited = f.crossref || f.xdata;
    if (inherited) note('unsupported', f.crossref ? 'crossref' : 'xdata', 'inherited fields from ' + inherited);
    const expectations = rules.types[type];
    if (!expectations) note('type', 'entry type', type);
    // No missing-field claims when inheritance may supply them, or when a
    // syntax error may have hidden fields.
    if (expectations && !inherited && !entry.broken) {
      for (const [kind, groups] of [['required', expectations.required],
        ['recommended', [...expectations.recommended, ...(style.profile?.recommend?.[type] || [])]]]) {
        for (const group of new Set(groups)) {
          if (!group.split('|').some(field => f[field]?.trim()) &&
              !(group === 'type' && ['phdthesis', 'mastersthesis'].includes(entry.type))) note(kind, group, group.replaceAll('|', ' or '));
        }
      }
    }
    if (f.url && !f.urldate) note('access', 'urldate');
    for (const field of ['date', 'urldate', 'origdate', 'eventdate']) {
      if (f[field] && !validDate(f[field], field === 'urldate')) note('date', field);
    }
    for (const field of ['year', 'month', 'doi']) {
      if (f[field] && !matches(field, f[field])) note(field, field, '', fixFor(field, entry));
    }
    if (f.date && (f.year || f.month)) note('dateOverrides', 'date');
    if (f.isbn && !validISBN(f.isbn)) note('isbn', 'isbn');
    if (f.url) {
      if (!matches('url', f.url)) note('url', 'url');
      if (matches('http', f.url)) note('http', 'url');
      if (f.doi && matches('doiUrl', f.url) && f.url.replace(new RegExp(rules.checks.doiUrl.pattern, 'i'), '').toLowerCase() === f.doi.toLowerCase()) note('doiUrl', 'url');
    }
    for (const field of rules.ignoredFields) if (f[field]) note('ignored', field);
    for (const field of style.disabled) if (f[field]) note('disabled', field, field);
    if (type === 'misc' && (f.journal || f.journaltitle)) note('miscArticle', 'entry type');
    for (const field of rules.nameFields) {
      if (!f[field]) continue;
      for (const name of splitTop(f[field], ' and ').map(s => s.trim())) {
        if (name.startsWith('{') && name.endsWith('}')) continue;
        for (const id of ['organization', 'separators', 'particle']) if (matches(id, name)) note(id, field);
        const parts = splitTop(name, ',').map(s => s.trim());
        if (parts.length > 3 || (parts.length === 2 && parts[0].split(/\s+/).length > 1 && parts[1].split(/\s+/).length > 1)) note('commas', field);
        if (parts.length < 3 && matches('suffix', name)) note('suffix', field);
        const words = name.split(/\s+/), family = (parts.length > 1 ? parts[0] : words.at(-1)).toLowerCase();
        const given = parts.length > 1 ? parts.at(-1) : words.slice(0, -1).join(' ');
        const identity = family + ':' + (given.match(/[A-Za-z]/)?.[0] || '').toLowerCase();
        const form = family + ':' + given.replace(/[.\s{}]/g, '').toLowerCase();
        if (given && people.has(identity) && people.get(identity).form !== form) note('nameForms', field, people.get(identity).name + ' (' + people.get(identity).key + ')');
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
        if (words.length) note('capitals', field, [...new Set(words)].join(', '));
      }
    }
    for (const [field, value] of Object.entries(f)) {
      if (matches('encoding', value)) note('encoding', field);
      if (!rules.verbatimFields.includes(field)) {
        const literal = literalText(value);
        const chars = [...literal.matchAll(new RegExp(rules.checks.special.pattern, 'g'))];
        if (chars.some(m => !escaped(literal, m.index))) note('special', field, '', fixFor('special', entry, field));
      }
    }
    const ids = [f.doi && 'doi:' + f.doi.toLowerCase(), f.title && 'title:' + f.title.normalize('NFKD').replace(/[^\p{L}\p{N}]/gu, '').toLowerCase()].filter(Boolean);
    const duplicate = ids.map(id => sources.get(id)).find(Boolean);
    if (duplicate && duplicate.key !== key) note('duplicateEntry', 'doi/title', duplicate.key, also(duplicate));
    for (const id of ids) sources.set(id, entry);
    if (unused && tex.length && !citations.all && !citations.found.has(key)) note('unused', 'key');
  }
  for (const [key, cited] of citations.found) if (!keys.has(key)) add('missing', key, 'citation', cited.name, {file: cited.name, line: cited.line});
  const order = Object.keys(rules.severities);
  findings.sort((a, b) => order.indexOf(a.severity) - order.indexOf(b.severity));
  return {style: style.style, entries: parsed.entries.length, findings,
    coverage: tex.length ? 'Only the supplied .tex files were checked for citations.' : 'No .tex files supplied; citation coverage was not checked.'};
}
