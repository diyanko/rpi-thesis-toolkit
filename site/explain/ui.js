// "Explain my error" (docs/explain-my-error.md): the page part. An extra only:
// with JavaScript off the page shows the table of known messages instead.
//
// The pasted text stays in this browser tab and is never sent anywhere. The
// reading is in core.js, next to this file; the known problems come from the
// page's <script type="application/json" id="explain-problems"> block, which
// scripts/build_site.py makes from KNOWN_PROBLEMS in scripts/build.py.
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
  var result = root.querySelector(".explain-result");
  var status = root.querySelector(".explain-status");
  var submit = root.querySelector("button[type=submit]");
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
  function para(parts) {
    var p = el("p");
    parts.forEach(function (part) { p.appendChild(typeof part === "string" ? document.createTextNode(part) : part); });
    return p;
  }
  function link(page, anchor, label) {
    return el("a", label, { href: page + ".html" + (anchor ? "#" + anchor : "") });
  }
  function where(error) {
    if (error.file && error.line) return "open " + error.file + " and go to line " + error.line;
    if (error.line) return "go to line " + error.line + " of the file LaTeX was reading (the log names it a few lines above the error)";
    return "";
  }

  function show(found) {
    result.textContent = "";
    var error = found.error, problem = found.problem;
    say(error ? "Found the first error" + (problem ? ": a known message." : ".") : problem ? "Found a known message."
      : "No LaTeX error found in the text.", "done");
    var head = el("h3", error ? "The first error" : problem ? "The message" : "No LaTeX error found", { tabindex: "-1" });
    result.appendChild(head);
    if (error) {
      var pre = el("pre", null, { tabindex: "0" });
      var code = pre.appendChild(el("code"));
      if (window.ToolsHighlight) window.ToolsHighlight.render(code, error.block);
      else code.textContent = error.block;
      result.appendChild(pre);
      var place = [];
      if (error.file) place.push("File: ", el("code", error.file), ". ");
      if (error.line) place.push("Line: " + error.line + ".");
      if (place.length) result.appendChild(para(place));
    } else if (!problem) {
      result.appendChild(el("p", "Nothing in the text looks like a LaTeX error. If the PDF was made, the log may be" +
        " from a run that worked; warnings are not errors. Otherwise paste the lines that start with ! or with a file name" +
        " and a line number (such as ./chapters/01-introduction.tex:13:), or the whole log."));
    }
    if (problem) {
      result.appendChild(el("h3", "What it means"));
      result.appendChild(el("p", problem.means));
      result.appendChild(el("h3", "What to try"));
      result.appendChild(el("p", problem.fix));
      var steps = el("ul");
      var at = error ? where(error) : "";
      var editor = problem.editor || (at ? at.charAt(0).toUpperCase() + at.slice(1) + "." : "");
      var overleaf = problem.overleaf || (at ? "Click the error under Logs and output files to jump there, or " + at + "." : "");
      if (editor) steps.appendChild(el("li", "In an editor on your computer: " + editor));
      if (overleaf) steps.appendChild(el("li", "On Overleaf: " + overleaf));
      if (steps.children.length) result.appendChild(steps);
      result.appendChild(para(["More in the guide: ", link(problem.guide[0], problem.guide[1], problem.guide[2]), "."]));
    } else {
      result.appendChild(el("h3", "Read it step by step"));
      var list = el("ol");
      (error ? [where(error) ? "Note the place: " + where(error) + "." : "Look for the file and line the log names just above the error.",
                "Look at that line and the line before it: the last thing on the l. line is where LaTeX stopped.",
                "Check the usual causes: a typo in a command, a missing }, a special character such as _ or & or %," +
                " or a wrong file name.",
                "Fix that one thing and compile again. Later errors are often side effects of the first."]
             : []).forEach(function (step) { list.appendChild(el("li", step)); });
      if (list.children.length) result.appendChild(list);
      result.appendChild(para(["See ", link("troubleshooting", "read-an-error-message", "Read an error message"),
                               ", the ", link("troubleshooting", "common-messages", "common messages"),
                               ", or ", link("troubleshooting", "ask-for-help", "ask for help"), "."]));
    }
    head.focus();
  }

  function ready() {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      // Edge cases first: nothing pasted, or far more than a log.
      if (State.busy && State.busy(submit)) return;
      var text = input.value;
      result.textContent = "";
      if (!/\S/.test(text)) {
        State.set(root, status, "", "Paste the error or the whole log in the box first.");
        input.focus();
        return;
      }
      if (text.length > 5000000) {
        fail("That is more than a log", "Paste the part that starts at the first line beginning with !, instead of the whole text.",
             "#where-to-copy-the-error-from", "Where to copy the error from");
        input.focus();
        return;
      }
      say("Reading the text…", "working");
      setTimeout(function () {
        show(window.ExplainCore.explain(text, problems));
      }, 30);
    });
    // New text makes the old answer stale: remove it.
    input.addEventListener("input", function () {
      if (!result.textContent && status.getAttribute("data-state") !== "done") return;
      result.textContent = "";
      say("The text changed. Choose Explain the error to read it again.");
    });
    root.querySelector(".explain-clear").addEventListener("click", function () {
      input.value = "";
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
