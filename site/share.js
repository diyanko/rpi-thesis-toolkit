// "Share this guide" on the home page. An extra only: with JavaScript off the
// button is a plain e-mail link. With it on, phones and tablets open the
// device's share sheet; elsewhere the button copies the link and says so.
// Nothing is counted or sent anywhere: the link is the site's own address.
(function () {
  "use strict";
  var button = document.querySelector("[data-share]");
  if (!button) return;
  var link = button.getAttribute("data-share");
  var status = document.querySelector(".share-status");
  var touch = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;

  function say(message) {
    if (!status) return;
    status.textContent = message;
    clearTimeout(say.timer);
    say.timer = setTimeout(function () { status.textContent = ""; }, 2500);
  }

  button.addEventListener("click", function (event) {
    if (touch && navigator.share) {
      event.preventDefault();
      navigator.share({ title: "RPI Thesis Toolkit", url: link }).catch(function () {});
    } else if (navigator.clipboard && navigator.clipboard.writeText) {
      event.preventDefault();
      navigator.clipboard.writeText(link).then(function () {
        say("Link copied");
      }, function () {
        window.location.href = button.href;   // no clipboard: fall back to the e-mail link
      });
    }
  });
})();
