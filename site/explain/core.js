// "Explain my error" (docs/explain-my-error.md): reading a pasted LaTeX error
// or log, without any page or window code, so scripts/tests/test_explain.py
// can run it in a headless browser. site/explain/ui.js shows the result.
//
//   explain(text, problems) -> {error, problem, notes}
//       error: the first real error, or null:
//              {file, line, message, context, block, read, rest, guessed};
//              file, line, context, read and rest may be "". read is the
//              part of the l.N line TeX had read when it stopped (it ends at
//              the problem), rest the part it had not read yet. guessed is
//              true when the message has no file name and the file is the
//              one the log shows TeX reading at that point.
//       problem: the first known problem it matches, or null.
//       notes: everything else worth knowing in a whole log, grouped and
//              counted, in the order of NOTES below:
//              {kind, title, what, count, items, problem}. title has the
//              count in it ("3 citations not found"); notes that say one
//              thing ("Compile again") have count 0 and no items. items (at
//              most MAX, widest box first) are {text, file, line, problem};
//              problem is the KNOWN_PROBLEMS entry with the fix, or null.
//       problems is the page's <script type="application/json"
//       id="explain-problems"> block, parsed: KNOWN_PROBLEMS in
//       scripts/build.py, the same table the build helper prints from.
//
// The first error is found as build.py's first_error() finds it, so the page
// and the build helper point at the same lines: a line starting "file:N: "
// (LaTeX's -file-line-error form, also Windows paths such as C:\thesis\a.tex)
// or "! ", up to the l.N line that shows where TeX stopped. TeX's generic stop
// lines (Emergency stop, Fatal error) count only when nothing else is there.
// TeX wraps its log at 79 bytes; those lines are joined first.
//
// The known problems are looked for in the first error; with no error in the
// text (a warning, or a message from latexmk or the editor), in all of it,
// where a message that stops the build comes before the warnings in NOTES.
// The file a warning belongs to comes from the log's "(./chapters/a.tex"
// ... ")" groups, as layout_warnings() in build.py reads them.
// Nothing is sent anywhere.
(function (root) {
  "use strict";
  var START = /^(?:(?:[A-Za-z]:)?[^:\s][^:]*\.\w+:\d+: |! )/;
  var GENERIC = /Emergency stop|==> Fatal error occurred|job aborted/;
  var NOISE = /^(?:See the .* (?:documentation|manual|Companion)|Type +H <return>|\s*\.\.\.\s*$|\s*$)/;
  var PLACE = /^((?:[A-Za-z]:)?[^:\s][^:]*\.\w+):(\d+): (.*)$/;
  var MAX = 5;   // items shown per group; the count says how many there are

  // The groups under the first error. problem is a KNOWN_PROBLEMS id (its
  // guide link is the fix); a title in two forms (one, many) follows a count.
  var NOTES = [
    { kind: "error", problem: "", title: ["more error", "more errors"],
      what: "Often side effects of the first error: fix that one, compile again, and see which remain." },
    { kind: "citation", problem: "undefined-reference", title: ["citation not found", "citations not found"],
      what: "Shown in bold in the PDF. Compile again first; if a key stays here, check its spelling in references.bib." },
    { kind: "reference", problem: "undefined-reference", title: ["reference not found", "references not found"],
      what: "Shown as ?? in the PDF. Compile again first; if a name stays here, check it against its \\label." },
    { kind: "biber", problem: "biber-not-run", title: ["Biber has not run"],
      what: "The bibliography step has not run since your last change. Compile again." },
    { kind: "rerun", problem: "rerun", title: ["Compile again"],
      what: "Numbers, references, or bookmarks changed in this run; the next compile settles them." },
    { kind: "seal", problem: "seal-missing", title: ["RPI seal not found"],
      what: "The title page shows a box where the RPI seal goes." },
    { kind: "character", problem: "missing-character", title: ["character missing", "characters missing"],
      what: "The font has no such character, so it is left out of the PDF." },
    { kind: "overfull", problem: "overfull-hbox", title: ["line too wide", "lines too wide"],
      what: "Something sticks out into the margin: often a long URL, word, table, or equation; the widest is listed first." },
    { kind: "underfull", problem: "underfull", title: ["loosely spaced line", "loosely spaced lines"],
      what: "LaTeX stretched the spaces, often after \\\\ or \\linebreak. Usually harmless; look if it shows in the PDF." }
  ];

  function bytes(line) {
    return typeof TextEncoder !== "undefined" ? new TextEncoder().encode(line).length : line.length;
  }

  function unwrap(text) {
    var lines = text.replace(/\r\n?/g, "\n").split("\n"), out = [];
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      while (bytes(lines[i]) === 79 && i + 1 < lines.length) line += lines[++i];
      out.push(line);
    }
    return out;
  }

  function clean(path) { return path.replace(/^\.[\\/]/, ""); }

  // The .tex file TeX was reading at the start of each line ("" when unknown).
  // Box contents and the source lines TeX shows after an error are text from
  // the thesis, where a ( or ) means nothing, so they are skipped.
  function files(lines) {
    var stack = [], at = [], skip = 0;
    lines.forEach(function (line, index) {
      var top = "";
      for (var k = stack.length - 1; k >= 0; k--) if (stack[k]) { top = stack[k]; break; }
      at.push(top);
      if (skip) {
        if (skip === "box") { if (!/\S/.test(line)) skip = 0; return; }
        skip -= 1;
        if (/^l\.\d+/.test(line)) skip = 1;   // and the rest of that source line
        return;
      }
      if (/^(?:Over|Under)full \\[hv]box/.test(line)) { skip = "box"; return; }
      if (START.test(line)) { skip = 12; return; }
      var token, tokens = /\(([^\s()]*)|\)/g;
      while ((token = tokens.exec(line))) {
        if (token[0] === ")") stack.pop();
        else stack.push(/\.tex$/.test(token[1]) ? clean(token[1]) : "");
      }
    });
    return at;
  }

  function firstError(lines) {
    var found = [];
    lines.forEach(function (line, index) { if (START.test(line)) found.push(index); });
    var real = found.filter(function (index) { return !GENERIC.test(lines[index]); });
    var pick = (real.length ? real : found)[0];
    if (pick === undefined) return null;
    var error = errorAt(lines, pick);
    error.index = pick;
    return error;
  }

  function errorAt(lines, pick) {
    var block = lines.slice(pick, pick + 12), context = "", read = "", rest = "";
    for (var k = 0; k < block.length; k++) {
      if (/^l\.\d+/.test(block[k])) {
        block = block.slice(0, k + 2);  // l.N and the rest of that source line
        context = block.slice(k).join("\n").replace(/\s+$/, "");
        read = block[k].replace(/^l\.\d+ ?/, "");
        rest = (block[k + 1] || "").replace(/^\s+|\s+$/g, "");
        break;
      }
    }
    block = block.filter(function (part) { return !NOISE.test(part); });
    var head = block[0], file = "", line = "", message = head.replace(/^! /, "");
    var place = head.match(PLACE);
    if (place) {
      file = clean(place[1]);
      line = place[2];
      message = place[3];
    } else {
      var at = context.match(/^l\.(\d+)/);
      if (at) line = at[1];
    }
    return { file: file, line: line, message: message.trim(), context: context, block: block.join("\n"),
             read: read.replace(/\s+$/, ""), rest: rest, guessed: false };
  }

  // Everything after the first error, grouped by NOTES kind.
  function collect(lines, error, reading, match) {
    var groups = {}, seen = {};
    function add(kind, key, item, weight) {
      if (seen[kind + "\n" + key]) return;
      seen[kind + "\n" + key] = true;
      (groups[kind] = groups[kind] || []).push({ item: item, weight: weight || 0 });
    }
    var first = error ? [error.file, error.line, error.message].join("\n") : "";
    lines.forEach(function (text, index) {
      var file = reading[index], found;
      if (START.test(text) && !GENERIC.test(text)) {
        if (error && index === error.index) return;
        var other = errorAt(lines, index);
        if (!other.file) other.file = file;
        var key = [other.file, other.line, other.message].join("\n");
        if (key === first) return;
        var problem = match(other.block);
        add("error", key, { text: other.message, file: other.file, line: other.line, problem: problem && problem.id });
      } else if ((found = text.match(/Citation [`']([^']*)' (?:on page \d+ )?undefined(?: on input line (\d+))?/))) {
        add("citation", found[1], { text: found[1], file: file, line: found[2] || "" });
      } else if ((found = text.match(/Reference [`']([^']*)' (?:on page \d+ )?undefined(?: on input line (\d+))?/))) {
        add("reference", found[1], { text: found[1], file: file, line: found[2] || "" });
      } else if (/Please \(re\)run Biber/.test(text)) {
        add("biber", "", null);
      } else if (/Label\(s\) may have changed|Rerun to get [a-z -]+ right/.test(text)) {
        add("rerun", "", null);
      } else if (/rpi-thesis Warning: RPI seal not found/.test(text)) {
        add("seal", "", null);
      } else if (/^Missing character: /.test(text)) {
        // A message of exactly 79 bytes looks like a wrapped one, so two can share a line.
        var lost = /Missing character: There is no (.+?) in font [^!]*!?/g;
        while ((found = lost.exec(text))) add("character", found[1], { text: found[1], file: file, line: "" });
      } else if ((found = text.match(/^(Over|Under)full \\([hv])box \((?:([\d.]+)pt too (?:wide|high)|badness (\d+))\)(?: in (?:paragraph|alignment) at lines (\d+)--(\d+)| detected at line (\d+))?/))) {
        var lines_ = found[5] ? (found[5] === found[6] ? found[5] : found[5] + "\u2013" + found[6]) : found[7] || "";
        var size = found[3] ? Math.round(parseFloat(found[3]) * 10) / 10 + " pt too " + (found[2] === "h" ? "wide" : "high") : "";
        var kind = found[1] === "Over" ? "overfull" : "underfull";
        add(kind, [file, lines_, found[3] || found[4], found[2]].join("\n"),
            { text: size, file: file, line: lines_ }, parseFloat(found[3] || found[4] || "0"));
      }
    });
    var notes = [];
    NOTES.forEach(function (note) {
      var list = groups[note.kind];
      if (!list) return;
      if (note.kind === "overfull" || note.kind === "underfull") {
        list = list.slice().sort(function (a, b) { return b.weight - a.weight; });   // stable: ties keep log order
      }
      var counted = note.title.length > 1;   // a note that appears once or many times reads the same
      notes.push({ kind: note.kind, title: counted ? list.length + " " + note.title[list.length === 1 ? 0 : 1] : note.title[0],
                   what: note.what, count: counted ? list.length : 0, problem: note.problem,
                   items: counted ? list.slice(0, MAX).map(function (entry) { return entry.item; }) : [] });
    });
    return notes;
  }

  function explain(text, problems) {
    var lines = unwrap(String(text || ""));
    var error = firstError(lines);
    var reading = files(lines);
    var tests = (problems || []).map(function (entry) { return [new RegExp(entry.pattern), entry]; });
    var byId = {};
    (problems || []).forEach(function (entry) { byId[entry.id] = entry; });
    function match(where) {
      for (var i = 0; i < tests.length; i++) if (tests[i][0].test(where)) return tests[i][1];
      return null;
    }
    var notes = collect(lines, error, reading, match);
    var problem = error ? match(error.block) : null;
    if (!error) {
      // No error: a message that stops the build (a missing tool) first, then
      // the warnings in the order of NOTES, then anything else in the table.
      var listed = {};
      NOTES.forEach(function (note) { if (note.problem) listed[note.problem] = true; });
      var all = lines.join("\n");
      for (var i = 0; i < tests.length && !problem; i++) {
        if (!listed[tests[i][1].id] && tests[i][0].test(all)) problem = tests[i][1];
      }
      if (!problem && notes.length && notes[0].problem) problem = byId[notes[0].problem] || null;
      if (!problem) problem = match(all);
    }
    notes = notes.filter(function (note) {
      // A message the page already explains above needs no second mention.
      return !(problem && note.problem === problem.id && !note.items.length);
    });
    notes.forEach(function (note) {
      note.problem = byId[note.problem] || null;
      note.items.forEach(function (item) { if (item.problem) item.problem = byId[item.problem] || null; });
    });
    if (error) {
      if (!error.file && reading[error.index]) { error.file = reading[error.index]; error.guessed = true; }
      delete error.index;
    }
    return { error: error, problem: problem, notes: notes };
  }

  root.ExplainCore = { explain: explain, unwrap: unwrap, NOTES: NOTES };
})(typeof self !== "undefined" ? self : this);
