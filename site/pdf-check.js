// "Check your PDF" (docs/check-pdf.md). An extra only: with JavaScript off the
// page explains the checks and links to the submission checklist instead.
//
// The PDF is read in this browser tab and never sent anywhere. The PDF reader
// (Mozilla's pdf.js, Apache-2.0) is fetched from cdnjs at a pinned version and
// used only when its SHA-384 matches the hash below, so a changed file is
// refused. To update it: pick a pdf.js release on cdnjs that matches the
// pdfjs-dist package on npm byte for byte, and replace VERSION and both hashes.
//
// The measurements follow scripts/check.py (the toolkit's own PDF tests), in
// PDF points (72 per inch) from the bottom-left corner of the page. Each
// finding cites a row of docs/project/requirements.md; build_site.py refuses
// the page if a `cite` below is not found there word for word.
(function () {
  "use strict";
  var root = document.querySelector("[data-pdf-check]");
  if (!root) return;
  var VERSION = "4.10.38";
  var CDN = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/" + VERSION + "/";
  var FILES = {
    lib: ["pdf.min.mjs", "sha384-+0ti2moQlmLN7WZHE2RHIf5lV8hHxhxEalN0il3YZceG26fUPyOkR0hp9daxk1i7"],
    worker: ["pdf.worker.min.mjs", "sha384-ToeVvShCxKc6CEvhHeMt0Q8A06pSPDbAlngO9nokrDmh914gk/pYd0N7D0a4Lz2o"]
  };
  var INCH = 72;
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
  if (!window.crypto || !crypto.subtle || !window.fetch || !window.DOMMatrix) return;
  Array.prototype.forEach.call(document.querySelectorAll("[data-pdf-check-nojs]"), function (node) {
    node.hidden = true;
  });
  root.hidden = false;

  function say(text) { status.textContent = text; }

  // ---------- Loading the PDF reader --------------------------------------
  var reader = null;
  function verified(name, hash) {
    return fetch(CDN + name, { credentials: "omit" }).then(function (response) {
      if (!response.ok) throw new Error("download");
      return response.arrayBuffer();
    }).then(function (bytes) {
      return crypto.subtle.digest("SHA-384", bytes).then(function (digest) {
        var text = btoa(String.fromCharCode.apply(null, new Uint8Array(digest)));
        if ("sha384-" + text !== hash) throw new Error("hash");
        return URL.createObjectURL(new Blob([bytes], { type: "text/javascript" }));
      });
    });
  }
  function loadReader() {
    if (!reader) {
      reader = Promise.all([verified.apply(null, FILES.lib), verified.apply(null, FILES.worker)])
        .then(function (urls) {
          return import(urls[0]).then(function (pdfjs) {
            pdfjs.GlobalWorkerOptions.workerSrc = urls[1];
            return pdfjs;
          });
        });
      reader.catch(function () { reader = null; });
    }
    return reader;
  }

  // ---------- Reading pages -------------------------------------------------
  function roman(number) {
    var result = "", table = [[1000, "m"], [900, "cm"], [500, "d"], [400, "cd"], [100, "c"],
      [90, "xc"], [50, "l"], [40, "xl"], [10, "x"], [9, "ix"], [5, "v"], [4, "iv"], [1, "i"]];
    table.forEach(function (pair) {
      while (number >= pair[0]) { result += pair[1]; number -= pair[0]; }
    });
    return result;
  }
  function squash(text) { return text.normalize("NFKC").replace(/\s+/g, ""); }
  function inches(points) { return (points / INCH).toFixed(2) + " in"; }

  // One page: its size, the text in the margins (the page number), and the
  // lines of the text block, top first.
  function readPage(pdf, number) {
    return pdf.getPage(number).then(function (page) {
      var view = page.view, width = view[2] - view[0], height = view[3] - view[1];
      return page.getTextContent().then(function (content) {
        var margin = [], body = [], sideways = [];
        content.items.forEach(function (item) {
          if (!item.str || !item.str.trim()) return;
          var t = item.transform;
          if (Math.abs(t[1]) > 0.01 || Math.abs(t[2]) > 0.01 || t[0] <= 0) {
            // Rotated text (a sideways table): keep only how far it spans
            // across the page, from the corners of its box.
            var a = Math.hypot(t[0], t[1]) || 1, b = Math.hypot(t[2], t[3]) || 1;
            var along = item.width / a, up = (item.height || 0) / b, xs = [0, 0, 0, 0];
            xs[0] = t[4]; xs[1] = t[4] + t[0] * along; xs[2] = t[4] + t[2] * up; xs[3] = xs[1] + t[2] * up;
            sideways.push({ left: Math.min.apply(null, xs) - view[0], right: Math.max.apply(null, xs) - view[0] });
            return;
          }
          var run = { x: t[4] - view[0], y: t[5] - view[1], width: item.width, str: item.str };
          // Outside the 1 in margins, with a little tolerance, as in check.py.
          (run.y < 70 || run.y > height - 70 ? margin : body).push(run);
        });
        page.cleanup();
        return { index: number - 1, width: width, height: height, margin: margin,
                 lines: lines(body), sideways: sideways };
      });
    });
  }
  function lines(runs) {
    runs.sort(function (a, b) { return b.y - a.y || a.x - b.x; });
    var result = [];
    runs.forEach(function (run) {
      var line = result[result.length - 1];
      if (!line || Math.abs(line.y - run.y) > 2) {
        line = { y: run.y, runs: [] };
        result.push(line);
      }
      line.runs.push(run);
    });
    result.forEach(function (line) {
      line.runs.sort(function (a, b) { return a.x - b.x; });
      var text = "", end = null;
      line.runs.forEach(function (run) {
        if (end !== null && run.x - end > 1) text += " ";
        text += run.str;
        end = run.x + run.width;
      });
      line.text = text.replace(/\s+/g, " ").trim();
    });
    return result;
  }

  // ---------- Checks ----------------------------------------------------------
  var LEADERS = /(?:\s*\.){3,}/;
  var ENTRY = /^(.*?)(?:\s*\.)*\s*([0-9]+|[ivxlcdm]+)$/;
  // A level-1 heading such as "1. INTRODUCTION", "A. DATA", or "REFERENCES":
  // capitals only, no dot leaders, no page number at the end, and not a
  // numbered lower level such as "1.1 METHODS" or "A.2 DATA".
  function isHeading(text) {
    if (!text || LEADERS.test(text) || /\s([0-9]+|[ivxlcdm]+)$/.test(text)) return false;
    if (/^(?:[0-9]+|[A-Z])\.[0-9]/.test(text)) return false;
    return (/^(?:[0-9]+|[A-Z])\.\s?[A-Z]/.test(text) || /[A-Z]{4,}/.test(text)) && !/[a-z]/.test(text);
  }

  function pageNumber(page) {
    if (!page.margin.length) return null;
    var runs = page.margin.slice().sort(function (a, b) { return a.x - b.x; });
    var text = runs.map(function (run) { return run.str; }).join("").replace(/\s+/g, "");
    var low = Math.min.apply(null, runs.map(function (r) { return r.y; }));
    var high = Math.max.apply(null, runs.map(function (r) { return r.y; }));
    var x = runs[0].x, y = runs[0].y, place = "elsewhere";
    var right = Math.max.apply(null, runs.map(function (r) { return r.x + r.width; }));
    var center = (x + right) / 2;
    // The class centers the number to within 1 pt; 6 pt (half a digit's
    // width either way of a few digits) allows for rounding in the reader.
    if (high - low < 1.5 && Math.abs(y - 54) < 1.5 && Math.abs(center - page.width / 2) < 6) place = "bottom";
    else if (high - low < 1.5 && Math.abs(y - (page.height - 54)) < 1.5 && x > page.width - 112) place = "top";
    return { text: text, place: place, x: x, y: y, right: right };
  }

  function analyse(pages, info) {
    var found = [];
    var numbers = pages.map(pageNumber);
    // Paper size.
    var wrong = pages.filter(function (p) {
      return Math.abs(p.width - 612) > 0.5 || Math.abs(p.height - 792) > 0.5;
    });
    found.push({
      title: "Paper size: US letter",
      cite: "§2.2 p. 16; FC", section: "page-layout-and-spacing",
      state: wrong.length ? "check" : "ok",
      summary: wrong.length
        ? wrong.length + " of " + pages.length + " pages are not 8.5 × 11 in."
        : "All " + pages.length + " pages are 8.5 × 11 in.",
      pages: wrong.map(function (p) {
        return "PDF page " + (p.index + 1) + ": " + inches(p.width) + " × " + inches(p.height);
      })
    });

    // Where the body starts: the page that opens Chapter 1, or else the
    // first page numbered 1.
    var body = -1, i;
    for (i = 1; i < pages.length && body < 0; i++) {
      var first = pages[i].lines.length ? pages[i].lines[0].text : "";
      if (/^(1\.\s?[A-Z]|CHAPTER 1\b)/.test(first) && isHeading(first)) body = i;
    }
    for (i = 1; i < pages.length && body < 0; i++) {
      if (numbers[i] && numbers[i].text === "1") body = i;
    }
    var label = function (i) {
      if (i === 0) return "i";
      if (body < 0 || i < body) return roman(i + 1);
      return String(i - body + 1);
    };
    var where = function (i) {
      return "PDF page " + (i + 1) + (i > 0 && numbers[i] ? " (printed " + numbers[i].text + ")" : "");
    };

    // Numbering: title page unnumbered, then ii, iii, ... and 1, 2, ...
    var numbering = [];
    if (numbers[0]) numbering.push("PDF page 1 (title page) shows \"" + numbers[0].text + "\" in the margin; the title page counts as i but shows no number.");
    if (body < 0) numbering.push("No page is numbered 1, so the start of Chapter 1 was not found.");
    for (i = 1; i < pages.length; i++) {
      if (!numbers[i]) numbering.push("PDF page " + (i + 1) + ": no page number found (expected " + label(i) + ").");
      else if (numbers[i].text !== label(i)) numbering.push("PDF page " + (i + 1) + ": shows \"" + numbers[i].text + "\", expected " + label(i) + ".");
    }
    found.push({
      title: "Page numbering: roman front matter, then 1 at Chapter 1",
      cite: "§1.1 p. 1; FC", cite2: "§2.2 p. 16", section: "page-numbers",
      state: numbering.length ? "check" : "ok",
      summary: numbering.length
        ? numbering.length + " page" + (numbering.length > 1 ? "s" : "") + " to look at."
        : "Title page unnumbered; front matter ii to " + roman(body) + "; Chapter 1 starts on PDF page " + (body + 1) + " as page 1.",
      pages: numbering
    });

    // Contents: entries and the pages they point to.
    // Contents entries name printed page numbers. When a number is printed
    // twice, an Arabic one means the body page.
    var byLabel = {};
    numbers.forEach(function (n, i) {
      if (n && (!(n.text in byLabel) || (/^[0-9]+$/.test(n.text) && i >= body && byLabel[n.text] < body))) byLabel[n.text] = i;
    });
    pages.forEach(function (p, i) { if (!numbers[i] && !(label(i) in byLabel)) byLabel[label(i)] = i; });
    var top = function (p) { return p.lines.length ? p.lines[0].text : ""; };
    var tocStart = -1;
    for (i = 0; i < Math.min(pages.length, 40); i++) {
      if (/^(TABLE OF )?CONTENTS$/i.test(top(pages[i]))) { tocStart = i; break; }
    }
    var entries = [], opening = {};
    if (tocStart >= 0) {
      var pending = "";
      for (i = tocStart; i < pages.length && (i === tocStart || !isHeading(top(pages[i]))); i++) {
        pages[i].lines.forEach(function (line, n) {
          if (i === tocStart && n === 0) return;
          if (/^page$/i.test(line.text)) return;
          var match = ENTRY.exec(line.text);
          if (match && (LEADERS.test(line.text) || /[0-9]$/.test(line.text) || isHeading((pending + match[1]).trim()))) {
            entries.push({ title: (pending + match[1]).trim(), label: match[2], from: i });
            pending = "";
          } else {
            pending += line.text + " ";
          }
        });
      }
      entries.forEach(function (entry) {
        entry.level1 = isHeading(entry.title);
        entry.target = byLabel[entry.label];
        if (entry.level1 && entry.target !== undefined) opening[entry.target] = true;
      });
    }
    pages.forEach(function (p, i) { if (i > 0 && isHeading(top(p))) opening[i] = true; });

    // Page-number position: bottom center on front matter and level-1
    // openings, top right elsewhere; 0.75 in from the edge.
    var placed = [];
    for (i = 1; i < pages.length; i++) {
      var n = numbers[i];
      if (!n) continue;
      var want = (body < 0 || i < body || opening[i]) ? "bottom" : "top";
      if (n.place !== want) {
        var measured = n.place === "elsewhere"
          ? "found " + inches(n.y) + " from the bottom edge, " + inches(n.x) + " from the left"
          : "found at the " + (n.place === "bottom" ? "bottom center" : "top right");
        placed.push(where(i) + ": expected " + (want === "bottom" ? "bottom center" : "top right") +
          " (" + (opening[i] ? "a level-1 heading starts here" : i < body ? "front matter" : "body page") + "), " + measured + ".");
      }
    }
    found.push({
      title: "Page-number position",
      cite: "§2.2 pp. 16-17; FC", section: "page-numbers",
      state: placed.length ? "check" : "ok",
      summary: placed.length
        ? placed.length + " page" + (placed.length > 1 ? "s" : "") + " with the number somewhere else."
        : "Bottom center on front matter and level-1 openings, top right on other pages, 0.75 in from the edge.",
      pages: placed
    });

    // Level-1 headings start at the top margin. The class puts the first
    // baseline 84 pt below the top edge; a heading lower than 96 pt (1.33 in)
    // is reported. TODO(verify): the 96 pt limit is this project's choice,
    // not a number from the manual.
    var low = [], openings = 0;
    Object.keys(opening).forEach(function (key) {
      var p = pages[+key];
      if (!p.lines.length) return;
      openings++;
      var depth = p.height - p.lines[0].y;
      if (depth > 96) low.push(where(p.index) + ": \"" + p.lines[0].text.slice(0, 60) + "\" starts " + inches(depth) + " from the top edge.");
    });
    found.push({
      title: "Level-1 headings at the top margin",
      cite: "§2.2; LT", section: "page-layout-and-spacing",
      state: low.length ? "check" : openings ? "ok" : "skip",
      summary: low.length
        ? low.length + " of " + openings + " heading pages start lower than the top margin."
        : openings ? "All " + openings + " pages that start with a level-1 heading start it at the top margin."
        : "No level-1 headings were recognized (the checker looks for headings in capitals).",
      pages: low
    });

    // Text inside the 1 in side margins. Pictures are not measured.
    var outside = [];
    pages.forEach(function (p) {
      var worst = 0;
      p.lines.forEach(function (line) {
        line.runs.forEach(function (run) {
          worst = Math.max(worst, 72 - run.x, run.x + run.width - (p.width - 72));
        });
      });
      p.sideways.forEach(function (run) {
        worst = Math.max(worst, 72 - run.left, run.right - (p.width - 72));
      });
      if (worst > 1.5) outside.push(where(p.index) + ": text reaches " + inches(worst) + " into the side margin.");
    });
    found.push({
      title: "Text inside the 1 in side margins",
      cite: "§2.2 p. 16; FC", section: "page-layout-and-spacing",
      state: outside.length ? "check" : "ok",
      summary: outside.length
        ? outside.length + " page" + (outside.length > 1 ? "s" : "") + " with text in a side margin. Long lines, equations, URLs, and wide tables are the usual cause."
        : "No text crosses the left or right margin. Figures and pictures were not measured; check them by eye.",
      pages: outside
    });

    // Contents entries identical to the headings they point to.
    var mismatch = [];
    entries.forEach(function (entry) {
      var p = pages[entry.target];
      if (!p) {
        mismatch.push("\"" + entry.title + "\" points to page " + entry.label + ", which was not found.");
        return;
      }
      var want = squash(entry.title);
      var text = p.lines.map(function (line) { return line.text; });
      // The class lists an APPENDICES line at the first appendix, which has no
      // heading of that name.
      var ok = /^APPENDI(CES|X)$/.test(entry.title) ? isHeading(text[0])
        : entry.level1 ? [1, 2, 3].some(function (k) { return squash(text.slice(0, k).join(" ")) === want; })
        : squash(text.join(" ")).indexOf(want) >= 0;
      if (!ok) {
        mismatch.push("\"" + entry.title + "\" (page " + entry.label + "): " +
          (entry.level1 ? "that page starts with \"" + (text[0] || "") .slice(0, 60) + "\"." : "not found on that page."));
      }
    });
    found.push({
      title: "Contents entries match the headings",
      cite: "§1.3 p. 4", section: "contents-and-lists",
      state: tocStart < 0 || !entries.length ? "skip" : mismatch.length ? "check" : "ok",
      summary: tocStart < 0
        ? "No page starting with CONTENTS or TABLE OF CONTENTS was found."
        : !entries.length ? "The contents page was found, but no entries could be read."
        : mismatch.length ? mismatch.length + " of " + entries.length + " entries differ from the page they point to."
        : "All " + entries.length + " entries match the text on the page they point to.",
      pages: mismatch
    });

    // Creator: the class writes its version into the PDF properties.
    var creator = (info && info.Creator) || "";
    var version = /rpi-thesis (\d{4}\/\d\d\/\d\d) v(\d+\.\d+\.\d+)/.exec(creator);
    var older = version && current && compare(version[2], current) < 0;
    found.push({
      title: "Toolkit version in the PDF",
      section: "", update: true,
      state: !version ? "skip" : older ? "check" : "ok",
      summary: !version
        ? (creator ? "Made with \"" + creator + "\", not the toolkit class, so there is no version to compare." : "The PDF names no creator, so there is no version to compare.")
        : "Made with rpi-thesis v" + version[2] + " (" + version[1] + ")" +
          (older ? "; v" + current + " is the newest. Read its change notes before you submit." : current ? ", the newest version." : "."),
      pages: []
    });
    return found;
  }
  function compare(a, b) {
    a = a.split(".").map(Number); b = b.split(".").map(Number);
    for (var i = 0; i < 3; i++) if (a[i] !== b[i]) return a[i] - b[i];
    return 0;
  }

  // ---------- Showing results ---------------------------------------------
  var STATES = { ok: "Looks right", check: "Look at this", skip: "Not checked" };
  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }
  function show(found, name, count) {
    results.textContent = "";
    var looks = found.filter(function (f) { return f.state === "check"; }).length;
    var heading = element("h3", "", "Results for " + name);
    heading.tabIndex = -1;
    results.appendChild(heading);
    results.appendChild(element("p", "pdf-check-summary",
      count + " pages read. " + (looks ? looks + " point" + (looks > 1 ? "s" : "") + " to look at." : "Nothing to look at among these points.") +
      " These checks cover only what is listed here; they are not an OGE review."));
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
        details.appendChild(element("summary", "", "Pages (" + f.pages.length + ")"));
        var pagesList = element("ul");
        f.pages.slice(0, 50).forEach(function (text) { pagesList.appendChild(element("li", "", text)); });
        if (f.pages.length > 50) pagesList.appendChild(element("li", "", "and " + (f.pages.length - 50) + " more"));
        details.appendChild(pagesList);
        item.appendChild(details);
      }
      var source = element("p", "pdf-check-source");
      if (f.cite) {
        source.appendChild(document.createTextNode("Manual " + f.cite + (f.cite2 ? " and " + f.cite2 : "") + ". "));
        if (requirements) {
          var link = element("a", "", "Requirements map");
          link.href = requirements + "#" + f.section;
          source.appendChild(link);
        }
      } else if (f.update) {
        source.appendChild(document.createTextNode("Not an OGE rule. "));
        if (updating) {
          var update = element("a", "", "Update the formatting safely");
          update.href = updating + "#update-the-formatting-safely";
          source.appendChild(update);
        }
      }
      item.appendChild(source);
      list.appendChild(item);
    });
    results.appendChild(list);
    heading.focus();
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
    loadReader().then(function (pdfjs) {
      say("Reading " + name + "…");
      return file.arrayBuffer().then(function (bytes) {
        return pdfjs.getDocument({ data: new Uint8Array(bytes), isEvalSupported: false }).promise;
      });
    }, function (error) {
      throw new Error(error && error.message === "hash" ? "hash" : "reader");
    }).then(function (pdf) {
      var pages = [], next = 1;
      function step() {
        if (next > pdf.numPages) return Promise.resolve();
        say("Reading page " + next + " of " + pdf.numPages + "…");
        return readPage(pdf, next++).then(function (page) { pages.push(page); return step(); });
      }
      return step().then(function () { return pdf.getMetadata(); }).then(function (meta) {
        var found = analyse(pages, meta && meta.info);
        pdf.destroy();
        say("");
        show(found, name, pages.length);
      });
    }).catch(function (error) {
      var message = error && error.message;
      say(message === "hash"
        ? "The PDF reader downloaded from cdnjs did not match its pinned version, so it was not used. Try again later, or use the checklist on the Submitting page."
        : message === "reader"
        ? "The PDF reader could not be downloaded from cdnjs.cloudflare.com. Check your connection and try again, or use the checklist on the Submitting page."
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
