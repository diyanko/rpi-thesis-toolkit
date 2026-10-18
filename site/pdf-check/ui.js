// "Check your PDF" (docs/check-pdf.md): the page part. An extra only: with
// JavaScript off the page explains the checks and links to the submission
// checklist instead.
//
// The PDF is read in this browser tab and never sent anywhere. The reading
// and the checks are in core.js; the PDF reader (pdf.js) is in pdfjs/, next to
// this file, so the page needs no other website. Both load only when a PDF
// is chosen. The rules and measurements come from the page's
// <script type="application/json" id="oge-rules"> block (scripts/rules.py):
// this file passes them to core.js and shows each rule's citation from them.
// The offline guide has no checker: build_site.py leaves these files out.
//
// Results open with a count per state, then the points to look at. A point
// that names pages has a "Show PDF page" button: one page view, drawn by
// pdf.js from the chosen file, with core.js's measurements drawn over it
// ("Seeing a page" below).
//
// One check runs at a time. Choosing another PDF replaces a running check,
// and Cancel stops it; either way core.js releases the PDF reader and its
// worker, and a stopped check never shows its results.
(function () {
  "use strict";
  var root = document.querySelector("[data-pdf-check]");
  var script = document.currentScript;
  if (!root || !script) return;
  var base = script.src.replace(/[^/]*$/, "");
  var input = root.querySelector("input[type=file]");
  var drop = root.querySelector(".pdf-check-drop");
  var status = root.querySelector(".pdf-check-status");
  var results = root.querySelector(".pdf-check-results");
  var cancel = root.querySelector(".pdf-check-cancel");
  var again = root.querySelector(".pdf-check-again");
  var button = root.querySelector(".tool-file-button");
  var names = root.querySelector("[data-file-names]");
  var current = root.getAttribute("data-version") || "";
  // Links from the page text, so they work on the website and offline.
  function pageLink(part) {
    var link = document.querySelector('.guide-content a[href*="' + part + '"]');
    return link ? link.getAttribute("href").split("#")[0] : "";
  }
  var requirements = pageLink("requirements");
  var updating = pageLink("going-further");

  // Without these the checker stays hidden and the page's explanation stays.
  // pdf.js needs Promise.withResolvers (Safari 17.4, Firefox 121, Chrome 119).
  if (!window.Promise || typeof Promise.withResolvers !== "function" ||
      !("noModule" in HTMLScriptElement.prototype) || !window.DOMMatrix) return;
  var oge;
  try {
    oge = JSON.parse(document.getElementById("oge-rules").textContent);
  } catch (error) {
    return;
  }
  if (!oge || !oge.rules || !oge.measures) return;
  Array.prototype.forEach.call(document.querySelectorAll("[data-pdf-check-nojs]"), function (node) {
    node.hidden = true;
  });
  root.hidden = false;

  // The shared states (ToolState in tools-highlight.js); plain text without it.
  var State = window.ToolState || { set: function (r, s, state, c) {
    s.textContent = typeof c === "string" ? c : c ? c.title + ". " + c.text : ""; } };
  function say(text, state) { State.set(root, status, state || "", text, button); }
  function fail(title, text, href, link) { State.set(root, status, "error", { title: title, text: text, href: href, link: link }); }
  var submission = pageLink("submission");
  var checklist = submission ? submission + "#final-pdf-checklist" : "";

  // ---------- Loading the checks and the PDF reader -----------------------
  // Loaded once; a load that fails or takes longer than LOAD_LIMIT is given
  // up (its script tag removed), and the next PDF tries again.
  var LOAD_LIMIT = 60000;
  var loading = null;
  function load() {
    if (!loading) {
      var tag = null;
      var core = new Promise(function (resolve, reject) {
        if (window.PdfCheckCore) return resolve(window.PdfCheckCore);
        tag = document.createElement("script");
        tag.src = base + "core.js";
        tag.onload = function () { window.PdfCheckCore ? resolve(window.PdfCheckCore) : reject(new Error("reader")); };
        tag.onerror = function () { reject(new Error("reader")); };
        document.head.appendChild(tag);
      });
      var both = core.then(function (checks) {
        return import(base + "pdfjs/pdf.min.mjs").then(function (pdfjs) {
          if (pdfjs.version !== checks.PDFJS_VERSION) throw new Error("reader");
          pdfjs.GlobalWorkerOptions.workerSrc = base + "pdfjs/pdf.worker.min.mjs";
          return { checks: checks, pdfjs: pdfjs };
        });
      });
      loading = new Promise(function (resolve, reject) {
        var timer = setTimeout(function () { reject(new Error("reader")); }, LOAD_LIMIT);
        both.then(function (tools) { clearTimeout(timer); resolve(tools); },
                  function () { clearTimeout(timer); reject(new Error("reader")); });
      });
      loading.catch(function () {
        loading = null;
        if (tag && !window.PdfCheckCore) tag.remove();
      });
    }
    return loading;
  }

  // ---------- Showing results ---------------------------------------------
  var STATES = { ok: "Looks right", differs: "Differs from the manual's wording", check: "Look at this",
                 unknown: "Could not tell", info: "Information" };
  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }
  function counts(found) {
    return tally(found).map(function (t) { return t.text; }).join(", ") + ".";
  }
  var NOT_REVIEW = "These checks cover only what is listed here; they are not an OGE review, and a clean result does not mean OGE will accept the PDF.";
  // "§1.1 p. 1; FC; §2.2 p. 16": each rule's Manual cell, each piece once.
  function citation(ids) {
    var pieces = [];
    ids.forEach(function (id) {
      oge.rules[id].cite.split("; ").forEach(function (piece) {
        // The requirements map's short names, spelled out for students.
        piece = piece.replace(/^FC\b/, "OGE Formatting Checklist").replace(/^LT\b/, "OGE LaTeX Formatting Tips");
        if (pieces.indexOf(piece) < 0) pieces.push(piece);
      });
    });
    return pieces.join("; ");
  }
  function source(f, links) {
    var node = element("p", "pdf-check-source");
    if (f.rules && f.rules.length) {
      node.appendChild(document.createTextNode("Manual " + citation(f.rules) + ". "));
      if (links && requirements) {
        var link = element("a", "", "Requirements map");
        link.href = requirements + "#" + oge.rules[f.rules[0]].section;
        node.appendChild(link);
      }
    } else {
      node.appendChild(document.createTextNode("Information only; not a rule from the manual. "));
      if (links && f.update && updating) {
        var update = element("a", "", "Update the formatting safely");
        update.href = updating + "#update-the-formatting-safely";
        node.appendChild(update);
      }
    }
    return node;
  }
  // Points that need a look come first, so the one that matters is not
  // the tenth of thirteen cards: look at this, differs, could not tell; then
  // looks right; then information. Within a group, the order of core.js.
  var ORDER = ["check", "differs", "unknown", "ok", "info"];
  var GROUPS = [{ title: "To look at first", states: ["check", "differs", "unknown"] },
                { title: "Looks right", states: ["ok"] },
                { title: "Information", states: ["info"] }];
  function ordered(found) {
    return found.slice().sort(function (a, b) {
      return ORDER.indexOf(a.state) - ORDER.indexOf(b.state) || found.indexOf(a) - found.indexOf(b);
    });
  }
  // "1 to look at", "9 look right", ...: one count per state that occurs.
  var TALLY = { check: ["to look at", "to look at"], differs: ["differs from the manual's wording", "differ from the manual's wording"],
                unknown: ["could not be told", "could not be told"], ok: ["looks right", "look right"], info: ["information", "information"] };
  function tally(found) {
    return ORDER.map(function (state) {
      var n = found.filter(function (f) { return f.state === state; }).length;
      return n ? { state: state, text: n + " " + TALLY[state][n === 1 ? 0 : 1] } : null;
    }).filter(Boolean);
  }
  function item(f) {
    var node = element("li", "pdf-check-item is-" + f.state);
    var head = element("p", "pdf-check-head");
    head.appendChild(element("span", "pdf-check-state", STATES[f.state]));
    head.appendChild(element("strong", "", f.title));
    node.appendChild(head);
    node.appendChild(element("p", "", f.summary));
    if (f.coverage) node.appendChild(element("p", "pdf-check-coverage", f.coverage));
    if (f.pages.length) {
      var details = element("details");
      details.appendChild(element("summary", "", "Details (" + f.pages.length + ")"));
      var pagesList = element("ul");
      f.pages.slice(0, 50).forEach(function (text) { pagesList.appendChild(element("li", "", text)); });
      if (f.pages.length > 50) pagesList.appendChild(element("li", "", "and " + (f.pages.length - 50) + " more (all are in the printout)"));
      details.appendChild(pagesList);
      node.appendChild(details);
    }
    if (f.shows && f.shows.length) {
      var row = element("p", "pdf-check-show");
      var open = element("button", "button button-secondary", f.shows.length === 1
        ? "Show PDF page " + (f.shows[0].page + 1)
        : "Show the " + f.shows.length + " pages, from PDF page " + (f.shows[0].page + 1));
      open.type = "button";
      open.setAttribute("data-icon", "eye");
      open.setAttribute("aria-expanded", "false");
      open.addEventListener("click", function () {
        if (viewer.button === open) closeViewer(true);
        else openViewer(node, open, f);
      });
      row.appendChild(open);
      node.appendChild(row);
    }
    node.appendChild(source(f, true));
    return node;
  }
  function showResults(found, name) {
    clearResults();
    var heading = element("h3", "", "Results for " + name);
    heading.tabIndex = -1;
    results.appendChild(heading);
    var overview = element("div", "pdf-check-overview tool-card");
    var counts = element("p", "pdf-check-tally");
    tally(found).forEach(function (t, k) {
      if (k) counts.appendChild(document.createTextNode(" "));
      counts.appendChild(element("span", "pdf-check-state is-" + t.state, t.text));
    });
    overview.appendChild(counts);
    overview.appendChild(element("p", "pdf-check-summary", NOT_REVIEW));
    var actions = element("p", "tool-actions");
    var print = element("button", "button button-secondary pdf-check-print-button", "Print or save the result");
    print.type = "button";
    print.setAttribute("data-icon", "print");
    print.addEventListener("click", function () { printReport(found, name); });
    actions.appendChild(print);
    overview.appendChild(actions);
    results.appendChild(overview);
    GROUPS.forEach(function (group) {
      var these = ordered(found).filter(function (f) { return group.states.indexOf(f.state) >= 0; });
      if (!these.length) return;
      results.appendChild(element("h4", "", group.title + " (" + these.length + ")"));
      var list = element("ul", "pdf-check-list");
      list.setAttribute("role", "list");
      these.forEach(function (f) { list.appendChild(item(f)); });
      results.appendChild(list);
    });
    heading.focus();
  }
  function clearResults() {
    closeViewer(false);
    results.textContent = "";
  }

  // ---------- Seeing a page ----------------------------------------------------
  // One viewer for the whole result: "Show PDF page N" moves it under that
  // point and draws the page with pdf.js, with the checker's own
  // measurements drawn over it. The PDF is opened again from the chosen file
  // (still only in this tab) when the viewer opens, and released, with its
  // worker, when it closes, when another PDF is chosen, or on Cancel.
  var SVG = "http://www.w3.org/2000/svg";
  var checked = null;   // {file, size} of the PDF the results are for
  var viewer = { node: null, button: null, finding: null, at: 0, task: null, doc: null, drawing: null, run: 0 };
  function inchText(id) {
    var pt = oge.measures[id] && oge.measures[id].pt;
    return String(Number((pt / 72).toFixed(2))) + " in";
  }
  function buildViewer() {
    var node = element("div", "pdf-check-viewer");
    node.id = "pdf-check-viewer";
    node.setAttribute("role", "region");
    node.setAttribute("aria-labelledby", "pdf-check-viewer-title");
    var title = element("p", "pdf-check-viewer-title");
    title.id = "pdf-check-viewer-title";
    title.tabIndex = -1;
    node.appendChild(title);
    var body = element("div", "pdf-check-viewer-body");
    body.appendChild(element("p", "pdf-check-viewer-note"));
    var frame = element("div", "pdf-check-page");
    var canvas = element("canvas");
    canvas.setAttribute("role", "img");
    frame.appendChild(canvas);
    var marks = document.createElementNS(SVG, "svg");
    marks.setAttribute("aria-hidden", "true");
    marks.setAttribute("focusable", "false");
    marks.setAttribute("preserveAspectRatio", "none");
    frame.appendChild(marks);
    body.appendChild(frame);
    var said = element("p", "pdf-check-viewer-status");
    said.setAttribute("role", "status");
    body.appendChild(said);
    body.appendChild(element("ul", "pdf-check-legend"));
    node.appendChild(body);
    var actions = element("p", "tool-actions");
    [["prev", "Previous page"], ["next", "Next page"], ["close", "Close"]].forEach(function (b, k) {
      var button = element("button", "button button-secondary pdf-check-viewer-" + b[0], b[1]);
      button.type = "button";
      button.setAttribute("data-icon", ["prev", "next", "remove"][k]);
      if (k) actions.appendChild(document.createTextNode(" "));
      actions.appendChild(button);
    });
    node.appendChild(actions);
    node.querySelector(".pdf-check-viewer-prev").addEventListener("click", function () { step(-1); });
    node.querySelector(".pdf-check-viewer-next").addEventListener("click", function () { step(1); });
    node.querySelector(".pdf-check-viewer-close").addEventListener("click", function () { closeViewer(true); });
    node.addEventListener("keydown", function (event) {
      if (event.key === "Escape") { event.preventDefault(); closeViewer(true); }
    });
    return node;
  }
  function openViewer(item, button, f) {
    if (!checked) return;
    if (viewer.button) viewer.button.setAttribute("aria-expanded", "false");
    if (!viewer.node) viewer.node = buildViewer();
    viewer.button = button;
    viewer.finding = f;
    viewer.at = 0;
    button.setAttribute("aria-expanded", "true");
    button.setAttribute("aria-controls", viewer.node.id);
    button.parentNode.after(viewer.node);
    draw();
    viewer.node.querySelector(".pdf-check-viewer-title").focus();
  }
  function step(by) {
    var shows = viewer.finding.shows;
    viewer.at = Math.max(0, Math.min(shows.length - 1, viewer.at + by));
    draw();
  }
  // Ends any drawing and releases the PDF reader and its worker; the canvas
  // gives back its memory.
  function release() {
    viewer.run++;
    if (viewer.drawing) { try { viewer.drawing.cancel(); } catch (error) { /* already done */ } }
    if (viewer.task) viewer.task.destroy().catch(function () {});
    viewer.task = viewer.doc = viewer.drawing = null;
    if (viewer.node) {
      var canvas = viewer.node.querySelector("canvas");
      canvas.width = canvas.height = 0;
      viewer.node.querySelector("svg").textContent = "";
    }
  }
  function closeViewer(focus) {
    release();
    var button = viewer.button;
    viewer.button = viewer.finding = null;
    if (viewer.node) {
      viewer.node.removeAttribute("data-drawn");
      viewer.node.remove();
    }
    if (button) {
      button.setAttribute("aria-expanded", "false");
      if (focus && button.isConnected) button.focus();
    }
  }
  function openDocument() {
    if (viewer.doc) return viewer.doc;
    var file = checked.file, size = checked.size;
    viewer.doc = load().then(function (tools) {
      return file.arrayBuffer().then(function (bytes) {
        if (bytes.byteLength !== size) throw new Error("changed");
        viewer.task = tools.pdfjs.getDocument({
          data: new Uint8Array(bytes), isEvalSupported: false, disableFontFace: true, useSystemFonts: false,
          enableXfa: false, stopAtErrors: false, verbosity: 0
        });
        return viewer.task.promise;
      });
    });
    return viewer.doc;
  }
  function draw() {
    var f = viewer.finding, shows = f.shows, at = viewer.at, shown = shows[at], node = viewer.node;
    var mine = ++viewer.run;
    if (viewer.drawing) { try { viewer.drawing.cancel(); } catch (error) { /* already done */ } }
    var title = node.querySelector(".pdf-check-viewer-title");
    title.textContent = "";
    // "PDF page 5 (printed 12): text ..." -> the title, and the rest as the note.
    var parts = /^(PDF page \d+(?: \(printed [^)]*\))?): (.+)$/.exec(shown.note);
    var rest = parts ? parts[2].charAt(0).toUpperCase() + parts[2].slice(1) : shown.note;
    title.appendChild(element("strong", "", parts ? parts[1] : "PDF page " + (shown.page + 1)));
    if (shows.length > 1) title.appendChild(document.createTextNode(" (" + (at + 1) + " of " + shows.length + " for this point)"));
    node.querySelector(".pdf-check-viewer-note").textContent = rest;
    var prev = node.querySelector(".pdf-check-viewer-prev"), next = node.querySelector(".pdf-check-viewer-next");
    prev.hidden = next.hidden = shows.length < 2;
    var focused = document.activeElement;
    prev.disabled = at === 0;
    next.disabled = at === shows.length - 1;
    if (focused === prev && prev.disabled) next.focus();
    if (focused === next && next.disabled) prev.focus();
    // The legend: only the marks this page has, in words.
    var keys = [];
    if (shown.box) keys.push(["box", "Solid box: the " + (shown.what || "text") + " this point is about, as the checker measured it."]);
    if (shown.guides.indexOf("margin") >= 0) keys.push(["margin", "Dashed line: the " + inchText("margin") + " margins."]);
    if (shown.guides.indexOf("number") >= 0) keys.push(["number", "Dotted lines: " + inchText("page-number-edge") +
      " from the top and bottom edges, the page-number distance in the manual. The checker measures to the bottom of the number."]);
    var legend = node.querySelector(".pdf-check-legend");
    legend.textContent = "";
    keys.forEach(function (k) {
      var li = element("li");
      li.appendChild(element("span", "pdf-check-key is-" + k[0]));
      li.lastChild.setAttribute("aria-hidden", "true");
      li.appendChild(document.createTextNode(k[1]));
      legend.appendChild(li);
    });
    legend.hidden = !keys.length;
    var canvas = node.querySelector("canvas"), marks = node.querySelector("svg");
    canvas.setAttribute("aria-label", "Picture of PDF page " + (shown.page + 1) + " of your PDF. " + shown.note +
      (keys.length ? " " + keys.map(function (k) { return k[1]; }).join(" ") : ""));
    marks.textContent = "";
    node.removeAttribute("data-drawn");
    var said = node.querySelector(".pdf-check-viewer-status");
    said.textContent = "Drawing PDF page " + (shown.page + 1) + "…";
    openDocument().then(function (pdf) {
      if (mine !== viewer.run) return null;
      return pdf.getPage(shown.page + 1).then(function (page) {
        if (mine !== viewer.run) return null;
        var base = page.getViewport({ scale: 1 });
        var frame = node.querySelector(".pdf-check-page");
        var wide = Math.max(200, frame.clientWidth || 320);
        var ratio = Math.min(window.devicePixelRatio || 1, 2);
        var scale = Math.min(wide * ratio, 2000) / base.width;
        var viewport = page.getViewport({ scale: scale });
        canvas.width = Math.round(viewport.width);
        canvas.height = Math.round(viewport.height);
        frame.style.aspectRatio = base.width + " / " + base.height;
        viewer.drawing = page.render({ canvas: canvas, viewport: viewport });
        return viewer.drawing.promise.then(function () {
          viewer.drawing = null;
          if (mine !== viewer.run) return;
          overlay(marks, page, base, shown);
          page.cleanup();
          said.textContent = "";
          node.setAttribute("data-drawn", String(shown.page + 1));
        });
      });
    }).catch(function (error) {
      if (mine !== viewer.run || (error && error.name === "RenderingCancelledException")) return;
      said.textContent = error && error.message === "changed"
        ? "The file has changed since it was checked, so this page cannot be drawn. Choose it again to check the new version."
        : "This page could not be drawn. The result above still stands; open the PDF in your PDF viewer to look at it.";
      if (error && error.message === "changed") release();
    });
  }
  // The checker's measurements, in points from the bottom-left corner of the
  // page (core.js), turned into the drawn page's own coordinates; pdf.js does
  // the turning for rotated pages.
  function overlay(svg, page, base, shown) {
    var view = page.view, unit = page.userUnit > 0 ? page.userUnit : 1;
    function at(x, y) { return base.convertToViewportPoint(x / unit + view[0], y / unit + view[1]); }
    var w = (view[2] - view[0]) * unit, h = (view[3] - view[1]) * unit;
    svg.setAttribute("viewBox", "0 0 " + base.width + " " + base.height);
    function add(kind, tag, attrs) {
      ["pdf-check-halo", "pdf-check-mark is-" + kind].forEach(function (cls) {
        var shape = document.createElementNS(SVG, tag);
        shape.setAttribute("class", cls);
        Object.keys(attrs).forEach(function (k) { shape.setAttribute(k, attrs[k]); });
        svg.appendChild(shape);
      });
    }
    function rect(kind, x0, y0, x1, y1) {
      var a = at(x0, y0), b = at(x1, y1);
      add(kind, "rect", { x: Math.min(a[0], b[0]), y: Math.min(a[1], b[1]),
                          width: Math.abs(b[0] - a[0]), height: Math.abs(b[1] - a[1]) });
    }
    function line(kind, x0, y0, x1, y1) {
      var a = at(x0, y0), b = at(x1, y1);
      add(kind, "line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1] });
    }
    if (shown.guides.indexOf("margin") >= 0) {
      var m = oge.measures.margin.pt;
      rect("margin", m, m, w - m, h - m);
    }
    if (shown.guides.indexOf("number") >= 0) {
      var e = oge.measures["page-number-edge"].pt;
      line("number", 0, e, w, e);
      line("number", 0, h - e, w, h - e);
    }
    if (shown.box) {
      var pad = 2, box = shown.box;
      rect("box", box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad);
    }
  }

  // ---------- The printout ----------------------------------------------------
  // A separate block shown only while printing, so the printout carries the
  // result alone: file name, date, versions, every check with its status and
  // source, and every page it names.
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function printStyle() {
    if (document.getElementById("pdf-check-print-style")) return;
    var style = element("style");
    style.id = "pdf-check-print-style";
    style.textContent =
      "@media screen { .pdf-check-print { display: none; } }\n" +
      "@media print {\n" +
      "  html.pdf-check-printing body > :not(.pdf-check-print) { display: none !important; }\n" +
      "  .pdf-check-print { font: 10.5pt/1.4 Georgia, 'Times New Roman', serif; color: #000; }\n" +
      "  .pdf-check-print h1 { font-size: 15pt; margin: 0 0 6pt; }\n" +
      "  .pdf-check-print p { margin: 0 0 6pt; }\n" +
      "  .pdf-check-print section { break-inside: avoid; border-top: 0.75pt solid #888; padding: 6pt 0 2pt; }\n" +
      "  .pdf-check-print h2 { font-size: 11pt; margin: 0 0 3pt; }\n" +
      "  .pdf-check-print ul { margin: 0 0 6pt; padding-left: 16pt; }\n" +
      "  .pdf-check-print .note { border: 1pt solid #000; padding: 6pt 8pt; }\n" +
      "}\n";
    document.head.appendChild(style);
  }
  function removePrintout() {
    var old = document.querySelector(".pdf-check-print");
    if (old) old.remove();
    document.documentElement.classList.remove("pdf-check-printing");
  }
  function printReport(found, name) {
    printStyle();
    removePrintout();
    var sheet = element("div", "pdf-check-print");
    var today = new Date();
    sheet.appendChild(element("h1", "", "PDF check: " + name));
    sheet.appendChild(element("p", "", "Checked " + today.getDate() + " " + MONTHS[today.getMonth()] + " " + today.getFullYear() +
      " with the RPI Thesis Toolkit's \"Check your PDF\" page" + (current ? " (toolkit v" + current + ")" : "") +
      ", an unofficial, community-made tool. " + counts(found)));
    sheet.appendChild(element("p", "note", NOT_REVIEW));
    ordered(found).forEach(function (f) {
      var part = element("section");
      part.appendChild(element("h2", "", STATES[f.state] + ": " + f.title));
      part.appendChild(element("p", "", f.summary));
      if (f.coverage) part.appendChild(element("p", "", f.coverage));
      if (f.pages.length) {
        var list = element("ul");
        f.pages.forEach(function (text) { list.appendChild(element("li", "", text)); });
        part.appendChild(list);
      }
      part.appendChild(source(f, false));
      sheet.appendChild(part);
    });
    if (/^https?:$/.test(location.protocol)) sheet.appendChild(element("p", "", "Page: " + location.href.split("#")[0]));
    document.body.appendChild(sheet);
    document.documentElement.classList.add("pdf-check-printing");
    // Gone after printing, so a later ordinary print of the page has no old result.
    var done = function () {
      if (sheet.parentNode) sheet.remove();
      if (!document.querySelector(".pdf-check-print")) document.documentElement.classList.remove("pdf-check-printing");
      window.removeEventListener("afterprint", done);
    };
    window.addEventListener("afterprint", done);
    window.print();
  }

  // ---------- Reading a file --------------------------------------------------
  // `run` numbers the checks: only the latest one may change the page.
  var run = 0, job = null;
  function stop() {
    if (job && job.cancel) job.cancel().catch(function () {});
    job = null;
    run++;
    cancel.hidden = true;
  }
  function finished() {
    cancel.hidden = true;
    again.hidden = false;
  }
  function check(file) {
    if (!file) return;
    stop();
    removePrintout();
    clearResults();
    checked = null;
    if (names) names.textContent = "Chosen: " + file.name;
    if (!/\.pdf$/i.test(file.name) && file.type !== "application/pdf") {
      fail("That is not a PDF", file.name + " is not a PDF file. Choose the PDF your editor made, often main.pdf, next to main.tex or under Download PDF on Overleaf.",
           checklist, "Final PDF checklist");
      input.value = "";
      finished();
      return;
    }
    var mine = ++run, myJob = job = {};
    function latest() {
      if (mine === run) return;
      var error = new Error("cancelled");
      error.name = "AbortError";
      throw error;
    }
    cancel.hidden = false;
    again.hidden = true;
    say("Loading the PDF reader…", "working");
    var name = file.name;
    var tools;
    load().then(function (loaded) {
      latest();
      tools = loaded;
      say("Reading " + name + "…", "working");
      return file.arrayBuffer();
    }).then(function (bytes) {
      latest();
      return tools.checks.read(tools.pdfjs, new Uint8Array(bytes), function (page, total) {
        if (mine === run) say("Reading page " + page + " of " + total + "…", "working");
      }, myJob);
    }).then(function (data) {
      latest();
      var found = tools.checks.analyse(data, { current: current, rules: oge });
      say("Checked " + name + ": " + counts(found), "done");
      checked = { file: file, size: data.fileSize };
      showResults(found, name);
    }).catch(function (error) {
      if (mine !== run) return;  // replaced or cancelled: the newer state stays
      clearResults();
      checked = null;
      if (error && error.message === "reader") {
        fail("The PDF reader did not start", location.protocol === "file:"
          ? "This browser does not let a page opened from a file start the PDF reader. Open \"Check your PDF\" on the toolkit's website instead; your PDF still stays on your computer. Or check by eye with the"
          : "It could not be loaded, perhaps because the connection dropped. Reload the page and try again, or check by eye with the",
          checklist, "Final PDF checklist");
      } else if (error && error.name === "PasswordException") {
        fail("This PDF has a password", name + " is protected, so the checker cannot open it. Check a copy saved without the password, as your editor makes it. More in the",
             checklist, "Final PDF checklist");
      } else {
        fail("This file could not be read as a PDF", name + " may be damaged or only partly saved. Compile again, then choose the new PDF. If it happens again, see",
             pageLink("troubleshooting") ? pageLink("troubleshooting") + "#clean-recompile" : "", "Clean recompile");
      }
    }).then(function () {
      if (mine !== run) return;
      job = null;
      finished();
      input.value = "";
    });
  }

  cancel.addEventListener("click", function () {
    stop();
    input.value = "";
    clearResults();
    checked = null;
    say("Check cancelled. Choose a PDF to start again.");
    input.focus();
  });
  again.addEventListener("click", function () {
    stop();
    removePrintout();
    clearResults();
    checked = null;
    if (names) names.textContent = "";
    say("");
    again.hidden = true;
    input.focus();
    input.click();
  });
  // While a check runs, the button cannot be pressed again; a dropped PDF still replaces it.
  drop.addEventListener("click", function (event) {
    if (button && button.hasAttribute("data-busy")) event.preventDefault();
  });

  input.addEventListener("change", function () { check(input.files[0]); });
  var onDrop = function (event) { check(event.dataTransfer.files[0]); };
  if (State.dropZone) State.dropZone(drop, onDrop);
  else drop.addEventListener("drop", function (event) { event.preventDefault(); onDrop(event); });
})();
