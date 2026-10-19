# -*- coding: utf-8 -*-
"""Migration initiale : ODT V2 -> fichiers Markdown du dossier content/.

À n'exécuter qu'une fois, au moment de la reprise. Après la migration, le Markdown
devient la source éditoriale et ce script ne doit plus être relancé sur un dépôt
où des clauses ont été modifiées : il écraserait les modifications. Il refuse donc
d'écrire si content/clauses/ contient déjà des fichiers, sauf option --force.

Règles appliquées :
- le texte de chaque cellule est repris tel quel (gras, italique, listes, liens,
  exposants, notes) ; aucune correction orthographique ou rédactionnelle ;
- l'identifiant est attribué une fois pour toutes (voir docs/modele-documentaire.md) ;
- le segment, le sous-segment et la phase reprennent la structure de l'ODT ;
  les sous-segments « Bureautiques / Data centers / Transverse » du segment
  Matériels viennent du classeur de préparation de Paul Saulnier ;
- les écarts avec le classeur Excel sont consignés dans chaque clause.

Usage : python scripts/migrate.py [--force]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import audit_compare  # noqa: E402
import odt_extract  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ODT = ROOT / "sources/originaux/clausier-numerique-responsable-v2.odt"
PDF = ROOT / "sources/originaux/clausier-numerique-responsable-v2.pdf"
CONTENT = ROOT / "content"
DATA = ROOT / "data"

# section de l'ODT -> (segment, préfixe d'identifiant, phase, sous-segment)
SECTIONS = {
    "1.1": ("commun", "COM-Q", "questionnaire", None),
    "1.2": ("commun", "COM-E", "exigences", None),
    "2.1": ("materiels", "MAT-Q", "questionnaire", "excel"),
    "2.2": ("materiels", "MAT-E", "exigences", "excel"),
    "3.2": ("cloud", "CLD-Q", "questionnaire", None),
    "3.3": ("cloud", "CLD-E", "exigences", None),
    "4.1": ("logiciels", "LOG-Q", "questionnaire", None),
    "4.2": ("logiciels", "LOG-E", "exigences", None),
    "5.1.1": ("prestations", "DEV-Q", "questionnaire", "developpement-integration-tma"),
    "5.1.2": ("prestations", "DEV-E", "exigences", "developpement-integration-tma"),
    "5.2.1": ("prestations", "INF-Q", "questionnaire", "infogerance-bureautique"),
    "6.3": ("ia", "IA-Q", "questionnaire", "ia-pret-a-l-emploi"),
    "6.4": ("ia", "IA-Q", "questionnaire", "ia-modeles-fondationnels"),
    "6.5": ("ia", "IA-Q", "questionnaire", "ia-infrastructure"),
}
EXCEL_SOUS_SEGMENT = {"Bureautiques": "bureautique", "Data centers": "datacenter",
                      "- Transverse -": "materiels-transverse"}
EXCEL_PHASE = {"RFI/RFP": "questionnaire", "CCAP & CCTP": "exigences"}


def header_label(h):
    """« Niveau 1(Must have) » -> « Niveau 1 (Must have) » : saut de ligne de l'en-tête."""
    return re.sub(r"(Niveau \d)\s*\(", r"\1 (", h)


def pdf_pages():
    pages = []
    for p in range(1, 45):
        t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-raw", str(PDF), "-"],
                           capture_output=True, text=True, check=True).stdout
        pages.append(audit_compare.letters(re.sub(r"Page \d+ / \d+", "", t)))
    return pages


def find_page(pages, cells, start):
    """Première page >= start contenant le début du texte de la ligne."""
    for c in cells:
        key = audit_compare.letters(audit_compare.md_to_text(c))[:25]
        if len(key) < 12:
            continue
        for i in range(start - 1, len(pages)):
            if key in pages[i]:
                return i + 1
    return None


def yaml_dump(d):
    return yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100)


def footnotes(notes):
    return "".join(f"\n[^{n}]: {t}" for n, t in notes)


def write(path, front, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{yaml_dump(front)}---\n\n{body.strip()}\n", encoding="utf-8")


def main(force=False):
    if any((CONTENT / "clauses").rglob("*.md")) and not force:
        sys.exit("content/clauses contient déjà des clauses : migration refusée (--force pour écraser).")
    events = odt_extract.read(ODT)
    comparison = audit_compare.main()
    by_odt = {(it["odt"]["table"], it["odt"]["ligne"]): it for it in comparison if it["odt"]}
    pages = pdf_pages()

    counters, ordres, page, clauses = {}, {}, 1, []
    for e in events:
        if e[0] != "table" or not e[1]["headers"]:
            continue
        t = e[1]
        section = t["headings"][-1].split()[0]
        segment, prefix, phase, sous = SECTIONS[section]
        headers = [header_label(h) for h in t["headers"]]
        for i, row in enumerate(t["rows"], start=1):
            counters[prefix] = counters.get(prefix, 0) + 1
            ordres[section] = ordres.get(section, 0) + 1
            cid = f"{prefix}-{counters[prefix]:02d}"
            found = find_page(pages, [c["md"] for c in row[1:]], page)
            page = found or page
            it = by_odt[(t["name"], i)]
            xl = it["excel"]
            sous_segment = sous
            if sous == "excel":
                sous_segment = EXCEL_SOUS_SEGMENT[xl["Sous segment"]]
            titre = audit_compare.md_to_text(row[0]["md"])
            front = {
                "id": cid,
                "titre": titre,
                "segment": segment,
                "sous_segment": sous_segment,
                "phase": phase,
                "section": section,
                "ordre": ordres[section],
                "statut": "validee",
                "version": "2.0",
                "source": {
                    "document": ODT.name,
                    "section": section,
                    "tableau": t["name"],
                    "ligne": i,
                    "page_pdf": page,
                    "colonnes": headers,
                },
            }
            if found is None:
                front["source"]["page_pdf_estimee"] = True
            merged = [headers[k] for k, c in enumerate(row) if "covered_by_row" in c]
            if merged:
                front["source"]["cellules_fusionnees"] = merged
            front["excel_preparation"] = excel_info(it, phase, headers)
            parts = [f"# {titre}"]
            notes = []
            for h, c in zip(headers[1:], row[1:]):
                if c["md"].strip():
                    parts.append(f"## {h}\n\n{c['md']}")
                notes += c["notes"]
            notes = list(dict.fromkeys(row[0]["notes"] + notes))
            body = "\n\n".join(parts) + ("\n" + footnotes(notes) if notes else "")
            path = CONTENT / "clauses" / segment / f"{cid}.md"
            write(path, front, body)
            clauses.append(cid)
    write_pages(events)
    print(f"{len(clauses)} clauses écrites dans content/clauses/")


def excel_info(it, phase, headers):
    xl = it["excel"]
    if xl is None:
        return {"ligne": None, "ecarts": ["Clause absente du classeur de préparation."]}
    ecarts = []
    xl_phase = EXCEL_PHASE.get(xl["Phase"])
    if xl_phase != phase:
        ecarts.append(f"Phase « {xl['Phase']} » dans le classeur ; la clause figure dans la "
                      f"partie {'questionnaire' if phase == 'questionnaire' else 'exigences'} de l'ODT.")
    forme = []
    for cell, c in zip(it["odt"]["cells"], it["comparaison"]):
        label = header_label(c["entete_odt"])
        if c["statut"] == "contenu":
            ecarts.append(f"{label} : texte différent dans la colonne « {c['colonne_excel']} » "
                          f"du classeur : « {short(xl[c['colonne_excel']])} ».")
        elif c["statut"] == "forme":
            forme.append(label)
        elif c["statut"] == "vide" and cell["text"]:
            ecarts.append(f"{label} : absent du classeur.")
    used = {c["colonne_excel"] for c in it["comparaison"]}
    for cell, c in zip(it["odt"]["cells"], it["comparaison"]):
        if cell["text"] and c["colonne_excel"] and list(used).count(c["colonne_excel"]) > 1:
            pass
    info = {"ligne": xl["ligne_excel"], "segment": xl["Segment"],
            "sous_segment": xl["Sous segment"] or None, "phase": xl["Phase"]}
    if forme:
        info["ecarts_de_forme"] = forme
    if ecarts:
        info["ecarts"] = ecarts
    return info


def short(s, n=160):
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


# ---------------------------------------------------------------- pages hors clauses

PAGES = {
    "REMERCIEMENTS": "remerciements",
    "SOMMAIRE": "sommaire",  # table des matières générée : aucun texte à reprendre
    "ENJEUX ET OBJECTIFS": "enjeux-et-objectifs",
    "L’APPROCHE": "approche",
    "COMMENT LIRE LE CLAUSIER NUMÉRIQUE RESPONSABLE ?": "comment-lire",
    "SOURCES DOCUMENTAIRES": "sources-documentaires",
    "LEXIQUE": "lexique",
}
SEGMENT_OF = {"1.": "commun", "2.": "materiels", "3.": "cloud", "4.": "logiciels",
              "5.": "prestations", "6.": "ia"}


def write_pages(events):
    """Textes hors tableaux : pages éditoriales et introductions de segments."""
    current = "couverture"
    buckets, order = {current: {"titre": "Page de couverture", "blocs": [], "notes": []}}, [current]
    for e in events:
        if e[0] == "h":
            _, level, txt = e
            if level == 1:
                key = PAGES.get(txt) or SEGMENT_OF.get(txt.split()[0])
                current = key
                if key not in buckets:
                    buckets[key] = {"titre": txt, "blocs": [], "notes": []}
                    order.append(key)
            else:
                buckets[current]["blocs"].append("#" * level + " " + txt)
        elif e[0] == "p":
            buckets[current]["blocs"].append(e[1])
            buckets[current]["notes"] += e[2]
        elif e[0] == "table" and not e[1]["headers"]:
            # tableau de mise en page des remerciements
            for c in e[1]["rows"][0]:
                if c["md"]:
                    buckets[current]["blocs"].append(c["md"])
        elif e[0] == "table":
            section = e[1]["headings"][-1].split()[0]
            marker = f'<!-- clauses section="{section}" -->'
            if marker not in buckets[current]["blocs"]:
                buckets[current]["blocs"].append(marker)
    for key in order:
        b = buckets[key]
        if not b["blocs"]:
            continue
        if key == "lexique":
            write_lexique(b)
            continue
        target = (CONTENT / "segments" / f"{key}.md") if key in SEGMENT_OF.values() \
            else (CONTENT / "pages" / f"{key}.md")
        front = {"titre_source": b["titre"], "source": {"document": ODT.name}}
        body = "\n\n".join(b["blocs"]) + ("\n" + footnotes(b["notes"]) if b["notes"] else "")
        write(target, front, body)


def write_lexique(b):
    """Lexique de l'ODT -> data/lexique.yml ; mentions finales -> pages/licence.md."""
    entries, cat, tail = [], None, []
    for bloc in b["blocs"]:
        if bloc.startswith("- "):
            for line in bloc.split("\n"):
                m = re.match(r"- \*\*(.+?)\*\*\s*(.*)$", line)
                if not m:
                    entries.append({"terme": None, "definition": line[2:], "categorie": cat,
                                    "a_verifier": True})
                    continue
                term, rest = m.group(1).strip(), m.group(2)
                # cas « **ESS (Économie Sociale et Solidair**e) structures… »
                tm = re.match(r"^(\S*\))\s*(.*)$", rest)
                if tm and term.count("(") > term.count(")"):
                    term, rest = term + tm.group(1), tm.group(2)
                rest = re.sub(r"^:\s*", "", rest.strip())
                entries.append({"terme": term, "definition": rest, "categorie": cat})
        elif not bloc.startswith("Pour faciliter") and len(bloc) < 60 and "\n" not in bloc \
                and not bloc.startswith(("**", ".", "visit", "d")):
            cat = bloc
        elif b["blocs"].index(bloc) > 1:
            tail.append(bloc)
    intro = b["blocs"][0]
    DATA.mkdir(exist_ok=True)
    (DATA / "lexique.yml").write_text(
        "# Lexique du clausier, repris de l'ODT V2 (section LEXIQUE).\n"
        + yaml_dump({"introduction": intro, "termes": entries}), encoding="utf-8")
    write(CONTENT / "pages" / "licence.md",
          {"titre_source": "Mentions finales du document", "source": {"document": ODT.name}},
          "\n\n".join(tail))


if __name__ == "__main__":
    main(force="--force" in sys.argv)
