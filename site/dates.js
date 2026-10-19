// Show footer dates, and dates marked data-ago, as "3 weeks ago", keeping the
// full date as a tooltip.
// Optional: without JavaScript the dates read as written, such as "on 14 Oct 2026".
(function () {
  "use strict";
  var day = 86400000;
  function ago(then) {
    var days = Math.floor((Date.now() - then) / day);
    if (isNaN(days) || days < 0) return "";
    if (days === 0) return "today";
    if (days === 1) return "yesterday";
    if (days < 14) return days + " days ago";
    if (days < 60) return Math.floor(days / 7) + " weeks ago";
    if (days < 365) return Math.floor(days / 30) + " months ago";
    return "over a year ago";
  }
  document.querySelectorAll(".site-footer time[datetime], time[datetime][data-ago]").forEach(function (time) {
    var parts = time.getAttribute("datetime").split("-");
    var text = ago(new Date(+parts[0], parts[1] - 1, +parts[2]).getTime());
    if (!text) return;
    time.title = time.textContent.replace(/^on /, "");
    time.textContent = text;
  });
})();
