# -*- coding: utf-8 -*-
"""Génère le site statique dans dist/site/ à partir du Markdown.

Choix : un générateur Python d'environ 400 lignes plutôt qu'Astro ou un autre outil
Node. Le projet a déjà besoin de Python (validation, Excel) ; un seul outillage, deux
dépendances (PyYAML, Markdown), aucun node_modules. Voir docs/architecture.md.

Toutes les adresses sont relatives : le site fonctionne à la racine d'un domaine comme
dans un sous-dossier, et en ouvrant les fichiers en local.

Usage : python scripts/build_site.py [--out dist/site]
"""
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

import markdown

sys.path.insert(0, str(Path(__file__).parent))
import clausier  # noqa: E402

ROOT = clausier.ROOT
ASSETS = ROOT / "site/assets"
EXCEL = ROOT / "dist/excel/Clausier-Numerique-Responsable-V2.xlsx"
PDF_V2 = ROOT / "sources/originaux/clausier-numerique-responsable-v2.pdf"
NOM_EXCEL = "Clausier-Numerique-Responsable-V2.xlsx"   # nom publié, cité par les pages
NIVEAUX = ("Niveau 1 (Must have)", "Niveau 2 (Nice to have)")
DESC = ("Clausier Numérique Responsable de l'INR et de la FTCC : 102 clauses types pour intégrer "
        "le numérique responsable dans les achats IT (RFI/RFP, CCAP/CCTP, contrats). Licence CC BY 4.0.")
STATUTS = {"brouillon": "brouillon", "en_revision": "en révision", "validee": "validée",
           "archivee": "archivée"}

esc = html.escape


def md(text):
    return markdown.markdown(text, extensions=["footnotes", "sane_lists"],
                             extension_configs={"footnotes": {"BACKLINK_TEXT": "↩"}})


def taille(path):
    n = path.stat().st_size
    return f"{n / 1_000_000:.1f} Mo".replace(".", ",") if n > 1_000_000 else f"{round(n / 1000)} Ko"


class Site:
    def __init__(self, out):
        self.out = out
        self.meta = clausier.load_yaml("metadata.yml")
        self.segs = clausier.segments()
        self.seg_by = {s["slug"]: s for s in self.segs["segments"]}
        self.sections = {sec["numero"]: (s, sec) for s in self.segs["segments"] for sec in s["sections"]}
        self.clauses = clausier.published(clausier.load_clauses())
        # empreinte des ressources : l'hébergeur les met en cache 7 jours
        h = hashlib.sha256()
        for f in sorted(ASSETS.iterdir()):
            h.update(f.read_bytes())
        self.version_assets = h.hexdigest()[:10]
        titres = [c["titre"] for c in self.clauses]
        self.partage = {t for t in titres if titres.count(t) > 1}

    # ------------------------------------------------------------ outils
    def sous(self, c):
        return {s["slug"]: s["libelle"] for s in self.seg_by[c["segment"]]["sous_segments"]}.get(
            c["sous_segment"], "")

    def precision(self, c):
        """Précision affichée quand l'intitulé est partagé (cellule fusionnée du V2)."""
        if c["titre"] not in self.partage:
            return ""
        com = clausier.md_to_plain(c.rubrique("Commentaires"))
        return com if com and len(com) <= 70 else ""

    def phase(self, c):
        return self.segs["phases"][c["phase"]]["libelle"]

    def head_seo(self, rel, titre, desc, jsonld):
        """URL canonique, OpenGraph et JSON-LD : adresses absolues, si l'URL du site est connue."""
        base = self.meta["liens"]["site"]
        out = []
        if base and not rel.endswith(".html"):
            url = base + rel
            out += [f'<link rel="canonical" href="{url}">', f'<meta property="og:url" content="{url}">']
        out += ['<meta property="og:type" content="website">', '<meta property="og:locale" content="fr_FR">',
                f'<meta property="og:site_name" content="{esc(self.meta["titre"])}">',
                f'<meta property="og:title" content="{esc(titre)}">',
                f'<meta property="og:description" content="{esc(desc)}">']
        if jsonld:
            data = json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
            out.append(f'<script type="application/ld+json">{data}</script>')
        return "\n".join(out)

    def org(self):
        return [{"@type": "Organization", "name": "Institut du Numérique Responsable (INR)",
                 "url": "https://institutnr.org/"},
                {"@type": "Organization", "name": "French Tech Corporate Community (FTCC)"}]

    def write(self, rel, body, titre, desc="", actif="", jsonld=None):
        depth = rel.count("/")
        r = "../" * depth
        desc = desc or DESC
        nav = [("", "Accueil"), ("clausier/", "Clausier"), ("mode-emploi/", "Mode d'emploi"),
               ("a-propos/", "À propos"), ("contribuer/", "Contribuer")]
        items = "".join(
            f'<li><a href="{r}{h}"{" aria-current=\"page\"" if actif == h else ""}>{esc(t)}</a></li>'
            for h, t in nav)
        sel_cur = ' aria-current="page"' if actif == "selection/" else ""
        items += (f'<li><a href="{r}selection/"{sel_cur}>Ma sélection '
                  f'<span class="compteur" data-compteur hidden>0</span></a></li>')
        depot = self.meta["depot"]["url"]
        lien_depot = (f'<p><a href="{depot}">Sources sur GitHub</a></p>' if depot
                      else "<p>Dépôt des sources : publication à venir.</p>")
        page_inr = self.meta["liens"]["page_inr"]
        if page_inr:
            lien_depot = f'<p><a href="{page_inr}">Le clausier sur institutnr.org</a></p>' + lien_depot
        page = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titre)}{"" if titre == self.meta["titre"] else " — " + self.meta["titre"]}</title>
<meta name="description" content="{esc(desc)}">
{self.head_seo(rel, titre, desc, jsonld)}
<link rel="stylesheet" href="{r}assets/style.css?v={self.version_assets}">
<script src="{r}assets/js.js?v={self.version_assets}"></script>
<script src="{r}assets/clausier.js?v={self.version_assets}" defer></script>
</head>
<body>
<a class="evitement" href="#contenu">Aller au contenu</a>
<header class="entete"><div class="entete-int">
<a class="marque" href="{r}"><b>Clausier Numérique Responsable</b><span>Version {self.meta["version"]}, FTCC et Institut du Numérique Responsable</span></a>
<nav class="nav" aria-label="Navigation principale"><ul>{items}</ul></nav>
</div></header>
<main id="contenu">
{body}
</main>
<footer class="pied"><div class="pied-int">
<div><p><b>Clausier Numérique Responsable V{self.meta["version"]}</b></p>
<p>© 2026 French Tech Corporate Community (FTCC) et Institut du Numérique Responsable (INR).
Licence <a href="{self.meta["licence_contenu"]["url"]}">{self.meta["licence_contenu"]["court"]}</a> :
réutilisation et modification libres, en citant la source. <a href="{r}credits/#reutiliser">Comment citer</a></p>
<p>Propositions : <a href="mailto:{self.meta["contact"]["propositions"]}">{self.meta["contact"]["propositions"]}</a></p></div>
<div><p><a href="{r}comment-lire/">Comment lire le clausier</a></p><p><a href="{r}lexique/">Lexique</a></p>
<p><a href="{r}sources/">Sources documentaires</a></p><p><a href="{r}methodologie/">Méthodologie</a></p>
<p><a href="{r}versions/">Historique des versions</a></p></div>
<div><p><a href="{r}credits/">Crédits</a></p><p><a href="{r}mentions-legales/">Mentions légales</a></p>
<p><a href="https://institutnr.org/">institutnr.org</a></p>{lien_depot}
<p>Site sans cookie ni mesure d'audience.</p></div>
</div></footer>
</body>
</html>
"""
        path = self.out / rel / "index.html" if not rel.endswith(".html") else self.out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page, encoding="utf-8")

    def ligne(self, c, r):
        pre = self.precision(c)
        precis = f'<span class="precis">{esc(pre)}</span>' if pre else ""
        return (f'<li class="ligne" data-id="{c.id}" data-segment="{c["segment"]}" data-phase="{c["phase"]}">'
                f'<span class="ident">{c.id}</span>'
                f'<span><a class="titre" href="{r}clausier/clauses/{c.id}/">{esc(c["titre"])}</a>{precis}</span>'
                f'<button type="button" class="retenir" data-id="{c.id}" aria-pressed="false">'
                f'<span class="etat">Retenir</span><span class="sr-only"> {c.id}</span></button></li>')

    def liste_section(self, num, r):
        items = "".join(self.ligne(c, r) for c in self.clauses if c["section"] == num)
        return f'<ul class="liste">{items}</ul>' if items else ""

    # ------------------------------------------------------------ pages
    def accueil(self):
        r = ""
        lignes, tot = [], {"questionnaire": 0, "exigences": 0}
        for s in self.segs["segments"]:
            cells = []
            for ph in ("questionnaire", "exigences"):
                n = sum(1 for c in self.clauses if c["segment"] == s["slug"] and c["phase"] == ph)
                tot[ph] += n
                cells.append(f'<td><a href="clausier/?segment={s["slug"]}&amp;phase={ph}" '
                             f'aria-label="{n} clauses {esc(s["libelle"])}, {ph}">{n}</a></td>' if n
                             else '<td><span class="vide" aria-label="aucune clause">–</span></td>')
            lignes.append(f'<tr><th scope="row"><a href="clausier/segments/{s["slug"]}/">'
                          f'{s["numero"]}. {esc(s["libelle"])}</a></th>{"".join(cells)}</tr>')
        excel = f'Télécharger le classeur Excel ({taille(EXCEL)})' if EXCEL.exists() else ""
        body = f"""
<div class="accueil">
<div>
<h1>Des clauses numérique responsable prêtes à intégrer dans vos achats IT</h1>
<p class="chapo">Questionnaires pour évaluer les soumissionnaires et exigences pour le cahier des
charges, en deux niveaux d'ambition. {len(self.clauses)} clauses, six segments d'achat, conçues
par une cinquantaine d'entreprises et d'organisations publiques.</p>
<div class="actions">
<a class="bouton" href="clausier/">Parcourir les clauses</a>
{f'<a class="bouton second" href="telechargements/{NOM_EXCEL}" download>{excel}</a>' if excel else ""}
</div>
<p>Cochez les clauses utiles à votre consultation, puis exportez-les depuis
<a href="selection/">Ma sélection</a>. Aucun compte, aucune donnée transmise.</p>
<p class="discret">Document d'origine : <a href="telechargements/{PDF_V2.name}">Clausier V2 en PDF</a>
({taille(PDF_V2)}, 44 pages). Version PDF générée depuis le site : à venir.</p>
</div>
<table class="matrice">
<caption>Nombre de clauses par segment et par partie</caption>
<thead><tr><th scope="col">Segment d'achat</th><th scope="col">Questionnaire<br>RFI/RFP</th><th scope="col">Exigences<br>CCAP & CCTP</th></tr></thead>
<tbody>{"".join(lignes)}</tbody>
<tfoot><tr><th scope="row">Total</th><td>{tot["questionnaire"]}</td><td>{tot["exigences"]}</td></tr></tfoot>
</table>
</div>
<div class="texte">
<h2>Deux niveaux pour chaque critère</h2>
<p>Le <b>Niveau 1 (Must have)</b> regroupe les éléments essentiels attendus dans la réponse.
Le <b>Niveau 2 (Nice to have)</b> regroupe les éléments complémentaires qui renforcent et
valorisent la réponse. Les critères, leur poids et les exigences sont à adapter à la stratégie
d'achat de chaque organisation. <a href="comment-lire/">Comment lire le clausier</a></p>
<h2>Qui porte le clausier</h2>
<p>La French Tech Corporate Community (FTCC) et l'Institut du Numérique Responsable (INR)
coordonnent le clausier. Richard Bury et Claire Lardière (EDF) en ont piloté la réalisation.
<a href="credits/">Voir les crédits</a></p>
<p>Institut du Numérique Responsable : « organisation de référence promouvant les pratiques du
numérique responsable » (lexique du V2). <a href="https://institutnr.org/">institutnr.org</a></p>
</div>
"""
        base = self.meta["liens"]["site"] or ""
        lic = self.meta["licence_contenu"]
        dataset = {
            "@context": "https://schema.org", "@type": "Dataset",
            "name": f'{self.meta["titre"]} V{self.meta["version"]}',
            "description": DESC, "inLanguage": "fr", "version": self.meta["version"],
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "creditText": lic["attribution"], "creator": self.org(),
            "keywords": ["numérique responsable", "achats responsables", "clausier", "RFI", "RFP",
                         "CCAP", "CCTP", "écoconception", "accessibilité numérique", "commande publique"],
            "isAccessibleForFree": True,
            "distribution": [
                {"@type": "DataDownload", "encodingFormat":
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                 "contentUrl": f"{base}telechargements/{NOM_EXCEL}"},
                {"@type": "DataDownload", "encodingFormat": "application/pdf",
                 "contentUrl": f"{base}telechargements/{PDF_V2.name}"},
                {"@type": "DataDownload", "encodingFormat": "application/json",
                 "contentUrl": f"{base}donnees/clauses.json"},
                {"@type": "DataDownload", "encodingFormat": "text/markdown",
                 "contentUrl": f"{base}llms-full.txt"}],
        }
        if base:
            dataset["url"] = base
        if self.meta["depot"]["url"]:
            dataset["sameAs"] = [self.meta["depot"]["url"], self.meta["liens"]["page_inr"]]
        self.write("", body, self.meta["titre"], actif="", jsonld=dataset)

    def catalogue(self):
        r = "../"
        segs = "".join(f'<label><input type="checkbox" name="segment" value="{s["slug"]}" checked> '
                       f'{esc(s["libelle"])}</label>' for s in self.segs["segments"])
        phases = "".join(f'<label><input type="checkbox" name="phase" value="{k}" checked> '
                         f'{esc(v["libelle"])}</label>' for k, v in self.segs["phases"].items())
        groupes = []
        for s in self.segs["segments"]:
            secs = []
            for sec in s["sections"]:
                secs.append(f'<div data-groupe><h3>{esc(sec["titre_source"])}</h3>'
                            f'{self.liste_section(sec["numero"], r)}</div>')
            groupes.append(f'<section class="groupe" data-groupe aria-labelledby="g-{s["slug"]}">'
                           f'<h2 id="g-{s["slug"]}"><a href="segments/{s["slug"]}/">{s["numero"]}. '
                           f'{esc(s["libelle"])}</a></h2>{"".join(secs)}</section>')
        body = f"""
<h1>Les clauses</h1>
<p class="chapo">{len(self.clauses)} clauses, dans l'ordre du clausier. Filtrez, recherchez,
puis cochez « Retenir » pour composer votre sélection.</p>
<div class="catalogue">
<form id="filtres" class="filtres" role="search" data-donnees="../donnees/clauses.json" aria-label="Filtrer les clauses">
<fieldset><legend><label for="q">Rechercher</label></legend>
<input type="search" id="q" name="q" placeholder="ex. réparabilité, RGAA, PUE" autocomplete="off"></fieldset>
<fieldset><legend>Partie</legend>{phases}</fieldset>
<fieldset><legend>Segment</legend>{segs}</fieldset>
<button type="button" class="bouton second" data-reinit>Tout afficher</button>
</form>
<div>
<p id="resultat" class="resultat" aria-live="polite"></p>
{"".join(groupes)}
</div>
</div>
"""
        self.write("clausier/", body, "Les clauses", actif="clausier/")

    def fiche(self, i, c):
        r = "../../../"
        seg = self.seg_by[c["segment"]]
        src = c["source"] or {}
        body_md = "\n\n".join(f"## {t}\n\n{m}" for t, m in c.rubriques)
        body_md += "".join(f"\n\n[^{n}]: {t}" for n, t in c.notes.items())
        rendu = md(body_md)
        notes = ""
        m = re.search(r'<div class="footnote">.*</div>\s*$', rendu, re.S)
        if m:
            notes, rendu = m.group(0).replace('class="footnote"', 'class="footnotes"'), rendu[:m.start()]
        blocs = re.split(r"(?=<h2>)", rendu)
        hors, niv = [], []
        for b in blocs:
            if not b.strip():
                continue
            t = re.match(r"<h2>(.*?)</h2>", b)
            titre = html.unescape(t.group(1)) if t else ""
            if titre in NIVEAUX:
                cls = "n1" if titre == NIVEAUX[0] else "n2"
                niv.append(f'<section class="niveau {cls} contenu">{b}</section>')
            else:
                hors.append(f'<section class="rubrique contenu">{b}</section>')
        pre = self.precision(c)
        prev_c = self.clauses[i - 1] if i > 0 else None
        next_c = self.clauses[i + 1] if i + 1 < len(self.clauses) else None
        voisin = lambda x, lab: (f'<a href="../{x.id}/">{lab} {x.id}</a>' if x else "<span></span>")  # noqa: E731
        sous = self.sous(c)
        sujet = f"Clausier NR V2 – proposition sur {c.id}"
        modifs = "".join(f"<li>{esc(m['date'])} : {esc(m['description'])}</li>"
                         for m in (c["modifications"] or []))
        body = f"""
<p class="fil"><a href="{r}clausier/">Clauses</a> / <a href="{r}clausier/segments/{seg["slug"]}/">{esc(seg["libelle"])}</a></p>
<div class="fiche-tete">
<span class="ident">{c.id}</span>
<h1>{esc(c["titre"])}</h1>
{f'<p class="chapo">{esc(pre)}</p>' if pre else ""}
<ul class="meta">
<li><b>Segment</b> {seg["numero"]}. {esc(seg["libelle"])}{(" / " + esc(sous)) if sous else ""}</li>
<li><b>Partie</b> {esc(self.phase(c))}</li>
<li><b>Section du V2</b> {esc(c["section"])}{f", page {src['page_pdf']}" if src.get("page_pdf") else ""}</li>
</ul>
<div class="actions"><button type="button" class="retenir" data-id="{c.id}" aria-pressed="false"><span class="etat">Retenir</span><span class="sr-only"> {c.id}</span></button></div>
</div>
{"".join(hors)}
{f'<div class="niveaux">{"".join(niv)}</div>' if niv else ""}
{notes}
<aside class="trace" aria-label="Origine de la clause">
<h2>Origine et suivi</h2>
<ul>
<li>Texte repris du Clausier Numérique Responsable V{esc(c["version"])}{f", section {esc(src.get('section', ''))}, page {src.get('page_pdf')}" if src.get("page_pdf") else ""}.</li>
<li>Statut : {STATUTS[c["statut"]]}.</li>
{f"<li>Modifications depuis le V2 :<ul>{modifs}</ul></li>" if modifs else "<li>Aucune modification depuis le V2.</li>"}
<li><a href="mailto:{self.meta["contact"]["propositions"]}?subject={esc(sujet)}">Proposer une modification de cette clause</a></li>
</ul>
</aside>
<nav class="voisins" aria-label="Clauses voisines">{voisin(prev_c, "Précédente :")}{voisin(next_c, "Suivante :")}</nav>
"""
        desc = f"{c.id} : {c['titre']}. {self.phase(c)}, segment {seg['libelle']}."
        base = self.meta["liens"]["site"] or ""
        ld = {"@context": "https://schema.org", "@type": "CreativeWork", "identifier": c.id,
              "name": f"{c.id} — {c['titre']}", "description": desc, "inLanguage": "fr",
              "genre": "Clause contractuelle type", "about": seg["titre_source"],
              "isPartOf": {"@type": "Dataset", "name": f'{self.meta["titre"]} V{self.meta["version"]}',
                           **({"url": base} if base else {})},
              "license": "https://creativecommons.org/licenses/by/4.0/",
              "creditText": self.meta["licence_contenu"]["attribution"], "creator": self.org()}
        if base:
            ld["url"] = f"{base}clausier/clauses/{c.id}/"
        self.write(f"clausier/clauses/{c.id}/", body, f"{c.id} {c['titre']}", desc, actif="clausier/",
                   jsonld=ld)

    def segment(self, s):
        r = "../../../"
        meta, body = clausier.load_page(ROOT / "content/segments" / f"{s['slug']}.md")
        def remplace(m):
            return "\n\n" + self.liste_section(m.group(1), r) + "\n\n"
        body = re.sub(r'\[([^\]]+)\]\(#_bookmark0\)', r"\1", body)  # signet ODT sans cible (D-05)
        parts = re.split(r'(<!-- clauses section="[^"]+" -->)', body)
        rendu = "".join(
            (self.liste_section(re.search(r'"(.+)"', p).group(1), r) if p.startswith("<!--") else md(p))
            for p in parts)
        page = f"""
<p class="fil"><a href="{r}clausier/">Clauses</a></p>
<h1>{s["numero"]}. {esc(s["libelle"])}</h1>
<p class="discret">Titre dans le V2 : {esc(meta["titre_source"])}</p>
<div class="contenu texte-large">{rendu}</div>
"""
        self.write(f"clausier/segments/{s['slug']}/", page, s["libelle"], actif="clausier/")

    def page_md(self, rel, src, titre, intro="", actif=""):
        meta, body = clausier.load_page(src)
        self.write(rel, f'<div class="texte contenu"><h1>{esc(titre)}</h1>{intro}{md(body)}</div>',
                   titre, meta.get("description", ""), actif)

    def pages(self):
        P = ROOT / "content/pages"
        S = ROOT / "content/site"
        for name, titre, actif in [("mode-emploi", "Mode d'emploi", "mode-emploi/"),
                                   ("methodologie", "Méthodologie", ""),
                                   ("contribuer", "Contribuer", "contribuer/"),
                                   ("mentions-legales", "Mentions légales", "")]:
            self.page_md(f"{name}/", S / f"{name}.md", titre, actif=actif)
        src_note = '<p class="discret">Texte du Clausier Numérique Responsable V2.</p>'
        self.page_md("comment-lire/", P / "comment-lire.md", "Comment lire le clausier", src_note)
        self.page_md("sources/", P / "sources-documentaires.md", "Sources documentaires", src_note)
        _, enjeux = clausier.load_page(P / "enjeux-et-objectifs.md")
        _, approche = clausier.load_page(P / "approche.md")
        self.write("a-propos/", f'<div class="texte contenu"><h1>À propos du clausier</h1>{src_note}'
                   f'<h2>Enjeux et objectifs</h2>{md(enjeux)}<h2>L\'approche</h2>{md(approche)}</div>',
                   "À propos", actif="a-propos/")
        # lexique
        lex = clausier.load_yaml("lexique.yml")
        cats, html_lex = [], []
        for t in lex["termes"]:
            if t["categorie"] not in cats:
                cats.append(t["categorie"])
        for cat in cats:
            items = "".join(f"<dt>{esc(t['terme'] or '')}</dt><dd>{md(t['definition'])[3:-4]}</dd>"
                            for t in lex["termes"] if t["categorie"] == cat)
            html_lex.append(f"<h2>{esc(cat)}</h2><dl class=\"lexique\">{items}</dl>")
        self.write("lexique/", f'<div class="texte contenu"><h1>Lexique</h1>{src_note}'
                   f'<p>{esc(lex["introduction"])}</p>{"".join(html_lex)}</div>', "Lexique")
        # crédits
        _, remerciements = clausier.load_page(P / "remerciements.md")
        lic = self.meta["licence_contenu"]
        self.write("credits/", f"""<div class="texte contenu"><h1>Crédits</h1>
<h2>Clausier Numérique Responsable V2</h2>
<p>Coordination : French Tech Corporate Community (FTCC) et Institut du Numérique Responsable (INR).</p>
<h3>Remerciements (texte du V2)</h3>
{md(remerciements)}
<h2>Classeur Excel</h2>
<p><b>Paul Saulnier</b> — Contribution initiale à la structuration et à la préparation du classeur
Excel du Clausier Numérique Responsable V2. Le classeur et le site reprennent son modèle de
colonnes, son classement par segment, sous-segment et phase, et son lexique catégorisé.</p>
<h2 id="reutiliser">Réutiliser le clausier</h2>
<p>{esc(lic["mention"])}</p>
<p>Vous pouvez copier, adapter, modifier et diffuser les clauses, y compris dans un cadre
commercial (marchés, prestations de conseil, outils), à condition de <b>citer la source</b>, de
fournir le lien vers la licence et d'indiquer si vous avez modifié le texte.
<a href="{lic["url"]}">Texte de la licence {lic["court"]}</a></p>
<p>Formule à reprendre :</p>
<blockquote><p>{esc(lic["attribution"])}</p></blockquote>
<p>Pour une clause adaptée, ajoutez par exemple « d'après la clause CLD-Q-01, modifiée ».</p>
<p class="discret">Le PDF du V2 d'origine porte encore la mention « CC BY-NC-ND 4.0 » ; la licence
CC BY 4.0 s'applique au clausier diffusé ici.</p>
<h2>Site</h2>
<p>Site statique généré à partir des sources Markdown du clausier, sans cookie, sans
police téléchargée, sans service tiers. Couleurs inspirées de la charte de l'INR.</p>
</div>""", "Crédits")
        # versions
        chg = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        chg = re.sub(r"\A# .*\n", "", chg)
        self.write("versions/", f'<div class="texte contenu"><h1>Historique des versions</h1>{md(chg)}</div>',
                   "Historique des versions")

    def selection(self):
        body = f"""
<h1>Ma sélection</h1>
<div id="selection" data-donnees="../donnees/clauses.json" data-racine="../">
<p id="sel-etat" class="resultat" aria-live="polite"></p>
<div id="sel-vide" class="vide-selection">
<p>Aucune clause retenue pour l'instant. Parcourez <a href="../clausier/">les clauses</a> et
cochez « Retenir » sur celles qui servent votre consultation.</p>
<p class="discret">La sélection est enregistrée dans ce navigateur uniquement.</p>
</div>
<div id="sel-actions" class="actions" hidden>
<button type="button" class="bouton" id="exp-md">Exporter en Markdown</button>
<button type="button" class="bouton second" id="exp-csv">Exporter en CSV (Excel, LibreOffice)</button>
<button type="button" class="bouton second" id="exp-txt">Exporter en texte</button>
<button type="button" class="bouton second" id="exp-print">Imprimer ou enregistrer en PDF</button>
<button type="button" class="bouton second" id="sel-vider">Vider la sélection</button>
</div>
<div id="sel-liste"></div>
</div>
<noscript><p>Cette page a besoin de JavaScript. Sans JavaScript, utilisez le
<a href="../telechargements/{NOM_EXCEL}">classeur Excel</a>.</p></noscript>
"""
        self.write("selection/", body, "Ma sélection", actif="selection/")

    def donnees(self):
        champ = {r["titre"]: r["champ"] for r in clausier.load_yaml("colonnes.yml")["rubriques"]}
        champs = clausier.load_yaml("colonnes.yml")["champs"]
        d = {
            "titre": self.meta["titre"] + " V" + self.meta["version"],
            "source": "Clausier Numérique Responsable V" + self.meta["version"] + ", FTCC et INR",
            "licence": self.meta["licence_contenu"]["mention"] + " À citer : "
                       + self.meta["licence_contenu"]["attribution"],
            "champs": champ,
            "colonnes_csv": [[k, v] for k, v in champs.items()],
            "clauses": [{
                "id": c.id, "titre": c["titre"], "segment": self.seg_by[c["segment"]]["libelle"],
                "sous_segment": self.sous(c), "phase": self.phase(c), "section": c["section"],
                "url": f"clausier/clauses/{c.id}/",
                "rubriques": [[t, m] for t, m in c.rubriques], "notes": c.notes,
            } for c in self.clauses],
        }
        p = self.out / "donnees/clauses.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    def robots_et_ia(self):
        """robots.txt, sitemap.xml, llms.txt (index) et llms-full.txt (texte intégral)."""
        base = self.meta["liens"]["site"]
        lic = self.meta["licence_contenu"]
        pages = sorted(p.relative_to(self.out).parent.as_posix() for p in self.out.rglob("index.html"))
        pages = ["" if p == "." else p + "/" for p in pages if p not in ("selection",)]
        robots = ["# Clausier Numérique Responsable : contenu sous licence CC BY 4.0, à citer.",
                  "User-agent: *", "Allow: /", "", "# Index pour les moteurs génératifs : /llms.txt",
                  "# Texte intégral du clausier : /llms-full.txt"]
        if base:
            robots += ["", f"Sitemap: {base}sitemap.xml"]
            urls = "".join(f"<url><loc>{base}{p}</loc></url>" for p in pages)
            (self.out / "sitemap.xml").write_text(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
                encoding="utf-8")
        (self.out / "robots.txt").write_text("\n".join(robots) + "\n", encoding="utf-8")
        b = base or ""
        idx = [f"# {self.meta['titre']} V{self.meta['version']}", "",
               f"> {DESC}", "",
               "Bibliothèque de clauses prérédigées : chaque organisation y prend ce qu'elle juge "
               "nécessaire et l'adapte à son contexte (consultation, RFI, RFP, cahier des charges, contrat). "
               "Chaque clause propose deux niveaux : Niveau 1 (Must have) et Niveau 2 (Nice to have).", "",
               f"Licence : {lic['nom']}. Citer : {lic['attribution']}", "",
               "## Documents", "",
               f"- [Texte intégral de toutes les clauses (Markdown)]({b}llms-full.txt)",
               f"- [Classeur Excel]({b}telechargements/{NOM_EXCEL})",
               f"- [Document PDF V2, qui fait foi]({b}telechargements/{PDF_V2.name})",
               f"- [Données JSON]({b}donnees/clauses.json)",
               f"- [Comment lire le clausier]({b}comment-lire/)",
               f"- [Page officielle sur institutnr.org]({self.meta['liens']['page_inr']})"]
        if self.meta["depot"]["url"]:
            idx.append(f"- [Sources sur GitHub]({self.meta['depot']['url']})")
        full = [f"# {self.meta['titre']} V{self.meta['version']} — texte intégral", "",
                f"> {lic['mention']} Citer : {lic['attribution']}", ""]
        for s_ in self.segs["segments"]:
            idx += ["", f"## {s_['numero']}. {s_['libelle']}", ""]
            full += [f"# {s_['titre_source']}", ""]
            for sec in s_["sections"]:
                full += [f"## {sec['titre_source']}", ""]
                for c in (x for x in self.clauses if x["section"] == sec["numero"]):
                    idx.append(f"- [{c.id} — {c['titre']}]({b}clausier/clauses/{c.id}/): {self.phase(c)}")
                    full += [f"### {c.id} — {c['titre']}", "",
                             f"Segment : {s_['libelle']}{' / ' + self.sous(c) if self.sous(c) else ''}. "
                             f"Partie : {self.phase(c)}. Adresse : {b}clausier/clauses/{c.id}/", ""]
                    for t, m in c.rubriques:
                        full += [f"#### {t}", "", m, ""]
                    full += [f"[^{n}]: {t}" for n, t in c.notes.items()]
                    if c.notes:
                        full.append("")
        (self.out / "llms.txt").write_text("\n".join(idx) + "\n", encoding="utf-8")
        (self.out / "llms-full.txt").write_text("\n".join(full) + "\n", encoding="utf-8")

    def build(self):
        if self.out.exists():
            shutil.rmtree(self.out)
        self.out.mkdir(parents=True)
        shutil.copytree(ASSETS, self.out / "assets")
        dl = self.out / "telechargements"
        dl.mkdir()
        if EXCEL.exists():
            shutil.copy2(EXCEL, dl / NOM_EXCEL)
        shutil.copy2(PDF_V2, dl / PDF_V2.name)
        self.accueil()
        self.catalogue()
        for i, c in enumerate(self.clauses):
            self.fiche(i, c)
        for s in self.segs["segments"]:
            self.segment(s)
        self.pages()
        self.selection()
        self.donnees()
        self.write("404.html", '<div class="texte"><h1>Page introuvable</h1><p>Cette adresse ne '
                   'correspond à aucune page. Les clauses sont listées dans le '
                   '<a href="clausier/">catalogue</a>.</p></div>', "Page introuvable")
        self.robots_et_ia()
        (self.out / ".nojekyll").write_text("", encoding="utf-8")
        shutil.copy2(ROOT / "site/htaccess", self.out / ".htaccess")
        return len(list(self.out.rglob("*.html")))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist/site"))
    a = ap.parse_args()
    n = Site(Path(a.out)).build()
    print(f"{n} pages -> {Path(a.out)}")
