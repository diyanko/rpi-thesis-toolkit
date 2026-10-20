// "Copy" buttons on code blocks. An extra only: with JavaScript off there are
// no buttons, and the code can still be selected and copied as usual.
// Where the clipboard is not available (some offline file:// pages), the
// button selects the code instead, ready for Ctrl+C or Cmd+C.
// The link after each section heading also copies the section's address.
(function () {
  "use strict";
  var live = document.createElement("p");   // read out by screen readers
  live.className = "visually-hidden";
  live.setAttribute("aria-live", "polite");
  document.body.appendChild(live);

  Array.prototype.forEach.call(document.querySelectorAll(".heading-link"), function (link) {
    link.addEventListener("click", function () {
      if (!navigator.clipboard || !navigator.clipboard.writeText) return;   // the link still jumps to the section
      navigator.clipboard.writeText(link.href).then(function () {
        link.classList.add("is-copied");
        live.textContent = "Link to this section copied.";
        clearTimeout(link.timer);
        link.timer = setTimeout(function () { link.classList.remove("is-copied"); live.textContent = ""; }, 1500);
      }, function () {});
    });
  });

  var blocks = document.querySelectorAll("pre > code");
  if (!blocks.length) return;

  function show(button, label, message) {
    button.textContent = label;
    button.dataset.icon = "check";
    live.textContent = message;
    clearTimeout(button.timer);
    button.timer = setTimeout(function () { button.textContent = "Copy"; button.dataset.icon = "copy"; live.textContent = ""; }, 1500);
  }

  Array.prototype.forEach.call(blocks, function (code) {
    var pre = code.parentNode, box = document.createElement("div"), button = document.createElement("button");
    var toolbar = document.createElement("div"), label = document.createElement("span");
    var labels = { tex: "LaTeX", latex: "LaTeX", sh: "Terminal command", bibtex: "BibTeX", prompt: "Example prompt", text: "Text" };
    var kind = labels[pre.className] || "Example";
    box.className = "code-block";
    pre.parentNode.insertBefore(box, pre);
    box.appendChild(pre);
    button.type = "button";
    button.className = "copy-button paper-button paper-button-sm";
    button.dataset.icon = "copy";
    button.setAttribute("aria-label", "Copy " + kind.toLowerCase());
    button.textContent = "Copy";
    toolbar.className = "code-toolbar";
    label.textContent = kind;
    toolbar.appendChild(label);
    toolbar.appendChild(button);
    box.insertBefore(toolbar, pre);
    button.addEventListener("click", function () {
      function select() {
        var range = document.createRange(), selection = window.getSelection();
        range.selectNodeContents(code);
        selection.removeAllRanges();
        selection.addRange(range);
        show(button, "Selected", "Text selected. Use your device's Copy command, or Control C or Command C on a keyboard.");
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code.textContent).then(function () {
          show(button, "Copied", "Text copied.");
        }, select);
      } else {
        select();
      }
    });
  });
})();
