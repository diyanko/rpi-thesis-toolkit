/* Optional guide search. No requests, storage, dependencies, or HTML injection. */
(function () {
  "use strict";
  var dialog = document.querySelector(".search-dialog");
  if (!dialog || !Array.isArray(window.GUIDE_SEARCH)) return;

  function normalize(text) {
    return text.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
      .replace(/[’']/g, "").replace(/\?\?+/g, " question marks ")
      .replace(/\$/g, " dollar ").replace(/&/g, " ampersand ")
      .replace(/\{/g, " openingbrace ").replace(/\}/g, " closingbrace ")
      .replace(/_/g, " underscore ").replace(/%/g, " percent ")
      .replace(/[^a-z0-9]+/g, " ").trim().replace(/\bback up\b/g, "backup")
      .replace(/\bquestionmarks?\b/g, "question marks")
      .replace(/\btoc\b/g, "contents").replace(/\blof\b/g, "list figures").replace(/\blot\b/g, "list tables")
      .replace(/\bvscode\b/g, "vs code").replace(/\btexlive\b/g, "tex live")
      .replace(/\bphd\b/g, "doctoral").replace(/\bdeng\b/g, "engineering doctorate").replace(/\bms\b/g, "masters")
      .replace(/\b(?:does not exist|doesnt exist|cannot be found|cant be found)\b/g, "not found")
      .replace(/\b(?:not working|does not work|doesnt work)\b/g, "broken")
      .replace(/\bcut off\b/g, "clipped")
      .replace(/\b(?:do not|does not|dont|doesnt|not|isnt|arent) (?:show up|showing|show|appear|appearing|display|displaying)\b/g, "missing")
      .replace(/\b(?:do not|does not|will not|dont|doesnt|wont|not) (?:update|updating|refresh|refreshing|change|changing)\b/g, "stale")
      .replace(/\b(?:timing out|time out|timeout|taking too long)\b/g, "timed out");
  }
  function words(text) { return normalize(text).split(/\s+/).filter(Boolean); }
  var groups = [
    ["bibliography", "references", "citation", "citations", "cite"],
    ["figure", "figures", "image", "images", "picture", "pictures", "photo", "photos", "photograph", "photographs"],
    ["compile", "compiled", "compiling", "compilation", "compiler", "recompile", "build", "building"],
    ["seal", "logo"], ["error", "errors", "problem", "problems", "troubleshooting", "broken"],
    ["install", "installation", "setup"], ["equation", "equations", "math", "mathematics"],
    ["submit", "submission", "submitting"], ["acknowledgment", "acknowledgments", "acknowledgements"],
    ["add", "insert", "include", "put"], ["change", "changing", "edit", "editing", "replace"],
    ["move", "moving", "jump", "jumps", "float", "floats", "floating", "placement", "position"],
    ["wrong", "different", "elsewhere"], ["empty", "blank", "missing", "absent", "disappeared", "gone", "invisible"],
    ["accent", "accented", "unicode", "characters", "garbled"],
    ["wide", "width", "overflow", "overfull", "oversized", "big", "huge", "large", "tall", "clipped", "cropped", "truncated"],
    ["backup", "backups", "protect", "restore", "recover", "recovery"], ["advisor", "supervisor", "chair"],
    ["parenthetical", "parentheses", "parencite"],
    ["share", "send", "sharing", "review"], ["code", "listing", "listings"],
    ["symbol", "symbols", "notation"], ["folder", "directory"],
    ["word", "docx"], ["slides", "presentation", "powerpoint"],
    ["download", "starter", "zip"], ["windows", "pc"], ["mac", "macos", "mactex"],
    ["bring", "import", "convert", "conversion", "migrate", "transfer"],
    ["number", "numbers", "numbered", "numeric", "numbering"],
    ["differences", "difference", "diff", "changes", "changed", "compare", "versions"],
    ["placeholder", "box", "boxes", "framed", "rectangles"], ["document", "draft"],
    ["brace", "braces", "curly", "bracket", "brackets", "openingbrace", "closingbrace"],
    ["update", "updated", "updating", "stale", "refresh"], ["source", "sources", "entry", "record"],
    ["abbreviation", "abbreviations", "acronym", "acronyms", "glossary", "glossaries", "nomenclature", "nomencl"],
    ["landscape", "sideways", "rotate", "rotated", "rotating", "sidewaystable", "sidewaysfigure"],
    ["subfigure", "subfigures", "subfig", "subcaption", "panel", "panels"],
    ["hyperlink", "hyperlinks", "hyperref", "hypersetup", "hidelinks"]
  ];
  var aliases = new Map();
  groups.forEach(function (group) { group.forEach(function (word) { aliases.set(word, group); }); });
  var stop = new Set(words("a an the i im ive my me how why what where when who do does did to for of in on is it its can could would should you your with and or this that these those please want need am are was were be been being have has had will wont dont doesnt didnt cant cannot not no from at as into about trying try use using used get getting got seems seem just really suddenly still already keeps keep says saying showing shows show see up all only thesis dissertation latex rpi instead than too taking official"));

  // Common short searches usually ask for the main task, not an obscure
  // error mentioning the same word. These routes boost existing guide text;
  // they never supply answers or manufacture destinations.
  var routes = [
    [/^(paste|convert|converter|word to latex|docs to latex|google docs to latex|markdown to latex|excel to latex|table to latex|bring (my|your) work in)$/, ["What it converts", "Put it in your thesis"]],
    [/^(apa|ieee|mla|chicago)( style)?$/, ["Change the citation style", "Print a full reference in the text"]],
    [/^(title page|committee|committee chair|graduation( month| year| date)?|masters( degree)?|doctoral( degree)?|engineering doctorate)$/, ["Put your name on it", "All thesis settings"]],
    [/^copyright( page)?$/, ["All thesis settings", "Put your name on it"]],
    [/^((re)?name (the |my )?pdf|pdf (file )?name|file ?name|output (file|name)|main pdf)$/, ["Name your PDF"]],
    // The five tools: short searches for a tool's job open the tool first.
    [/^(settings|settings builder|settings form|metadata( tex)?|title page settings|thesis settings)$/, ["Settings builder", "All thesis settings", "Put your name on it"]],
    [/^(bib|bib file|references bib|(references?|bib|bibliography|citations?) (check|checker)|check (references?|bib|bibliography|citations?))$/, ["Check your references", "Citations and references"]],
    [/^(error|errors|error message|explain|explain error|compile error|latex error|log|log file|main log)$/, ["Explain my error", "Read an error message"]],
    [/^(pdf (check|checker)|check pdf|check final pdf)$/, ["Check your PDF", "Final PDF checklist"]],
    [/^(list )?(abbreviations?|acronyms?|glossary|glossaries|nomenclature|symbols? list)$/, ["Add a list of symbols or abbreviations"]],
    [/^((landscape|sideways|rotate|rotated|rotating)( (page|pages|table|tables|figure|figures))?|(rotate|turn) (table|figure|page)( sideways)?)$/, ["Too wide for the page?"]],
    [/^(page (number|numbers|numbering)( roman| arabic| roman numerals| position| placement)?|pagination|roman( numerals?)?)$/,
      ["Your words and your formatting are separate", "What OGE commonly flags", "Final PDF checklist"]],
    [/^(font size|font sizes|10pt|11pt|12pt|class options?)$/, ["Where customizations belong", "Your words and your formatting are separate"]],
    [/^(hyperlinks?|hyperref|link colou?rs?)$/, ["Where customizations belong"]],
    [/^signatures?( page| pages| form| forms)?$/, ["The path to graduation", "Official resources"]],
    [/^(mendeley|endnote|jabref|reference manager)( export)?$/, ["If you can't use Zotero: paste an entry by hand", "Step 2: Collect and cite sources with Zotero"]],
    [/^(bibliography|references|reference list|bib|refs) (missing|empty)$/, ["The reference list is empty", "Citation `...' undefined, or Reference `...' undefined, or ?? or a bold citation key in the PDF"], "troubleshooting"],
    [/^(abstract|acknowledg[em]+ents?|front matter)$/, ["What each file does", "Optional sections"]],
    [/^appendi(x|ces)$/, ["What each file does", "Optional sections"]],
    [/^(main tex|file structure|files)$/, ["What each file does"]],
    [/^(preamble( tex)?|packages)$/, ["Where customizations belong"]],
    [/^(cls|rpi thesis cls|class file)$/, ["What each file does", "Your words and your formatting are separate"]],
    [/^(refs|bibliography|references)$/, ["Citations and references", "Step 2: Collect and cite sources with Zotero"], "citations"],
    [/^biber$/, ['What "compiling" does', "Bold citation keys and question marks"]],
    [/^biber error$/, ["Citations and references", "Clean recompile"], "troubleshooting"],
    [/^(tex live|mac|windows|linux)( install| setup)?$/, ["Step 3a: Your-computer route"]],
    [/^overleaf( install| setup)?$/, ["Step 3b: Overleaf route"]],
    [/^vs code( install| setup)?$/, ["Step 3a: Your-computer route", "Clean recompile"]],
    [/^(symbol|symbols)$/, ["Find a symbol's command", "Add a list of symbols or abbreviations"]],
    [/^(contents|table contents|list figures|list tables)$/, ["All thesis settings", 'What "compiling" does']],
    [/^(margins|font|fonts|double spacing|line spacing)$/, ["Your words and your formatting are separate", "Final PDF checklist"]],
    [/^(update template|update class|upgrade)$/, ["Update the formatting safely"]],
    [/^(eps|svg|tiff?|bmp|heic|webp)( file| files| image| images| figure| figures)?$/, ["Export a chart or convert an image", "Add a figure"]],
    [/^(deadline|submission deadline|forms|requirements)$/, ["Official resources", "The path to graduation"]]
  ];
  // Pasted compiler warnings whose wording differs from the guide's row
  // names. The third item says the row answers that message directly.
  var logRoutes = [
    [/\bcitation\b.*\bundefined\b|\bundefined citations\b/i, ["Citation `...' undefined, or Reference `...' undefined, or ?? or a bold citation key in the PDF", "Bold citation keys and question marks"], true],
    [/\bempty bibliography\b/i, ["The reference list is empty"], true],
    [/\breference\b.*\bundefined\b|\bundefined references\b|\blabel\(?s\)? may have changed\b|\brerun to get cross-references\b/i,
      ["Citation `...' undefined, or Reference `...' undefined, or ?? or a bold citation key in the PDF", "Cross-references"], true],
    [/\blabel\b.*\bmultiply[- ]defined\b|\bmultiply-defined labels\b/i, ["Cross-references", "Citation `...' undefined, or Reference `...' undefined, or ?? or a bold citation key in the PDF"], false],
    [/\bfile\b.*\.(?:png|jpe?g|pdf|eps|svg|tiff?)\b.*\bnot found\b|\bpdftex\.def error\b.*\bnot found\b|\bcannot determine size of graphic\b/i,
      ["LaTeX Error: File `figures/...' not found", "Add a figure"], true],
    [/\bunknown graphics extension\b/i, ["Export a chart or convert an image", "Add a figure"], true],
    [/\benvironment sideways(?:table|figure) undefined\b/i, ["Too wide for the page?"], true]
  ];

  // Bounded Damerau-Levenshtein tolerates adjacent swapped letters too.
  function distance(a, b, limit) {
    if (Math.abs(a.length - b.length) > limit) return limit + 1;
    var before, previous = Array.from({length: b.length + 1}, function (_, i) { return i; });
    for (var i = 1; i <= a.length; i++) {
      var row = [i];
      for (var j = 1; j <= b.length; j++) {
        row[j] = Math.min(row[j - 1] + 1, previous[j] + 1, previous[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) row[j] = Math.min(row[j], before[j - 2] + 1);
      }
      if (Math.min.apply(null, row) > limit) return limit + 1;
      before = previous; previous = row;
    }
    return previous[b.length];
  }

  var vocabulary = new Map();
  var entries = window.GUIDE_SEARCH.map(function (entry) {
    var all = new Set();
    var fields = [entry.title, entry.tasks || "", entry.context, entry.page, entry.text].map(function (text) {
      var tokens = new Map();
      words(text).forEach(function (token) { tokens.set(token, (tokens.get(token) || 0) + 1); all.add(token); });
      return tokens;
    });
    all.forEach(function (token) { vocabulary.set(token, (vocabulary.get(token) || 0) + 1); });
    return {source: entry, fields: fields, title: normalize(entry.title), text: normalize(entry.text), tasks: normalize(entry.tasks || ""),
      signatures: (entry.signatures || []).map(normalize)};
  });

  function firstError(query) {
    // Capture TeX's diagnostic before single-line inputs remove newlines.
    // Also recover a diagnostic from an already flattened compiler log.
    var tex = query.match(/(?:^|[\r\n.):])\s*!\s*([^!\r\n]+?)(?=\r?\n|\bl\.\d+\b|!|$)/);
    var fileLine = /\.(?:tex|sty|cls|ltx|def|aux|bbl|toc):\d+(?::\d+)?:/i;
    var taggedStart = query.search(/\.(?:tex|sty|cls|ltx|def|aux|bbl|toc):\d+(?::\d+)?:|^(?:\[[^\]]+\]\s*)?(?:ERROR|FATAL)\b/im);
    if (tex && (taggedStart < 0 || tex.index < taggedStart)) return "! " + tex[1].trim();
    var lines = query.split(/\r?\n/);
    var logPattern = /(?:(?:latex|package|class|biber).*?error|^(?:\[[^\]]+\]\s*)?(?:error|fatal)\b|:\s*error\b|undefined control sequence|missing\s+\S+\s+inserted|runaway argument|ENOENT|emergency stop|fatal error)/i;
    var line = lines.find(function (text) { return fileLine.test(text) || logPattern.test(text); })
      || lines.find(function (text) { return /(?:latex|package|class|biber).*?warning|overfull/i.test(text); });
    return line ? line.split(/\bl\.\d+\b|!\s*==>/)[0].trim() : "";
  }

  function analyze(query) {
    var line = firstError(query);
    // A lone context line such as "l.42 \foo" is still a pasted log.
    if (!line && /^\s*l\.\d+\b/.test(query)) line = query.trim();
    var selected = line ? line.replace(/^.*?:\d+(?::\d+)?:\s*/, "")
      // Drop the generic prefix and positions; keep the message itself.
      .replace(/^\s*!?\s*(?:(?:LaTeX|pdfTeX|Package\s+\S+|Class\s+\S+)\s+)?(?:Error|Warning|Info)\s*:\s*/i, "")
      .replace(/\s*\(?\bon (?:input )?line \d+\)?|\bon page \d+\b|^\s*l\.\d+\s*/gi, " ") : query;
    var phrase = normalize(selected);
    var logRouteTitles = [];
    logRoutes.forEach(function (route) {
      if (route[0].test(line || query)) route[1].forEach(function (title) { logRouteTitles.push({title: title, exact: route[2]}); });
    });
    if (line) phrase = phrase.replace(/\b\d+(?:pt|in|cm|mm|px)?\b/g, " ").replace(/\b(?:paragraph|lines?|badness|high|low)\b/g, " ").replace(/\s+/g, " ").trim();
    var failedCompile = /\b(wont|dont|doesnt|cannot|cant|failed|fails|stops?|stopped|will not|does not)\b/.test(phrase)
      && /\b(pdf|compile|compiling|build|building)\b/.test(phrase);
    var tokens = Array.from(new Set(words(phrase).filter(function (word) { return !stop.has(word) && !/^\d+$/.test(word); }))).slice(0, 32);
    if (!tokens.length) tokens = words(phrase).filter(function (word) { return ["latex", "thesis", "dissertation", "rpi"].includes(word); });
    var inserted = selected.match(/\bmissing\s+(\S+)\s+inserted\b/i);
    return {phrase: phrase, log: Boolean(line), inserted: inserted && inserted[1], failed: failedCompile, logRoutes: logRouteTitles,
      // Length and size limits are institutional rules the guide does not restate.
      policy: !line && (/\b(oge|rpi|university)\b/.test(phrase) && /\b(allow|allowed|policy|policies|permission|permit|approved)\b/.test(phrase)
        || /\b(word|page|length|size) limits?\b|\bhow long (should|can|must|may|is|are)\b.*\b(abstract|thesis|dissertation|title|chapters?)\b|\b(maximum|max|minimum|min) (length|pages|words|size)\b|\bhow many (pages|words)\b/.test(phrase)),
      pdfLocation: /\bwhere\b/.test(phrase) && /\bpdf\b/.test(phrase),
      draftImages: /\b(figures?|pictures?|photos?|images?)\b/.test(phrase) && /\b(box|boxes|rectangles?|placeholder)\b/.test(phrase),
      citationStyle: /\b(switch|change|instead)\b/.test(phrase) && /\b(apa|ieee|chicago|mla|author year|numbered)\b/.test(phrase),
      explainFiles: /\bwhat\b/.test(phrase) && /\b(file|cls|tex|preamble|metadata)\b/.test(phrase),
      metadata: /\b(change|edit|set|put|add)\b/.test(phrase) && /\b(name|degree|committee|chair|supervisor|graduation)\b/.test(phrase)
        && !/\b(citation|source|reference|bib)\b/.test(phrase),
      tokens: tokens};
  }

  function tokenMatches(token, exactOnly) {
    var result = new Map(), alternatives = aliases.get(token) || [token];
    vocabulary.forEach(function (_, word) {
      if (word === token) result.set(word, 1);
      else if (alternatives.indexOf(word) !== -1) result.set(word, 0.9);
      else if (token.length >= 3 && (word === token + "s" || token === word + "s")) result.set(word, 0.95);
      // Pasted logs are exact text: no prefixes or spelling corrections.
      else if (exactOnly) return;
      else if (token.length >= 3 && word.startsWith(token)) result.set(word, 0.72);
      else if (token.length >= 4) {
        var limit = token.length >= 8 ? 2 : 1, edits = distance(token, word, limit);
        if (edits <= limit) result.set(word, (edits === 1 ? 0.64 : 0.42) - 0.12 * Math.abs(token.length - word.length));
      }
    });
    Array.from(result).forEach(function (match) {
      (aliases.get(match[0]) || []).forEach(function (word) { result.set(word, Math.max(result.get(word) || 0, match[1] * 0.85)); });
    });
    // Rare terms distinguish topics; ubiquitous words such as PDF do not.
    var frequency = 0;
    result.forEach(function (quality, word) { if (quality >= 0.8) frequency = Math.max(frequency, vocabulary.get(word) || 0); });
    if (!frequency) result.forEach(function (_, word) { frequency = Math.max(frequency, vocabulary.get(word) || 0); });
    return {matches: result, weight: Math.log(1 + (entries.length + 1) / (frequency + 1))};
  }

  function search(query) {
    var request = analyze(query);
    if (request.policy) {
      var resources = entries.filter(function (entry) { return entry.source.title === "Official resources"; })
        .map(function (entry) { return {entry: entry.source, score: 0}; });
      resources.policy = true;
      return resources;
    }
    if (!request.tokens.length) return [];
    var routeWords = request.tokens.map(function (token) {
      if (vocabulary.has(token)) return token;
      var closest = token, best = 3, tied = false;
      aliases.forEach(function (_, word) {
        var edits = distance(token, word, token.length >= 8 ? 2 : 1);
        if (edits < best) { closest = word; best = edits; tied = false; }
        else if (edits === best && closest !== word) tied = true;
      });
      return !tied && best <= (token.length >= 8 ? 2 : 1) ? closest : token;
    }).join(" ");
    var routeTitles = request.logRoutes.slice();
    routes.forEach(function (route) {
      if (route[0].test(routeWords)) routeTitles = routeTitles.concat(route[1].map(function (title) { return {title: title, page: route[2]}; }));
    });
    var terms = request.tokens.map(function (token) { return tokenMatches(token, request.log); }), totalWeight = terms.reduce(function (sum, term) { return sum + term.weight; }, 0);
    var fieldWeights = [10, 8, 2, 1.5, 1];
    var results = entries.map(function (entry) {
      var inserted = entry.source.title.match(/\bmissing\s+(\S+)\s+inserted\b/i);
      // These are distinct TeX errors, even when most words are identical.
      if (request.inserted && inserted && request.inserted !== inserted[1]) return null;
      var score = 0, coverage = 0, closeness = 0, matched = 0;
      terms.forEach(function (term) {
        var best = 0, support = 0, closest = 0;
        entry.fields.forEach(function (field, f) {
          var fieldBest = 0;
          term.matches.forEach(function (quality, word) {
            var count = field.get(word);
            if (!count) return;
            closest = Math.max(closest, quality);
            // Repetition saturates; a long section cannot win by sheer size.
            fieldBest = Math.max(fieldBest, quality * fieldWeights[f] * (1 + 0.15 * count / (count + 1)));
          });
          best = Math.max(best, fieldBest); support += fieldBest;
        });
        if (best) { coverage += term.weight; closeness += term.weight * Math.min(1, closest / 0.6); matched++; score += term.weight * (best + support * 0.12); }
      });
      coverage /= totalWeight; closeness /= totalWeight;
      // A distant spelling only half covers a word, so a lone far-fetched
      // match (dedication ~ education) is not offered as an answer.
      if (closeness < 0.55) coverage = closeness;
      var titlePhrase = entry.title.includes(request.phrase), bodyPhrase = entry.text.includes(request.phrase);
      var exactMessage = entry.source.kind === "message" && (entry.title.length > 8 && request.phrase.includes(entry.title)
        || entry.signatures.some(function (signature) { return request.phrase.includes(signature); }));
      if (titlePhrase || exactMessage) score += 35;
      if (entry.tasks.includes(request.phrase)) score += 25;
      if (bodyPhrase) score += 12;
      if (request.failed && ["When a compile stops", "Read an error message"].includes(entry.source.title)) {
        score += 45; coverage = 1; matched++;
      }
      if (request.pdfLocation && entry.source.title === "Where the PDF ends up") { score += 60; coverage = 1; matched++; }
      if (request.draftImages && entry.source.title === "Overleaf says the compile timed out") { score += 70; coverage = 1; matched++; }
      if (request.citationStyle && entry.source.title === "Change the citation style") { score += 70; coverage = 1; matched++; }
      if (request.explainFiles && entry.source.title === "What each file does") { score += 60; coverage = 1; matched++; }
      if (request.metadata && entry.source.title === "Put your name on it") { score += 60; coverage = 1; matched++; }
      if (exactMessage) { score += 60; coverage = 1; }
      if (request.inserted && /^[{}]$/.test(request.inserted) && /brace error/i.test(entry.source.title)) {
        score += 60; coverage = 1; matched++;
      }
      var routePosition = routeTitles.findIndex(function (route) {
        return route.title === entry.source.title && (!route.page || entry.source.href.split("#")[0].split("/").pop() === route.page + ".html");
      });
      if (routePosition >= 0) { score += 90 - routePosition * 15; coverage = 1; matched++; }
      var logAnswer = routePosition >= 0 && routeTitles[routePosition].exact;
      if (!matched || coverage < 0.55) return null;
      score *= coverage * coverage;
      return {entry: entry.source, score: score, coverage: coverage, exact: exactMessage || titlePhrase || bodyPhrase || logAnswer};
    }).filter(Boolean).sort(function (a, b) {
      // Resolve equal scores the same way in every browser locale.
      return b.score - a.score || (a.entry.href < b.entry.href ? -1 : a.entry.href > b.entry.href ? 1 : 0);
    });
    // A confident, specific result suppresses weak one-word coincidences.
    if (results.length) results = results.filter(function (result) { return result.score >= results[0].score * 0.22; });
    results.related = Boolean(results.length && (results[0].coverage < 0.99 || request.log && !results[0].exact));
    // Unknown logs get clearly labeled reading/help links, never an invented fix.
    if (request.log && (!results.length || !results[0].exact && results[0].coverage < 0.8)) {
      results = entries.filter(function (entry) { return ["Read an error message", "When a compile stops", "Ask for help"].includes(entry.source.title); })
        .map(function (entry) { return {entry: entry.source, score: 0}; });
      results.unknownError = true;
    } else if (!results.length) {
      // Nothing matched: offer the task index and the troubleshooting page.
      results = ["How do I…?", "Fixing problems"].map(function (page) {
        return entries.find(function (entry) { return entry.source.title === page && entry.source.page === page; });
      }).filter(Boolean).map(function (entry) { return {entry: entry.source, score: 0}; });
      results.none = true;
    }
    results.log = request.log;
    // Highlight the words that actually matched, including aliases and
    // corrected spellings, not only the letters typed.
    results.highlight = new Set();
    terms.forEach(function (term) {
      term.matches.forEach(function (quality, word) { if (quality >= 0.4) results.highlight.add(word); });
    });
    return results;
  }

  var root = new URL(dialog.dataset.root || "./", document.baseURI);
  function element(tag, className, text) {
    var node = document.createElement(tag);
    node.className = className;
    node.textContent = text;
    return node;
  }
  function matcher(query, matched) {
    var terms = words(query).filter(function (word) { return !stop.has(word); });
    return function (part) {
      var word = normalize(part);
      return word.length > 1 && (matched && matched.has(word)
        || terms.some(function (term) { return term.length > 1 && word.startsWith(term); }));
    };
  }
  function excerpt(text, isMatch) {
    // Start near the passage with the most distinct matched words.
    var hits = [], found, pattern = /[A-Za-z0-9]+/g;
    while ((found = pattern.exec(text))) if (isMatch(found[0])) hits.push({at: found.index, word: normalize(found[0])});
    var position = -1, most = 0;
    hits.forEach(function (hit) {
      var near = new Set(hits.filter(function (other) { return other.at >= hit.at && other.at < hit.at + 120; })
        .map(function (other) { return other.word; }));
      if (near.size > most) { most = near.size; position = hit.at; }
    });
    var start = Math.max(0, position - 65);
    if (start) start = text.indexOf(" ", start) + 1;
    var snippet = text.slice(start, start + 185);
    if (start + 185 < text.length) snippet = snippet.replace(/\s+\S*$/, "") + "…";
    return (start ? "…" : "") + snippet;
  }
  function highlighted(text, isMatch) {
    var fragment = document.createDocumentFragment();
    // Split without altering offsets in the displayed text; punctuation stays.
    text.split(/([a-zA-Z0-9]+)/).forEach(function (part) {
      if (isMatch(part)) fragment.appendChild(element("mark", "", part));
      else fragment.appendChild(document.createTextNode(part));
    });
    return fragment;
  }
  var fields = [];
  document.querySelectorAll("[data-search]").forEach(function (section) {
    var input = section.querySelector("input"), list = section.querySelector("ol"), status = section.querySelector('[role="status"]');
    var timer;
    function update() {
      clearTimeout(timer);
      var query = input.value.trim();
      list.replaceChildren();
      if (!query) { status.textContent = ""; return; }
      if (normalize(query).length < 2) { status.textContent = "Type at least two letters or numbers."; return; }
      var results = search(query), shown = results.slice(0, 8);
      status.textContent = results.length ? (results.length > 8 ? "Showing 8 of " + results.length + " results." : results.length + (results.length === 1 ? " result." : " results.")) : "No matching sections. Try fewer words or a different topic. The task links on How do I…? can also help.";
      var isMatch = results.none || results.policy ? function () { return false; } : matcher(query, results.highlight);
      if (results.none) status.textContent = "No matching sections. Try fewer or different words, or start from one of these pages.";
      else if (results.unknownError) status.textContent = "This exact error is not covered in the guide. These sections explain how to read it and get help.";
      else if (results.policy) status.textContent = "For institutional policy, check the current official resources.";
      else if (results.related) status.textContent = "Related sections found for part of your question. Try fewer words to narrow the search.";
      // A pasted error: offer the tool that reads the whole message first.
      var explain = results.log && entries.find(function (entry) { return entry.source.title === "Explain my error" && entry.source.page === "Explain my error"; });
      if (explain && !location.pathname.endsWith(explain.source.href.split("#")[0])) {
        var tool = element("a", "search-result search-result-tool", "");
        tool.href = new URL(explain.source.href.split("#")[0], root).href + "#text=" + encodeURIComponent(query.slice(0, 4000));
        tool.appendChild(element("span", "search-result-page", "Tool"));
        tool.appendChild(element("span", "search-result-title", "Explain this error"));
        tool.appendChild(element("span", "search-result-text", "Opens Explain my error with your message filled in. Nothing is uploaded."));
        list.appendChild(element("li", "", "")).appendChild(tool);
      }
      shown.forEach(function (result) {
        var entry = result.entry, item = element("li", "", ""), link = element("a", "search-result", "");
        link.href = new URL(entry.href, root).href;
        var title = element("span", "search-result-title", "");
        title.appendChild(highlighted(entry.title, isMatch));
        link.appendChild(element("span", "search-result-page", entry.page + (entry.kind === "message" ? " / Common messages" : "")));
        link.appendChild(title);
        var summary = element("span", "search-result-text", "");
        summary.appendChild(highlighted(excerpt(entry.text, isMatch), isMatch));
        link.appendChild(summary);
        item.appendChild(link);
        list.appendChild(item);
      });
      list.scrollTop = 0;
    }
    input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(update, 100); });
    input.addEventListener("paste", function (event) {
      if (!event.clipboardData) return;
      var pasted = event.clipboardData.getData("text/plain");
      if (!/[\r\n]/.test(pasted)) return;
      event.preventDefault();
      var replacement = firstError(pasted) || pasted.replace(/[\r\n]+/g, " ");
      var value = input.value.slice(0, input.selectionStart) + replacement + input.value.slice(input.selectionEnd);
      input.value = value.slice(0, input.maxLength > 0 ? input.maxLength : value.length);
      update();
    });
    input.addEventListener("search", update);
    section.addEventListener("keydown", function (event) {
      if (event.isComposing) return;
      if (event.target === input && (event.key === "Enter" || event.key === "ArrowDown")) update();
      var links = Array.from(list.querySelectorAll("a")), index = links.indexOf(document.activeElement);
      if (event.key === "ArrowDown" && links.length) {
        event.preventDefault(); links[Math.min(index + 1, links.length - 1)].focus();
      } else if (event.key === "ArrowUp" && index >= 0) {
        event.preventDefault(); (index ? links[index - 1] : input).focus();
      } else if (event.key === "Enter" && event.target === input && links.length) {
        event.preventDefault(); links[0].click();
      }
    });
    update();
    section.hidden = false;
    fields.push({section: section, input: input, update: update});
  });

  var dialogField = fields.find(function (field) { return dialog.contains(field.section); });
  function openSearch() {
    if (dialog.open) return;
    dialog.showModal();
    dialogField.section.querySelector("ol").scrollTop = 0;
    dialogField.input.focus();
    dialogField.input.select();
  }
  if (typeof dialog.showModal === "function") {
    document.querySelectorAll("[data-search-open]").forEach(function (button) {
      button.addEventListener("click", openSearch);
      button.hidden = false;
    });
    dialog.querySelector(".search-close").addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("keydown", function (event) {
      // A search input can otherwise consume Escape just to clear its value.
      if (event.key === "Escape" && !event.isComposing) { event.preventDefault(); dialog.close(); }
    });
    dialog.addEventListener("click", function (event) {
      var rect = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
    });
    // Native dialog closing restores focus before a link navigates. Restoring it
    // again from the later close event would scroll away from a same-page result.
    dialog.addEventListener("click", function (event) {
      // Same-page section links must dismiss the modal as well as navigate.
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      if (event.target.closest(".search-result")) dialog.close();
    });
    document.addEventListener("keydown", function (event) {
      if ((event.ctrlKey || event.metaKey) && !event.altKey && event.key.toLowerCase() === "k") {
        event.preventDefault(); openSearch();
      } else if (event.key === "/" && !event.ctrlKey && !event.metaKey && !event.altKey && !event.isComposing && !dialog.open) {
        // "/" also opens search, unless the reader is typing somewhere.
        var target = event.target;
        if (target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return;
        event.preventDefault(); openSearch();
      }
    });
  }
  // A link with ?q=... opens search with that query (handouts, issue replies).
  var shared = new URLSearchParams(location.search).get("q");
  if (shared && dialogField && typeof dialog.showModal === "function") {
    openSearch();
    dialogField.input.value = shared.slice(0, 4000);
    dialogField.update();
  }
  // A deep link may land inside an optional example. Reveal its ancestors.
  function revealTarget() {
    var id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    var target = document.getElementById(id);
    if (target && target.tagName === "DETAILS") target.open = true;
    if (target) for (var parent = target.parentElement; parent; parent = parent.parentElement) {
      if (parent.tagName === "DETAILS") parent.open = true;
    }
    if (target && target.closest("details")) target.scrollIntoView();
  }
  revealTarget();
  window.addEventListener("hashchange", revealTarget);
})();
