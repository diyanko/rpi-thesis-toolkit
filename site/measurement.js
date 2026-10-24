/* Optional aggregate measurement. No visitor IDs; no student input is read. */
(function () {
  "use strict";
  var script = document.currentScript;
  if (!script) return;
  var site = new URL(script.dataset.site);
  // Local previews, offline copies and browser automation send no measurements.
  if (location.origin !== site.origin || !location.pathname.startsWith(site.pathname)) return;
  var preference = "rpi-thesis-measurement";
  var counted = "rpi-thesis-download-counted";
  var disabled = true;
  try {
    var url = new URL(location.href);
    var choice = url.searchParams.get("measurement");
    if (choice === "off") localStorage.setItem(preference, "off");
    if (choice === "on") localStorage.removeItem(preference);
    if (choice === "off" || choice === "on") {
      url.searchParams.delete("measurement");
      history.replaceState(null, "", url.href);
    }
    disabled = localStorage.getItem(preference) === "off";
  } catch (_) { /* If the preference cannot be read, leave measurement off. */ }
  disabled = disabled || navigator.webdriver || navigator.globalPrivacyControl === true || navigator.doNotTrack === "1";

  document.querySelectorAll("[data-measurement-controls]").forEach(function (box) { box.hidden = false; });
  document.querySelectorAll("[data-measurement-status]").forEach(function (box) {
    box.textContent = disabled ? "Measurement is off in this browser." : "Aggregate measurement is on in this browser.";
  });
  document.querySelectorAll("[data-measurement-choice]").forEach(function (button) {
    button.addEventListener("click", function () {
      // The query form also works if browser storage is unavailable.
      var next = new URL(location.href);
      next.searchParams.set("measurement", button.dataset.measurementChoice);
      location.replace(next.href);
    });
  });
  if (disabled) return;

  if (script.dataset.token) {
    var beacon = document.createElement("script");
    beacon.type = "module";
    beacon.src = "https://static.cloudflareinsights.com/beacon.min.js";
    beacon.dataset.cfBeacon = JSON.stringify({token: script.dataset.token});
    document.head.appendChild(beacon);
  }
  var endpoint = script.dataset.counter;
  if (!endpoint) return;
  var repository = new URL(script.dataset.repository);
  var releases = repository.pathname + "/releases/download/";
  function asset(address, nested) {
    var link;
    try { link = new URL(address, location.href); } catch (_) { return ""; }
    if (!nested && link.origin === "https://www.overleaf.com" && link.pathname === "/docs") {
      var source = asset(link.searchParams.get("snip_uri") || "", true);
      return source === "overleaf" ? "overleaf" : "";
    }
    if (link.origin === repository.origin && link.pathname.startsWith(releases)) {
      var name = link.pathname.slice(releases.length);
      if (/^v[\d.]+\/rpi-thesis-starter-v[\d.]+\.zip$/.test(name)) return "starter";
      if (/^v[\d.]+\/rpi-thesis-overleaf-v[\d.]+\.zip$/.test(name)) return "overleaf";
      if (/^v[\d.]+\/rpi-thesis\.cls$/.test(name)) return "class";
    }
    if (link.origin === site.origin) {
      if (link.pathname === site.pathname + "downloads/rpi-thesis.cls") return "class";
      if (link.pathname === site.pathname + "downloads/rpi-thesis-cheatsheet.pdf") return "cheatsheet";
    }
    return "";
  }
  function record(event) {
    if (!event.isTrusted || event.defaultPrevented || (event.type === "auxclick" && event.button !== 1)) return;
    var anchor = event.target.closest && event.target.closest("a[href]");
    if (!anchor) return;
    var kind = asset(anchor.href);
    if (!kind) return;
    try {
      if (sessionStorage.getItem(counted)) return;
      sessionStorage.setItem(counted, "1");
    } catch (_) { return; } // No reliable session flag: skip rather than count every click.
    // No credentials, referrer, page URL, session flag, or user-provided text is sent.
    try {
      fetch(endpoint, {method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({asset: kind}), credentials: "omit", referrerPolicy: "no-referrer", keepalive: true}).catch(function () {});
    } catch (_) { /* Download links keep working even without measurement. */ }
  }
  document.addEventListener("click", record);
  document.addEventListener("auxclick", record);
}());
