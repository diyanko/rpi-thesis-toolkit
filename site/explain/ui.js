// "Explain my error" (docs/explain-my-error.md): the page part. An extra only:
// with JavaScript off the page shows the table of known messages instead.
//
// The pasted text, or the chosen .log file, stays in this browser tab and is
// never sent anywhere or saved. The reading is in core.js, next to this file;
// the known problems come from the page's <script type="application/json"
// id="explain-problems"> block, which scripts/build_site.py makes from
// KNOWN_PROBLEMS in scripts/build.py.
// Classic scripts only, so the page also works in the offline guide.
(function () {
  "use strict";
  var root = document.querySelector("[data-explain]");
  var script = document.currentScript;
  var data = document.getElementById("explain-problems");
  if (!root || !script || !data) return;
  var problems = JSON.parse(data.textContent);
  var form = root.querySelector("form");
  var input = root.querySelector("textarea");
  var picker = root.querySelector("input[type=file]");
  var names = root.querySelector("[data-file-names]");
  var result = root.querySelector(".explain-result");
  var status = root.querySelector(".explain-status");
  var submit = root.querySelector("button[type=submit]");
  var MAX_SIZE = 5000000;
  // The shared states (ToolState in tools-highlight.js); plain text without it.
  var State = window.ToolState || { set: function (r, s, state, c) {
    s.textContent = typeof c === "string" ? c : c ? c.title + ". " + c.text : ""; } };
  function say(text, state) { State.set(root, status, state || "", text, submit); }
  function fail(title, text, href, link) { State.set(root, status, "error", { title: title, text: text, href: href, link: link }); }

  function el(tag, text, attrs) {
    var node = document.createElement(tag);
    if (text) node.textContent = text;
    Object.keys(attrs || {}).forEach(function (name) { node.setAttribute(name, attrs[name]); });
    return node;
  }
  function para(parts, tag) {
    var p = el(tag || "p");
    parts.forEach(function (part) { p.appendChild(typeof part === "string" ? document.createTextNode(part) : part); });
    return p;
  }
  function link(page, anchor, label) {
    return el("a", label, { href: page + ".html" + (anchor ? "#" + anchor : "") });
  }
  function guideLink(problem) { return link(problem.guide[0], problem.guide[1], problem.guide[2]); }
  function colored(node, text) {
    if (window.ToolsHighlight) window.ToolsHighlight.render(node, text);
    else node.textContent = text;
    return node;
  }
  // "line 13" or "lines 23–26"
  function lines(line) { return (/\D/.test(line) ? "lines " : "line ") + line; }
  function where(error) {
    if (error.file && error.line) return "open " + error.file + " and go to line " + error.line;
    if (error.line) return "go to line " + error.line + " of the file LaTeX was reading (the log names it a few lines above the error)";
    return "";
  }

  // The error as LaTeX printed it, with the part of the l.N line that LaTeX
  // read before it stopped highlighted: the problem is at its end.
  function block(error) {
    var pre = el("pre", null, { tabindex: "0" });
    var code = pre.appendChild(el("code"));
    var parts = error.block.split("\n"), at = -1;
    for (var i = 0; i < parts.length; i++) if (/^l\.\d+/.test(parts[i])) { at = i; break; }
    if (at < 0 || !error.read) {
      colored(code, error.block);
      return pre;
    }
    var prefix = parts[at].match(/^l\.\d+ ?/)[0];
    if (at) code.appendChild(colored(el("span"), parts.slice(0, at).join("\n") + "\n"));
    code.appendChild(document.createTextNode(prefix));
    code.appendChild(colored(el("mark"), parts[at].slice(prefix.length)));
    code.appendChild(el("span", " (LaTeX stopped here)", { "class": "visually-hidden" }));
    if (at + 1 < parts.length) code.appendChild(colored(el("span"), "\n" + parts.slice(at + 1).join("\n")));
    return pre;
  }

  // Where to look, in the two places students write.
  function goThere(error) {
    var list = el("ul");
    if (error.file && error.line) {
      var first = error.line.split(/\D/)[0];
      // TODO(verify): VS Code's Quick Open accepts file:line (Ctrl+P, Cmd+P on a Mac); recheck in the current version.
      list.appendChild(para(["In VS Code: press Ctrl+P (Cmd+P on a Mac), type ",
                             el("code", error.file + ":" + first), " and press Enter."], "li"));
      list.appendChild(para(["On Overleaf: click the error under Logs and output files to jump there, or open ",
                             el("code", error.file), " in the file list and go to " + lines(error.line) + "."], "li"));
    } else if (error.line) {
      list.appendChild(el("li", "Go to line " + error.line + " of the file LaTeX was reading: the log names it a few lines above the error."));
      list.appendChild(el("li", "On Overleaf: click the error under Logs and output files to jump there."));
    }
    return list;
  }

  // Everything else in the log, collapsed: one line per kind, with a count,
  // a few words on what it means, the first few places, and the fix.
  function more(notes, open) {
    var box = el("details", null, { "class": "explain-more" });
    if (open) box.open = true;
    // The summary counts: "3 citations not found, 1 line too wide, and 2 notes".
    var counted = notes.filter(function (note) { return note.count; }).map(function (note) { return note.title; });
    var single = notes.length - counted.length;
    if (single) counted.push(single === 1 && !counted.length ? "1 note" : single + (single === 1 ? " note" : " notes"));
    if (counted.length > 1) counted[counted.length - 1] = "and " + counted[counted.length - 1];
    box.appendChild(el("summary", "Also in the log: " + counted.join(counted.length > 2 ? ", " : " ")));
    var list = box.appendChild(el("ul"));
    notes.forEach(function (note) {
      var item = list.appendChild(el("li"));
      var line = [el("strong", note.title + "."), " " + note.what];
      if (note.problem) line.push(" Fix: ", guideLink(note.problem), ".");
      item.appendChild(para(line));
      if (!note.items.length) return;
      var places = item.appendChild(el("ul"));
      note.items.forEach(function (entry) {
        var parts = [];
        var place = (entry.file ? entry.file : "") + (entry.line ? (entry.file ? ", " : "") + lines(entry.line) : "");
        if (note.kind === "error") {
          parts.push((place ? place + ": " : "") + entry.text);
          if (entry.problem) parts.push(" (", guideLink(entry.problem), ")");
        } else if (note.kind === "overfull" || note.kind === "underfull") {
          parts.push(place || "the log does not say where");
          if (entry.text) parts.push(": " + entry.text);
        } else {
          parts.push(el("code", entry.text));
          if (place) parts.push(" in " + place);
        }
        places.appendChild(para(parts, "li"));
      });
      if (note.count > note.items.length) places.appendChild(el("li", "and " + (note.count - note.items.length) + " more"));
    });
    return box;
  }

  function show(found) {
    result.textContent = "";
    var error = found.error, problem = found.problem, notes = found.notes || [];
    var also = notes.length ? " More from the log is listed under it." : "";
    say((error ? "Found the first error" + (problem ? ": a known message." : ".") : problem ? "Found a known message."
      : notes.length ? "No LaTeX error found." : "No LaTeX error found in the text.") + also, "done");
    var head = el("h3", error ? "The first error" : problem ? "The message" : "No LaTeX error found", { tabindex: "-1" });
    result.appendChild(head);
    if (error) {
      result.appendChild(block(error));
      if (error.file || error.line) {
        result.appendChild(para(error.file ? [error.guessed ? "LaTeX was reading " : "File: ", el("code", error.file),
                                              error.line ? ", " + lines(error.line) + "." : "."]
                                           : ["Line: " + error.line + "."]));
      }
      if (error.read) result.appendChild(el("p", "The highlighted part of the l." + error.line.split(/\D/)[0] + " line is what" +
        " LaTeX read before it stopped: the problem is at its end or just before it."));
    } else if (!problem && !notes.length) {
      result.appendChild(el("p", "Nothing in the text looks like a LaTeX error. If the PDF was made, the log may be" +
        " from a run that worked; warnings are not errors. Otherwise paste the lines that start with ! or with a file name" +
        " and a line number (such as ./chapters/01-introduction.tex:13:), or the whole log."));
    } else if (!problem) {
      result.appendChild(el("p", "LaTeX reported no error in this text, so the PDF was probably made. The warnings below" +
        " are worth a look before you submit."));
    }
    var steps = error && !(problem && problem.editor) ? goThere(error) : el("ul");
    if (steps.children.length) {
      result.appendChild(el("h3", "Where to look"));
      result.appendChild(steps);
    }
    if (problem) {
      result.appendChild(el("h3", "What it means"));
      result.appendChild(el("p", problem.means));
      result.appendChild(el("h3", "What to try"));
      result.appendChild(el("p", problem.fix));
      // The l. line ends where TeX stopped: its last command is the unknown one.
      var stop = problem.id === "undefined-command" && error && error.read.match(/\\[A-Za-z@]+\*?/g);
      if (stop) result.appendChild(para(["Here that is probably ", el("code", stop[stop.length - 1]), "."]));
      var own = el("ul");
      if (problem.editor) own.appendChild(el("li", "In an editor on your computer: " + problem.editor));
      if (problem.overleaf) own.appendChild(el("li", "On Overleaf: " + problem.overleaf));
      if (own.children.length) result.appendChild(own);
      result.appendChild(para(["More in the guide: ", guideLink(problem), "."]));
    } else if (error) {
      result.appendChild(el("h3", "Read it step by step"));
      var list = el("ol");
      [where(error) ? "Note the place: " + where(error) + "." : "Look for the file and line the log names just above the error.",
       "Look at that line and the line before it: the last thing on the l. line is where LaTeX stopped.",
       "Check the usual causes: a typo in a command, a missing }, a special character such as _ or & or %," +
       " or a wrong file name.",
       "Fix that one thing and compile again. Later errors are often side effects of the first."
      ].forEach(function (step) { list.appendChild(el("li", step)); });
      result.appendChild(list);
    }
    if (notes.length) result.appendChild(more(notes, !error));
    if (!problem) {
      result.appendChild(para(["See ", link("troubleshooting", "read-an-error-message", "Read an error message"),
                               ", the ", link("troubleshooting", "common-messages", "common messages"),
                               ", or ", link("troubleshooting", "ask-for-help", "ask for help"), "."]));
    }
    head.focus();
  }

  var pending = 0;   // the explanation waiting to be shown, cancelled by new text or Clear
  var revision = 0;  // a file being read is dropped when the text changes meanwhile
  function run() {
    if (State.busy && State.busy(submit)) return;
    var text = input.value;
    result.textContent = "";
    // Edge cases first: nothing pasted, or far more than a log.
    if (!/\S/.test(text)) {
      State.set(root, status, "", "Paste the error or the whole log in the box first, or choose the .log file.");
      input.focus();
      return;
    }
    if (text.length > MAX_SIZE) {
      fail("That is more than a log", "Paste the part that starts at the first line beginning with !, instead of the whole text.",
           "#where-to-copy-the-error-from", "Where to copy the error from");
      input.focus();
      return;
    }
    say("Reading the text…", "working");
    clearTimeout(pending);
    pending = setTimeout(function () {
      pending = 0;
      show(window.ExplainCore.explain(text, problems));
    }, 30);
  }

  // A chosen or dropped .log file: read here, put in the box, and explained.
  function read(list) {
    var file = list && list[0];
    if (!file) return;
    var mine = ++revision;
    clearTimeout(pending);
    pending = 0;
    result.textContent = "";
    if (names) names.textContent = "";
    if (!/\.(?:log|txt)$/i.test(file.name)) {
      fail("Choose the .log file", file.name + " is not a LaTeX log. Choose main.log, in the build folder or next to main.tex," +
           " or copy the error from your editor and paste it in the box.", "#where-to-copy-the-error-from", "Where to copy the error from");
      return;
    }
    if (file.size > MAX_SIZE) {
      fail("That is more than a log", file.name + " is larger than 5 MB. Open it, copy the part from the first line" +
           " beginning with !, and paste that in the box.", "#where-to-copy-the-error-from", "Where to copy the error from");
      return;
    }
    say("Reading " + file.name + " on your computer…", "working");
    var reader = new FileReader();
    reader.onload = function () {
      if (mine !== revision) return;
      input.value = String(reader.result || "");
      if (names) names.textContent = "Read: " + file.name + " (nothing was uploaded)";
      say("");
      run();
    };
    reader.onerror = function () {
      if (mine === revision) fail("The file could not be read", "Open " + file.name + " in your editor, copy all of its text," +
                                  " and paste it in the box.");
    };
    reader.readAsText(file);
  }

  function ready() {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      run();
    });
    // New text makes the old answer stale: remove it.
    input.addEventListener("input", function () {
      revision++;
      if (names) names.textContent = "";
      if (pending) { clearTimeout(pending); pending = 0; say(""); }
      if (!result.textContent && status.getAttribute("data-state") !== "done") return;
      result.textContent = "";
      say("The text changed. Choose Explain the error to read it again.");
    });
    // A file dropped on the text box is read like a chosen one, not opened by the browser.
    input.addEventListener("drop", function (event) {
      if (!event.dataTransfer || !event.dataTransfer.files.length) return;
      event.preventDefault();
      read(event.dataTransfer.files);
    });
    if (picker) {
      picker.addEventListener("change", function () { read(picker.files); picker.value = ""; });
      var drop = root.querySelector("[data-drop]");
      if (drop && State.dropZone) State.dropZone(drop, function (event) { read(event.dataTransfer.files); });
      else if (drop) {
        drop.addEventListener("dragover", function (event) { event.preventDefault(); });
        drop.addEventListener("drop", function (event) { event.preventDefault(); read(event.dataTransfer.files); });
      }
    }
    root.querySelector(".explain-clear").addEventListener("click", function () {
      clearTimeout(pending);
      pending = 0;
      revision++;
      input.value = "";
      if (names) names.textContent = "";
      result.textContent = "";
      say("");
      input.focus();
    });
    root.hidden = false;
    var note = document.querySelector("[data-explain-nojs]");
    if (note) note.hidden = true;
  }
  var tag = document.createElement("script");
  tag.src = script.src.replace(/[^/]*$/, "") + "core.js";
  tag.onload = ready;
  document.head.appendChild(tag);
})();
