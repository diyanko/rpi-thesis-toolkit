// "Bring your work in" (docs/bring-your-work-in.md): the page part. An extra
// only: with JavaScript off the page explains the same steps by hand.
//
// What is pasted or dropped is read in this browser tab and never sent
// anywhere. The paste is intercepted: its rich text (text/html) is handed to
// core.js as a string, never put into the page, and the plain text goes into
// the box. The LaTeX is shown as text (colored by tools-highlight.js), one
// span per line, so a note can mark the lines it is about. The preview is
// built from core.preview(), the LaTeX read back, with elements and text
// nodes only. Nothing is stored. Works from the website and from the offline
// guide (file: pages).
(function () {
  "use strict";
  var root = document.querySelector("[data-convert]");
  var script = document.currentScript;
  if (!root || !script || !window.DOMParser) return;
  var base = script.src.replace(/[^/]*$/, "");
  var input = root.querySelector(".convert-input");
  var output = root.querySelector(".convert-output");
  var sketch = root.querySelector(".convert-preview");
  var views = root.querySelectorAll("input[name=convert-view]");
  var status = root.querySelector(".convert-status");
  var source = root.querySelector(".convert-source");
  var results = root.querySelector(".convert-results");
  var copy = root.querySelector(".convert-copy");
  var download = root.querySelector(".convert-download");
  var LIMIT = 2000000;
  // Links from the page text, so they work on the website and offline.
  function pageLink(part) {
    var link = document.querySelector('.guide-content a[href*="' + part + '.html"]');
    return link ? link.getAttribute("href").split("#")[0] : "";
  }
  var SAMPLE = "## Field sites\n\nWe visited **three sites** over *two seasons*. About 40% of R&D_budget went to site #2.\n\n" +
    "- Site A, on the river\n- Site B, in the hills\n\n| Site | Visits | Weather |\n| --- | --- | --- |\n" +
    "| A | 12 | Dry |\n| B | 18 | Wet & cold |\n\nMore at [the project page](https://example.org/field_notes).\n";

  var core = null, pasted = null, result = null, timer = 0;
  var revision = 0;          // goes up with every new input, so a late file read is ignored
  var lineNodes = [];        // the LaTeX's lines, as spans in the output
  var sketchDone = false;    // the preview is drawn when it is first shown
  var marked = null;         // {note, at}: the note whose places are marked, and the current place
  var tag = document.createElement("script");
  tag.src = base + "core.js";
  tag.onload = function () {
    core = window.ConvertCore;
    if (!core) return;
    Array.prototype.forEach.call(document.querySelectorAll("[data-convert-nojs]"), function (node) { node.hidden = true; });
    root.hidden = false;
  };
  document.head.appendChild(tag);

  // The shared states (ToolState in tools-highlight.js); plain text without it.
  var State = window.ToolState || { set: function (r, s, state, c) {
    s.textContent = typeof c === "string" ? c : c ? c.title + ". " + c.text : ""; } };
  function say(text, state) { State.set(root, status, state || "", text); }
  function fail(title, text, href, link) { State.set(root, status, "error", { title: title, text: text, href: href, link: link }); }
  var CONVERTS = "#what-it-converts";
  function element(name, className, text) {
    var node = document.createElement(name);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }
  function chapter() {
    var checked = root.querySelector("input[name=convert-start]:checked");
    return !!checked && checked.value === "chapter";
  }

  // ---------- The LaTeX, one span per line ----------
  function renderLatex(text) {
    output.textContent = "";
    lineNodes = [];
    if (!text) return;
    var fragment = document.createDocumentFragment(), current = null;
    function newLine() { current = element("span", "convert-line"); lineNodes.push(current); fragment.appendChild(current); }
    var tokens = window.ToolsHighlight ? window.ToolsHighlight.tokens(text) : [{ type: "", text: text }];
    newLine();
    tokens.forEach(function (token) {
      token.text.split("\n").forEach(function (part, index) {
        if (index) { current.appendChild(document.createTextNode("\n")); newLine(); }
        if (!part) return;
        if (!token.type) current.appendChild(document.createTextNode(part));
        else current.appendChild(element("span", "tok-" + token.type, part));
      });
    });
    if (!current.firstChild) { fragment.removeChild(current); lineNodes.pop(); }
    output.appendChild(fragment);
  }

  // ---------- The preview: the LaTeX read back by core.preview ----------
  function inlineNodes(parent, nodes) {
    nodes.forEach(function (n) {
      var node;
      if (n.t === "text") { parent.appendChild(document.createTextNode(n.text)); return; }
      if (n.t === "strong" || n.t === "em" || n.t === "sup" || n.t === "sub") node = element(n.t);
      else if (n.t === "code") node = element("code", "", n.text);
      else if (n.t === "math") node = element("code", "convert-math", n.text);
      else if (n.t === "mark") node = element("mark", "", n.text);
      else if (n.t === "picture") node = element("span", "convert-picture", "Picture not copied" + (n.alt ? ": " + n.alt : ""));
      else if (n.t === "link") {
        var href = core.safeLink(n.href);
        node = element(href ? "a" : "span");
        if (href) { node.href = href; node.target = "_blank"; node.rel = "noopener noreferrer"; }
      } else return;
      if (n.children) inlineNodes(node, n.children);
      parent.appendChild(node);
    });
  }
  function lines(node, from, to) {
    node.setAttribute("data-from", from);
    node.setAttribute("data-to", to);
    return node;
  }
  var HEADING = ["convert-chapter", "convert-section", "convert-subsection", "convert-subsubsection"];
  function blockNodes(parent, blocks) {
    blocks.forEach(function (b) {
      var node = null;
      if (b.type === "heading") {
        node = element("p", "convert-heading " + HEADING[b.level]);
        node.appendChild(element("span", "convert-number", b.number));
        inlineNodes(node, b.children);
      } else if (b.type === "para") {
        node = element("p");
        inlineNodes(node, b.children);
      } else if (b.type === "list") {
        node = listNode(b);
      } else if (b.type === "table") {
        node = tableNode(b);
      } else if (b.type === "quote") {
        node = element("blockquote");
        blockNodes(node, b.blocks);
      } else if (b.type === "code") {
        node = element("pre", "convert-code", b.text);
      } else if (b.type === "math") {
        node = element("div", "convert-equation");
        node.appendChild(element("code", "convert-math", b.text));
        node.appendChild(element("span", "convert-number", b.number));
      } else if (b.type === "picture") {
        node = element("p", "convert-picture", "Picture not copied" + (b.alt ? ": " + b.alt : "") + ". Add it from figures/.");
      }
      if (node) parent.appendChild(lines(node, b.from, b.to));
    });
  }
  function listNode(b) {
    var node = element(b.ordered ? "ol" : "ul");
    b.items.forEach(function (item) {
      var li = lines(element("li"), item.from, item.to);
      var text = lines(element("span"), item.line, item.line);
      inlineNodes(text, item.children);
      li.appendChild(text);
      item.lists.forEach(function (sub) { li.appendChild(lines(listNode(sub), sub.from, sub.to)); });
      node.appendChild(li);
    });
    return node;
  }
  function tableNode(b) {
    var wrap = element("div", "convert-table");
    var table = element("table");
    var caption = element("caption");
    if (b.captionLine !== undefined) lines(caption, b.captionLine, b.captionLine);
    caption.appendChild(element("span", "convert-number", "Table " + b.number + ":"));
    caption.appendChild(document.createTextNode(" "));
    var words = element("span", b.placeholder ? "convert-placeholder" : "");
    inlineNodes(words, b.caption || []);
    caption.appendChild(words);
    table.appendChild(caption);
    var head = b.head ? element("thead") : null, body = element("tbody");
    b.rows.forEach(function (row, r) {
      var inHead = !!head && r < b.head;
      var tr = lines(element("tr"), row.line, row.line);
      row.cells.forEach(function (cell, c) {
        var td = element(inHead ? "th" : "td", b.align[c] === "r" ? "is-number" : "");
        if (inHead) td.scope = "col";
        inlineNodes(td, cell);
        tr.appendChild(td);
      });
      (inHead ? head : body).appendChild(tr);
    });
    if (head) table.appendChild(head);
    table.appendChild(body);
    wrap.appendChild(table);
    return wrap;
  }
  function drawSketch() {
    sketch.textContent = "";
    sketchDone = true;
    if (!result || !result.latex) return;
    sketch.appendChild(element("p", "convert-preview-note",
      "A rough preview of the LaTeX, not your PDF: fonts, spacing, and page breaks differ, and math shows as its LaTeX. N stands for the chapter's number."));
    blockNodes(sketch, core.preview(result.latex).blocks);
  }
  function previewing() { return !!root.querySelector("input[name=convert-view][value=preview]:checked"); }
  function setView() {
    var on = previewing();
    output.hidden = on;
    sketch.hidden = !on;
    if (on && !sketchDone) drawSketch();
    paintMarks(true, false);
  }

  // ---------- Marking where a note applies ----------
  // Every place of the chosen note is marked, the current one more strongly,
  // and scrolled into view in the LaTeX or the preview, whichever is shown.
  function shown() { return sketch.hidden ? output : sketch; }
  function scrollInside(box, node) {   // the box, not the page: node near the box's top third
    var top = node.getBoundingClientRect().top - box.getBoundingClientRect().top + box.scrollTop;
    box.scrollTop = Math.max(0, top - box.clientHeight / 3);
  }
  // In the preview: the elements whose lines lie inside the place, outermost
  // first; otherwise the innermost element that holds it.
  function sketchNodes(place) {
    var all = Array.prototype.slice.call(sketch.querySelectorAll("[data-from]"));
    function from(n) { return +n.getAttribute("data-from"); }
    function to(n) { return +n.getAttribute("data-to"); }
    var within = all.filter(function (n) { return from(n) >= place.from && to(n) <= place.to; });
    within = within.filter(function (n) { return !within.some(function (o) { return o !== n && o.contains(n); }); });
    if (within.length) return within;
    var holding = all.filter(function (n) { return from(n) <= place.from && to(n) >= place.to; });
    return holding.length ? [holding[holding.length - 1]] : [];
  }
  function paintMarks(scroll, page) {
    Array.prototype.forEach.call(root.querySelectorAll(".is-marked"), function (n) { n.classList.remove("is-marked", "is-current"); });
    if (!marked) return;
    var first = null;
    marked.note.places.forEach(function (place, k) {
      var nodes = sketch.hidden ? lineNodes.slice(place.from, place.to + 1) : sketchNodes(place);
      nodes.forEach(function (n) {
        n.classList.add("is-marked");
        if (k === marked.at) { n.classList.add("is-current"); if (!first) first = n; }
      });
    });
    if (!first || !scroll) return;
    var box = shown();
    scrollInside(box, first);
    var edge = box.getBoundingClientRect();
    if (page !== false && (edge.top < 0 || edge.bottom > window.innerHeight)) box.scrollIntoView({ block: "nearest" });
  }
  function showWhere(note) {
    var count = note.places.length;
    marked = { note: note, at: marked && marked.note === note ? (marked.at + 1) % count : 0 };
    paintMarks(true);
    var place = note.places[marked.at];
    var spot = place.from === place.to ? "line " + (place.from + 1) : "lines " + (place.from + 1) + " to " + (place.to + 1);
    say("Marked " + (previewing() ? "in the preview, from " : "") + spot + " of the LaTeX" +
        (count > 1 ? ": place " + (marked.at + 1) + " of " + count + ". Press again for the next." : "."));
  }

  function show() {
    results.textContent = "";
    marked = null;
    sketchDone = false;
    sketch.textContent = "";
    if (!result || !result.latex) {
      renderLatex("");
      source.textContent = "";
      copy.disabled = download.disabled = true;
      return;
    }
    renderLatex(result.latex);   // colored; Copy uses result.latex
    if (previewing()) drawSketch();
    source.textContent = "(read as " + result.sourceName + ")";
    copy.disabled = download.disabled = false;
    var next = element("section", "convert-next");
    next.appendChild(element("h3", "", "Next steps"));
    var steps = element("ol");
    result.steps.forEach(function (text) { steps.appendChild(element("li", "", text)); });
    next.appendChild(steps);
    results.appendChild(next);
    var left = element("section", "convert-left");
    left.appendChild(element("h3", "", result.notes.length ? "Not converted, or worth a look" : "Nothing left over"));
    if (!result.notes.length) {
      left.appendChild(element("p", "", "Everything pasted was converted. Still read the result next to your original."));
    } else {
      var list = element("ul", "convert-notes");
      result.notes.forEach(function (note) {
        var item = element("li", "", note.text + " ");
        var href = note.page && pageLink(note.page);
        if (href) {
          var link = element("a", "", "How");
          link.href = href + "#" + note.anchor;
          item.appendChild(link);
        }
        if (note.places.length) {
          var row = element("p", "convert-where");
          var button = element("button", "button button-secondary button-small",
            note.places.length > 1 ? "Show where (" + note.places.length + " places)" : "Show where");
          button.type = "button";
          button.setAttribute("data-icon", "eye");
          button.addEventListener("click", function () { showWhere(note); });
          row.appendChild(button);
          item.appendChild(row);
        }
        list.appendChild(item);
      });
      left.appendChild(list);
    }
    results.appendChild(left);
  }

  function run() {
    clearTimeout(timer);
    if (!core) return;
    var text = input.value;
    if (!pasted && !/\S/.test(text)) {
      result = null;
      show();
      say("");
      return;
    }
    if (text.length > LIMIT) {
      result = null;
      show();
      fail("Too much text at once", "Convert one chapter or section at a time, so the result stays easy to check.", CONVERTS, "What it converts");
      return;
    }
    try {
      result = core.convert(pasted || { html: "", text: text }, { chapter: chapter() });
    } catch (error) {
      result = null;
      show();
      fail("This text could not be converted", "Try a smaller part of it, or do it by hand:", "#without-the-converter", "Without the converter");
      return;
    }
    show();
    if (!result.latex) {
      fail("Nothing to convert", "No text was found in what was pasted. Paste the words themselves; pictures go in figures/.", CONVERTS, "What it converts");
      return;
    }
    say("Converted, read as " + result.sourceName + "." +
        (result.escaped ? " " + result.escaped + " special character" + (result.escaped > 1 ? "s were" : " was") + " given a backslash." : "") +
        (result.notes.length ? " " + result.notes.length + (result.notes.length > 1 ? " points" : " point") + " to look at below." : ""), "done");
  }
  function later() {
    clearTimeout(timer);
    timer = setTimeout(run, 150);
  }

  // A paste replaces the box with its plain text; its rich text is kept
  // aside (as a string) until the box is edited. Rich text over the limit
  // still goes to core.js, which converts the plain text and says so.
  function take(data) {
    revision++;
    var html = "", text = "";
    try {
      html = data.getData("text/html") || "";
      text = data.getData("text/plain") || "";
    } catch (error) { /* some browsers refuse one of the types */ }
    if (!html && !text) return false;
    if (html) {
      pasted = { html: html, text: text };
      input.value = text;
      pasted.shown = input.value;
    } else {
      pasted = null;
      var start = input.selectionStart, end = input.selectionEnd;
      if (typeof input.setRangeText === "function" && start !== undefined) {
        input.setRangeText(text, start, end, "end");
      } else {
        input.value += text;
      }
    }
    run();
    return true;
  }
  input.addEventListener("paste", function (event) {
    if (!event.clipboardData) return;  // the browser pastes plain text itself
    event.preventDefault();
    if (!take(event.clipboardData)) fail("Only text can be converted", "Pictures go in figures/ and are added with a line of LaTeX.", "writing.html#add-a-figure", "Add a figure");
  });
  input.addEventListener("input", function () {
    revision++;
    if (pasted && input.value !== pasted.shown) pasted = null;  // edited: read the box as it is now
    later();
  });

  // Dropping text works like pasting it; a dropped file is read only if it is
  // plain text (Markdown, text, or tab-separated cells). A read that finishes
  // after newer input (another drop, a paste, typing, Clear) is ignored.
  function dropped(event) {
    var data = event.dataTransfer;
    if (!data) return;
    var file = data.files && data.files[0];
    if (file) {
      var asked = ++revision;
      if (!/\.(md|markdown|txt|text|tsv|tab)$/i.test(file.name) || file.size > LIMIT || typeof file.text !== "function") {
        fail(file.name + " cannot be read here", "Only Markdown, text, and tab-separated files are read. Open it, select the text, copy it, and paste it here.", CONVERTS, "What it converts");
        return;
      }
      file.text().then(function (text) {
        if (asked !== revision) return;
        pasted = null;
        input.value = text;
        run();
      }, function () {
        if (asked === revision) fail(file.name + " could not be read", "Open it, select the text, copy it, and paste it here.", CONVERTS, "What it converts");
      });
      return;
    }
    if (!take(data)) fail("Only text can be converted", "Pictures go in figures/ and are added with a line of LaTeX.", "writing.html#add-a-figure", "Add a figure");
  }
  if (State.dropZone) State.dropZone(input, dropped);
  else input.addEventListener("drop", function (event) { event.preventDefault(); dropped(event); });

  Array.prototype.forEach.call(root.querySelectorAll("input[name=convert-start]"), function (radio) {
    radio.addEventListener("change", run);
  });
  Array.prototype.forEach.call(views, function (radio) { radio.addEventListener("change", setView); });
  root.querySelector(".convert-example").addEventListener("click", function () {
    revision++;
    pasted = null;
    input.value = SAMPLE;
    run();
  });
  root.querySelector(".convert-clear").addEventListener("click", function () {
    revision++;
    pasted = null;
    input.value = "";
    run();
    input.focus();
  });

  function selectOutput() {
    var range = document.createRange();
    range.selectNodeContents(output);
    var selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
  }
  copy.addEventListener("click", function () {
    if (!result || !result.latex) return;
    var done = function () { say("Copied. Paste it into your chapter file."); };
    var fallback = function () {
      if (output.hidden) { root.querySelector("input[name=convert-view][value=latex]").checked = true; setView(); }
      selectOutput();
      say("The LaTeX is selected: press Ctrl+C (or Cmd+C on a Mac) to copy it.");
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(result.latex).then(done, fallback);
    else fallback();
  });
  download.addEventListener("click", function () {
    if (!result || !result.latex || !window.Blob || !window.URL || !URL.createObjectURL) {
      fail("This browser cannot save the file", "Use Copy instead, and paste into a new .tex file in chapters/.");
      return;
    }
    var url = URL.createObjectURL(new Blob([result.latex], { type: "application/x-tex" }));
    var link = element("a");
    link.href = url;
    link.download = result.filename;
    link.hidden = true;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
    say("Saved as " + result.filename + " in your downloads folder.");
  });
})();
