# -*- coding: utf-8 -*-
"""Génère dist/excel/Clausier-Numerique-Responsable-V2.xlsx à partir du Markdown.

Le classeur reprend le modèle du classeur de préparation de Paul Saulnier (colonnes
Critère, Commentaire, Exigences, Livrables, Questions, Niveau 1, Niveau 2, Segment,
Sous segment, Phase ; tableaux structurés ; lexique catégorisé) et ajoute :
identifiants, sélection des clauses, regroupement automatique des clauses retenues,
références et crédits.

Fonctions Excel utilisées : IF, COUNTIF, INDEX, MATCH, IFERROR (Excel 2007 et suivants,
LibreOffice Calc). Aucune macro.

Le fichier est reproductible : deux générations à partir du même contenu donnent le
même fichier, octet pour octet.

Usage : python scripts/build_excel.py [--selection ID,ID,...] [--out chemin]
        --selection pré-coche des clauses (tests).
"""
import argparse
import io
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

sys.path.insert(0, str(Path(__file__).parent))
import clausier  # noqa: E402

ROOT = clausier.ROOT
OUT = ROOT / "dist/excel/Clausier-Numerique-Responsable-V2.xlsx"
FIXED_DATE = datetime(2026, 8, 1)  # date fixe : fichier reproductible

FONT = "Arial"
BLEU = "194F6E"      # bleu INR (institutnr.org, --ascension-blue)
ENCRE = "173B4F"
SAISIE = "FFF2CC"    # cellules à remplir par l'utilisateur
F_BASE = Font(name=FONT, size=10)
F_BOLD = Font(name=FONT, size=10, bold=True)
F_TITLE = Font(name=FONT, size=16, bold=True, color=BLEU)
F_H2 = Font(name=FONT, size=12, bold=True, color=ENCRE)
F_LINK = Font(name=FONT, size=10, color="0563C1", underline="single")
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Border(bottom=Side(style="thin", color="D8E3E6"))

CATALOGUE = "Catalogue"
SELECTION = "Sélection"
RETENUES = "Clauses retenues"
DONNEES = "Données"
MARQUE = "¶"   # remplace les sauts de ligne dans la feuille Données (voir sheet_donnees)
CHAMPS = ["commentaire", "exigences", "livrables", "questions", "niveau_1", "niveau_2"]


def rows_for(clauses):
    segs = clausier.segments()
    colonnes = clausier.load_yaml("colonnes.yml")
    champ_of = {r["titre"]: r["champ"] for r in colonnes["rubriques"]}
    seg_by = {s["slug"]: s for s in segs["segments"]}
    phases = segs["phases"]
    titles = [c["titre"] for c in clauses]
    out = []
    for c in clauses:
        seg = seg_by[c["segment"]]
        sous = {s["slug"]: s["libelle"] for s in seg["sous_segments"]}.get(c["sous_segment"], "")
        vals = {k: "" for k in CHAMPS}
        for titre, md in c.rubriques:
            vals[champ_of[titre]] = clausier.md_to_plain(md, c.notes)
        libelle = c["titre"]
        if titles.count(c["titre"]) > 1 and vals["commentaire"] and len(vals["commentaire"]) <= 70:
            libelle = f"{c['titre']} — {vals['commentaire']}"
        out.append({
            "id": c.id, "segment": seg["libelle_excel"], "sous_segment": sous,
            "phase": phases[c["phase"]]["libelle_excel"], "critere": c["titre"],
            "libelle": libelle, "section": c["section"],
            "page": (c["source"] or {}).get("page_pdf") or "", **vals,
        })
    return out


def style_header(ws, row, ncols):
    for col in range(1, ncols + 1):
        cell = ws.cell(row, col)
        cell.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=BLEU)
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def add_table(ws, name, ref):
    t = Table(displayName=name, ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showRowStripes=True)
    ws.add_table(t)


def widths(ws, values):
    for i, w in enumerate(values, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def text_block(ws, row, text, font=F_BASE, height=None):
    ws.cell(row, 1, text).font = font
    ws.cell(row, 1).alignment = WRAP
    if height:
        ws.row_dimensions[row].height = height
    return row + 1


def sheet_presentation(wb, meta, n):
    ws = wb.active
    ws.title = "Présentation"
    widths(ws, [110])
    r = text_block(ws, 1, f"{meta['titre']} — version {meta['version']}", F_TITLE, 26)
    r = text_block(ws, r, f"Coordonné par {' et '.join(meta['editeurs'])}. {n} clauses.", F_BOLD)
    r += 1
    r = text_block(ws, r, "Présentation", F_H2)
    for para in [
        "Le présent clausier type vise à aider les prescripteurs et les acheteurs à rédiger les "
        "documents de consultation et à évaluer les offres des soumissionnaires de manière "
        "rigoureuse et objective.",
        "Pour chaque segment, il propose deux parties : des critères attendus en phase amont d’un "
        "marché, formulés sous forme de questionnaire (RFI/RFP) visant à sélectionner et évaluer les "
        "soumissionnaires ; des exigences à satisfaire par les titulaires sur la durée de vie du "
        "marché, à intégrer dans les documents contractuels (CCAP & CCTP).",
        "Chaque critère présente autant que possible deux niveaux : un niveau socle « Must have » "
        "(Niveau 1) et un niveau plus ambitieux « Nice to have » (Niveau 2).",
        "(Texte repris de la section « Comment lire le Clausier Numérique Responsable ? » du "
        "document V2 et de la feuille Notice du classeur de préparation.)",
    ]:
        r = text_block(ws, r, para, height=42)
    r += 1
    r = text_block(ws, r, "Mode d’emploi du classeur", F_H2)
    for para in [
        f"1. Feuille « {CATALOGUE} » : toutes les clauses, avec leur texte complet. Utilisez les "
        "flèches de filtre des en-têtes (Segment, Sous segment, Phase…) pour consulter un périmètre.",
        f"2. Feuille « {SELECTION} » : choisissez « Oui » dans la colonne « Retenir » (cellules "
        "jaunes) pour chaque clause utile à votre consultation. Les filtres fonctionnent aussi ici.",
        f"3. Feuille « {RETENUES} » : les clauses retenues s’y regroupent automatiquement, dans "
        "l’ordre du clausier, avec leur texte complet. Copiez-les dans vos documents de consultation.",
        "4. Les identifiants (ex. COM-Q-01) sont stables : ils désignent la même clause dans le "
        "classeur, sur le site et dans le dépôt Markdown. Citez-les dans vos échanges.",
        "Les critères, leur poids et les exigences sont à adapter aux spécificités et à la stratégie "
        "d’achat de chaque organisation.",
    ]:
        r = text_block(ws, r, para, height=30)
    r += 1
    r = text_block(ws, r, "Licence et réutilisation", F_H2)
    r = text_block(ws, r, meta["licence_contenu"]["mention"] + " Réutilisation et modification libres, "
                   "y compris commerciales, à condition de citer la source et d’indiquer les "
                   "modifications.", height=30)
    r = text_block(ws, r, "À citer : " + meta["licence_contenu"]["attribution"], F_BOLD, height=30)
    r = text_block(ws, r, "Propositions d’actualisation : " + meta["contact"]["propositions"])
    r += 1
    r = text_block(ws, r, "Crédits : voir la feuille « Crédits ».", F_BOLD)
    text_block(ws, r, "Fichier généré automatiquement à partir des sources Markdown du clausier. "
               "Ne modifiez pas les clauses ici : proposez vos modifications sur le dépôt.",
               Font(name=FONT, size=9, italic=True, color="55707E"))


CAT_COLS = [("ID", "id", 11), ("Critère", "critere", 30), ("Commentaire", "commentaire", 40),
            ("Exigences", "exigences", 45), ("Livrables", "livrables", 40),
            ("Questions", "questions", 50), ("Niveau 1 (Must have)", "niveau_1", 45),
            ("Niveau 2 (Nice to have)", "niveau_2", 45), ("Segment", "segment", 15),
            ("Sous segment", "sous_segment", 22), ("Phase", "phase", 13),
            ("Section V2", "section", 9), ("Page PDF V2", "page", 9)]


def sheet_catalogue(wb, rows):
    ws = wb.create_sheet(CATALOGUE)
    for j, (h, _, _) in enumerate(CAT_COLS, start=1):
        ws.cell(1, j, h)
    style_header(ws, 1, len(CAT_COLS))
    for i, row in enumerate(rows, start=2):
        for j, (_, key, _) in enumerate(CAT_COLS, start=1):
            cell = ws.cell(i, j, row[key])
            cell.font = F_BOLD if key in ("id", "critere") else F_BASE
            cell.alignment = WRAP
    widths(ws, [w for _, _, w in CAT_COLS])
    ws.freeze_panes = "C2"
    add_table(ws, "Catalogue", f"A1:{get_column_letter(len(CAT_COLS))}{len(rows) + 1}")


SEL_COLS = [("ID", 11), ("Segment", 15), ("Sous segment", 24), ("Phase", 13),
            ("Clause", 60), ("Retenir", 10), ("Rang", 7)]


def sheet_selection(wb, rows, preselect):
    ws = wb.create_sheet(SELECTION)
    n = len(rows)
    last = n + 3
    ws["A1"] = "Choisissez « Oui » dans la colonne « Retenir » (cellules jaunes) pour chaque clause à retenir."
    ws["A1"].font = F_BOLD
    ws["A2"] = "Clauses retenues :"
    ws["A2"].font = F_BOLD
    ws["C2"] = f'=COUNTIF(F4:F{last},"Oui")'
    ws["C2"].font = F_BOLD
    for j, (h, _) in enumerate(SEL_COLS, start=1):
        ws.cell(3, j, h)
    style_header(ws, 3, len(SEL_COLS))
    dv = DataValidation(type="list", formula1='"Oui,Non"', allow_blank=True,
                        promptTitle="Retenir la clause ?", prompt="Oui pour l’ajouter à la feuille « Clauses retenues ».",
                        showInputMessage=True)
    ws.add_data_validation(dv)
    for i, row in enumerate(rows, start=4):
        vals = [row["id"], row["segment"], row["sous_segment"], row["phase"], row["libelle"]]
        for j, v in enumerate(vals, start=1):
            ws.cell(i, j, v).font = F_BOLD if j == 1 else F_BASE
            ws.cell(i, j).alignment = WRAP
        sel = ws.cell(i, 6, "Oui" if row["id"] in preselect else None)
        sel.fill = PatternFill("solid", fgColor=SAISIE)
        sel.font = F_BOLD
        sel.alignment = Alignment(horizontal="center", vertical="top")
        rank = ws.cell(i, 7, f'=IF(F{i}="Oui",COUNTIF(F$4:F{i},"Oui"),"")')
        rank.font = Font(name=FONT, size=9, color="55707E")
    dv.add(f"F4:F{last}")
    widths(ws, [w for _, w in SEL_COLS])
    ws.freeze_panes = "B4"
    add_table(ws, "Selection", f"A3:G{last}")


RET_COLS = [("N°", None, 5), ("ID", "id", 11), ("Critère", "critere", 30),
            ("Commentaire", "commentaire", 40), ("Exigences", "exigences", 45),
            ("Livrables", "livrables", 40), ("Questions", "questions", 50),
            ("Niveau 1 (Must have)", "niveau_1", 45), ("Niveau 2 (Nice to have)", "niveau_2", 45),
            ("Segment", "segment", 15), ("Phase", "phase", 13)]


def sheet_donnees(wb, rows):
    """Copie masquée du catalogue, sauts de ligne remplacés par MARQUE.

    LibreOffice perd les sauts de ligne d'un texte renvoyé par INDEX. La feuille Clauses
    retenues lit donc cette copie et rétablit les sauts avec SUBSTITUTE(…;MARQUE;CHAR(10)),
    ce qui fonctionne sous Excel comme sous LibreOffice.
    """
    ws = wb.create_sheet(DONNEES)
    for j, (h, _, _) in enumerate(CAT_COLS, start=1):
        ws.cell(1, j, h)
    for i, row in enumerate(rows, start=2):
        for j, (_, key, _) in enumerate(CAT_COLS, start=1):
            v = row[key]
            ws.cell(i, j, v.replace("\n", MARQUE) if isinstance(v, str) else v)
    ws.sheet_state = "hidden"


def sheet_retenues(wb, n):
    ws = wb.create_sheet(RETENUES)
    cat_col = {key: get_column_letter(j) for j, (_, key, _) in enumerate(CAT_COLS, start=1)}
    sel_last = n + 3
    cat_last = n + 1
    ws["A1"] = "Clauses retenues dans la feuille « Sélection », regroupées automatiquement. Ne pas saisir ici."
    ws["A1"].font = F_BOLD
    for j, (h, _, _) in enumerate(RET_COLS, start=1):
        ws.cell(2, j, h)
    style_header(ws, 2, len(RET_COLS))
    q_sel, q_cat = f"'{SELECTION}'", f"'{DONNEES}'"
    for k in range(1, n + 1):
        i = k + 2
        ws.cell(i, 1, f'=IF(B{i}="","",{k})')
        ws.cell(i, 2, f'=IFERROR(INDEX({q_sel}!$A$4:$A${sel_last},'
                      f'MATCH({k},{q_sel}!$G$4:$G${sel_last},0)),"")')
        for j, (_, key, _) in enumerate(RET_COLS[2:], start=3):
            col = cat_col[key]
            ws.cell(i, j, f'=IF($B{i}="","",SUBSTITUTE(INDEX({q_cat}!${col}$2:${col}${cat_last},'
                          f'MATCH($B{i},{q_cat}!$A$2:$A${cat_last},0))&"","{MARQUE}",CHAR(10)))')
        for j in range(1, len(RET_COLS) + 1):
            ws.cell(i, j).font = F_BOLD if j in (2, 3) else F_BASE
            ws.cell(i, j).alignment = WRAP
    widths(ws, [w for _, _, w in RET_COLS])
    ws.freeze_panes = "D3"


def sheet_lexique(wb):
    lex = clausier.load_yaml("lexique.yml")
    ws = wb.create_sheet("Lexique")
    ws["A1"] = lex["introduction"]
    ws["A1"].font = F_BASE
    ws["A1"].alignment = WRAP
    ws.merge_cells("A1:C1")
    ws.row_dimensions[1].height = 30
    for j, h in enumerate(["Terme", "Définition", "Catégorie"], start=1):
        ws.cell(3, j, h)
    style_header(ws, 3, 3)
    for i, t in enumerate(lex["termes"], start=4):
        for j, v in enumerate([t["terme"], t["definition"], t["categorie"]], start=1):
            ws.cell(i, j, clausier.md_to_plain(v or "")).font = F_BOLD if j == 1 else F_BASE
            ws.cell(i, j).alignment = WRAP
    widths(ws, [38, 90, 36])
    ws.freeze_panes = "A4"
    add_table(ws, "Lexique", f"A3:C{len(lex['termes']) + 3}")


def sheet_references(wb):
    refs = clausier.load_yaml("references.yml")["references"]
    ws = wb.create_sheet("Références")
    ws["A1"] = "Sources documentaires citées par le clausier (section « Sources documentaires » du V2)."
    ws["A1"].font = F_BOLD
    for j, h in enumerate(["Référence", "Adresse"], start=1):
        ws.cell(3, j, h)
    style_header(ws, 3, 2)
    for i, ref in enumerate(refs, start=4):
        ws.cell(i, 1, ref["titre"]).font = F_BASE
        ws.cell(i, 1).alignment = WRAP
        link = ws.cell(i, 2, ref["url"])
        link.hyperlink = ref["url"]
        link.font = F_LINK
        link.alignment = WRAP
    widths(ws, [70, 80])
    add_table(ws, "References", f"A3:B{len(refs) + 3}")


def sheet_credits(wb, meta):
    ws = wb.create_sheet("Crédits")
    widths(ws, [110])
    _, remerciements = clausier.load_page(ROOT / "content/pages/remerciements.md")
    r = text_block(ws, 1, "Crédits", F_TITLE, 24)
    r = text_block(ws, r, "Classeur Excel", F_H2)
    r = text_block(ws, r, "Paul Saulnier — Contribution initiale à la structuration et à la préparation "
                   "du classeur Excel du Clausier Numérique Responsable V2. Le présent classeur reprend "
                   "son modèle de colonnes, son classement par segment, sous-segment et phase, et son "
                   "lexique catégorisé.", height=42)
    r += 1
    r = text_block(ws, r, "Clausier Numérique Responsable V2", F_H2)
    r = text_block(ws, r, "Coordination : " + " et ".join(meta["editeurs"]) + ".")
    r = text_block(ws, r, "Pilotage : " + " ; ".join(meta["pilotage"]) + ".", height=30)
    r += 1
    r = text_block(ws, r, "Remerciements (texte du V2)", F_H2)
    for line in remerciements.split("\n\n"):
        r = text_block(ws, r, clausier.md_to_plain(line))
    r += 1
    r = text_block(ws, r, "Licence", F_H2)
    r = text_block(ws, r, meta["licence_contenu"]["mention"] + " " + meta["licence_contenu"]["url"], height=30)
    text_block(ws, r, "À citer : " + meta["licence_contenu"]["attribution"], F_BOLD, height=30)


def print_setup(wb):
    """Impression : paysage A4, ajusté à la largeur, ligne d'en-tête répétée."""
    titles = {CATALOGUE: "1:1", SELECTION: "3:3", RETENUES: "2:2", "Lexique": "3:3", "Références": "3:3"}
    for ws in wb.worksheets:
        ws.page_setup.orientation = "landscape" if ws.title in (CATALOGUE, RETENUES) else "portrait"
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_margins.left = ws.page_margins.right = 0.4
        if ws.title in titles:
            ws.print_title_rows = titles[ws.title]
        ws.oddFooter.center.text = "&A — page &P / &N"


def build(out=OUT, preselect=()):
    meta = clausier.load_yaml("metadata.yml")
    clauses = clausier.published(clausier.load_clauses())
    rows = rows_for(clauses)
    wb = Workbook()
    sheet_presentation(wb, meta, len(rows))
    sheet_catalogue(wb, rows)
    sheet_selection(wb, rows, set(preselect))
    sheet_retenues(wb, len(rows))
    sheet_lexique(wb)
    sheet_references(wb)
    sheet_credits(wb, meta)
    sheet_donnees(wb, rows)
    print_setup(wb)
    p = wb.properties
    p.title = f"{meta['titre']} V{meta['version']}"
    p.creator = "Institut du Numérique Responsable (INR)"
    p.lastModifiedBy = None
    p.description = ("Généré à partir du dépôt Markdown du clausier. Classeur fondé sur le travail "
                     "de structuration de Paul Saulnier.")
    p.keywords = "numérique responsable; achats; clausier; RFI; RFP; CCAP; CCTP"
    p.created = p.modified = FIXED_DATE
    buf = io.BytesIO()
    wb.save(buf)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(_normalize_zip(buf.getvalue()))
    return out, len(rows)


def _normalize_zip(data):
    """Dates fixes dans l'archive : même contenu, même fichier."""
    src = zipfile.ZipFile(io.BytesIO(data))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            z = zipfile.ZipInfo(info.filename, date_time=(2026, 8, 1, 0, 0, 0))
            z.compress_type = zipfile.ZIP_DEFLATED
            data = src.read(info.filename)
            if info.filename == "docProps/core.xml":
                # openpyxl impose la date d'enregistrement : on la fixe
                data = re.sub(rb"(<dcterms:modified[^>]*>)[^<]*", rb"\g<1>2026-08-01T00:00:00Z", data)
            dst.writestr(z, data)
    return buf.getvalue()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", default="")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    path, n = build(Path(a.out), [x for x in a.selection.split(",") if x])
    print(f"{n} clauses -> {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
