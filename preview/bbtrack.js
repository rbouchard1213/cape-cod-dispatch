/* Busy Bees — first-party visitor counting (bbtrack.js).
   Counts page views, taps on buttons and links, how far a request
   gets, and the page a visit ends on. Run by Busy Bees itself, in
   Busy Bees' own Workspace — no outside analytics company, no ad
   trackers, nothing shared or sold.

   Never sent: names, phone numbers, addresses, anything typed into
   a box, IP addresses. The visit id is random, made fresh for each
   visit, kept only in this tab, and exists only to join one visit's
   own steps together (started -> ... -> sent). It is never used to
   follow anyone between visits, and no screen anywhere shows a
   single person's visit — the office side shows totals and rates.

   Your choice: the Privacy page's toggle sets bb_no_track in this
   browser and this logger checks it before every send; the
   browser's Do Not Track setting is honored the same way. Sending
   is fire-and-forget — if the counter is unreachable the page
   simply carries on. */
(function () {
  "use strict";
  var ENDPOINT = "https://script.google.com/macros/s/AKfycbzoOal_JmYyjT5Z9hviIJXdG0DtC5kY8_oycSp85DBb9R5d7y7-oUuKcJqdjSxvG60a/exec";
  if (!ENDPOINT) { return; }

  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function optedOut() {
    if (lsGet("bb_no_track") === "1") { return true; }
    try {
      var d = navigator.doNotTrack || window.doNotTrack;
      return d === "1" || d === "yes";
    } catch (e) { return false; }
  }
  if (optedOut()) { return; }

  /* Random per-visit id — a funnel join key, nothing more. */
  var sid = "";
  try { sid = sessionStorage.getItem("bb_sid") || ""; } catch (e) { }
  if (!sid) {
    sid = "v";
    var chars = "0123456789abcdef";
    for (var i = 0; i < 16; i++) { sid += chars.charAt(Math.floor(Math.random() * 16)); }
    try { sessionStorage.setItem("bb_sid", sid); } catch (e) { }
  }

  function device() {
    var ua = navigator.userAgent || "";
    if (/iPad|Tablet/i.test(ua)) { return "tablet"; }
    if (/Android/i.test(ua)) { return /Mobile/i.test(ua) ? "phone" : "tablet"; }
    if (/Mobi|iPhone|iPod/i.test(ua)) { return "phone"; }
    return "desktop";
  }

  function refHost() {
    try {
      if (!document.referrer) { return ""; }
      var h = new URL(document.referrer).hostname;
      return (h && h !== location.hostname) ? h : "";
    } catch (e) { return ""; }
  }

  function stepFor(p) {
    if (/\/customer\/town\.html$/.test(p)) { return "town"; }
    if (/\/customer\/category\.html$/.test(p)) { return "category"; }
    if (/\/customer\/other\.html$/.test(p)) { return "describe"; }
    if (/\/customer\/details\.html$/.test(p)) { return "details"; }
    if (/\/customer\/review\.html$/.test(p)) { return "review"; }
    if (/\/customer\/sent\.html$/.test(p)) { return "submitted"; }
    if (/\/customer\//.test(p)) { return "job"; }
    return "";
  }

  function reviewCode() {
    /* Only on the gated review pages — the gate already discloses that
       activity there is recorded. The test site itself stays anonymous. */
    try {
      if (location.pathname.indexOf("/review/") === -1) { return ""; }
      return (lsGet("bb_code") || "").toUpperCase().replace(/[^A-Z0-9-]/g, "").slice(0, 12);
    } catch (e) { return ""; }
  }

  function send(type, element, beacon) {
    if (optedOut()) { return; }
    var payload = {
      page: location.pathname,
      event: type,
      element: (element || "").slice(0, 80),
      step: stepFor(location.pathname),
      ref: refHost(),
      device: device(),
      session: sid,
      code: reviewCode()
    };
    var body = JSON.stringify(payload);
    try {
      if (beacon && navigator.sendBeacon) {
        if (navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "text/plain;charset=utf-8" }))) { return; }
      }
      fetch(ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: body, keepalive: true, mode: "no-cors"
      }).catch(function () { });
    } catch (e) { /* counting never breaks the site */ }
  }

  send("pageview", "");
  var here = stepFor(location.pathname);
  if (here === "details" || here === "review" || here === "submitted") {
    send("form_step", "");
  }

  document.addEventListener("click", function (e) {
    var t = e.target;
    while (t && t !== document) {
      if (t.getAttribute) {
        var tag = t.getAttribute("data-track");
        if (tag) { send("click", tag); return; }
      }
      if (t.tagName === "A") {
        var href = t.getAttribute("href") || "";
        var base = href.split("?")[0].split("#")[0].split("/").pop();
        if (base) { send("click", "link:" + base); }
        return;
      }
      t = t.parentNode;
    }
  }, false);

  var exited = false;
  window.addEventListener("pagehide", function () {
    if (exited) { return; }
    exited = true;
    send("pageexit", "", true);
  });
})();
