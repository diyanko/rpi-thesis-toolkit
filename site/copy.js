// "Copy" buttons on code blocks. An extra only: with JavaScript off there are
// no buttons, and the code can still be selected and copied as usual.
// Where the clipboard is not available (some offline file:// pages), the
// button selects the code instead, ready for Ctrl+C or Cmd+C.
(function () {
  "use strict";
  var blocks = document.querySelectorAll("pre > code");
  if (!blocks.length) return;
  var live = document.createElement("p");   // read out by screen readers
  live.className = "visually-hidden";
  live.setAttribute("aria-live", "polite");
  document.body.appendChild(live);

  function show(button, label, message) {
    button.textContent = label;
    live.textContent = message;
    clearTimeout(button.timer);
    button.timer = setTimeout(function () { button.textContent = "Copy"; live.textContent = ""; }, 1500);
  }

  Array.prototype.forEach.call(blocks, function (code) {
    var pre = code.parentNode, box = document.createElement("div"), button = document.createElement("button");
    box.className = "code-block";
    pre.parentNode.insertBefore(box, pre);
    box.appendChild(pre);
    button.type = "button";
    button.className = "copy-button";
    button.textContent = "Copy";
    box.appendChild(button);
    button.addEventListener("click", function () {
      function select() {
        var range = document.createRange(), selection = window.getSelection();
        range.selectNodeContents(code);
        selection.removeAllRanges();
        selection.addRange(range);
        show(button, "Selected", "Code selected. Press Control C, or Command C on a Mac, to copy it.");
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code.textContent).then(function () {
          show(button, "Copied", "Code copied.");
        }, select);
      } else {
        select();
      }
    });
  });
})();
