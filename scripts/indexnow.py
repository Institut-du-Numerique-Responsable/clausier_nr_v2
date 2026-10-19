#!/usr/bin/env python3
"""Signale les URL du site publié aux moteurs IndexNow (Bing, Yandex, Seznam, Naver).

Lit le sitemap de dist/site/ et envoie la liste à api.indexnow.org. À lancer après
`make deploy` : le moteur vérifie la clé sur le site en ligne.

    python scripts/indexnow.py            # affiche ce qui serait envoyé
    python scripts/indexnow.py --envoyer  # envoie
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clausier  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
POINT_D_ENTREE = "https://api.indexnow.org/indexnow"


def main():
    meta = clausier.load_yaml("metadata.yml")
    base, cle = meta["liens"]["site"], meta.get("indexnow_cle")
    if not base or not cle:
        sys.exit("liens.site ou indexnow_cle manquant dans data/metadata.yml")
    sitemap = (RACINE / "dist/site/sitemap.xml").read_text(encoding="utf-8")
    urls = re.findall(r"<loc>(.*?)</loc>", sitemap)
    hote = re.match(r"https?://([^/]+)/", base).group(1)
    corps = {"host": hote, "key": cle, "keyLocation": f"{base}{cle}.txt", "urlList": urls}
    print(f"{len(urls)} URL pour {hote}, clé {corps['keyLocation']}")
    if "--envoyer" not in sys.argv:
        return
    req = urllib.request.Request(POINT_D_ENTREE, data=json.dumps(corps).encode(),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print("réponse", r.status)


if __name__ == "__main__":
    main()
