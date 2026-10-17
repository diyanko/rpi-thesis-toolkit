// "Explain my error" (docs/explain-my-error.md): reading a pasted LaTeX error
// or log, without any page or window code, so scripts/tests/test_explain.py
// can run it in a headless browser. site/explain/ui.js shows the result.
//
//   explain(text, problems) -> {error, problem}
//       error: the first real error, or null:
//              {file, line, message, context, block}; file and context may be "".
//       problem: the first known problem it matches, or null.
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
// text (a warning, or a message from latexmk or the editor), in all of it.
// Nothing is sent anywhere.
(function (root) {
  "use strict";
  var START = /^(?:(?:[A-Za-z]:)?[^:\s][^:]*\.\w+:\d+: |! )/;
  var GENERIC = /Emergency stop|==> Fatal error occurred|job aborted/;
  var NOISE = /^(?:See the .* (?:documentation|manual|Companion)|Type +H <return>|\s*\.\.\.\s*$|\s*$)/;

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

  function firstError(lines) {
    var found = [];
    lines.forEach(function (line, index) { if (START.test(line)) found.push(index); });
    var real = found.filter(function (index) { return !GENERIC.test(lines[index]); });
    var pick = (real.length ? real : found)[0];
    if (pick === undefined) return null;
    var block = lines.slice(pick, pick + 12), context = "";
    for (var k = 0; k < block.length; k++) {
      if (/^l\.\d+/.test(block[k])) {
        block = block.slice(0, k + 2);  // l.N and the rest of that source line
        context = block.slice(k).join("\n").replace(/\s+$/, "");
        break;
      }
    }
    block = block.filter(function (part) { return !NOISE.test(part); });
    var head = block[0], file = "", line = "", message = head.replace(/^! /, "");
    var place = head.match(/^((?:[A-Za-z]:)?[^:\s][^:]*\.\w+):(\d+): (.*)$/);
    if (place) {
      file = place[1].replace(/^\.[\\/]/, "");
      line = place[2];
      message = place[3];
    } else {
      var at = context.match(/^l\.(\d+)/);
      if (at) line = at[1];
    }
    return { file: file, line: line, message: message.trim(), context: context, block: block.join("\n") };
  }

  function explain(text, problems) {
    var lines = unwrap(String(text || ""));
    var error = firstError(lines);
    var tests = (problems || []).map(function (entry) { return [new RegExp(entry.pattern), entry]; });
    function match(where) {
      for (var i = 0; i < tests.length; i++) if (tests[i][0].test(where)) return tests[i][1];
      return null;
    }
    var problem = error ? match(error.block) : match(lines.join("\n"));
    return { error: error, problem: problem };
  }

  root.ExplainCore = { explain: explain, unwrap: unwrap };
})(typeof self !== "undefined" ? self : this);
