// Full-size pictures (diagrams, the class example) open as a dialog
// on the same page: Escape, Close, or a click beside the picture closes it, and
// focus goes back to the link. An extra only: each "View larger" link points at the
// picture file itself, so with JavaScript off (or an old browser) it opens the
// picture on its own, with the browser's Back button to return.
(function () {
  "use strict";
  if (typeof HTMLDialogElement !== "function") return;   // older browsers keep the plain link

  // The picture sits in a scrollable box. When it is wider or taller than the
  // screen (a phone), the box takes keyboard focus so the arrow keys, Page Up/Down,
  // Home and End pan it; otherwise it stays out of the Tab order.
  function pan(dialog) {
    var box = dialog.querySelector(".viewer-pan");
    if (!box) {
      var img = dialog.querySelector("img");
      if (!img) return;
      box = document.createElement("div");
      box.className = "viewer-pan";
      box.setAttribute("role", "region");
      box.setAttribute("aria-label", (dialog.getAttribute("aria-label") || "Picture") + ", scrollable");
      img.parentNode.insertBefore(box, img);
      box.appendChild(img);
    }
    var scrolls = box.scrollWidth > box.clientWidth + 1 || box.scrollHeight > box.clientHeight + 1;
    if (scrolls) box.setAttribute("tabindex", "0"); else box.removeAttribute("tabindex");
    return box;
  }

  function openDialog(id) {
    var dialog = id && document.getElementById(id);
    if (!dialog || dialog.tagName !== "DIALOG") return false;
    if (!dialog.open) dialog.showModal();
    var box = pan(dialog);
    var img = dialog.querySelector("img");
    if (box && !box.hasAttribute("tabindex") && img && !img.complete) {
      img.addEventListener("load", function () { pan(dialog); }, { once: true });
    }
    return true;
  }
  window.addEventListener("resize", function () {
    document.querySelectorAll("dialog.viewer[open]").forEach(pan);
  });

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
    var id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (e) { return; }   // a malformed hash such as "#%"
    if (id.indexOf("view-") === 0 && openDialog(id)) {
      try { history.replaceState(null, "", location.pathname + location.search); } catch (e) { /* file:// pages */ }
    }
  }
  fromHash();
  window.addEventListener("hashchange", fromHash);   // a same-page #view-NAME link

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
