# -*- coding: utf-8 -*-
"""Audit : compare ligne à ligne les tableaux de l'ODT et le classeur Excel de préparation.

Produit build/audit/comparaison.json. Ne modifie aucune source.

Méthode :
1. chaque ligne de tableau de l'ODT est une clause candidate ;
2. chaque ligne du tableau « Tableau1 » de la feuille Clausier de l'Excel aussi ;
3. on aligne les deux séquences sur le texte complet de la ligne ;
4. pour chaque cellule de l'ODT, on cherche la colonne Excel qui la contient
   et on classe l'écart : identique, différence de mise en forme seulement
   (espaces, tirets, puces, retours ligne), ou différence de contenu.
"""
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).parent))
import odt_extract  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ODT = ROOT / "sources/originaux/clausier-numerique-responsable-v2.odt"
XLSX = ROOT / "sources/originaux/clausier-nr-v2-prepa-excel-paul-saulnier.xlsx"
OUT = ROOT / "build/audit/comparaison.json"

EXCEL_COLS = ["Critère", "Commentaire", "Exigences", "Livrables", "Questions",
              "Niveau 1", "Niveau 2", "Segment", "Sous segment", "Phase"]
CONTENT_COLS = EXCEL_COLS[:7]


def md_to_text(s):
    s = re.sub(r"\[\^\d+\]", "", s)
    s = re.sub(r"</?sup>", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = s.replace("**", "").replace("*", "")
    s = re.sub(r"^\s*- ", "", s, flags=re.M)
    return odt_extract.plain(s)


def letters(s):
    """Empreinte insensible à la mise en forme : lettres et chiffres seulement."""
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(ch for ch in s if ch.isalnum())


def classify(a, b):
    if odt_extract.plain(a) == odt_extract.plain(b):
        return "identique"
    if letters(a) == letters(b):
        return "forme"
    return "contenu"


def odt_rows():
    events = odt_extract.read(ODT)
    rows = []
    for e in events:
        if e[0] != "table" or not e[1]["headers"]:
            continue
        t = e[1]
        for i, r in enumerate(t["rows"]):
            rows.append({
                "table": t["name"], "section": t["headings"][-1], "ligne": i + 1,
                "cells": [{"entete": h, "text": md_to_text(c["md"]),
                           "fusion": "covered_by_row" in c}
                          for h, c in zip(t["headers"], r)],
            })
    return rows


def excel_rows():
    wb = openpyxl.load_workbook(XLSX)
    ws = wb["Clausier"]
    rows = []
    for r in range(3, ws.max_row + 1):
        vals = {h: (ws.cell(r, i + 1).value or "") for i, h in enumerate(EXCEL_COLS)}
        rows.append({"ligne_excel": r, **{k: str(v) for k, v in vals.items()}})
    return rows


def row_key(text):
    return letters(text)[:4000]


def main():
    o, x = odt_rows(), excel_rows()
    ok = [row_key(" ".join(c["text"] for c in r["cells"])) for r in o]
    xk = [row_key(" ".join(r[c] for c in CONTENT_COLS)) for r in x]
    # alignement par meilleure similarité, en conservant l'ordre
    sm = difflib.SequenceMatcher(None, ok, xk, autojunk=False)
    pairs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            pairs += [(i, j) for i, j in zip(range(i1, i2), range(j1, j2))]
        else:
            js = list(range(j1, j2))
            for i in range(i1, i2):
                best = max(js, key=lambda j: difflib.SequenceMatcher(None, ok[i], xk[j]).ratio(),
                           default=None)
                if best is not None and difflib.SequenceMatcher(None, ok[i], xk[best]).ratio() > 0.6:
                    pairs.append((i, best))
                    js.remove(best)
                else:
                    pairs.append((i, None))
            pairs += [(None, j) for j in js]
    result = []
    for i, j in pairs:
        item = {"odt": o[i] if i is not None else None, "excel": x[j] if j is not None else None}
        if i is not None and j is not None:
            comp = []
            for c in o[i]["cells"]:
                if not c["text"]:
                    best = None
                else:
                    best = max(CONTENT_COLS, key=lambda col: difflib.SequenceMatcher(
                        None, letters(c["text"]), letters(x[j][col])).ratio())
                comp.append({"entete_odt": c["entete"], "colonne_excel": best,
                             "statut": classify(c["text"], x[j][best]) if best else
                             ("vide" if not any(x[j][k] for k in []) else "vide")})
            used = {c["colonne_excel"] for c in comp if c["colonne_excel"]}
            extra = [col for col in CONTENT_COLS if col not in used and x[j][col].strip()]
            item["comparaison"] = comp
            item["colonnes_excel_sans_equivalent"] = extra
        result.append(item)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    return result


if __name__ == "__main__":
    res = main()
    print(f"{len(res)} paires écrites dans {OUT.relative_to(ROOT)}")
