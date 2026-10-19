# -*- coding: utf-8 -*-
"""Visuels de présentation du clausier (page WordPress, diaporamas, réseaux).

Produit dans dist/visuels/, en PNG et en WebP :
- la page de garde et une page de tableau du PDF V2 ;
- les feuilles Catalogue, Sélection et Clauses retenues du classeur généré, rendues par
  LibreOffice (vrai fichier, avec trois clauses retenues à titre d'exemple) ;
- l'accueil, une fiche clause et le catalogue du site, capturés par Chrome sans interface.

Prérequis : poppler (pdftoppm), LibreOffice (soffice), Google Chrome ou Chromium, cwebp
(facultatif), Pillow (requirements-visuels.txt). Le site et le classeur doivent être
construits (make build).

Usage : python scripts/build_visuels.py
"""
import functools
import http.server
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

import openpyxl
from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).parent))
import build_excel  # noqa: E402
import clausier  # noqa: E402

ROOT = clausier.ROOT
OUT = ROOT / "dist/visuels"
PDF_V2 = ROOT / "sources/originaux/clausier-numerique-responsable-v2.pdf"
SITE = ROOT / "dist/site"
EXEMPLE = ["COM-Q-13", "CLD-Q-01", "DEV-E-04"]   # clauses retenues dans l'exemple
CHROME = os.environ.get("CHROME") or next(
    (c for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                 shutil.which("google-chrome") or "", shutil.which("chromium") or ""] if c and Path(c).exists()),
    None)


def trim(img, marge=24):
    """Recadre les marges blanches, puis remet une marge régulière."""
    fond = Image.new(img.mode, img.size, (255, 255, 255))
    box = ImageChops.difference(img, fond).getbbox()
    if not box:
        return img
    l, t, r, b = box
    return img.crop((max(l - marge, 0), max(t - marge, 0),
                     min(r + marge, img.width), min(b + marge, img.height)))


def save(img, nom, largeur_max=1600):
    if img.width > largeur_max:
        img = img.resize((largeur_max, round(img.height * largeur_max / img.width)), Image.LANCZOS)
    png = OUT / f"{nom}.png"
    img.convert("RGB").save(png, optimize=True)
    if shutil.which("cwebp"):
        subprocess.run(["cwebp", "-quiet", "-q", "82", str(png), "-o", str(OUT / f"{nom}.webp")], check=True)
    print(f"  {png.relative_to(ROOT)} ({img.width}x{img.height})")


def pdf_page(pdf, page, dpi, tmp):
    base = tmp / f"p{page}"
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(dpi), "-png",
                    "-singlefile", str(pdf), str(base)], check=True)
    return Image.open(f"{base}.png").convert("RGB")


def visuels_pdf(tmp):
    couverture = pdf_page(PDF_V2, 1, 150, tmp)
    save(couverture, "pdf-v2-page-de-garde", 1240)
    vignette = couverture.copy()
    vignette.thumbnail((600, 850))
    save(vignette, "pdf-v2-page-de-garde-vignette", 600)
    save(pdf_page(PDF_V2, 8, 130, tmp), "pdf-v2-page-08-questionnaire", 1240)


FEUILLES = {
    # feuille : (zone imprimée, nom du visuel)
    "Catalogue": ("A1:H6", "excel-catalogue"),
    "Sélection": ("A1:G22", "excel-selection"),
    "Clauses retenues": ("A1:I5", "excel-clauses-retenues"),
    "Présentation": ("A1:A30", "excel-presentation"),
}


def visuels_excel(tmp):
    if not shutil.which("soffice"):
        print("  LibreOffice absent : visuels du classeur ignorés")
        return
    source = tmp / "exemple.xlsx"
    build_excel.build(source, preselect=EXEMPLE)
    for feuille, (zone, nom) in FEUILLES.items():
        wb = openpyxl.load_workbook(source)
        for ws in wb.worksheets:
            ws.sheet_state = "visible" if ws.title == feuille else "hidden"
        ws = wb[feuille]
        wb.active = wb.worksheets.index(ws)
        ws.print_area = zone
        ws.print_options.gridLines = True
        ws.print_options.headings = True
        ws.oddFooter.center.text = ""
        fichier = tmp / f"{nom}.xlsx"
        wb.save(fichier)
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(fichier)],
                       check=True, capture_output=True, timeout=180)
        save(trim(pdf_page(tmp / f"{nom}.pdf", 1, 150, tmp)), nom)


class _Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def visuels_site(tmp):
    if not CHROME:
        print("  Chrome absent : captures du site ignorées")
        return
    handler = functools.partial(_Silencieux, directory=str(SITE))
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{serveur.server_address[1]}/"
    pages = [("", "site-accueil", (1440, 900)), ("clausier/", "site-catalogue", (1440, 900)),
             ("clausier/clauses/MAT-Q-02/", "site-fiche-clause", (1440, 1000)),
             ("", "site-accueil-mobile", (390, 844))]
    try:
        for chemin, nom, (w, h) in pages:
            png = tmp / f"{nom}.png"
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            "--force-device-scale-factor=2", f"--window-size={w},{h}",
                            f"--screenshot={png}", base + chemin],
                           check=True, capture_output=True, timeout=60)
            save(Image.open(png).convert("RGB"), nom, 2 * w if w < 600 else 1600)
    finally:
        serveur.shutdown()


def main():
    if not (SITE / "index.html").exists():
        sys.exit("dist/site absent : lancez d'abord « make build ».")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        print("PDF V2")
        visuels_pdf(tmp)
        print("Classeur")
        visuels_excel(tmp)
        print("Site")
        visuels_site(tmp)
    shutil.copy2(ROOT / "docs/visuels.md", OUT / "LISEZMOI.md")


if __name__ == "__main__":
    main()
