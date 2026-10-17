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
  var current = root.getAttribute("data-version") || "";
  // Links from the page text, so they work on the website and offline.
  function pageLink(part) {
    var link = document.querySelector('.guide-content a[href*="' + part + '"]');
    return link ? link.getAttribute("href").split("#")[0] : "";
  }
  var requirements = pageLink("requirements");
  var updating = pageLink("going-further");

  // Without these the checker stays hidden and the page's explanation stays.
  if (!window.Promise || !("noModule" in HTMLScriptElement.prototype) || !window.DOMMatrix) return;
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

  function say(text) { status.textContent = text; }

  // ---------- Loading the checks and the PDF reader -----------------------
  var loading = null;
  function load() {
    if (!loading) {
      var core = new Promise(function (resolve, reject) {
        if (window.PdfCheckCore) return resolve(window.PdfCheckCore);
        var tag = document.createElement("script");
        tag.src = base + "core.js";
        tag.onload = function () { window.PdfCheckCore ? resolve(window.PdfCheckCore) : reject(new Error("reader")); };
        tag.onerror = function () { reject(new Error("reader")); };
        document.head.appendChild(tag);
      });
      loading = core.then(function (checks) {
        return import(base + "pdfjs/pdf.min.mjs").then(function (pdfjs) {
          if (pdfjs.version !== checks.PDFJS_VERSION) throw new Error("reader");
          pdfjs.GlobalWorkerOptions.workerSrc = base + "pdfjs/pdf.worker.min.mjs";
          return { checks: checks, pdfjs: pdfjs };
        });
      }).catch(function () { throw new Error("reader"); });
      loading.catch(function () { loading = null; });
    }
    return loading;
  }

  // ---------- Showing results ---------------------------------------------
  var STATES = { ok: "Looks right", check: "Look at this", unknown: "Could not tell", info: "Information" };
  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }
  function counts(found) {
    var looks = found.filter(function (f) { return f.state === "check"; }).length;
    var unsure = found.filter(function (f) { return f.state === "unknown"; }).length;
    return (looks ? looks + " point" + (looks > 1 ? "s" : "") + " to look at" : "Nothing to look at among these points") +
      (unsure ? "; " + unsure + " could not be told" : "") + ".";
  }
  var NOT_REVIEW = "These checks cover only what is listed here; they are not an OGE review, and a clean result does not mean OGE will accept the PDF.";
  // "§1.1 p. 1; FC; §2.2 p. 16": each rule's Manual cell, each piece once.
  function citation(ids) {
    var pieces = [];
    ids.forEach(function (id) {
      oge.rules[id].cite.split("; ").forEach(function (piece) {
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
  function show(found, name) {
    results.textContent = "";
    var heading = element("h3", "", "Results for " + name);
    heading.tabIndex = -1;
    results.appendChild(heading);
    results.appendChild(element("p", "pdf-check-summary", counts(found) + " " + NOT_REVIEW));
    var list = element("ul", "pdf-check-list");
    list.setAttribute("role", "list");
    found.forEach(function (f) {
      var item = element("li", "pdf-check-item is-" + f.state);
      var head = element("p", "pdf-check-head");
      head.appendChild(element("span", "pdf-check-state", STATES[f.state]));
      head.appendChild(element("strong", "", f.title));
      item.appendChild(head);
      item.appendChild(element("p", "", f.summary));
      if (f.pages.length) {
        var details = element("details");
        details.appendChild(element("summary", "", "Details (" + f.pages.length + ")"));
        var pagesList = element("ul");
        f.pages.slice(0, 50).forEach(function (text) { pagesList.appendChild(element("li", "", text)); });
        if (f.pages.length > 50) pagesList.appendChild(element("li", "", "and " + (f.pages.length - 50) + " more (all are in the printout)"));
        details.appendChild(pagesList);
        item.appendChild(details);
      }
      item.appendChild(source(f, true));
      list.appendChild(item);
    });
    results.appendChild(list);
    var actions = element("p");
    var print = element("button", "button button-secondary", "Print or save the result");
    print.type = "button";
    print.addEventListener("click", function () { printReport(found, name); });
    actions.appendChild(print);
    results.appendChild(actions);
    heading.focus();
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
  function printReport(found, name) {
    printStyle();
    var old = document.querySelector(".pdf-check-print");
    if (old) old.remove();
    var sheet = element("div", "pdf-check-print");
    var today = new Date();
    sheet.appendChild(element("h1", "", "PDF check: " + name));
    sheet.appendChild(element("p", "", "Checked " + today.getDate() + " " + MONTHS[today.getMonth()] + " " + today.getFullYear() +
      " with the RPI Thesis Toolkit's \"Check your PDF\" page" + (current ? " (toolkit v" + current + ")" : "") +
      ", an unofficial, community-made tool. " + counts(found)));
    sheet.appendChild(element("p", "note", NOT_REVIEW));
    found.forEach(function (f) {
      var part = element("section");
      part.appendChild(element("h2", "", STATES[f.state] + ": " + f.title));
      part.appendChild(element("p", "", f.summary));
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
    var done = function () {
      document.documentElement.classList.remove("pdf-check-printing");
      window.removeEventListener("afterprint", done);
    };
    window.addEventListener("afterprint", done);
    window.print();
  }

  // ---------- Reading a file --------------------------------------------------
  var busy = false;
  function check(file) {
    if (!file || busy) return;
    if (!/\.pdf$/i.test(file.name) && file.type !== "application/pdf") {
      say("That is not a PDF. Choose the PDF your editor made (often main.pdf).");
      return;
    }
    busy = true;
    results.textContent = "";
    say("Loading the PDF reader…");
    var name = file.name;
    var tools;
    load().then(function (loaded) {
      tools = loaded;
      say("Reading " + name + "…");
      return file.arrayBuffer();
    }).then(function (bytes) {
      return tools.checks.read(tools.pdfjs, new Uint8Array(bytes), function (page, total) {
        say("Reading page " + page + " of " + total + "…");
      });
    }).then(function (data) {
      var found = tools.checks.analyse(data, { current: current, rules: oge });
      say("");
      show(found, name);
    }).catch(function (error) {
      say(error && error.message === "reader"
        ? (location.protocol === "file:"
          ? "This browser does not let a page opened from a file start the PDF reader. Open \"Check your PDF\" on the toolkit's website instead (your PDF still stays on your computer), or use the checklist on the Submitting page."
          : "The PDF reader could not be loaded. Reload the page and try again, or use the checklist on the Submitting page.")
        : error && error.name === "PasswordException"
        ? "This PDF is protected with a password. Check a copy without the password."
        : "This file could not be read as a PDF.");
    }).then(function () {
      busy = false;
      input.value = "";
    });
  }

  input.addEventListener("change", function () { check(input.files[0]); });
  ["dragenter", "dragover"].forEach(function (type) {
    drop.addEventListener(type, function (event) {
      event.preventDefault();
      drop.classList.add("is-over");
    });
  });
  ["dragleave", "drop"].forEach(function (type) {
    drop.addEventListener(type, function () { drop.classList.remove("is-over"); });
  });
  drop.addEventListener("drop", function (event) {
    event.preventDefault();
    check(event.dataTransfer.files[0]);
  });
})();
