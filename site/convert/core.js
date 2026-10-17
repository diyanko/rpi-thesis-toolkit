// "Bring your work in" (docs/bring-your-work-in.md): reading pasted text and
// writing LaTeX, without any page code, so scripts/tests/test_convert.py can
// run it in a headless browser. site/convert/ui.js is the page part.
//
//   convert({html, text}, {chapter: false}) -> {latex, source, notes, steps,
//       filename, kind, escaped}
//       html is the clipboard's text/html (may be ""), text its text/plain.
//
// Two steps. Readers (Word, Google Docs, spreadsheet cells, other rich text,
// Markdown, plain text, tab-separated cells) build a small tree of plain
// objects: blocks (heading, para, list, table, quote, code, math, picture)
// holding inline pieces (text, strong, em, code, link, math, sup, sub,
// picture). Only the writer turns the tree into LaTeX, so escaping happens in
// one place (escapeText), chosen by context: prose, URL, code, math, label.
//
// Privacy: pasted HTML is never put into the page. It is parsed with
// DOMParser into a document that has no window, so nothing in it runs or
// loads, and before that every element that could load something (pictures,
// frames, styles, scripts, media, links) is removed from the string; a
// picture leaves only a marker so the result can say where it was.
//
// Clipboard shapes (Word's mso-list paragraphs, Google Docs' docs-internal-guid
// wrapper and font-weight spans, spreadsheet tables) follow what those
// programs are known to write. TODO(verify): capture fresh clipboard HTML from
// current Word (Windows and macOS) and Google Docs and check these readers;
// anything not recognized is read as ordinary rich text or plain text.
(function (root) {
  "use strict";

  var LIMIT = 2000000;
  var EQ = "\u0001EQ\u0001";  // where an equation from Word was, until the writer marks it          // characters of pasted HTML or text read at most
  var MAX_ROWS = 500, MAX_COLS = 30, MAX_DEPTH = 200;

  // ---------- Escaping ------------------------------------------------------
  // Prose: the ten characters LaTeX treats specially.
  var SPECIAL = { "\\": "\\textbackslash{}", "{": "\\{", "}": "\\}", "%": "\\%", "&": "\\&", "_": "\\_",
                  "#": "\\#", "$": "\\$", "~": "\\textasciitilde{}", "^": "\\textasciicircum{}" };
  // Characters with a better LaTeX form. Greek letters and math symbols go
  // through \ensuremath, which prints them with both engines.
  var MATH = {
    "α": "\\alpha", "β": "\\beta", "γ": "\\gamma", "δ": "\\delta", "ε": "\\varepsilon", "ϵ": "\\epsilon",
    "ζ": "\\zeta", "η": "\\eta", "θ": "\\theta", "ϑ": "\\vartheta", "ι": "\\iota", "κ": "\\kappa",
    "λ": "\\lambda", "μ": "\\mu", "ν": "\\nu", "ξ": "\\xi", "ο": "o", "π": "\\pi", "ρ": "\\rho",
    "ς": "\\varsigma", "σ": "\\sigma", "τ": "\\tau", "υ": "\\upsilon", "φ": "\\varphi", "ϕ": "\\phi",
    "χ": "\\chi", "ψ": "\\psi", "ω": "\\omega",
    "Γ": "\\Gamma", "Δ": "\\Delta", "Θ": "\\Theta", "Λ": "\\Lambda", "Ξ": "\\Xi", "Π": "\\Pi",
    "Σ": "\\Sigma", "Υ": "\\Upsilon", "Φ": "\\Phi", "Ψ": "\\Psi", "Ω": "\\Omega",
    "Α": "\\mathrm{A}", "Β": "\\mathrm{B}", "Ε": "\\mathrm{E}", "Ζ": "\\mathrm{Z}", "Η": "\\mathrm{H}",
    "Ι": "\\mathrm{I}", "Κ": "\\mathrm{K}", "Μ": "\\mathrm{M}", "Ν": "\\mathrm{N}", "Ο": "\\mathrm{O}",
    "Ρ": "\\mathrm{P}", "Τ": "\\mathrm{T}", "Χ": "\\mathrm{X}",
    "±": "\\pm", "×": "\\times", "÷": "\\div", "−": "-", "≤": "\\leq", "≥": "\\geq", "≠": "\\neq",
    "≈": "\\approx", "∞": "\\infty", "→": "\\rightarrow", "←": "\\leftarrow", "↔": "\\leftrightarrow",
    "⇒": "\\Rightarrow", "⇔": "\\Leftrightarrow", "∑": "\\sum", "∏": "\\prod", "√": "\\surd",
    "∂": "\\partial", "∇": "\\nabla", "∈": "\\in", "∉": "\\notin", "⊂": "\\subset", "⊆": "\\subseteq",
    "∪": "\\cup", "∩": "\\cap", "∀": "\\forall", "∃": "\\exists", "∅": "\\emptyset", "∝": "\\propto",
    "∼": "\\sim", "≡": "\\equiv", "⋅": "\\cdot", "∘": "\\circ", "′": "^{\\prime}", "″": "^{\\prime\\prime}"
  };
  var TEXT = { "\u00a0": "~", "\u2013": "--", "\u2014": "---", "\u2026": "\\dots{}", "\u2010": "-", "\u2011": "-",
               "\u2009": "\\,", "\u202f": "\\,", "\u2002": " ", "\u2003": " ", "\u2004": " ", "\u2005": " ",
               "\u2006": " ", "\u2007": " ", "\u2008": " ", "\t": " " };
  // Dropped: soft hyphens, zero-width and direction marks, control characters.
  var DROP = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f\u00ad\u200b-\u200f\u2028\u2029\u2060\ufeff]/;
  // Printed by the starter's fonts as they are (Latin letters with accents,
  // Latin-1 signs, typographic quotes and marks). Anything else is kept and
  // listed for the student to check. TODO(verify): confirm with both engines
  // that every character in this range prints without a missing-glyph warning.
  var KEEP = /[\u0020-\u007e\u00a1-\u017f\u2018\u2019\u201a\u201c\u201d\u201e\u2020\u2021\u2022\u2030\u2122]/;

  // escapeText(text, state): prose. state counts escaped characters and
  // collects characters that may not print.
  function escapeText(text, state) {
    var out = "";
    for (var i = 0; i < text.length; i++) {
      var c = text.charAt(i);
      var code = text.charCodeAt(i);
      if (code >= 0xd800 && code <= 0xdbff && i + 1 < text.length) c = text.substr(i++, 2);
      if (SPECIAL[c]) { out += SPECIAL[c]; if (state) state.escaped++; }
      else if (TEXT[c] !== undefined) out += TEXT[c];
      else if (MATH[c]) out += "\\ensuremath{" + MATH[c] + "}";
      else if (c === "\n" || c === "\r") out += " ";
      else if (DROP.test(c)) continue;
      else {
        if (!KEEP.test(c) && state && state.odd.indexOf(c) < 0) state.odd.push(c);
        out += c;
      }
    }
    return out;
  }
  // A URL as the argument of \href (hyperref): % and # need a backslash;
  // braces, backslashes, spaces, and other characters are percent-encoded.
  function escapeUrl(url) {
    return url.replace(/[\\{}\s^]|[^\x21-\x7e]/gu, function (c) { return encodeURIComponent(c); })
              .replace(/[%#]/g, function (c) { return "\\" + c; });
  }
  // A label or file name: lowercase ASCII letters, digits, and hyphens.
  function slug(text, fallback) {
    var s = String(text || "").normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
    if (s.length > 32) s = s.slice(0, 32).replace(/-[^-]*$/, "");
    return s || fallback;
  }
  // Only web and e-mail addresses become links.
  function safeLink(href) {
    href = String(href || "").trim();
    var google = /^https?:\/\/(?:www\.)?google\.[a-z.]+\/url\?(?:.*&)?q=([^&]+)/i.exec(href);
    if (google) { try { href = decodeURIComponent(google[1]); } catch (e) { return ""; } }
    return /^(https?:\/\/[^\s]+|mailto:[^\s]+)$/i.test(href) ? href : "";
  }

  // ---------- Notes: what was not converted, or needs a look ------------------
  // id -> [text for one, text for several ({n} is the number), guide page,
  // section]; ui.js turns page and section into a link.
  var NOTES = {
    picture: ["1 picture was not copied; a % line in the LaTeX marks where it was. Save it in figures/ and add a figure there.",
              "{n} pictures were not copied; a % line in the LaTeX marks where each was. Save each one in figures/ and add a figure there.",
              "writing", "add-a-figure"],
    footnote: ["1 footnote was not converted. Its marker stays as plain text, such as [1], and its text is at the end. Move the text into \\footnote{...} at the marker.",
               "{n} footnotes were not converted. Each marker stays as plain text, such as [1], and the footnote text is at the end. Move each one into \\footnote{...} at its marker.",
               "bring-your-draft", "from-word-or-google-docs"],
    footnote_md: ["Markdown footnotes ([^1]) were kept as text. Move each one into \\footnote{...} at its marker.",
                  "Markdown footnotes ([^1]) were kept as text. Move each one into \\footnote{...} at its marker.",
                  "bring-your-draft", "from-markdown"],
    equation: ["1 equation from Word was not converted; it is marked [equation]. Write it again in LaTeX.",
               "{n} equations from Word were not converted; each is marked [equation]. Write each one again in LaTeX.",
               "writing", "equations"],
    "display-math": ["1 display equation went into a numbered equation environment. Check it and its label.",
                     "{n} display equations went into numbered equation environments. Check each one and its label.",
                     "writing", "equations"],
    citation: ["Citation keys such as [@key] were kept as text. Change each one to \\parencite{key}, with the key from references.bib.",
               "Citation keys such as [@key] were kept as text. Change each one to \\parencite{key}, with the key from references.bib.",
               "writing", "cite-a-source"],
    comment: ["1 comment was left out.", "{n} comments were left out.", "", ""],
    link: ["1 link was kept as text only: only web and e-mail addresses become links.",
           "{n} links were kept as text only: only web and e-mail addresses become links.", "", ""],
    caption: ["1 table needs a caption: replace \"Your full caption, ending with a period.\"",
              "{n} tables need a caption: replace \"Your full caption, ending with a period.\"", "writing", "edit-a-table"],
    merged: ["1 table had merged cells, which were split into separate cells. Check it; a heading over two columns uses \\multicolumn.",
             "{n} tables had merged cells, which were split into separate cells. Check them; a heading over two columns uses \\multicolumn.",
             "writing", "edit-a-table"],
    wide: ["1 table has more than six columns and may be too wide for the page.",
           "{n} tables have more than six columns and may be too wide for the page.", "writing", "too-wide-for-the-page"],
    big: ["1 table was cut to " + MAX_ROWS + " rows and " + MAX_COLS + " columns.",
          "{n} tables were cut to " + MAX_ROWS + " rows and " + MAX_COLS + " columns.", "", ""],
    chapters: ["", "{n} headings became \\chapter. Keep one chapter per file: split the result, one file for each chapter.", "writing", "chapters"],
    deep: ["1 heading was deeper than LaTeX's levels and became \\subsubsection.",
           "{n} headings were deeper than LaTeX's levels and became \\subsubsection.", "writing", "paragraphs-and-headings"],
    nested: ["A list was nested more than four levels deep; the deeper items moved up to the fourth level.",
             "Lists were nested more than four levels deep; the deeper items moved up to the fourth level.", "", ""],
    code: ["1 code block went into a verbatim environment, which prints it exactly as written.",
           "{n} code blocks went into verbatim environments, which print them exactly as written.", "", ""],
    odd: ["", "", "writing", "find-a-symbols-command"],
    cut: ["The pasted text was too long; only the first " + LIMIT + " characters were read.",
          "The pasted text was too long; only the first " + LIMIT + " characters were read.", "", ""]
  };
  function Notes() { this.count = {}; this.odd = []; }
  Notes.prototype.add = function (id, n) { this.count[id] = (this.count[id] || 0) + (n === undefined ? 1 : n); };
  Notes.prototype.list = function () {
    var out = [], count = this.count, odd = this.odd;
    Object.keys(NOTES).forEach(function (id) {
      var n = count[id], spec = NOTES[id], text;
      if (id === "odd") {
        if (!odd.length) return;
        text = "These characters may not print with the starter's fonts, and may stop the compile: " + odd.slice(0, 20).join(" ") +
          (odd.length > 20 ? " and " + (odd.length - 20) + " more" : "") +
          ". Check them in the PDF, or replace each one with its LaTeX command.";
      } else if (!n) {
        return;
      } else {
        text = (n === 1 ? spec[0] : spec[1]).replace("{n}", String(n));
      }
      out.push({ id: id, text: text, page: spec[2], anchor: spec[3] });
    });
    return out;
  };

  // ---------- Tree helpers ---------------------------------------------------
  function txt(text) { return { type: "text", text: text }; }
  function plain(nodes) {
    return nodes.map(function (n) {
      return n.type === "text" ? n.text : n.type === "math" || n.type === "code" ? n.text : n.children ? plain(n.children) : "";
    }).join("");
  }
  function hasContent(nodes) {
    return nodes.some(function (n) {
      return n.type === "picture" || n.type === "math" || n.type === "code" ||
        (n.type === "text" ? /[^\s\u00a0]/.test(n.text) : n.children ? hasContent(n.children) : false);
    });
  }
  // Rebuild nesting from a flat run of list items {level, ordered, children}.
  function nestItems(flat, notes) {
    var rootList = null, stack = [];
    flat.forEach(function (item) {
      var level = Math.max(1, item.level || 1);
      if (level > 4) { notes.add("nested"); level = 4; }
      while (stack.length > level) stack.pop();
      while (stack.length < level) {
        var list = { type: "list", ordered: item.ordered, items: [] };
        if (!stack.length) rootList = list;
        else {
          var parent = stack[stack.length - 1];
          if (!parent.items.length) parent.items.push({ children: [], lists: [] });
          parent.items[parent.items.length - 1].lists.push(list);
        }
        stack.push(list);
      }
      stack[stack.length - 1].items.push({ children: item.children, lists: [] });
    });
    return rootList;
  }

  // ---------- Reading HTML (Word, Google Docs, spreadsheets, web pages) ------
  // Removed from the string before parsing: anything that could load or run.
  var STRIP = /<(script|style|iframe|object|embed|video|audio|noscript|template|svg|math|title|head|xml|canvas|frameset|frame)\b[\s\S]*?<\/\1\s*>/gi;
  var VOID = /<(link|meta|base|source|track|param|input|embed|frame|v:imagedata|area)\b[^>]*>/gi;
  function cleanHtml(html) {
    return html
      .replace(/<!--\[if[\s\S]*?<!\[endif\]-->/gi, "")
      .replace(/<!--[\s\S]*?-->/g, "")
      .replace(/<math\b[\s\S]*?<\/math\s*>/gi, "<x-equation></x-equation>")
      .replace(/<svg\b[\s\S]*?<\/svg\s*>/gi, "<x-picture></x-picture>")
      .replace(STRIP, "")
      .replace(VOID, "")
      .replace(/<(img|v:shape|image|picture)\b[^>]*>/gi, function (tag) {
        var alt = /\salt\s*=\s*("[^"]*"|'[^']*')/i.exec(tag);
        return "<x-picture" + (alt ? " data-alt=" + alt[1] : "") + "></x-picture>";
      })
      .replace(/<\/(picture|v:shape)>/gi, "")
      .replace(/<[a-z][^>]*>/gi, function (tag) {
        // Inside tags only: no attribute that names something to load. Link
        // targets (href) stay; they are read as text, never followed.
        return tag.replace(/\s(?:src|srcset|background|poster|data|action|formaction|xlink:href|lowsrc|dynsrc|ping)\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "")
                  .replace(/url\s*\(/gi, "nourl(");
      });
  }
  function style(el) { return (el.getAttribute && el.getAttribute("style") || "").toLowerCase(); }
  function detect(html) {
    if (/google-sheets-html-origin/i.test(html)) return "sheets";
    if (/urn:schemas-microsoft-com:office:excel|ProgId\s+content=["']?Excel/i.test(html)) return "excel";
    if (/docs-internal-guid/i.test(html)) return "gdocs";
    if (/urn:schemas-microsoft-com:office:word|class=["']?Mso|mso-/i.test(html)) return "word";
    return "html";
  }

  function readHtml(html, notes) {
    var source = detect(html);
    var doc = new DOMParser().parseFromString(cleanHtml(html), "text/html");
    var body = doc.body;
    var blocks = [];
    var depth = 0;

    function marks(el, m) {
      var tag = el.tagName.toLowerCase(), s = style(el);
      m = { strong: m.strong, em: m.em };
      if (tag === "b" || tag === "strong") m.strong = !/font-weight\s*:\s*(normal|[1-4]00)\b/.test(s);
      if (tag === "i" || tag === "em" || tag === "cite" || tag === "dfn") m.em = !/font-style\s*:\s*normal/.test(s);
      var weight = /font-weight\s*:\s*([a-z0-9]+)/.exec(s);
      if (weight) m.strong = /^(bold|bolder|[6-9]00)$/.test(weight[1]);
      var italic = /font-style\s*:\s*([a-z]+)/.exec(s);
      if (italic) m.em = italic[1] === "italic" || italic[1] === "oblique";
      return m;
    }
    function hidden(el) {
      var s = style(el);
      return /display\s*:\s*none|mso-hide\s*:\s*all|visibility\s*:\s*hidden/.test(s) || el.hasAttribute("hidden");
    }
    function wrap(nodes, m) {
      if (m.em) nodes = [{ type: "em", children: nodes }];
      if (m.strong) nodes = [{ type: "strong", children: nodes }];
      return nodes;
    }
    // inline(node, m) -> inline pieces. m: formatting from the parents.
    function inline(node, m) {
      if (node.nodeType === 3) return node.nodeValue ? wrap([txt(node.nodeValue)], m) : [];
      if (node.nodeType !== 1 || hidden(node)) return [];
      var tag = node.tagName.toLowerCase(), s = style(node), cls = node.getAttribute("class") || "";
      if (tag === "x-picture") { notes.add("picture"); return [{ type: "picture", alt: node.getAttribute("data-alt") || "" }]; }
      if (tag === "x-equation" || /cambria math/.test(s)) return [{ type: "equation" }];
      if (tag === "br") return [txt(" ")];
      if (tag === "o:p" && !/[^\s\u00a0]/.test(node.textContent)) return [];
      if (/mso-list\s*:\s*ignore/.test(s)) return [];
      if (/MsoCommentReference/i.test(cls) || /mso-comment-reference/.test(s) ||
          (tag === "a" && /^#_msocom_/i.test(node.getAttribute("href") || ""))) return [];  // counted with the comment list
      var href = tag === "a" ? node.getAttribute("href") || "" : "";
      if (tag === "a" && /^#(_ftn|_edn|ftnt|cmnt)/i.test(href)) {
        if (/^#cmnt/i.test(href)) { notes.add("comment"); return []; }
        if (!/ref/i.test(href)) notes.add("footnote");  // the marker, not the link back from the footnote text
        return [txt(node.textContent.replace(/\s+/g, ""))];
      }
      var m2 = marks(node, m);
      var children = [];
      if (++depth > MAX_DEPTH) { depth--; return [txt(node.textContent)]; }
      Array.prototype.forEach.call(node.childNodes, function (child) { children = children.concat(inline(child, m2)); });
      depth--;
      if (tag === "code" || tag === "tt" || tag === "kbd" || tag === "samp") return wrap([{ type: "code", text: plain(children) }], m);
      if ((tag === "sup" || tag === "sub") && /^\s*\[?\d+\]?\s*$/.test(plain(children)) && /ftn|footnote/i.test(node.innerHTML)) return children;
      if (tag === "sup" || /vertical-align\s*:\s*super/.test(s)) return [{ type: "sup", children: children }];
      if (tag === "sub" || /vertical-align\s*:\s*sub/.test(s)) return [{ type: "sub", children: children }];
      if (tag === "a" && href) {
        var safe = safeLink(href);
        if (safe) return [{ type: "link", href: safe, children: children }];
        if (href.charAt(0) !== "#") notes.add("link");
      }
      return children;
    }
    function inlineOf(el) {
      var nodes = [];
      Array.prototype.forEach.call(el.childNodes, function (child) { nodes = nodes.concat(inline(child, { strong: false, em: false })); });
      return nodes;
    }
    // Word list paragraph: style "mso-list:l0 level2 lfo1"; its marker span
    // (mso-list:Ignore) says whether it is numbered.
    function wordItem(el) {
      var s = style(el), m = /mso-list\s*:\s*(l\d+)\s+level(\d)/.exec(s);
      if (!m && !/MsoListParagraph/i.test(el.getAttribute("class") || "")) return null;
      var marker = "";
      var ignore = el.querySelector("[style*='mso-list:Ignore' i], [style*='mso-list: Ignore' i]");
      if (ignore) marker = ignore.textContent.replace(/[\s\u00a0]+/g, "");
      return { group: m ? m[1] : "word", level: m ? +m[2] : 1, ordered: /^(\(?[0-9]+|[a-z]|[ivxlc]+)[.)]$/i.test(marker), children: inlineOf(el) };
    }
    function listItems(list, level, flat) {
      var ordered = list.tagName.toLowerCase() === "ol";
      Array.prototype.forEach.call(list.children, function (child) {
        var tag = child.tagName.toLowerCase();
        if (tag === "ul" || tag === "ol") return listItems(child, level + 1, flat);  // Google Docs nests lists directly
        if (tag !== "li") return;
        var aria = +child.getAttribute("aria-level") || level;
        var s = style(child);
        var isOrdered = /list-style-type\s*:\s*(decimal|lower|upper)/.test(s) ? true : /list-style-type\s*:\s*(disc|circle|square|none)/.test(s) ? false : ordered;
        var parts = [], sub = [];
        Array.prototype.forEach.call(child.childNodes, function (n) {
          var t = n.nodeType === 1 ? n.tagName.toLowerCase() : "";
          if (t === "ul" || t === "ol") sub.push(n);
          else {
            if (parts.length && (t === "p" || t === "div")) parts.push(txt(" "));
            parts = parts.concat(n.nodeType === 1 && (t === "p" || t === "div") ? inlineOf(n) : inline(n, { strong: false, em: false }));
          }
        });
        flat.push({ level: aria, ordered: isOrdered, children: parts });
        sub.forEach(function (n) { listItems(n, aria + 1, flat); });
      });
    }
    function readTable(table) {
      var rows = [], merged = false;
      var trs = Array.prototype.filter.call(table.querySelectorAll("tr"), function (tr) { return tr.closest("table") === table; });
      trs.slice(0, MAX_ROWS + 1).forEach(function (tr, r) {
        var row = rows[r] = rows[r] || [];
        Array.prototype.forEach.call(tr.children, function (cell) {
          var t = cell.tagName.toLowerCase();
          if (t !== "td" && t !== "th") return;
          var col = 0;
          while (row[col] !== undefined) col++;
          var colspan = Math.min(Math.max(1, +cell.getAttribute("colspan") || 1), MAX_COLS);
          var rowspan = Math.min(Math.max(1, +cell.getAttribute("rowspan") || 1), MAX_ROWS);
          if (colspan > 1 || rowspan > 1) merged = true;
          var content = [], m = marks(cell, { strong: false, em: false });  // spreadsheets style the cell itself
          Array.prototype.forEach.call(cell.childNodes, function (n) {
            if (content.length && n.nodeType === 1 && /^(p|div|li|br)$/i.test(n.tagName)) content.push(txt(" "));
            content = content.concat(n.nodeType === 1 && /^(table)$/i.test(n.tagName) ? [txt(n.textContent)] : inline(n, m));
          });
          for (var dr = 0; dr < rowspan; dr++) {
            var target = rows[r + dr] = rows[r + dr] || [];
            for (var dc = 0; dc < colspan; dc++) target[col + dc] = dr === 0 && dc === 0 ? content : [];
          }
        });
      });
      if (merged) notes.add("merged");
      return tableBlock(rows.filter(Boolean));
    }
    function captionOf(el) {
      return /MsoCaption/i.test(el.getAttribute("class") || "") ? true : false;
    }
    function walk(parent) {
      var buf = [];
      function flush() {
        if (hasContent(buf)) blocks.push({ type: "para", children: buf });
        buf = [];
      }
      Array.prototype.forEach.call(parent.childNodes, function (node) {
        if (node.nodeType === 3) { buf.push(txt(node.nodeValue)); return; }
        if (node.nodeType !== 1 || hidden(node)) return;
        var tag = node.tagName.toLowerCase(), s = style(node);
        var h = /^h([1-6])$/.exec(tag);
        if (/mso-element\s*:\s*comment-list/.test(s)) {  // Word's comments, after the text
          flush();
          notes.add("comment", Math.max(1, node.querySelectorAll("[style*='mso-element:comment' i]").length));
          return;
        }
        if (tag === "p" && node.querySelector("a[href^='#cmnt_ref']")) { flush(); return; }  // a Google Docs comment
        if (h) {
          flush();
          blocks.push({ type: "heading", level: +h[1], children: inlineOf(node) });
        } else if (tag === "p" || (tag === "div" && !node.querySelector("p,div,h1,h2,h3,h4,h5,h6,ul,ol,table,blockquote,pre"))) {
          flush();
          var item = wordItem(node);
          var cls = node.getAttribute("class") || "";
          if (item) blocks.push({ type: "item", group: item.group, level: item.level, ordered: item.ordered, children: item.children });
          else if (/MsoTitle\b/i.test(cls)) blocks.push({ type: "heading", level: 1, children: inlineOf(node) });
          else {
            var kids = inlineOf(node);
            if (hasContent(kids)) blocks.push({ type: "para", children: kids, caption: captionOf(node) });
          }
        } else if (tag === "ul" || tag === "ol") {
          flush();
          var flat = [];
          listItems(node, 1, flat);
          flat.forEach(function (i) { blocks.push({ type: "item", level: i.level, ordered: i.ordered, children: i.children }); });
        } else if (tag === "table") {
          flush();
          blocks.push(readTable(node));
        } else if (tag === "blockquote") {
          flush();
          var start = blocks.length;
          walk(node);
          var inner = blocks.splice(start);
          blocks.push({ type: "quote", blocks: inner });
        } else if (tag === "pre") {
          flush();
          blocks.push({ type: "code", text: node.textContent.replace(/\n$/, "") });
        } else if (tag === "hr") {
          flush();
        } else if (/^(div|section|article|main|body|center|header|footer|aside|nav|form|fieldset|figure|dl|google-sheets-html-origin)$/.test(tag) ||
                   (/^(b|span|font)$/.test(tag) && node.querySelector("p,h1,h2,h3,h4,h5,h6,ul,ol,table,div"))) {
          // A container (Google Docs wraps the whole paste in <b id="docs-internal-guid...">).
          flush();
          if (++depth <= MAX_DEPTH) walk(node);
          else blocks.push({ type: "para", children: [txt(node.textContent)] });  // too deep: keep the words
          depth--;
        } else if (tag === "li") {
          flush();
          blocks.push({ type: "item", level: 1, ordered: false, children: inlineOf(node) });
        } else {
          buf = buf.concat(inline(node, { strong: false, em: false }));
        }
      });
      flush();
    }
    walk(body);
    return { source: source, blocks: groupItems(attachCaptions(blocks), notes) };
  }
  // Consecutive list items become one (nested) list. A new Word list (its
  // mso-list id), or an outer item of the other kind (numbered or not),
  // starts another.
  function groupItems(blocks, notes) {
    var out = [], run = [];
    function end() { if (run.length) out.push(nestItems(run, notes)); run = []; }
    blocks.forEach(function (b) {
      if (b.type !== "item") { end(); out.push(b); return; }
      if (run.length && ((b.group && b.group !== run[0].group) || (b.level <= run[0].level && b.ordered !== run[0].ordered))) end();
      run.push(b);
    });
    end();
    return out;
  }
  // A caption paragraph ("Table 2: Sites", or Word's Caption style) right
  // before or after a table becomes its caption.
  var CAPTION = /^\s*table\s+[0-9A-Z.\-]+\s*[:.\-\u2013\u2014]?\s*/i;
  function attachCaptions(blocks) {
    for (var i = 0; i < blocks.length; i++) {
      if (blocks[i].type !== "table" || blocks[i].caption) continue;
      [i - 1, i + 1].some(function (j) {
        var b = blocks[j];
        if (!b || b.type !== "para" || b.used) return false;
        var text = plain(b.children);
        if (!(b.caption || CAPTION.test(text)) || text.length > 300) return false;
        blocks[i].caption = text.replace(CAPTION, "").trim();
        b.used = true;
        return true;
      });
    }
    return blocks.filter(function (b) { return !b.used; });
  }
  function tableBlock(rows) {
    var width = 0;
    rows = rows.slice(0, MAX_ROWS).map(function (row) { return row.slice(0, MAX_COLS); });
    rows.forEach(function (row) { width = Math.max(width, row.length); });
    rows = rows.map(function (row) {
      var full = [];
      for (var c = 0; c < width; c++) full.push(row[c] || []);
      return full;
    }).filter(function (row) { return row.some(hasContent); });
    // Drop columns that are empty in every row.
    var keep = [];
    for (var c = 0; c < width; c++) keep.push(rows.some(function (row) { return hasContent(row[c]); }));
    rows = rows.map(function (row) { return row.filter(function (_, k) { return keep[k]; }); });
    return { type: "table", rows: rows };
  }

  // ---------- Reading tab-separated cells -----------------------------------
  // Excel and Google Sheets copy cells as text with tabs between cells; a
  // cell holding a tab, a line break, or a quote is put in double quotes, with
  // its quotes doubled. Returns rows, or null if the text is not a grid.
  function readTsv(text) {
    if (text.indexOf("\t") < 0) return null;
    var rows = [], row = [], cell = "", i = 0, quoted = false, start = true;
    text = text.replace(/\r\n?/g, "\n").replace(/\n+$/, "");
    while (i < text.length) {
      var c = text.charAt(i);
      if (quoted) {
        if (c === '"' && text.charAt(i + 1) === '"') { cell += '"'; i += 2; continue; }
        if (c === '"' && (i + 1 === text.length || /[\t\n]/.test(text.charAt(i + 1)))) { quoted = false; i++; continue; }
        if (c === '"') return null;
        cell += c; i++; continue;
      }
      if (start && c === '"') { quoted = true; start = false; i++; continue; }
      start = false;
      if (c === "\t") { row.push(cell); cell = ""; start = true; i++; continue; }
      if (c === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; start = true; i++; continue; }
      cell += c; i++;
    }
    if (quoted) return null;
    row.push(cell); rows.push(row);
    var cols = rows[0].length;
    if (rows.length < 2 || cols < 2 || rows.some(function (r) { return r.length !== cols; })) return null;
    return rows;
  }

  // ---------- Reading Markdown and plain text ---------------------------------
  // A basic CommonMark subset: # headings, paragraphs, - and 1. lists,
  // **bold**, *italics*, `code`, [links](https://...), > quotes, ``` code,
  // pipe tables, $math$ and $$display math$$.
  function looksLikeMarkdown(text) {
    return /^#{1,6}\s+\S/m.test(text) || /\*\*\S[\s\S]*?\S\*\*/.test(text) || /^\s*[-*+]\s+\S/m.test(text) ||
      /^```/m.test(text) || /\[[^\]\n]+\]\([^)\s]+\)/.test(text) || /^\|.*\|\s*$/m.test(text) ||
      /(^|\s)_\S[^_\n]*\S_(\s|[.,;:!?]|$)/m.test(text) || /(^|\s)\*\S[^*\n]*\*(\s|[.,;:!?]|$)/m.test(text) ||
      /^\s*>\s/m.test(text) || /\$\$/.test(text);
  }

  function readInline(text, notes, markdown) {
    if (!markdown) return [txt(text)];
    var out = [];
    var i = 0, buf = "";
    function push() { if (buf) out.push(txt(buf)); buf = ""; }
    if (/\[@[A-Za-z0-9_:.\-]+/.test(text)) notes.add("citation");
    if (/\[\^[^\]]+\]/.test(text)) notes.add("footnote_md");
    while (i < text.length) {
      var rest = text.slice(i), m;
      var prev = i ? text.charAt(i - 1) : " ";
      if (rest.charAt(0) === "\\" && /^[\\`*_{}\[\]()#+\-.!$|>]/.test(rest.charAt(1))) { buf += rest.charAt(1); i += 2; continue; }
      if ((m = /^(`+)([\s\S]*?[^`])\1(?!`)/.exec(rest))) { push(); out.push({ type: "code", text: m[2].replace(/^ (.*) $/, "$1") }); i += m[0].length; continue; }
      if ((m = /^!\[([^\]]*)\]\(([^)]*)\)/.exec(rest))) { push(); notes.add("picture"); out.push({ type: "picture", alt: m[1] }); i += m[0].length; continue; }
      if ((m = /^\[([^\]]+)\]\(([^)\s]*)(?:\s+"[^"]*")?\)/.exec(rest))) {
        push();
        var safe = safeLink(m[2]);
        if (!safe) notes.add("link");
        var kids = readInline(m[1], { add: function () {} }, true);
        out.push(safe ? { type: "link", href: safe, children: kids } : { type: "span", children: kids });
        i += m[0].length; continue;
      }
      if ((m = /^<((?:https?:\/\/|mailto:)[^\s>]+)>/.exec(rest))) { push(); out.push({ type: "link", href: m[1], children: [txt(m[1].replace(/^mailto:/, ""))] }); i += m[0].length; continue; }
      if ((m = /^\$([^\s$](?:[^$\n]*[^\s$])?)\$(?![0-9])/.exec(rest)) && !/[0-9]/.test(prev)) { push(); out.push({ type: "math", text: m[1] }); i += m[0].length; continue; }
      if ((m = /^(\*\*|__)(?=\S)([\s\S]*?\S)\1/.exec(rest)) && !(m[1] === "__" && /\w/.test(prev))) {
        push(); out.push({ type: "strong", children: readInline(m[2], notes, true) }); i += m[0].length; continue;
      }
      if ((m = /^(\*|_)(?=[^\s*_])([\s\S]*?[^\s\\])\1(?!\1)/.exec(rest)) && !(m[1] === "_" && (/\w/.test(prev) || /^\w/.test(rest.slice(m[0].length))))) {
        push(); out.push({ type: "em", children: readInline(m[2], notes, true) }); i += m[0].length; continue;
      }
      buf += rest.charAt(0); i++;
    }
    push();
    return out;
  }
  function pipeCells(line) {
    var cells = [], cell = "";
    line = line.trim().replace(/^\|/, "").replace(/\|$/, "");
    for (var i = 0; i < line.length; i++) {
      if (line.charAt(i) === "\\" && line.charAt(i + 1) === "|") { cell += "|"; i++; }
      else if (line.charAt(i) === "|") { cells.push(cell.trim()); cell = ""; }
      else cell += line.charAt(i);
    }
    cells.push(cell.trim());
    return cells;
  }
  function readMarkdown(text, notes, markdown) {
    var lines = text.replace(/\r\n?/g, "\n").split("\n");
    var blocks = [], para = [], i = 0;
    var blankSplit = /\n\s*\n/.test(text);
    function flush() {
      if (para.length) {
        var kids = readInline(para.join(markdown ? "\n" : " ").replace(/\s+$/, ""), notes, markdown);
        if (hasContent(kids)) blocks.push({ type: "para", children: kids });
      }
      para = [];
    }
    while (i < lines.length) {
      var line = lines[i], m;
      if (!/\S/.test(line)) { flush(); i++; continue; }
      if (!markdown) {
        para.push(line.trim());
        if (!blankSplit) flush();  // one paragraph per line when the text has no blank lines
        i++; continue;
      }
      if ((m = /^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$/.exec(line))) {
        flush(); blocks.push({ type: "heading", level: m[1].length, children: readInline(m[2], notes, true) }); i++; continue;
      }
      if ((m = /^ {0,3}(```+|~~~+)/.exec(line))) {
        flush();
        var fence = m[1], code = [];
        i++;
        while (i < lines.length && lines[i].trim().indexOf(fence) !== 0) code.push(lines[i++]);
        i++;
        notes.add("code");
        blocks.push({ type: "code", text: code.join("\n") });
        continue;
      }
      if (/^\s*\$\$/.test(line)) {
        flush();
        var body = line.replace(/^\s*\$\$/, "");
        var closed = /\$\$\s*$/.test(body);
        body = body.replace(/\$\$\s*$/, "");
        var math = [body];
        i++;
        while (!closed && i < lines.length) {
          var l = lines[i++];
          if (/\$\$\s*$/.test(l)) { math.push(l.replace(/\$\$\s*$/, "")); closed = true; } else math.push(l);
        }
        notes.add("display-math");
        blocks.push({ type: "math", text: math.join("\n").trim() });
        continue;
      }
      if (/^ {0,3}([-*_])(\s*\1){2,}\s*$/.test(line)) { flush(); i++; continue; }
      if (/^\s*\|/.test(line) && i + 1 < lines.length && /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/.test(lines[i + 1])) {
        flush();
        var rows = [pipeCells(line)];
        i += 2;
        while (i < lines.length && /^\s*\|/.test(lines[i])) rows.push(pipeCells(lines[i++]));
        blocks.push(tableBlock(rows.map(function (r) { return r.map(function (c) { return readInline(c, notes, true); }); })));
        continue;
      }
      if (/^ {0,3}>/.test(line)) {
        flush();
        var quoted = [];
        while (i < lines.length && /^ {0,3}>/.test(lines[i])) quoted.push(lines[i++].replace(/^ {0,3}> ?/, ""));
        blocks.push({ type: "quote", blocks: readMarkdown(quoted.join("\n"), notes, true) });
        continue;
      }
      if ((m = /^(\s*)([-*+]|\d{1,9}[.)])\s+(.*)$/.exec(line))) {
        flush();
        var flat = [], indents = [];
        while (i < lines.length) {
          var item = /^(\s*)([-*+]|\d{1,9}[.)])\s+(.*)$/.exec(lines[i]);
          if (item) {
            var indent = item[1].replace(/\t/g, "    ").length;
            // A different kind of marker at the outer level starts a new list.
            if (flat.length && indent <= (indents[0] || 0) && /\d/.test(item[2]) !== flat[0].ordered) break;
            while (indents.length && indent < indents[indents.length - 1]) indents.pop();
            if (!indents.length || indent > indents[indents.length - 1]) indents.push(indent);
            flat.push({ level: indents.length, ordered: /\d/.test(item[2]), text: [item[3]] });
            i++;
          } else if (/\S/.test(lines[i]) && /^\s+\S/.test(lines[i]) && flat.length) {
            flat[flat.length - 1].text.push(lines[i].trim()); i++;          // a continuation line
          } else if (/\S/.test(lines[i]) && flat.length && !/^\s*$/.test(lines[i - 1])) {
            flat[flat.length - 1].text.push(lines[i].trim()); i++;          // a lazy continuation
          } else if (!/\S/.test(lines[i]) && i + 1 < lines.length && /^(\s*)([-*+]|\d{1,9}[.)])\s+/.test(lines[i + 1])) {
            i++;                                                            // a blank line between items
          } else break;
        }
        blocks.push(nestItems(flat.map(function (f) {
          return { level: f.level, ordered: f.ordered, children: readInline(f.text.join(" "), notes, true) };
        }), notes));
        continue;
      }
      para.push(line.replace(/^\s+/, ""));
      i++;
    }
    flush();
    return blocks;
  }

  // ---------- Writing LaTeX -----------------------------------------------------
  function write(blocks, options, notes) {
    var state = { escaped: 0, odd: notes.odd };
    var chapter = !!options.chapter;
    var out = [];
    var labels = {};
    var counts = { tab: 0, eq: 0 };
    var levels = [];
    (function collect(list) {
      list.forEach(function (b) { if (b.type === "heading") levels.push(b.level); if (b.type === "quote") collect(b.blocks); });
    })(blocks);
    var top = levels.length ? Math.min.apply(null, levels) : 1;
    var firstHeading = blocks.filter(function (b) { return b.type === "heading"; })[0];
    var base = slug(firstHeading && plain(firstHeading.children), chapter ? "new-chapter" : "pasted");
    var kind = chapter ? "chapter" : (blocks.length && blocks.every(function (b) { return b.type === "table"; }) ? "table" : "body");

    function label(prefix, text) {
      var name = prefix + ":" + slug(text, base);
      if (labels[name]) { var n = 2; while (labels[name + "-" + n]) n++; name += "-" + n; }
      labels[name] = true;
      return name;
    }
    function inlines(nodes, ctx) {
      return nodes.map(function (n) { return piece(n, ctx); }).join("");
    }
    // Spaces at the edges of bold or italics move outside the command.
    function wrapCmd(cmd, inner) {
      var lead = /^\s*/.exec(inner)[0], tail = /\s*$/.exec(inner)[0];
      var core = inner.trim();
      if (!core) return inner ? " " : "";
      return (lead ? " " : "") + cmd + "{" + core + "}" + (tail ? " " : "");
    }
    function piece(n, ctx) {
      switch (n.type) {
        case "text":
          // A no-break space stays (~) only between two words.
          var t = n.text.replace(/[ \t\r\n]*\u00a0[\u00a0 \t\r\n]*/g, function (m) { return m === "\u00a0" ? m : " "; });
          // Chapter titles in CAPITALS; Greek letters keep their case (they are symbols).
          if (ctx.upper) t = t.replace(/[^\u0370-\u03ff]+/g, function (part) { return part.toUpperCase(); });
          return escapeText(t, state).replace(/\s+/g, " ");
        case "equation": return EQ;
        case "strong": return ctx.heading ? inlines(n.children, ctx) : wrapCmd("\\textbf", inlines(n.children, ctx));
        case "em": return wrapCmd("\\emph", inlines(n.children, ctx));
        case "span": return inlines(n.children, ctx);
        case "sup": return wrapCmd("\\textsuperscript", inlines(n.children, ctx));
        case "sub": return wrapCmd("\\textsubscript", inlines(n.children, ctx));
        case "code": return "\\texttt{" + escapeText(n.text, state).replace(/\s+/g, " ") + "}";
        case "math": return "$" + n.text + "$";
        case "picture": ctx.pictures.push(n.alt); return " ";
        case "link":
          var text = inlines(n.children, ctx).trim();
          if (ctx.heading) return text;
          var bare = n.href.replace(/^mailto:/i, ""), shown = plain(n.children).trim();
          if (!text || shown === n.href || shown === bare) {
            // \url breaks long addresses across lines; it also works inside
            // another command unless the address holds % # \ { } or spaces.
            if (!/^mailto:/i.test(n.href) && /^[\x21-\x7e]+$/.test(n.href) && !/[%#\\{}^]/.test(n.href)) return "\\url{" + n.href + "}";
            return "\\href{" + escapeUrl(n.href) + "}{" + escapeText(bare, null) + "}";
          }
          return "\\href{" + escapeUrl(n.href) + "}{" + text + "}";
        default: return "";
      }
    }
    function line(nodes, ctx) {
      ctx = ctx || {};
      ctx.pictures = ctx.pictures || [];
      var text = inlines(nodes, ctx).replace(/\s+/g, " ").trim().replace(/^~+|~+$/g, "").trim();
      // Word writes each run of an equation separately: one marker for each equation.
      text = text.replace(new RegExp("(" + EQ + "[ ~]*)+", "g"), function (m) { notes.add("equation"); return "[equation]" + (/[ ~]$/.test(m) ? " " : ""); });
      return text.trim();
    }
    // "[" at the start of an \item or a table row would be read as an option.
    function guard(text) { return text.charAt(0) === "[" ? "{[}" + text.slice(1) : text; }
    function pictureLines(pictures, indent) {
      pictures.forEach(function (alt) {
        alt = String(alt || "").replace(/[\s\u0000-\u001f]+/g, " ").trim().slice(0, 120);
        out.push(indent + "% A picture was here" + (alt ? " (\"" + alt + "\")" : "") +
          ". Save it in figures/ and add a figure: see the guide, Writing basics, \"Add a figure\".");
      });
    }
    function heading(b) {
      var depth = b.level - top;
      var commands = chapter ? ["chapter", "section", "subsection", "subsubsection"] : ["section", "subsection", "subsubsection"];
      if (depth >= commands.length) { notes.add("deep"); depth = commands.length - 1; }
      var ctx = { heading: true, upper: chapter && depth === 0, pictures: [] };
      var text = line(b.children, ctx) || (depth === 0 && chapter ? "TITLE" : "Heading");
      if (out.length && out[out.length - 1] !== "" && !/^% !TEX/.test(out[out.length - 1])) out.push("");
      out.push("\\" + commands[depth] + "{" + text + "}");
      if (chapter && depth === 0) out.push("\\label{" + label("chap", plain(b.children)) + "}");
      out.push("");
      pictureLines(ctx.pictures, "");
    }
    function list(b, indent) {
      var env = b.ordered ? "enumerate" : "itemize";
      out.push(indent + "\\begin{" + env + "}");
      b.items.forEach(function (item) {
        var ctx = { pictures: [] };
        var text = line(item.children, ctx);
        out.push(indent + "  \\item" + (text ? " " + guard(text) : ""));
        pictureLines(ctx.pictures, indent + "  ");
        item.lists.forEach(function (sub) { list(sub, indent + "  "); });
      });
      out.push(indent + "\\end{" + env + "}");
    }
    function table(b) {
      var rows = b.rows;
      if (!rows.length) return;
      var cols = rows[0].length;
      if (cols > 6) notes.add("wide");
      if (rows.length >= MAX_ROWS || cols >= MAX_COLS) notes.add("big");
      var pictures = [];
      var cells = rows.map(function (row) { return row.map(function (c) { return line(c, { pictures: pictures }); }); });
      var spec = "";
      var longCols = 0, numeric = [];
      for (var c = 0; c < cols; c++) {
        var body = rows.slice(1).map(function (r) { return plain(r[c]).trim(); }).filter(Boolean);
        var isNumber = body.length > 0 && body.every(function (v) { return /^[-+\u2212(]?[$\u20ac\u00a3]?\d[\d,.\s]*%?\)?$/.test(v); });
        var longest = Math.max.apply(null, rows.map(function (r) { return plain(r[c]).length; }));
        numeric.push(isNumber ? "r" : longest > 30 ? "p" : "l");
        if (!isNumber && longest > 30) longCols++;
      }
      var share = longCols ? Math.max(0.15, Math.round((0.85 - 0.1 * (cols - longCols)) / longCols * 100) / 100) : 0;
      numeric.forEach(function (k) { spec += k === "p" ? "p{" + share + "\\linewidth}" : k; });
      counts.tab++;
      var caption = b.caption ? escapeText(b.caption, state).replace(/\s+/g, " ").trim() : "";
      if (!caption) notes.add("caption");
      if (out.length && out[out.length - 1] !== "") out.push("");
      out.push("\\begin{table}[htbp]", "  \\centering",
               "  \\caption{" + (caption || "Your full caption, ending with a period.") + "}",
               "  \\label{" + label("tab", b.caption || rows[0].map(plain).join(" ") || base + "-" + counts.tab) + "}",
               "  \\begin{tabular}{" + spec + "}", "    \\toprule");
      cells.forEach(function (row, r) {
        out.push("    " + row.map(guard).join(" & ") + " \\\\");
        if (r === 0 && cells.length > 1) out.push("    \\midrule");
      });
      out.push("    \\bottomrule", "  \\end{tabular}", "\\end{table}", "");
      pictureLines(pictures, "");
    }
    function block(b, indent) {
      if (b.type === "heading") return heading(b);
      if (b.type === "para") {
        var ctx = { pictures: [] };
        var text = line(b.children, ctx);
        if (text) out.push(indent + text, "");
        pictureLines(ctx.pictures, indent);
        if (ctx.pictures.length && out[out.length - 1] !== "") out.push("");
        return;
      }
      if (b.type === "list") { list(b, indent); out.push(""); return; }
      if (b.type === "table") return table(b);
      if (b.type === "quote") {
        out.push(indent + "\\begin{quote}");
        b.blocks.forEach(function (inner) { block(inner, indent + "  "); });
        if (out[out.length - 1] === "") out.pop();
        out.push(indent + "\\end{quote}", "");
        return;
      }
      if (b.type === "code") {
        out.push("\\begin{verbatim}", b.text.replace(/\\end\{verbatim\}/g, "\\end {verbatim}"), "\\end{verbatim}", "");
        return;
      }
      if (b.type === "math") {
        counts.eq++;
        out.push("\\begin{equation}", "  " + b.text.replace(/\n/g, "\n  "),
                 "  \\label{" + label("eq", base + "-" + counts.eq) + "}", "\\end{equation}", "");
      }
    }

    if (chapter) {
      out.push("% !TEX root = ../main.tex");
      var first = blocks[0];
      if (!first || first.type !== "heading" || first.level !== top) {
        out.push("\\chapter{TITLE}", "\\label{chap:" + base + "}", "");
        labels["chap:" + base] = true;
      }
      var chapters = blocks.filter(function (b) { return b.type === "heading" && b.level === top; }).length;
      if (chapters > 1) notes.add("chapters", chapters);
    }
    blocks.forEach(function (b) { block(b, ""); });
    while (out.length && out[out.length - 1] === "") out.pop();
    var latex = out.join("\n").replace(/\n{3,}/g, "\n\n");
    return { latex: latex ? latex + "\n" : "", escaped: state.escaped, kind: kind, base: base };
  }

  // ---------- Next steps --------------------------------------------------------
  function steps(result, chapter) {
    var file = result.base;
    if (chapter) {
      return [
        "Save it as chapters/" + file + ".tex (Download .tex gives it that name; rename it to match your chapter order, such as 04-" + file + ".tex).",
        "In main.tex, add \\include{chapters/" + file + "} where the chapter belongs, among the other \\include lines.",
        "Replace the chapter title if needed: one \\chapter per file, in CAPITALS.",
        "Compile, and read the PDF next to your original."
      ];
    }
    if (result.kind === "table") {
      return [
        "Open the chapter file in chapters/ where the table belongs, and paste it between two paragraphs.",
        "Write a full caption, and refer to the table in the text with Table~\\ref{...} and its label.",
        "Compile, and compare every cell with your original."
      ];
    }
    return [
      "Open the chapter file in chapters/ where this text belongs, such as chapters/02-research.tex, and paste it below the \\chapter{...} and \\label{...} lines (or where it belongs further down).",
      "For a chapter of its own, choose \"A new chapter\" above instead.",
      "Compile, and read the PDF next to your original."
    ];
  }

  // ---------- The whole conversion -------------------------------------------------
  var NAMES = { word: "Word", gdocs: "Google Docs", sheets: "Google Sheets cells", excel: "Excel cells", html: "Rich text",
                markdown: "Markdown", text: "Plain text", tsv: "Spreadsheet cells" };
  function convert(input, options) {
    options = options || {};
    var notes = new Notes();
    var html = String(input && input.html || ""), text = String(input && input.text || "");
    if (html.length > LIMIT) { html = ""; notes.add("cut"); text = text.slice(0, LIMIT); }
    if (text.length > LIMIT) { text = text.slice(0, LIMIT); notes.add("cut"); }
    var read = null;
    if (/<[a-z][\s\S]*>/i.test(html)) {
      read = readHtml(html, notes);
      if (!read.blocks.length) { read = null; notes = new Notes(); }
    }
    if (!read) {
      var grid = readTsv(text);
      if (grid) read = { source: "tsv", blocks: [tableBlock(grid.map(function (r) { return r.map(function (c) { return [txt(c)]; }); }))] };
    }
    if (!read) {
      var md = looksLikeMarkdown(text);
      read = { source: md ? "markdown" : "text", blocks: readMarkdown(text, notes, md) };
    }
    var result = write(read.blocks, options, notes);
    return {
      latex: result.latex,
      source: read.source,
      sourceName: NAMES[read.source],
      kind: result.kind,
      escaped: result.escaped,
      filename: result.base + ".tex",
      notes: result.latex ? notes.list() : [],
      steps: result.latex ? steps(result, !!options.chapter) : []
    };
  }

  root.ConvertCore = { convert: convert, escapeText: escapeText, escapeUrl: escapeUrl, slug: slug, readTsv: readTsv,
                       cleanHtml: cleanHtml, safeLink: safeLink };
})(typeof window !== "undefined" ? window : this);
