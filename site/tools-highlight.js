// Colored LaTeX in tool output (the converter, the settings builder, the
// error explainer). An extra only: without it, or with JavaScript off, the
// same text shows in one color. Copy and Download always use the plain text.
//
// The pattern and the tok-* class names match highlight_latex() in
// scripts/build_site.py, which colors the guide's code blocks at build time;
// the colors are the --code-* tokens in site/site.css. Text is added with
// text nodes only, never as HTML.
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
})();
