// Full-size pictures (diagrams, anatomy pages, the class example) open as a dialog
// on the same page: Escape, Close, or a click beside the picture closes it, and
// focus goes back to the link. An extra only: each "View larger" link points at the
// picture file itself, so with JavaScript off (or an old browser) it opens the
// picture on its own, with the browser's Back button to return.
(function () {
  "use strict";
  if (typeof HTMLDialogElement !== "function") return;   // older browsers keep the plain link

  function openDialog(id) {
    var dialog = id && document.getElementById(id);
    if (!dialog || dialog.tagName !== "DIALOG") return false;
    if (!dialog.open) dialog.showModal();
    return true;
  }

  // "View larger" shows only where the dialog would really be larger: a drawing
  // already shown near its full-size width does not need the link. On phones a
  // drawing with a narrow version always keeps it: the dialog shows the wide
  // drawing, which can be panned.
  function tidy() {
    var phone = window.matchMedia("(max-width: 600px)").matches;
    document.querySelectorAll("figure.diagram").forEach(function (figure) {
      var img = figure.querySelector(":scope > img, :scope > picture > img");
      var link = figure.querySelector(":scope > .diagram-open");
      if (!img || !link || !img.naturalWidth) return;
      if (phone && figure.classList.contains("has-narrow")) { link.hidden = false; return; }
      var shown = img.getBoundingClientRect().width;
      var ratio = img.naturalHeight / img.naturalWidth;
      var large = Math.min(window.innerWidth - 96, 1400, (window.innerHeight - 96) / ratio);
      link.hidden = shown > 0 && shown >= large * 0.85;
    });
  }
  window.addEventListener("load", tidy);
  window.addEventListener("resize", function () { clearTimeout(tidy.timer); tidy.timer = setTimeout(tidy, 150); });

  // An old address such as page.html#view-NAME opens its picture, then the hash goes.
  function fromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (id.indexOf("view-") === 0 && openDialog(id)) {
      history.replaceState(null, "", location.pathname + location.search);
    }
  }
  fromHash();

  document.addEventListener("click", function (event) {
    // Modified clicks keep the browser's new-tab, new-window and download actions.
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (!event.target.closest) return;
    var link = event.target.closest("a[data-viewer]");
    if (link) {
      if (openDialog(link.getAttribute("data-viewer"))) event.preventDefault();
      return;
    }
    var close = event.target.closest("dialog[open] .viewer-close");
    if (close) {
      event.preventDefault();
      close.closest("dialog").close();
    } else if (event.target.matches("dialog.viewer[open]")) {
      event.target.close();   // a click beside the picture
    }
  });
})();
