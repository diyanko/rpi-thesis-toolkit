// "Bring your work in" (docs/bring-your-work-in.md): the page part. An extra
// only: with JavaScript off the page explains the same steps by hand.
//
// What is pasted or dropped is read in this browser tab and never sent
// anywhere. The paste is intercepted: its rich text (text/html) is handed to
// core.js as a string, never put into the page, and the plain text goes into
// the box. The LaTeX is shown with textContent. Nothing is stored.
// Works from the website and from the offline guide (file: pages).
(function () {
  "use strict";
  var root = document.querySelector("[data-convert]");
  var script = document.currentScript;
  if (!root || !script || !window.DOMParser) return;
  var base = script.src.replace(/[^/]*$/, "");
  var input = root.querySelector(".convert-input");
  var output = root.querySelector(".convert-output");
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
  var tag = document.createElement("script");
  tag.src = base + "core.js";
  tag.onload = function () {
    core = window.ConvertCore;
    if (!core) return;
    Array.prototype.forEach.call(document.querySelectorAll("[data-convert-nojs]"), function (node) { node.hidden = true; });
    root.hidden = false;
  };
  document.head.appendChild(tag);

  function say(text) { status.textContent = text; }
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

  function show() {
    results.textContent = "";
    if (!result || !result.latex) {
      output.textContent = "";
      source.textContent = "";
      copy.disabled = download.disabled = true;
      return;
    }
    output.textContent = result.latex;
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
    try {
      result = core.convert(pasted || { html: "", text: text }, { chapter: chapter() });
    } catch (error) {
      result = null;
      show();
      say("This text could not be converted. Try a smaller part of it.");
      return;
    }
    show();
    say(result.latex
      ? "Converted, read as " + result.sourceName + "." +
        (result.escaped ? " " + result.escaped + " special character" + (result.escaped > 1 ? "s were" : " was") + " given a backslash." : "")
      : "Nothing to convert was found in what was pasted.");
  }
  function later() {
    clearTimeout(timer);
    timer = setTimeout(run, 150);
  }

  // A paste replaces the box with its plain text; its rich text is kept
  // aside (as a string) until the box is edited.
  function take(data) {
    var html = "", text = "";
    try {
      html = data.getData("text/html") || "";
      text = data.getData("text/plain") || "";
    } catch (error) { /* some browsers refuse one of the types */ }
    if (html.length > LIMIT) html = "";
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
    if (!take(event.clipboardData)) say("Only text can be converted. Pictures go in figures/; the guide's \"Add a figure\" section shows how.");
  });
  input.addEventListener("input", function () {
    if (pasted && input.value !== pasted.shown) pasted = null;  // edited: read the box as it is now
    later();
  });

  // Dropping text works like pasting it; a dropped file is read only if it is
  // plain text (Markdown, text, or tab-separated cells).
  ["dragenter", "dragover"].forEach(function (type) {
    input.addEventListener(type, function (event) {
      event.preventDefault();
      root.classList.add("is-over");
    });
  });
  ["dragleave", "drop"].forEach(function (type) {
    input.addEventListener(type, function () { root.classList.remove("is-over"); });
  });
  input.addEventListener("drop", function (event) {
    event.preventDefault();
    var data = event.dataTransfer;
    if (!data) return;
    var file = data.files && data.files[0];
    if (file) {
      if (!/\.(md|markdown|txt|text|tsv|tab)$/i.test(file.name) || file.size > LIMIT || typeof file.text !== "function") {
        say(file.name + " cannot be read here. Open it, select the text, copy it, and paste it here. Files from Word, Excel, or PowerPoint are not read yet.");
        return;
      }
      file.text().then(function (text) {
        pasted = null;
        input.value = text;
        run();
      }, function () { say(file.name + " could not be read."); });
      return;
    }
    if (!take(data)) say("Only text can be converted.");
  });

  Array.prototype.forEach.call(root.querySelectorAll("input[name=convert-start]"), function (radio) {
    radio.addEventListener("change", run);
  });
  root.querySelector(".convert-example").addEventListener("click", function () {
    pasted = null;
    input.value = SAMPLE;
    run();
  });
  root.querySelector(".convert-clear").addEventListener("click", function () {
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
      selectOutput();
      say("The LaTeX is selected: press Ctrl+C (or Cmd+C on a Mac) to copy it.");
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(result.latex).then(done, fallback);
    else fallback();
  });
  download.addEventListener("click", function () {
    if (!result || !result.latex || !window.Blob || !window.URL || !URL.createObjectURL) {
      say("This browser cannot save the file. Use Copy instead, and paste into a new file.");
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
