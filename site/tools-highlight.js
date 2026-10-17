// Colored LaTeX in tool output (the converter, the settings builder, the
// error explainer). An extra only: without it, or with JavaScript off, the
// same text shows in one color. Copy and Download always use the plain text.
//
// The pattern and the tok-* class names match highlight_latex() in
// scripts/build_site.py, which colors the guide's code blocks at build time;
// the colors are the --code-* tokens in site/site.css. Text is added with
// text nodes only, never as HTML.
//
// Also the shared tool states (ToolState, at the end), used by every tool.
(function () {
  "use strict";
  var TOKENS = new RegExp(
    "(\\\\\\([\\s\\S]*?\\\\\\)|\\\\\\[[\\s\\S]*?\\\\\\]|\\$\\$[\\s\\S]*?\\$\\$|\\$(?:[^$\\\\\\n]|\\\\.)+\\$)" +  // math
    "|(\\\\(?:[A-Za-z@]+\\*?|[^A-Za-z@\\n]))" +   // a command, or an escaped character such as \%
    "|(%[^\\n]*)" +                             // a comment
    "|([{}])|(\\[)|(\\])" +                     // braces; brackets around options
    "|(@[A-Za-z]+)", "g");                      // a BibTeX entry type

  // Plain text -> [{type, text}], type "" for plain. Text inside [ ] on one line is an option.
  function tokens(text) {
    var out = [], depth = 0, pos = 0, match;
    function push(type, piece) { if (piece) out.push({ type: type, text: piece }); }
    function plain(piece) {
      piece.split("\n").forEach(function (line, index) {
        if (index) { push("", "\n"); depth = 0; }
        push(depth ? "opt" : "", line);
      });
    }
    TOKENS.lastIndex = 0;
    while ((match = TOKENS.exec(text))) {
      plain(text.slice(pos, match.index));
      pos = TOKENS.lastIndex;
      if (match[5]) { depth += 1; push("opt", match[5]); }
      else if (match[6]) { push("opt", match[6]); depth = Math.max(0, depth - 1); }
      else if (match[1]) push("math", match[1]);
      else if (match[2] || match[7]) push("cmd", match[2] || match[7]);
      else if (match[3]) push("com", match[3]);
      else push("brace", match[4]);
    }
    plain(text.slice(pos));
    return out;
  }

  // Replace node's contents with the colored text.
  function render(node, text) {
    node.textContent = "";
    if (!text) return;
    var fragment = document.createDocumentFragment();
    tokens(String(text)).forEach(function (token) {
      if (!token.type) { fragment.appendChild(document.createTextNode(token.text)); return; }
      var span = document.createElement("span");
      span.className = "tok-" + token.type;
      span.textContent = token.text;
      fragment.appendChild(span);
    });
    node.appendChild(fragment);
  }

  window.ToolsHighlight = { tokens: tokens, render: render };

  // The shared tool states (docs/project/components.md, "Tool states"): one
  // status line per tool, a live region (role="status") that is
  //   ""         empty (first load, or after Clear)
  //   "working"  a calm indicator before the text; the tool is aria-busy and
  //              the busy button cannot be pressed again
  //   "done"     a one-line summary; results follow under it
  //   "error"    a .tool-error box: a short title, what happened and the fix,
  //              and a guide link. Announced by the live region.
  // Each tool's ui.js falls back to plain status text without this file.
  function setState(root, status, state, content, button) {
    status.textContent = "";
    status.setAttribute("data-state", state || "");
    if (state === "working") root.setAttribute("aria-busy", "true");
    else root.removeAttribute("aria-busy");
    Array.prototype.forEach.call(root.querySelectorAll("[data-busy]"), function (node) {
      node.removeAttribute("data-busy");
      node.removeAttribute("aria-disabled");
    });
    if (state === "working" && button) {
      button.setAttribute("data-busy", "");
      button.setAttribute("aria-disabled", "true");
    }
    if (!content) return;
    if (typeof content === "string") { status.textContent = content; return; }
    var box = document.createElement("div");
    box.className = "tool-error";
    var title = document.createElement("p");
    title.className = "tool-error-title";
    title.textContent = content.title;
    box.appendChild(title);
    var text = document.createElement("p");
    text.textContent = content.text;
    if (content.href) {
      text.appendChild(document.createTextNode(" "));
      var link = document.createElement("a");
      link.href = content.href;
      link.textContent = content.link;
      text.appendChild(link);
      text.appendChild(document.createTextNode("."));
    }
    box.appendChild(text);
    status.appendChild(box);
  }
  // True while a button is busy: its click does nothing.
  function busy(button) { return button.hasAttribute("data-busy"); }

  // A drop zone: the same blue look on every tool while something is over it.
  // Children fire their own enter and leave events, so they are counted.
  function dropZone(zone, onDrop) {
    var depth = 0;
    zone.addEventListener("dragenter", function (event) { event.preventDefault(); depth++; zone.classList.add("is-over"); });
    zone.addEventListener("dragover", function (event) { event.preventDefault(); });
    zone.addEventListener("dragleave", function () { if (--depth <= 0) { depth = 0; zone.classList.remove("is-over"); } });
    zone.addEventListener("drop", function (event) {
      event.preventDefault();
      depth = 0;
      zone.classList.remove("is-over");
      onDrop(event);
    });
  }

  window.ToolState = { set: setState, busy: busy, dropZone: dropZone };
})();
