/* Clausier Numérique Responsable : filtres, recherche, sélection locale, exports.
   Aucune dépendance, aucune requête hors du site. La sélection reste dans le navigateur. */
(function () {
  "use strict";
  var CLE = "clausier-nr-v2-selection";
  var donnees = null;

  /* ---------- sélection (stockage local) ---------- */
  function lire() {
    try { var v = JSON.parse(localStorage.getItem(CLE) || "[]"); return Array.isArray(v) ? v : []; }
    catch (e) { return []; }
  }
  function ecrire(ids) {
    try { localStorage.setItem(CLE, JSON.stringify(ids)); } catch (e) { /* navigation privée */ }
    majCompteur();
  }
  function basculer(id) {
    var ids = lire(), i = ids.indexOf(id);
    if (i < 0) { ids.push(id); } else { ids.splice(i, 1); }
    ecrire(ids);
    return i < 0;
  }
  function majCompteur() {
    var n = lire().length;
    document.querySelectorAll("[data-compteur]").forEach(function (el) {
      el.textContent = n;
      el.hidden = n === 0;
    });
  }
  function majBouton(b, retenue) {
    b.setAttribute("aria-pressed", retenue ? "true" : "false");
    b.querySelector(".etat").textContent = retenue ? "Retenue" : "Retenir";
    var ligne = b.closest(".ligne");
    if (ligne) { ligne.classList.toggle("retenue", retenue); }
  }
  function initBoutons() {
    var ids = lire();
    document.querySelectorAll("button.retenir[data-id]").forEach(function (b) {
      majBouton(b, ids.indexOf(b.dataset.id) >= 0);
      b.addEventListener("click", function () { majBouton(b, basculer(b.dataset.id)); });
    });
  }

  /* ---------- données des clauses (chargées à la demande) ---------- */
  function charger(url) {
    if (donnees) { return Promise.resolve(donnees); }
    return fetch(url).then(function (r) {
      if (!r.ok) { throw new Error("HTTP " + r.status); }
      return r.json();
    }).then(function (d) { donnees = d; return d; });
  }
  function normaliser(s) {
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, " ");
  }
  function texteBrut(md) {
    return md.replace(/<sup>([^<]*)<\/sup>/g, "$1")
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, function (m, t, u) { return t === u ? t : t + " (" + u + ")"; })
      .replace(/\[\^([^\]]+)\]/g, "[$1]")
      .replace(/\*\*\*(.+?)\*\*\*/g, "$1").replace(/\*\*(.+?)\*\*/g, "$1")
      .replace(/(^|[^\w*])\*(\S(?:.*?\S)?)\*(?![\w*])/g, "$1$2").replace(/\*\*/g, "")
      .replace(/^(\s*)- /gm, "$1• ");
  }

  /* ---------- catalogue : filtres et recherche ---------- */
  function initCatalogue() {
    var form = document.getElementById("filtres");
    if (!form) { return; }
    var lignes = Array.prototype.slice.call(document.querySelectorAll(".ligne[data-id]"));
    var groupes = document.querySelectorAll("[data-groupe]");
    var sortie = document.getElementById("resultat");
    var q = document.getElementById("q");
    var index = null;

    var params = new URLSearchParams(location.search);
    ["segment", "phase"].forEach(function (nom) {
      var vals = params.getAll(nom);
      if (vals.length) {
        form.querySelectorAll("input[name=" + nom + "]").forEach(function (c) { c.checked = vals.indexOf(c.value) >= 0; });
      }
    });
    if (params.get("q")) { q.value = params.get("q"); }

    function coches(nom) {
      return Array.prototype.filter.call(form.querySelectorAll("input[name=" + nom + "]"), function (c) { return c.checked; })
        .map(function (c) { return c.value; });
    }
    function appliquer() {
      var segs = coches("segment"), phases = coches("phase");
      var mots = normaliser(q.value).split(" ").filter(Boolean);
      var n = 0;
      lignes.forEach(function (li) {
        var ok = segs.indexOf(li.dataset.segment) >= 0 && phases.indexOf(li.dataset.phase) >= 0;
        if (ok && mots.length) {
          var t = index ? index[li.dataset.id] : normaliser(li.textContent);
          ok = mots.every(function (m) { return t.indexOf(m) >= 0; });
        }
        li.hidden = !ok;
        if (ok) { n++; }
      });
      groupes.forEach(function (g) { g.hidden = !g.querySelector(".ligne:not([hidden])"); });
      sortie.textContent = n === 0 ? "Aucune clause ne correspond. Élargissez les filtres ou modifiez la recherche."
        : n + (n > 1 ? " clauses affichées" : " clause affichée") + (mots.length && !index ? " (recherche dans les intitulés, texte complet en cours de chargement)" : "");
      var p = new URLSearchParams();
      if (segs.length < form.querySelectorAll("input[name=segment]").length) { segs.forEach(function (s) { p.append("segment", s); }); }
      if (phases.length < 2) { phases.forEach(function (s) { p.append("phase", s); }); }
      if (q.value) { p.set("q", q.value); }
      history.replaceState(null, "", location.pathname + (p.toString() ? "?" + p : ""));
    }
    function chargerIndex() {
      if (index) { return; }
      charger(form.dataset.donnees).then(function (d) {
        index = {};
        d.clauses.forEach(function (c) {
          index[c.id] = normaliser([c.id, c.titre].concat(c.rubriques.map(function (r) { return r[1]; })).join(" "));
        });
        appliquer();
      }).catch(function () { sortie.textContent = "Texte complet indisponible : la recherche porte sur les intitulés."; });
    }
    form.addEventListener("change", appliquer);
    var minuterie = null;
    q.addEventListener("input", function () {
      chargerIndex();
      clearTimeout(minuterie);
      minuterie = setTimeout(appliquer, 150);
    });
    q.addEventListener("focus", chargerIndex, { once: true });
    form.addEventListener("submit", function (e) { e.preventDefault(); });
    form.querySelector("[data-reinit]").addEventListener("click", function () {
      form.querySelectorAll("input[type=checkbox]").forEach(function (c) { c.checked = true; });
      q.value = "";
      appliquer();
    });
    if (q.value) { chargerIndex(); }
    appliquer();
  }

  /* ---------- page « Ma sélection » ---------- */
  function initSelection() {
    var zone = document.getElementById("selection");
    if (!zone) { return; }
    var liste = document.getElementById("sel-liste");
    var etat = document.getElementById("sel-etat");
    var actions = document.getElementById("sel-actions");

    function el(tag, cls, txt) {
      var e = document.createElement(tag);
      if (cls) { e.className = cls; }
      if (txt !== undefined) { e.textContent = txt; }
      return e;
    }
    function retenues(d) {
      var ids = lire();
      return d.clauses.filter(function (c) { return ids.indexOf(c.id) >= 0; });
    }
    function afficher(d) {
      var cs = retenues(d);
      liste.textContent = "";
      actions.hidden = cs.length === 0;
      etat.textContent = cs.length === 0 ? "" : cs.length + (cs.length > 1 ? " clauses retenues, dans l'ordre du clausier." : " clause retenue.");
      document.getElementById("sel-vide").hidden = cs.length > 0;
      cs.forEach(function (c) {
        var art = el("article", "sel-clause");
        var tete = el("p", "");
        var a = el("a", "ident", c.id);
        a.href = zone.dataset.racine + c.url;
        tete.appendChild(a);
        tete.appendChild(document.createTextNode("  " + c.segment + (c.sous_segment ? " / " + c.sous_segment : "") + ", " + c.phase));
        art.appendChild(tete);
        art.appendChild(el("h2", "", c.titre));
        c.rubriques.forEach(function (r) {
          art.appendChild(el("h3", "", r[0]));
          var p = el("div", "contenu texte-brut");
          p.textContent = texteBrut(r[1]);
          art.appendChild(p);
        });
        var notes = Object.keys(c.notes);
        if (notes.length) {
          art.appendChild(el("p", "discret", notes.map(function (n) { return "[" + n + "] " + c.notes[n]; }).join("\n")));
        }
        var b = el("button", "bouton second no-print", "Retirer de la sélection");
        b.type = "button";
        b.addEventListener("click", function () { basculer(c.id); afficher(d); });
        art.appendChild(b);
        liste.appendChild(art);
      });
    }
    function telecharger(nom, type, contenu) {
      var url = URL.createObjectURL(new Blob([contenu], { type: type }));
      var a = el("a");
      a.href = url; a.download = nom;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    }
    function exportMarkdown(d) {
      var out = ["# " + d.titre + " — sélection", "", "Source : " + d.source + ". " + d.licence, ""];
      retenues(d).forEach(function (c) {
        out.push("## " + c.id + " — " + c.titre, "", "*" + c.segment + (c.sous_segment ? " / " + c.sous_segment : "") + ", " + c.phase + "*", "");
        c.rubriques.forEach(function (r) { out.push("### " + r[0], "", r[1], ""); });
        Object.keys(c.notes).forEach(function (n) { out.push("[^" + n + "]: " + c.notes[n]); });
        if (Object.keys(c.notes).length) { out.push(""); }
      });
      return out.join("\n");
    }
    function exportTexte(d) {
      var out = [d.titre + " — sélection", "Source : " + d.source + ". " + d.licence, ""];
      retenues(d).forEach(function (c) {
        out.push("=".repeat(70), c.id + " — " + c.titre, c.segment + (c.sous_segment ? " / " + c.sous_segment : "") + ", " + c.phase, "");
        c.rubriques.forEach(function (r) { out.push(r[0] + " :", texteBrut(r[1]), ""); });
        Object.keys(c.notes).forEach(function (n) { out.push("[" + n + "] " + c.notes[n]); });
      });
      return out.join("\n");
    }
    function exportCsv(d) {
      var champs = d.colonnes_csv;
      var esc = function (s) { return '"' + String(s || "").replace(/"/g, '""') + '"'; };
      var lignes = [["ID", "Segment", "Sous segment", "Phase", "Critère"].concat(champs.map(function (c) { return c[1]; })).map(esc).join(";")];
      retenues(d).forEach(function (c) {
        var v = {};
        c.rubriques.forEach(function (r) { v[d.champs[r[0]]] = texteBrut(r[1]); });
        lignes.push([c.id, c.segment, c.sous_segment, c.phase, c.titre].concat(champs.map(function (k) { return v[k[0]]; })).map(esc).join(";"));
      });
      return "﻿" + lignes.join("\r\n");
    }
    charger(zone.dataset.donnees).then(function (d) {
      afficher(d);
      document.getElementById("exp-md").addEventListener("click", function () { telecharger("clausier-nr-selection.md", "text/markdown;charset=utf-8", exportMarkdown(d)); });
      document.getElementById("exp-csv").addEventListener("click", function () { telecharger("clausier-nr-selection.csv", "text/csv;charset=utf-8", exportCsv(d)); });
      document.getElementById("exp-txt").addEventListener("click", function () { telecharger("clausier-nr-selection.txt", "text/plain;charset=utf-8", exportTexte(d)); });
      document.getElementById("exp-print").addEventListener("click", function () { window.print(); });
      document.getElementById("sel-vider").addEventListener("click", function () { ecrire([]); afficher(d); });
    }).catch(function () {
      etat.textContent = "Le texte des clauses n'a pas pu être chargé. Rechargez la page.";
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    majCompteur();
    initBoutons();
    initCatalogue();
    initSelection();
  });
})();
