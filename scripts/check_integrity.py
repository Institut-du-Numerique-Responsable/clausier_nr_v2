# -*- coding: utf-8 -*-
"""Rapport d'intégrité : le Markdown reprend-il tout le document V2, sans perte ?

Contrôles :
1. chaque ligne de tableau de l'ODT correspond à une et une seule clause
   (source.tableau + source.ligne) ;
2. le texte de chaque cellule est identique au Markdown de la clause
   (comparaison exacte du Markdown produit par odt_extract) ;
   une clause portant un journal « modifications » est signalée comme modifiée,
   pas comme erronée ;
3. chaque paragraphe hors tableau de l'ODT se retrouve dans content/pages,
   content/segments ou data/lexique.yml ;
4. chaque mot de chaque clause figure dans le PDF V2 (contrôle du rendu).

Écrit docs/audit/rapport-integrite.md. Code de sortie 1 si une perte est détectée.
Dépendances : lxml, PyYAML, poppler (pdftotext).

Usage : python scripts/check_integrity.py
"""
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import clausier  # noqa: E402
import odt_extract  # noqa: E402
from audit_compare import letters, md_to_text  # noqa: E402

ROOT = clausier.ROOT
ODT = ROOT / "sources/originaux/clausier-numerique-responsable-v2.odt"
PDF = ROOT / "sources/originaux/clausier-numerique-responsable-v2.pdf"
REPORT = ROOT / "docs/audit/rapport-integrite.md"


def header_label(h):
    return re.sub(r"(Niveau \d)\s*\(", r"\1 (", h)


def words(s):
    return set(re.findall(r"\w{3,}", md_to_text(s).lower()))


def main():
    events = odt_extract.read(ODT)
    clauses = clausier.load_clauses()
    by_src = {}
    for c in clauses:
        src = c["source"] or {}
        if src.get("tableau"):
            by_src.setdefault((src["tableau"], src["ligne"]), []).append(c)

    rows_total, identical, modified, losses, extra = 0, 0, [], [], []
    seen = set()
    for e in events:
        if e[0] != "table" or not e[1]["headers"]:
            continue
        t = e[1]
        headers = [header_label(h) for h in t["headers"]]
        for i, row in enumerate(t["rows"], start=1):
            rows_total += 1
            found = by_src.get((t["name"], i), [])
            if len(found) != 1:
                losses.append(f"{t['name']} ligne {i} : {len(found)} clause(s) correspondante(s)")
                continue
            c = found[0]
            seen.add(c.id)
            diffs = []
            if md_to_text(row[0]["md"]) != c["titre"]:
                diffs.append(f"titre : « {c['titre']} »")
            for h, cell in zip(headers[1:], row[1:]):
                if cell["md"].strip() != c.rubrique(h).strip():
                    diffs.append(h)
            known = set(headers[1:])
            for h, _ in c.rubriques:
                if h not in known:
                    diffs.append(f"rubrique ajoutée : {h}")
            if not diffs:
                identical += 1
            elif c["modifications"]:
                modified.append((c.id, diffs))
            else:
                losses.append(f"{c.id} : texte différent de l'ODT sans modification consignée : "
                              + ", ".join(diffs))
    for c in clauses:
        if c.id not in seen:
            extra.append(f"{c.id} ({c['statut']}) : clause sans équivalent dans le V2")

    # paragraphes hors tableaux
    corpus = []
    for p in list((ROOT / "content/pages").glob("*.md")) + list((ROOT / "content/segments").glob("*.md")):
        meta, body = clausier.load_page(p)
        corpus += [meta.get("titre_source", ""), body]
    lex = clausier.load_yaml("lexique.yml")
    corpus.append(lex["introduction"])
    corpus += [f"{t['terme'] or ''} {t['definition']}" for t in lex["termes"]]
    corpus += sorted({t["categorie"] for t in lex["termes"] if t["categorie"]})
    corpus = letters(" ".join(md_to_text(x) for x in corpus))
    para_total, para_missing = 0, []
    for e in events:
        if e[0] == "p":
            para_total += 1
            for line in e[1].split("\n"):
                if letters(md_to_text(line)) not in corpus:
                    para_missing.append(md_to_text(line)[:90])
        # le sommaire est régénéré par chaque livrable : il n'est pas repris
        if e[0] == "h" and e[2] != "SOMMAIRE" and letters(e[2]) not in corpus:
            para_missing.append("titre : " + e[2])

    # rendu PDF
    pdf = subprocess.run(["pdftotext", "-raw", str(PDF), "-"], capture_output=True, text=True,
                         check=True).stdout
    pdf = pdf.lower()
    pdf_words = set(re.findall(r"\w+", pdf))
    # césures : « nor- » en fin de ligne, la suite « mé » plus bas (tableaux en colonnes)
    prefixes = set(re.findall(r"(\w+)-\s*$", pdf, flags=re.M))

    def in_pdf(w):
        return w in pdf_words or any(w[:k] in prefixes and w[k:] in pdf_words
                                     for k in range(2, len(w) - 1))
    pdf_gaps = {}
    for c in clauses:
        if c.id not in seen:
            continue
        w = words(c["titre"] + " " + " ".join(md for _, md in c.rubriques))
        missing = sorted(x for x in w if not in_pdf(x))
        if missing:
            pdf_gaps[c.id] = missing

    statuts = Counter(c["statut"] for c in clauses)
    lines = [
        "# Rapport d'intégrité documentaire",
        "",
        f"Généré le {date.today().isoformat()} par `scripts/check_integrity.py`. Ne pas modifier à la main.",
        "",
        "Référence : `sources/originaux/clausier-numerique-responsable-v2.odt` (document maître V2) "
        "et son rendu `clausier-numerique-responsable-v2.pdf` (44 pages).",
        "",
        "## Synthèse",
        "",
        "| Contrôle | Résultat |",
        "|---|---|",
        f"| Lignes de tableaux du V2 | {rows_total} |",
        f"| Clauses Markdown | {len(clauses)} ({', '.join(f'{k} : {v}' for k, v in statuts.items())}) |",
        f"| Clauses identiques au V2, rubrique par rubrique | {identical} |",
        f"| Clauses modifiées avec journal de modifications | {len(modified)} |",
        f"| Pertes ou écarts non consignés | {len(losses)} |",
        f"| Clauses sans équivalent dans le V2 | {len(extra)} |",
        f"| Paragraphes hors tableaux du V2 | {para_total} |",
        f"| Paragraphes ou titres introuvables dans content/ | {len(para_missing)} |",
        f"| Clauses dont un mot manque dans le texte du PDF | {len(pdf_gaps)} |",
        "",
    ]
    if losses:
        lines += ["## Pertes ou écarts non consignés", ""] + [f"- {x}" for x in losses] + [""]
    if modified:
        lines += ["## Clauses modifiées (journal présent)", ""]
        lines += [f"- {cid} : {', '.join(d)}" for cid, d in modified] + [""]
    if extra:
        lines += ["## Clauses ajoutées depuis le V2", ""] + [f"- {x}" for x in extra] + [""]
    if para_missing:
        lines += ["## Textes hors tableaux introuvables", ""] + [f"- {x}" for x in para_missing] + [""]
    lines += ["## Contrôle du rendu PDF", ""]
    if pdf_gaps:
        lines += ["Mots présents dans le Markdown mais absents du texte extrait du PDF. "
                  "Les césures avec tiret sont recollées. Un mot coupé sans tiret dans une colonne "
                  "étroite (ex. « applic » / « atifs ») apparaît ici sans qu'il y ait de perte : "
                  "vérifier à l'œil à la page indiquée.", ""]
        page = {c.id: (c["source"] or {}).get("page_pdf") for c in clauses}
        lines += [f"- {cid} (page {page[cid]}) : {', '.join(m[:12])}{' …' if len(m) > 12 else ''}"
                  for cid, m in pdf_gaps.items()]
    else:
        lines += ["Tous les mots des clauses figurent dans le texte extrait du PDF."]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[8:20]))
    return 1 if (losses or para_missing) else 0


if __name__ == "__main__":
    sys.exit(main())
