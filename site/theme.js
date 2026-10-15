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
    document.addEventListener("click", function (event) {
      if (!control.contains(event.target)) close(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !menu.hidden) {
        event.preventDefault();
        close(true);
      }
    });
    control.addEventListener("focusout", function (event) {
      if (!control.contains(event.relatedTarget)) close(false);
    });
    control.hidden = false;
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready);
  else ready();

  window.addEventListener("storage", function (event) {
    if (event.key === key || event.key === null) apply(event.newValue);
  });
  window.addEventListener("beforeprint", function () { pictures("light"); });
  window.addEventListener("afterprint", function () { pictures(root.getAttribute("data-theme") || "system"); });
})();
