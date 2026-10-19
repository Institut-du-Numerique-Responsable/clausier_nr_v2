/* Mesure d'audience Matomo de l'INR : sans cookie, respecte Do Not Track.
   Configuration lue sur la balise <script data-matomo data-site> (aucun script inline : CSP). */
(function () {
  "use strict";
  var balise = document.currentScript;
  if (!balise || !balise.dataset.matomo || !balise.dataset.site) { return; }
  if (navigator.doNotTrack === "1" || window.doNotTrack === "1") { return; }
  var u = balise.dataset.matomo;
  var _paq = window._paq = window._paq || [];
  _paq.push(["disableCookies"]);
  _paq.push(["setDoNotTrack", true]);
  _paq.push(["trackPageView"]);
  _paq.push(["enableLinkTracking"]);
  _paq.push(["setTrackerUrl", u + "matomo.php"]);
  _paq.push(["setSiteId", balise.dataset.site]);
  var s = document.createElement("script");
  s.async = true;
  s.src = u + "matomo.js";
  document.head.appendChild(s);
})();
