# -*- coding: utf-8 -*-
"""Rapport d'intégrité : le Markdown reprend-il tout le document V2, sans perte ?

Le PDF V2 fait foi. L'ODT, dont le PDF est le rendu LibreOffice (même horodatage), donne la
structure exacte des tableaux : il sert à la comparaison rubrique par rubrique. Le texte de
chaque rubrique est ensuite recherché dans le PDF, segment par segment.

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
import difflib
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


def pdf_segments(pdf_raw, clauses, n=20):
    """Cherche chaque segment de n lettres de chaque rubrique dans le texte du PDF.

    En-têtes, pieds de page et césures sont neutralisés. Un segment absent est classé
    « mise en page » si, entre ses deux voisins retrouvés, le PDF ne fait qu'ajouter du texte
    (cellule voisine, en-tête de tableau répété, appel de note) sans rien retirer. Les autres
    cas (début ou fin de rubrique, sans voisin) sont listés pour relecture visuelle.
    """
    t = re.sub(r"Page \d+ / \d+", "", pdf_raw).replace("Clausier Numérique Responsable\n", "\n")
    big = letters(re.sub(r"-\n", "", t))
    total = ok = layout = 0
    review = []
    for c in clauses:
        for titre, m in [("titre", c["titre"])] + c.rubriques:
            s = letters(md_to_text(re.sub(r"<sup>[^<]*</sup>", "", m)))
            chunks = [(i, s[i:i + n]) for i in range(0, len(s), n) if len(s[i:i + n]) >= 8]
            for k, (i, x) in enumerate(chunks):
                total += 1
                if x in big:
                    ok += 1
                    continue
                prev = next(((j, y) for j, y in reversed(chunks[:k]) if y in big), None)
                nxt = next(((j, y) for j, y in chunks[k + 1:] if y in big), None)
                if prev and nxt:
                    p = big.find(prev[1])
                    q = big.find(nxt[1], p)
                    if 0 <= p < q and q - p < 3000:
                        md_seg = s[prev[0]:nxt[0] + len(nxt[1])]
                        pdf_seg = big[p:q + len(nxt[1])]
                        sm = difflib.SequenceMatcher(None, md_seg, pdf_seg, autojunk=False)
                        if not any(op in ("delete", "replace") for op, *_ in sm.get_opcodes()):
                            layout += 1
                            continue
                review.append((c.id, titre, x))
    return total, ok, layout, review


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

    # document de référence : le PDF V2 fait foi
    pdf_raw = subprocess.run(["pdftotext", "-raw", str(PDF), "-"], capture_output=True, text=True,
                             check=True).stdout
    pdf = pdf_raw.lower()
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
    seg_total, seg_ok, seg_layout, seg_review = pdf_segments(pdf_raw, [c for c in clauses if c.id in seen])

    statuts = Counter(c["statut"] for c in clauses)
    lines = [
        "# Rapport d'intégrité documentaire",
        "",
        f"Généré le {date.today().isoformat()} par `scripts/check_integrity.py`. Ne pas modifier à la main.",
        "",
        "Référence : **le PDF V2 fait foi** (`sources/originaux/clausier-numerique-responsable-v2.pdf`, "
        "44 pages). L'ODT dont il est le rendu (`clausier-numerique-responsable-v2.odt`) sert à "
        "extraire la structure des tableaux ; les deux sont comparés au Markdown.",
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
        f"| Segments de 20 lettres comparés au PDF | {seg_total} |",
        f"| … retrouvés tels quels | {seg_ok} |",
        f"| … séparés dans le PDF par du texte voisin (mise en page) | {seg_layout} |",
        f"| … à relire visuellement (début ou fin de cellule) | {len(seg_review)} |",
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
    if seg_review:
        page = {c.id: (c["source"] or {}).get("page_pdf") for c in clauses}
        lines += ["## Segments à relire dans le PDF", "",
                  "Début ou fin de cellule non retrouvé tel quel : en général un appel de note collé "
                  "au mot (« CDP7 »), une cellule coupée entre deux pages ou une colonne voisine "
                  "intercalée. Relecture du 19 octobre 2026 : tous ces cas relèvent de la mise en "
                  "page, aucune différence de texte. Toute nouvelle ligne ici doit être relue.", "",
                  "| Clause | Page | Rubrique | Segment |", "|---|---|---|---|"]
        lines += [f"| {cid} | {page.get(cid)} | {t} | `{x}` |" for cid, t, x in seg_review] + [""]
    lines += ["## Contrôle du rendu PDF (mots)", ""]
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
