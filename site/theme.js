// Apply a saved appearance before the stylesheet paints. Without this optional
// script, CSS follows the device setting. Storage may be unavailable offline.
(function () {
  "use strict";
  var key = "rpi-thesis-appearance";
  var root = document.documentElement;
  var control, toggle, menu;

  function pictures(theme) {
    document.querySelectorAll("[data-theme-asset]").forEach(function (picture) {
      var attribute = picture.getAttribute("data-theme-asset");
      var source = picture.getAttribute("data-theme-" + theme);
      if (source && (attribute === "src" || attribute === "srcset" || attribute === "href")) {
        if (picture.getAttribute(attribute) !== source) picture.setAttribute(attribute, source);
      }
    });
    // WebKit does not always re-pick a <picture> image when only a <source>
    // changes; setting the <img> src again makes it choose.
    document.querySelectorAll("picture > img").forEach(function (img) {
      var src = img.getAttribute("src");
      if (src) img.src = src;
    });
  }

  function apply(value) {
    var theme = value === "light" || value === "dark" ? value : "system";
    if (theme === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", theme);
    pictures(theme);
    if (control) {
      control.setAttribute("data-mode", theme);
      var label = theme.charAt(0).toUpperCase() + theme.slice(1);
      toggle.setAttribute("aria-label", "Appearance: " + label);
      toggle.title = "Change appearance (" + label + ")";
      control.querySelectorAll("[data-theme-choice]").forEach(function (button) {
        button.setAttribute("aria-pressed", String(button.getAttribute("data-theme-choice") === theme));
      });
    }
  }

  try { apply(localStorage.getItem(key)); }
  catch (error) { apply("system"); }

  function ready() {
    control = document.querySelector(".appearance");
    if (!control) return;
    toggle = control.querySelector(".appearance-toggle");
    menu = control.querySelector(".appearance-menu");
    apply(root.getAttribute("data-theme"));
    function close(restoreFocus) {
      menu.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
      if (restoreFocus) toggle.focus();
    }
    toggle.addEventListener("click", function () {
      var opening = menu.hidden;
      menu.hidden = !opening;
      toggle.setAttribute("aria-expanded", String(opening));
      if (opening) menu.querySelector('[aria-pressed="true"]').focus();
    });
    control.querySelectorAll("[data-theme-choice]").forEach(function (button) {
      button.addEventListener("click", function () {
        var choice = button.getAttribute("data-theme-choice");
        apply(choice);
        try {
          if (choice === "system") localStorage.removeItem(key);
          else localStorage.setItem(key, choice);
        } catch (error) { /* Changing this page still works without storage. */ }
        close(true);
      });
    });
    // pointerdown, not click: iOS fires no click for a tap on plain text.
    document.addEventListener("pointerdown", function (event) {
      if (!menu.hidden && !control.contains(event.target)) close(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !menu.hidden) {
        event.preventDefault();
        close(true);
      }
    });
    // Close when focus moves to something else on the page (Tab). Safari does
    // not focus a button on click, so focus moving to nothing (relatedTarget
    // null) is a click in progress: the document click handler decides then.
    control.addEventListener("focusout", function (event) {
      if (event.relatedTarget && !control.contains(event.relatedTarget)) close(false);
    });
    control.hidden = false;
  }
  // The header's Guide and Tools menus (native details): one open at a time,
  // closed by Esc (focus returns to its name) or a click outside.
  function menus() {
    var all = Array.prototype.slice.call(document.querySelectorAll(".nav-menu"));
    all.forEach(function (menu) {
      menu.addEventListener("toggle", function () {
        if (menu.open) all.forEach(function (other) { if (other !== menu) other.open = false; });
      });
    });
    document.addEventListener("click", function (event) {
      all.forEach(function (menu) { if (menu.open && !menu.contains(event.target)) menu.open = false; });
    });
    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;
      all.forEach(function (menu) {
        if (menu.open) { menu.open = false; menu.querySelector("summary").focus(); }
      });
    });
  }
  function start() { ready(); menus(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();

  window.addEventListener("storage", function (event) {
    if (event.key === key || event.key === null) apply(event.newValue);
  });
  window.addEventListener("beforeprint", function () { pictures("light"); });
  window.addEventListener("afterprint", function () { pictures(root.getAttribute("data-theme") || "system"); });
})();
