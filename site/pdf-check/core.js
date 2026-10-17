// "Check your PDF" (docs/check-pdf.md): reading and analysis, without any page
// or window code, so scripts/tests/test_pdf_check.py and scripts/check_pdfs.py can
// run it in a headless browser. site/pdf-check/ui.js shows the results.
//
//   read(pdfjs, bytes, progress, job) -> plain data: page sizes, text pieces
//       with their positions, fonts, whether anything is drawn, the bookmarks.
//       job.cancel() (set by read) stops it; the reader and its worker are
//       always released, whether it succeeds, fails, or is cancelled.
//   analyse(data, {current: "0.7.0", rules: RULES}) -> one result per check.
//       RULES is the page's <script type="application/json" id="oge-rules">
//       block (scripts/rules.py), parsed: ui.js passes it in.
//
// Every check measures only what is on the page, whatever program made the
// PDF; only the toolkit-version line reads this class's own wording. A check
// that could not measure something says "unknown" and why; it never passes.
// A check that measured a small difference from the manual's wording, within
// the bounds of the Measurements table (see CONFIRM below), says "differs":
// softer than "check", and never a pass.
// Rule checks name rows of docs/project/requirements.md by id, as
// `rules: ["page-size"]`; ui.js shows each row's citation from RULES. Every
// number they compare with is a row of its Measurements table, read here as
// `measure("margin")`. RULE_IDS and MEASURE_IDS below list every id this file
// uses: build_site.py refuses the page if one is not in the requirements map,
// and analyse() refuses an id that is not in these lists or in RULES, so a
// check cannot quietly use an unknown id. Information checks (fonts, blank
// pages, file size, version) are not manual rules and say so.
//
// Positions are PDF points (72 per inch) from the bottom-left corner of the
// page, as in scripts/check.py.
//
// The PDF reader is Mozilla's pdf.js (Apache-2.0): the legacy build of the
// pdfjs-dist package, which also runs in older browsers, kept unchanged in
// site/pdf-check/pdfjs/ with its LICENSE. To update it, run this in the
// repository folder with the new version (macOS or Linux), then set
// PDFJS_VERSION below to match (build_site.py checks it) and run
// scripts/tests/test_pdf_check.py:
//   cd site/pdf-check/pdfjs && curl -sL https://registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-6.3.289.tgz | tar -xz --strip-components=1 package/LICENSE package/legacy/build/pdf.min.mjs package/legacy/build/pdf.worker.min.mjs && mv legacy/build/* . && rm -r legacy
(function (root) {
  "use strict";
  var PDFJS_VERSION = "6.3.289";
  var INCH = 72;
  // build_site.py reads these two lists as JSON: keep each on one line, in double quotes.
  var RULE_IDS = ["page-size", "front-roman", "body-arabic", "page-number-position", "heading-top", "contents-match", "contents-entries"];
  var MEASURE_IDS = ["paper-width", "paper-height", "paper-tolerance", "margin", "margin-tolerance", "margin-band", "page-number-edge", "page-number-tolerance", "page-number-center", "heading-baseline", "heading-tolerance", "heading-limit", "contents-column", "page-number-near", "page-number-far", "margin-overrun", "heading-far", "heading-size-tolerance"];

  // The numbers the checks compare with, from the Measurements table of the
  // requirements map. TODO(verify): the tolerances there (paper size, margin,
  // page-number distance and center, margin band, heading depth and
  // tolerance, contents column, and the bounds of "differs" below) are this
  // project's choices for measuring, not numbers from the manual.
  function limitsOf(rules) {
    var table = (rules && rules.measures) || {};
    function measure(id) {
      if (MEASURE_IDS.indexOf(id) < 0) throw new Error("PdfCheckCore: the measurement " + id + " is not in MEASURE_IDS.");
      var pt = table[id] && table[id].pt;
      if (typeof pt !== "number" || !isFinite(pt) || pt <= 0) {
        throw new Error("PdfCheckCore: the measurement " + id + " is not a positive number in the rules data (docs/project/requirements.md).");
      }
      return pt;
    }
    return {
      width: measure("paper-width"), height: measure("paper-height"), paper: measure("paper-tolerance"),
      margin: measure("margin"), over: measure("margin-tolerance"), band: measure("margin-band"),
      edge: measure("page-number-edge"), edgeTolerance: measure("page-number-tolerance"),
      center: measure("page-number-center"), heading: measure("heading-limit"),
      baseline: measure("heading-baseline"), baselineTolerance: measure("heading-tolerance"),
      column: measure("contents-column"),
      near: measure("page-number-near"), far: measure("page-number-far"),
      overrun: measure("margin-overrun"), headingFar: measure("heading-far"),
      headingSize: measure("heading-size-tolerance")
    };
  }

  // ---------- Reading a PDF with pdf.js ------------------------------------
  // The operators that put something on the page (text, pictures, lines and
  // shapes). A page without any of them is blank.
  var PAINT = ["showText", "showSpacedText", "nextLineShowText", "nextLineSetSpacingShowText",
    "paintImageXObject", "paintInlineImageXObject", "paintImageMaskXObject",
    "paintImageMaskXObjectGroup", "paintImageXObjectRepeat", "paintImageMaskXObjectRepeat",
    "paintSolidColorImageMask", "paintInlineImageXObjectGroup", "shadingFill", "constructPath",
    "stroke", "closeStroke", "fill", "eoFill", "fillStroke", "eoFillStroke",
    "closeFillStroke", "closeEOFillStroke"];

  function read(pdfjs, bytes, progress, job) {
    var size = bytes.length;
    var task = pdfjs.getDocument({
      data: bytes, isEvalSupported: false, disableFontFace: true, useSystemFonts: false,
      enableXfa: false, stopAtErrors: false, verbosity: 0
    });
    var stopped = false;
    function going() {
      if (!stopped) return;
      var error = new Error("cancelled");
      error.name = "AbortError";
      throw error;
    }
    if (job) job.cancel = function () { stopped = true; return task.destroy(); };
    var paint = {};
    PAINT.forEach(function (name) { if (name in pdfjs.OPS) paint[pdfjs.OPS[name]] = true; });
    var reading = task.promise.then(function (pdf) {
      var data = { fileSize: size, pages: [], info: {}, outline: null };
      var next = 1;
      function step() {
        going();
        if (next > pdf.numPages) return Promise.resolve();
        if (progress) progress(next, pdf.numPages);
        return readPage(pdf, next++, paint, pdfjs.OPS.setFont).then(function (page) {
          data.pages.push(page);
          return step();
        });
      }
      return step().then(function () {
        return pdf.getMetadata().catch(function () { return null; });
      }).then(function (meta) {
        going();
        var info = (meta && meta.info) || {};
        ["Creator", "Producer"].forEach(function (key) {
          if (typeof info[key] === "string") data.info[key] = info[key];
        });
        return readOutline(pdf).catch(function () { return null; });
      }).then(function (outline) {
        going();
        data.outline = outline;
        return data;
      });
    });
    // Release the reader (and its worker) in every case, then hand on the
    // result or the error; a cancelled read always ends as cancelled.
    function release() { return task.destroy().catch(function () {}); }
    return reading.then(function (data) {
      return release().then(function () { going(); return data; });
    }, function (error) {
      return release().then(function () { going(); throw error; });
    });
  }

  function readPage(pdf, number, paint, setFont) {
    return pdf.getPage(number).then(function (page) {
      // A page's UserUnit (1 unless the PDF says otherwise) is the size of
      // its unit in points: positions and sizes here are physical points.
      var view = page.view, unit = page.userUnit > 0 ? page.userUnit : 1;
      var out = { width: (view[2] - view[0]) * unit, height: (view[3] - view[1]) * unit, rotate: page.rotate || 0,
                  items: [], fonts: null, drawn: null };
      return page.getTextContent().then(function (content) {
        content.items.forEach(function (item) {
          if (typeof item.str !== "string" || !item.transform) return;
          var t = item.transform;
          out.items.push({ str: item.str,
                           transform: [t[0] * unit, t[1] * unit, t[2] * unit, t[3] * unit,
                                       (t[4] - view[0]) * unit, (t[5] - view[1]) * unit],
                           width: item.width * unit, height: (item.height || 0) * unit });
        });
        // The operator list names the fonts and shows whether anything is
        // drawn. If it cannot be read, fonts and drawn stay null (unknown).
        return page.getOperatorList().then(function (list) {
          var ids = {}, drawn = false;
          for (var i = 0; i < list.fnArray.length; i++) {
            var fn = list.fnArray[i];
            if (paint[fn]) drawn = true;
            if (fn === setFont && list.argsArray[i]) ids[list.argsArray[i][0]] = true;
          }
          return Promise.all(Object.keys(ids).map(function (id) {
            return fontOf(page.commonObjs, id);
          })).then(function (fonts) {
            out.fonts = fonts;
            out.drawn = drawn;
          });
        }).catch(function () {});
      }).then(function () {
        page.cleanup();
        return out;
      });
    });
  }

  function fontOf(objects, id) {
    return new Promise(function (resolve) {
      var done = false;
      function finish(font) {
        if (done) return;
        done = true;
        var known = font && typeof font === "object" && "missingFile" in font;
        resolve({
          name: String((known && font.name) || id).replace(/^[A-Z]{6}\+/, ""),
          // Type 3 fonts draw their letters inside the PDF, so they count as embedded.
          embedded: known ? Boolean(font.isType3Font || !font.missingFile) : null
        });
      }
      try {
        if (objects.has(id)) finish(objects.get(id));
        else objects.get(id, finish);
      } catch (error) {
        finish(null);
      }
      setTimeout(function () { finish(null); }, 5000);
    });
  }

  // Top-level bookmarks and the page each opens (0-based), or null.
  function readOutline(pdf) {
    return pdf.getOutline().then(function (items) {
      return Promise.all((items || []).map(function (item) {
        var dest = typeof item.dest === "string" ? pdf.getDestination(item.dest) : Promise.resolve(item.dest);
        return dest.then(function (target) {
          if (!Array.isArray(target) || !target.length) return null;
          return typeof target[0] === "number" ? target[0] : pdf.getPageIndex(target[0]);
        }).catch(function () { return null; }).then(function (page) {
          return { title: String(item.title || ""), page: typeof page === "number" ? page : null };
        });
      }));
    });
  }

  // ---------- Small helpers --------------------------------------------------
  function roman(number) {
    var result = "", table = [[1000, "m"], [900, "cm"], [500, "d"], [400, "cd"], [100, "c"],
      [90, "xc"], [50, "l"], [40, "xl"], [10, "x"], [9, "ix"], [5, "v"], [4, "iv"], [1, "i"]];
    table.forEach(function (pair) {
      while (number >= pair[0]) { result += pair[1]; number -= pair[0]; }
    });
    return result;
  }
  var ROMAN = /^m{0,3}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})$/i;
  // A printed page number: digits or a Roman numeral, perhaps "Page 3" or "- 3 -".
  function numberIn(text) {
    var token = text.replace(/^[\s\-–—]+|[\s\-–—]+$/g, "").replace(/^page\s*/i, "");
    if (/^[0-9]{1,4}$/.test(token) || (token && token.length < 12 && ROMAN.test(token))) return token;
    return null;
  }
  function squash(text) { return text.normalize("NFKC").replace(/\s+/g, ""); }
  function plain(text) { return squash(text).toLowerCase().replace(/[^0-9a-zÀ-￿]/g, ""); }
  function inches(points) { return (points / INCH).toFixed(2) + " in"; }
  function plural(count, word, many) { return count + " " + (count === 1 ? word : (many || word + "s")); }
  // "All 12 pages are" or "The only page is".
  function every(count, word, one, more, many) {
    return count === 1 ? "The only " + word + " " + one : "All " + plural(count, word, many) + " " + more;
  }
  function size(width, height) {
    var short = function (points) { return String(Number((points / INCH).toFixed(2))); };
    return short(width) + " × " + short(height) + " in";
  }
  // "PDF pages 1-3, 7" from 0-based indexes.
  function pageList(indexes) {
    var parts = [], start = null, end = null;
    indexes.concat([null]).forEach(function (i) {
      if (i !== null && end !== null && i === end + 1) { end = i; return; }
      if (start !== null) parts.push(start === end ? String(start + 1) : (start + 1) + "-" + (end + 1));
      start = end = i;
    });
    return (indexes.length === 1 ? "PDF page " : "PDF pages ") + parts.join(", ");
  }

  // "8.27 × 11.69 in: PDF pages 1-12", one line per page size.
  function groups(list) {
    var by = {}, keys = [];
    list.forEach(function (p) {
      var key = size(p.width, p.height);
      if (!by[key]) { by[key] = []; keys.push(key); }
      by[key].push(p.index);
    });
    return keys.map(function (key) { return key + ": " + pageList(by[key]); });
  }

  // ---------- Preparing pages --------------------------------------------------
  // Each page: text in the top and bottom margins (the page number), the
  // lines of the text block, top first, and the span of any sideways text.
  function prepare(page, index, limits) {
    var margin = [], body = [], sideways = [], text = false;
    page.items.forEach(function (item) {
      if (!item.str || !item.str.trim()) return;
      text = true;
      var t = item.transform;
      if (Math.abs(t[1]) > 0.01 || Math.abs(t[2]) > 0.01 || t[0] <= 0) {
        // Rotated text (a sideways table): keep how far it spans across the
        // page, from the corners of its box.
        var a = Math.hypot(t[0], t[1]) || 1, b = Math.hypot(t[2], t[3]) || 1;
        var along = item.width / a, up = (item.height || 0) / b;
        var xs = [t[4], t[4] + t[0] * along, t[4] + t[2] * up, t[4] + t[0] * along + t[2] * up];
        var ys = [t[5], t[5] + t[1] * along, t[5] + t[3] * up, t[5] + t[1] * along + t[3] * up];
        sideways.push({ str: item.str, left: Math.min.apply(null, xs), right: Math.max.apply(null, xs),
                        bottom: Math.min.apply(null, ys), top: Math.max.apply(null, ys) });
        return;
      }
      var run = { x: t[4], y: t[5], width: item.width, size: Math.abs(t[3]) || item.height || 0, str: item.str };
      (run.y < limits.band || run.y > page.height - limits.band ? margin : body).push(run);
    });
    margin = lines(margin);
    body = lines(body);
    // A page number set farther in than the margin band (other programs and
    // classes do this): a lone number as the last or first line, set apart
    // from the text block by more than a line.
    if (!margin.some(function (line) { return numberIn(line.text); }) && body.length) {
      var apart = function (line, other) {
        return !other || Math.abs(other.y - line.y) > 1.5 * Math.max(line.size, other.size);
      };
      var n = body.length;
      if (numberIn(body[n - 1].text) && apart(body[n - 1], body[n - 2])) margin.push(body.pop());
      else if (numberIn(body[0].text) && apart(body[0], body[1])) margin.unshift(body.shift());
    }
    return { index: index, width: page.width, height: page.height, text: text, fonts: page.fonts,
             drawn: page.drawn, margin: margin, lines: body, sideways: sideways };
  }
  function lines(runs) {
    runs.sort(function (a, b) { return b.y - a.y || a.x - b.x; });
    var result = [];
    runs.forEach(function (run) {
      var line = result[result.length - 1];
      var big = line ? Math.max(line.size, run.size) : 0;
      // A superscript or subscript (in math, say) is smaller type, raised or
      // lowered by less than about half the line's type size: it belongs to
      // the line, whose baseline stays that of its largest type.
      var near = line && Math.abs(line.y - run.y) <= 2;
      var script = line && !near && Math.min(line.size, run.size) < 0.9 * big && Math.abs(line.y - run.y) <= 0.6 * big;
      if (!near && !script) {
        line = { y: run.y, size: run.size, runs: [] };
        result.push(line);
      } else if (run.size > line.size) {
        line.y = run.y;
        line.size = run.size;
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
      line.x = line.runs[0].x;
      line.right = Math.max.apply(null, line.runs.map(function (r) { return r.x + r.width; }));
      line.size = Math.max.apply(null, line.runs.map(function (r) { return r.size; }));
      line.y = Math.min.apply(null, line.runs.filter(function (r) { return r.size >= 0.9 * line.size; })
        .map(function (r) { return r.y; }));
    });
    return result;
  }

  // The page number: a margin line that is a number, or the number at either
  // end of a running header or footer. Sideways numbers (a landscape page)
  // count too, with no position.
  function pageNumber(page, limits) {
    for (var k = 0; k < page.margin.length; k++) {
      var line = page.margin[k], runs = line.runs, found = null;
      var text = numberIn(line.text);
      if (text) found = { text: text, x: line.x, right: line.right, y: line.y, size: line.size, runs: runs };
      else {
        [runs[runs.length - 1], runs[0]].some(function (run) {
          var t = numberIn(run.str);
          if (t) found = { text: t, x: run.x, right: run.x + run.width, y: run.y, size: run.size, runs: [run] };
          return Boolean(t);
        });
      }
      if (found) return place(found, page, limits);
    }
    // Only a sideways number wholly outside a side margin is a page number;
    // other sideways numbers (a cell of a sideways table) are ordinary text.
    for (k = 0; k < page.sideways.length; k++) {
      var side = page.sideways[k], number = numberIn(side.str);
      if (number && (side.right < limits.margin || side.left > page.width - limits.margin)) {
        return { text: number, place: "sideways", side: side, runs: [] };
      }
    }
    return page.margin.length ? { text: null, margin: page.margin.map(function (l) { return l.text; }).join(" / ") } : null;
  }
  function place(found, page, limits) {
    var center = (found.x + found.right) / 2, w = page.width, h = page.height;
    var vertical = found.y < h / 2 ? "bottom" : "top";
    var horizontal = Math.abs(center - w / 2) < limits.center ? "center"
      : center < w / 3 ? "left" : center > 2 * w / 3 ? "right" : "off center";
    // Measured to the baseline, as the page-number-edge measurement says.
    var distance = vertical === "bottom" ? found.y : h - found.y;
    found.place = found.x < 0 || found.right > w || found.y < 0 || found.y > h ? "outside the page"
      : vertical + " " + horizontal;
    found.distance = distance;
    found.edgeOk = Math.abs(distance - limits.edge) <= limits.edgeTolerance;
    return found;
  }

  // ---------- Headings and the contents ---------------------------------------
  var LEADERS = /(?:\s*\.){3,}/;
  var ENTRY = /^(.*?)(?:\s*\.)*\s*([0-9]+|[ivxlcdm]+)$/;
  // A level-1 heading in capitals, such as "1. INTRODUCTION", "A. DATA", or
  // "REFERENCES": no dot leaders, and not a
  // numbered lower level such as "1.1 METHODS" or "A.2 DATA".
  // A title may end in a number, such as a year: the page number is in the
  // margin, not on the heading's line.
  function isHeading(text) {
    if (!text || LEADERS.test(text)) return false;
    if (/^(?:[0-9]+|[A-Z])\.[0-9]/.test(text)) return false;
    return (/^(?:[0-9]+|[A-Z])\.\s?[A-Z]/.test(text) || /[A-Z]{4,}/.test(text)) && !/[a-z]/.test(text);
  }
  function top(page) { return page.lines.length ? page.lines[0].text : ""; }
  function entryLike(text) {
    var match = ENTRY.exec(text);
    return Boolean(match && (LEADERS.test(text) || /[0-9]$/.test(text)));
  }
  // The right end of a contents page's page-number column: the farthest
  // right of its lines that end in a number.
  function numberColumn(page) {
    var ends = page.lines.filter(function (l) { return ENTRY.test(l.text); }).map(function (l) { return l.right; });
    return ends.length ? Math.max.apply(null, ends) : null;
  }
  // A heading's text for comparing a contents entry with a page: no spaces
  // and no hyphens (so a title may wrap, or be hyphenated, at different
  // places in each), no "Chapter" or
  // "Appendix" label before its number or letter, and no period or colon
  // right after that number or letter. Many classes, RPI's official template
  // among them, print "CHAPTER 1" over "INTRODUCTION" on the page and
  // "1. INTRODUCTION" in the contents: both give "1INTRODUCTION".
  function key(text) {
    return squash(text).replace(/[-\u2010\u00ad]/g, "").replace(/^(?:chapter|appendix)(?=[0-9A-Z])/i, "")
      .replace(/^([0-9]+|[A-Z])[.:](?=[^0-9])/, "$1");
  }
  // `want` is the whole text of 1 to 5 lines in a row, starting at the first
  // line only if `first` is set: a heading, not a phrase in a paragraph.
  function sameLines(want, texts, first) {
    want = key(want);
    return texts.some(function (_, start) {
      return (!first || start === 0) && [1, 2, 3, 4, 5].some(function (k) {
        return start + k <= texts.length && key(texts.slice(start, start + k).join(" ")) === want;
      });
    });
  }

  // A small measured difference from the manual's wording on a point listed
  // under "Needs OGE confirmation" in docs/project/requirements.md is
  // reported as "differs", not "check"; the summary names both values.
  var CONFIRM = "If you are unsure whether this is acceptable, confirm it with OGE.";

  // ---------- The checks ---------------------------------------------------------
  function analyse(data, options) {
    options = options || {};
    var limits = limitsOf(options.rules);
    var pages = data.pages.map(function (page, index) { return prepare(page, index, limits); });
    var count = pages.length;
    var found = [];
    // The body text size: the type size of most lines. A level-1 heading is
    // never smaller (manual §2.3), so capitals in smaller type at the top of
    // a page, such as the labels inside a figure, open nothing.
    var typeCount = {}, bodySize = 0;
    pages.forEach(function (p) {
      p.lines.forEach(function (l) {
        var k = l.size.toFixed(1);
        typeCount[k] = (typeCount[k] || 0) + 1;
        if (!bodySize || typeCount[k] > typeCount[bodySize.toFixed(1)]) bodySize = Number(k);
      });
    });
    function opens(p) {
      return p.lines.length > 0 && isHeading(top(p)) && p.lines[0].size >= bodySize - limits.headingSize;
    }
    var anyText = pages.some(function (p) { return p.text; });
    var NO_TEXT = "No text could be read from any page. The PDF may be a scan, or its text may have been turned into shapes; check this point by eye.";

    // Paper size: US letter, upright or sideways.
    var letter = function (p) {
      var a = Math.min(p.width, p.height), b = Math.max(p.width, p.height);
      return Math.abs(a - limits.width) <= limits.paper && Math.abs(b - limits.height) <= limits.paper;
    };
    var wrong = pages.filter(function (p) { return !letter(p); });
    var LETTER = size(limits.width, limits.height);
    found.push({
      id: "paper", title: "Paper size: US letter", rules: ["page-size"],
      state: !count ? "unknown" : wrong.length ? "check" : "ok",
      summary: !count ? "The PDF has no pages."
        : wrong.length ? wrong.length + " of " + plural(count, "page") + " are not " + LETTER + "."
        : every(count, "page", "is", "are") + " " + LETTER + ".",
      pages: groups(wrong)
    });

    // The same page size throughout (upright and sideways pages count alike).
    var sizes = {}, order = [];
    pages.forEach(function (p) {
      var key = size(Math.min(p.width, p.height), Math.max(p.width, p.height));
      if (!sizes[key]) { sizes[key] = []; order.push(key); }
      sizes[key].push(p.index);
    });
    order.sort(function (a, b) { return sizes[b].length - sizes[a].length; });
    found.push({
      id: "same-size", title: "The same page size on every page", rules: ["page-size"],
      state: !count ? "unknown" : order.length > 1 ? "check" : "ok",
      summary: !count ? "The PDF has no pages."
        : order.length > 1 ? "The pages come in " + order.length + " sizes; most are " + order[0] + "."
        : every(count, "page", "is", "are") + " " + order[0] + ".",
      pages: order.length > 1 ? order.slice(1).map(function (key) {
        return key + ": " + pageList(sizes[key]);
      }) : []
    });

    var numbers = pages.map(function (page) { return pageNumber(page, limits); });
    // The class writes its name and version into the PDF properties.
    var creator = (data.info && data.info.Creator) || "";
    var version = /rpi-thesis (\d{4}\/\d\d\/\d\d) v(\d+\.\d+\.\d+)/.exec(creator);
    // The contents page: the first of the first 40 pages that starts with
    // CONTENTS or TABLE OF CONTENTS.
    var tocStart = -1, tocEnd = -1, i;
    for (i = 0; i < Math.min(count, 40); i++) {
      if (/^(TABLE OF )?CONTENTS$/i.test(top(pages[i]))) { tocStart = i; break; }
    }
    var numbered = numbers.filter(function (n) { return n && n.text; }).length;

    // Where the body starts: the page that opens Chapter 1, or else the
    // first page numbered 1.
    var body = -1;
    for (i = 1; i < count && body < 0; i++) {
      var first = top(pages[i]);
      if (/^(1\.\s?[A-Z]|CHAPTER 1\b)/.test(first) && opens(pages[i])) body = i;
    }
    for (i = 1; i < count && body < 0; i++) {
      if (numbers[i] && numbers[i].text === "1") body = i;
    }
    var label = function (i) {
      if (i === 0) return "i";
      if (body < 0 || i < body) return roman(i + 1);
      return String(i - body + 1);
    };
    var where = function (i) {
      return "PDF page " + (i + 1) + (i > 0 && numbers[i] && numbers[i].text ? " (printed " + numbers[i].text + ")" : "");
    };

    // Numbering: title page unnumbered, then ii, iii, ... and 1, 2, ...
    var numbering = [], notes = [];
    if (numbers[0] && numbers[0].text) numbering.push("PDF page 1 (title page) shows \"" + numbers[0].text + "\" in the margin; the title page counts as i but shows no number.");
    if (body < 0) numbering.push("No page is numbered 1, so the start of Chapter 1 was not found.");
    if (body >= 0 && body <= tocStart) numbering.push(where(body) + " is numbered 1, but the contents starts on or after it; the front matter, contents included, is numbered ii, iii, ...");
    for (i = 1; i < count; i++) {
      var n = numbers[i];
      if (!n || !n.text) {
        var absent = "PDF page " + (i + 1) + ": no page number found (expected " + label(i) + ")" +
          (n && n.margin ? "; the margin has \"" + n.margin.slice(0, 60) + "\"." : ".");
        // Libraries and ProQuest add an unnumbered notice page to the end of
        // the copies they distribute: a last page alone without a number is a
        // note, not a point to look at.
        if (i === count - 1 && i > 1 && numbers[i - 1] && numbers[i - 1].text) {
          notes.push(absent + " It is the last page; a notice page that a library or ProQuest adds has no number, but a page of your thesis needs one.");
        } else numbering.push(absent);
      }
      else if (n.text !== label(i)) numbering.push("PDF page " + (i + 1) + ": shows \"" + n.text + "\", expected " + label(i) + ".");
    }
    found.push({
      id: "numbering", title: "Page numbering: roman front matter, then 1 at Chapter 1",
      rules: ["front-roman", "body-arabic"],
      state: !anyText ? "unknown" : numbering.length ? "check" : "ok",
      summary: !anyText ? NO_TEXT
        : !numbered ? "No page numbers were found as text on any page. If your PDF shows them, they may be pictures; check them by eye."
        : numbering.length ? plural(numbering.length, "point") + " to look at."
        : "Title page unnumbered; front matter " + (body > 1 ? "ii to " + roman(body) : "none") + "; Chapter 1 starts on PDF page " + (body + 1) + " as page 1." +
          (notes.length ? " The last page has no number: see the details." : ""),
      pages: anyText ? numbering.concat(notes) : []
    });

    // Level-1 openings, from three sources: a heading in capitals at the top
    // of the page, a top-level bookmark whose title starts the page, and the
    // contents entries (below).
    var opening = {}, own = {};
    pages.forEach(function (p, i) { if (i > 0 && opens(p)) opening[i] = own[i] = top(p); });
    (data.outline || []).forEach(function (mark) {
      if (mark.page === null || mark.page <= 0 || mark.page >= count) return;
      var p = pages[mark.page], want = plain(mark.title);
      var start = plain(p.lines.slice(0, 3).map(function (l) { return l.text; }).join(" "));
      if (want && start.indexOf(want) >= 0) opening[mark.page] = own[mark.page] = own[mark.page] || mark.title;
    });

    // Contents: entries and the pages they point to. Entries name printed
    // page numbers; when a number is printed twice, an Arabic one means the
    // body page.
    var byLabel = {};
    numbers.forEach(function (n, i) {
      if (n && n.text && (!(n.text in byLabel) || (/^[0-9]+$/.test(n.text) && i >= body && byLabel[n.text] < body))) byLabel[n.text] = i;
    });
    pages.forEach(function (p, i) { if (!(numbers[i] && numbers[i].text) && !(label(i) in byLabel)) byLabel[label(i)] = i; });
    var entries = [];
    if (tocStart >= 0) {
      var pending = "", column = numberColumn(pages[tocStart]);
      // Where the first contents page's entries start, and their type size:
      // a later page may begin with the first line of an entry that wraps,
      // which has no page number and may look like a heading.
      var entryLines = pages[tocStart].lines.slice(1).filter(function (l) { return entryLike(l.text); });
      var left = entryLines.length ? Math.min.apply(null, entryLines.map(function (l) { return l.x; })) : null;
      var entrySize = entryLines.length ? Math.max.apply(null, entryLines.map(function (l) { return l.size; })) : 0;
      var wrapped = function (line) {
        return left !== null && Math.abs(line.x - left) <= 2 && line.size <= entrySize + limits.headingSize;
      };
      for (i = tocStart; i < count; i++) {
        var p = pages[i];
        // The number ending a line is a page number only after dot leaders
        // or in the page-number column (that of the first contents page);
        // otherwise the title goes on (it may end in a year) on the next line.
        var atColumn = function (line) { return column !== null && column - line.right <= limits.column; };
        var first = p.lines[0];
        // A later page continues the contents only if most of its lines are entries.
        if (i > tocStart && ((opens(p) && !(ENTRY.test(first.text) && atColumn(first)) && !wrapped(first)) ||
            p.lines.filter(function (l) { return entryLike(l.text); }).length * 2 < p.lines.length)) break;
        tocEnd = i;
        p.lines.forEach(function (line, k) {
          if (i === tocStart && k === 0) return;
          if (/^page$/i.test(line.text)) return;
          var match = ENTRY.exec(line.text);
          if (match && (LEADERS.test(line.text) || atColumn(line))) {
            var title = (pending + match[1]).trim();
            if (title) entries.push({ title: title, label: match[2] });  // a lone number names no heading
            pending = "";
          } else if (!pending && /^[0-9]+$/.test(line.text)) {
            // A number alone (a stray superscript, say) starts no entry.
          } else {
            pending += line.text + " ";
          }
        });
      }
      entries.forEach(function (entry) {
        entry.level1 = isHeading(entry.title);
        entry.target = byLabel[entry.label];
        if (entry.level1 && entry.target !== undefined && entry.target > 0) opening[entry.target] = opening[entry.target] || entry.title;
      });
    }
    var openings = Object.keys(opening).map(Number).sort(function (a, b) { return a - b; });

    // Page-number position: bottom center on front matter and level-1
    // openings, top right elsewhere.
    var placed = [], positioned = 0, away = {}, awayOrder = [], farOff = [];
    for (i = 1; i < count; i++) {
      n = numbers[i];
      if (!n || !n.text) continue;
      positioned++;
      if (n.place === "sideways") {
        placed.push(where(i) + ": the number is turned sideways (a landscape page); check its position by eye.");
        continue;
      }
      var want = (body < 0 || i < body || opening[i]) ? "bottom center" : "top right";
      var why = opening[i] ? "a level-1 heading starts here" : i < body || body < 0 ? "front matter" : "body page";
      if (n.place !== want) {
        placed.push(where(i) + ": expected " + want + " (" + why + "), found " + n.place +
          (n.place === "outside the page" ? "." : ", " + inches(n.distance) + " from the " + n.place.split(" ")[0] + " edge."));
      }
      // The distance from the nearer edge, measured wherever the number is.
      if (n.place === "outside the page" || n.edgeOk) continue;
      var edge = n.place.split(" ")[0];
      if (n.distance < limits.near || n.distance > limits.far) {
        farOff.push(where(i) + ": " + inches(n.distance) + " from the " + edge + " edge; the manual asks for " + inches(limits.edge) + ".");
      } else {
        var at = inches(n.distance) + " from the " + edge + " edge";
        if (!away[at]) { away[at] = []; awayOrder.push(at); }
        away[at].push(i);
      }
    }
    found.push({
      id: "position", title: "Page-number position", rules: ["page-number-position"],
      state: !anyText || !positioned ? "unknown" : placed.length ? "check" : "ok",
      summary: !anyText ? NO_TEXT
        : !positioned ? "No page numbers were found as text after the title page, so their position could not be measured."
        : placed.length ? plural(placed.length, "page") + " with the number somewhere else."
        : "Bottom center on front matter and level-1 openings, top right on other pages.",
      pages: placed
    });
    var awayPages = awayOrder.map(function (at) { return at + ": " + pageList(away[at]) + "."; });
    found.push({
      id: "distance", title: "Page-number distance from the edge", rules: ["page-number-position"],
      state: !anyText || !positioned ? "unknown" : farOff.length ? "check" : awayOrder.length ? "differs" : "ok",
      summary: !anyText ? NO_TEXT
        : !positioned ? "No page numbers were found as text after the title page, so their distance from the edge could not be measured."
        : farOff.length ? plural(farOff.length, "page") + " with the number far from the " + inches(limits.edge) + " the manual asks for."
        : awayOrder.length ? "The manual asks for " + inches(limits.edge) + " from the edge; this PDF has " +
          awayOrder.join(", ") + ". " + CONFIRM
        : every(positioned, "page number", "is", "are") + " " + inches(limits.edge) + " from the edge.",
      pages: farOff.concat(awayPages)
    });

    // Level-1 headings start at the top margin. On a PDF this class made,
    // at the class's own baseline; on any other PDF (other fonts and
    // settings), no lower than heading-limit. TODO(verify): heading-limit and
    // heading-tolerance are this project's choices, not numbers from the manual.
    var low = [], lower = [], deepest = 0, measured = 0;
    openings.forEach(function (index) {
      var p = pages[index];
      if (!p.lines.length) return;
      measured++;
      var depth = p.height - p.lines[0].y;
      var start = where(index) + ": \"" + p.lines[0].text.slice(0, 60) + "\" starts " + inches(depth) + " from the top edge";
      if (version && Math.abs(depth - limits.baseline) > limits.baselineTolerance) {
        low.push(start + "; this class puts it " + inches(limits.baseline) + " from the top edge.");
      } else if (!version && depth > limits.headingFar) {
        low.push(start + ".");
      } else if (!version && depth > limits.heading) {
        lower.push(start + ".");
        deepest = Math.max(deepest, depth);
      }
    });
    found.push({
      id: "headings", title: "Level-1 headings at the top margin", rules: ["heading-top"],
      state: !anyText ? "unknown" : !measured ? "unknown" : low.length ? "check" : lower.length ? "differs" : "ok",
      summary: !anyText ? NO_TEXT
        : !measured ? "No level-1 headings were recognized: the checker looks for headings in capitals, PDF bookmarks, and contents entries in capitals."
        : low.length ? low.length + " of " + plural(measured, "heading page") + (version ? " do not start at the class's heading position." : " start lower than the top margin.")
        : lower.length ? "The manual asks for level-1 headings at the top margin; " + lower.length + " of " + plural(measured, "heading page") +
          " start a little lower, down to " + inches(deepest) + " from the top edge. " + CONFIRM
        : every(measured, "page", "that starts", "that start") + " with a level-1 heading " + (measured === 1 ? "starts" : "start") + " it at the top margin" +
          (version ? ", where this class puts it." : "."),
      pages: low.concat(lower)
    });

    // Text inside the side margins. Pictures and drawings are not measured.
    // Running headers and footers count too; only the page number is left out.
    var outside = [], slight = [], widest = 0;
    pages.forEach(function (p) {
      var worst = 0, number = numbers[p.index] || {};
      p.lines.concat(p.margin).forEach(function (line) {
        line.runs.forEach(function (run) {
          if ((number.runs || []).indexOf(run) >= 0) return;
          worst = Math.max(worst, limits.margin - run.x, run.x + run.width - (p.width - limits.margin));
        });
      });
      p.sideways.forEach(function (run) {
        if (run === number.side) return; // the page number of a landscape page
        worst = Math.max(worst, limits.margin - run.left, run.right - (p.width - limits.margin));
      });
      if (worst <= limits.over) return;
      var point = where(p.index) + ": text reaches " + inches(worst) + " into the side margin.";
      if (worst > limits.overrun) outside.push(point);
      else { slight.push(point); widest = Math.max(widest, worst); }
    });
    found.push({
      id: "margins", title: "Text inside the " + String(Number((limits.margin / INCH).toFixed(2))) + " in side margins",
      rules: ["page-size"],
      state: !anyText ? "unknown" : outside.length ? "check" : slight.length ? "differs" : "ok",
      summary: !anyText ? NO_TEXT
        : outside.length ? plural(outside.length + slight.length, "page") + " with text in a side margin. Long lines, equations, URLs, and wide tables are the usual cause."
        : slight.length ? "The manual asks for " + String(Number((limits.margin / INCH).toFixed(2))) + " in side margins; on " +
          plural(slight.length, "page") + " text reaches slightly into one, up to " + inches(widest) +
          ", usually a long line, equation, or URL. " + CONFIRM
        : "No text crosses the left or right margin. Figures and pictures were not measured; check them by eye.",
      pages: outside.concat(slight).sort(function (a, b) { return parseInt(a.slice(9), 10) - parseInt(b.slice(9), 10); })
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
      var ok = /^APPENDI(CES|X)$/.test(entry.title) ? isHeading(text[0]) : sameLines(want, text, entry.level1);
      if (!ok) {
        mismatch.push("\"" + entry.title + "\" (page " + entry.label + "): " +
          (entry.level1 ? "that page starts with \"" + (text[0] || "").slice(0, 60) + "\"." : "not found on that page."));
      }
    });
    var NO_TOC = "No page starting with CONTENTS or TABLE OF CONTENTS was found in the first 40 pages.";
    found.push({
      id: "contents", title: "Contents entries match the headings", rules: ["contents-match"],
      state: tocStart < 0 || !entries.length ? "unknown" : mismatch.length ? "check" : "ok",
      summary: !anyText ? NO_TEXT
        : tocStart < 0 ? NO_TOC
        : !entries.length ? "The contents page was found, but no entries could be read."
        : mismatch.length ? mismatch.length + " of " + plural(entries.length, "entry", "entries") + " differ from the page they point to."
        : every(entries.length, "entry", "matches", "match", "entries") + " the text on the page " + (entries.length === 1 ? "it points" : "they point") + " to.",
      pages: mismatch
    });

    // Every level-1 heading after the contents is listed in it.
    // An entry lists the heading only if it is that heading: the page's
    // first lines, or the bookmark's title, perhaps after its number ("1
    // Introduction" for "Introduction"). Another entry for the same page,
    // such as its first section, does not.
    function lists(entry, index) {
      if (entry.target !== index) return false;
      if (sameLines(squash(entry.title), pages[index].lines.map(function (l) { return l.text; }), true)) return true;
      var head = plain(String(own[index])), title = plain(entry.title);
      return Boolean(head) && (title === head ||
        (title.slice(-head.length) === head && /^(?:[0-9]+|[a-z])$/.test(title.slice(0, -head.length))));
    }
    var after = Object.keys(own).map(Number).filter(function (index) { return index > tocEnd; }).sort(function (a, b) { return a - b; });
    var unlisted = after.filter(function (index) {
      return !entries.some(function (entry) { return lists(entry, index); });
    }).map(function (index) {
      return where(index) + ": \"" + String(own[index]).slice(0, 60) + "\" has no contents entry pointing to this page.";
    });
    found.push({
      id: "listed", title: "Every level-1 heading is in the contents", rules: ["contents-entries"],
      state: tocStart < 0 || !entries.length || !after.length ? "unknown" : unlisted.length ? "check" : "ok",
      summary: !anyText ? NO_TEXT
        : tocStart < 0 ? NO_TOC
        : !entries.length ? "The contents page was found, but no entries could be read."
        : !after.length ? "No level-1 headings after the contents were recognized (headings in capitals or PDF bookmarks)."
        : unlisted.length ? unlisted.length + " of " + plural(after.length, "level-1 heading") + " are not in the contents."
        : every(after.length, "level-1 heading", "after the contents has", "after the contents have") + " an entry. Lower-level headings were not checked.",
      pages: unlisted
    });

    // Fonts embedded in the PDF. TODO(verify): no row of the requirements
    // map makes embedded fonts an OGE rule, so this is information only.
    var fonts = {}, fontOrder = [], fontsUnread = [];
    pages.forEach(function (p) {
      if (p.fonts === null || p.fonts === undefined) { fontsUnread.push(p.index); return; }
      p.fonts.forEach(function (font) {
        var key = font.name + "\u0000" + font.embedded;
        if (!fonts[key]) { fonts[key] = { name: font.name, embedded: font.embedded, pages: [] }; fontOrder.push(key); }
        if (fonts[key].pages[fonts[key].pages.length - 1] !== p.index) fonts[key].pages.push(p.index);
      });
    });
    var missing = fontOrder.map(function (k) { return fonts[k]; }).filter(function (f) { return f.embedded === false; });
    var unsure = fontOrder.map(function (k) { return fonts[k]; }).filter(function (f) { return f.embedded === null; });
    var fontPages = missing.map(function (f) { return f.name + ": not embedded; used on " + pageList(f.pages) + "."; })
      .concat(unsure.map(function (f) { return f.name + ": could not tell; used on " + pageList(f.pages) + "."; }));
    if (fontsUnread.length) fontPages.push("Fonts could not be read on " + pageList(fontsUnread) + ".");
    found.push({
      id: "fonts", title: "Fonts embedded in the PDF", info: true,
      state: missing.length ? "check" : (fontsUnread.length || unsure.length) ? "unknown" : "ok",
      summary: missing.length ? missing.length + (missing.length === 1 ? " font is" : " fonts are") + " not embedded: " + missing.map(function (f) { return f.name; }).join(", ") + ". The PDF may then look different on another computer."
        : fontsUnread.length || unsure.length ? "Some fonts could not be read, so this could not be told for every page."
        : fontOrder.length ? every(fontOrder.length, "font", "is", "are") + " embedded."
        : "The PDF uses no fonts.",
      pages: fontPages
    });

    // Blank pages: no text and nothing drawn.
    var blank = [], blankUnknown = [];
    pages.forEach(function (p) {
      if (p.text) return;
      if (p.drawn === false) blank.push(p.index);
      else if (p.drawn !== true) blankUnknown.push(p.index);
    });
    found.push({
      id: "blank", title: "Blank pages", info: true,
      state: blank.length ? "check" : blankUnknown.length ? "unknown" : "ok",
      summary: blank.length ? pageList(blank) + (blank.length === 1 ? " has" : " have") + " no text and nothing drawn on it. A blank page is often left over from a page break; check that you meant it."
        : blankUnknown.length ? "Whether " + pageList(blankUnknown) + " " + (blankUnknown.length === 1 ? "is" : "are") + " blank could not be told."
        : "No blank pages.",
      pages: []
    });

    // File size, for information. TODO(verify): the requirements map sets no
    // file-size limit; check OGE's current submission page for any upload limit.
    var bytes = data.fileSize || 0;
    found.push({
      id: "size", title: "File size", info: true, state: "info",
      summary: (bytes >= 1e6 ? (bytes / 1e6).toFixed(1) + " MB" : Math.max(1, Math.round(bytes / 1e3)) + " kB") +
        " (" + String(bytes).replace(/\B(?=(\d{3})+(?!\d))/g, ",") + " bytes), " + plural(count, "page") + ". The requirements map lists no file-size limit.",
      pages: []
    });

    // Toolkit version (version and creator are read above).
    var current = options.current || "";
    var older = version && current && compare(version[2], current) < 0;
    var newer = version && current && compare(version[2], current) > 0;
    found.push({
      id: "version", title: "Toolkit version in the PDF", info: true, update: true,
      state: !version ? "info" : older ? "check" : "ok",
      summary: !version
        ? (creator ? "Made with \"" + creator.slice(0, 80) + "\", not the toolkit class, so there is no version to compare." : "The PDF names no creator, so there is no version to compare.")
        : "Made with rpi-thesis v" + version[2] + " (" + version[1] + ")" +
          (older ? "; this guide offers v" + current + ". Read its change notes before you submit."
            : newer ? "; newer than v" + current + ", the version this guide offers."
            : current ? ", the version this guide offers." : "."),
      pages: []
    });
    var known = (options.rules && options.rules.rules) || {};
    found.forEach(function (f) {
      (f.rules || []).forEach(function (id) {
        if (RULE_IDS.indexOf(id) < 0) throw new Error("PdfCheckCore: the rule " + id + " is not in RULE_IDS.");
        if (!known[id]) throw new Error("PdfCheckCore: the rule " + id + " is not in the rules data (docs/project/requirements.md).");
      });
    });
    return found;
  }
  function compare(a, b) {
    a = a.split(".").map(Number); b = b.split(".").map(Number);
    for (var i = 0; i < 3; i++) if (a[i] !== b[i]) return a[i] - b[i];
    return 0;
  }

  root.PdfCheckCore = { PDFJS_VERSION: PDFJS_VERSION, RULE_IDS: RULE_IDS, MEASURE_IDS: MEASURE_IDS,
                        read: read, analyse: analyse };
})(typeof self !== "undefined" ? self : this);
