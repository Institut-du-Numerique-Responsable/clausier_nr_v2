# -*- coding: utf-8 -*-
"""Tests documentaires : validité du Markdown, intégrité face au V2, sources intactes."""
import hashlib
import shutil
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import clausier  # noqa: E402
import validate  # noqa: E402


class TestContenu(unittest.TestCase):
    def test_validation_sans_erreur(self):
        _, errors, _ = validate.check()
        self.assertEqual(errors, [])

    def test_nombre_de_clauses_du_v2(self):
        v2 = [c for c in clausier.load_clauses() if (c["source"] or {}).get("tableau")]
        self.assertEqual(len(v2), 102)

    def test_identifiants_uniques_et_stables(self):
        ids = [c.id for c in clausier.load_clauses()]
        self.assertEqual(len(ids), len(set(ids)))
        # quelques identifiants de référence, à ne jamais réattribuer
        attendus = {"COM-Q-01": "Labels et démarches RSE appliquées aux activités numériques et IT",
                    "CLD-Q-01": "PUE", "IA-Q-06": "Sobriété du Modèle",
                    "DEV-E-02": "Le TITULAIRE doit garantir la comptabilité du SERVICE sur des matériels anciens"}
        par_id = {c.id: c for c in clausier.load_clauses()}
        for cid, titre in attendus.items():
            self.assertTrue(par_id[cid]["titre"].startswith(titre[:40]), cid)

    def test_validateur_detecte_un_doublon(self):
        src = ROOT / "content/clauses/commun/COM-Q-01.md"
        copie = ROOT / "content/clauses/commun/COM-Q-99.md"
        try:
            copie.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            _, errors, _ = validate.check()
            self.assertTrue(any("COM-Q-99.md" in e and "nom du fichier" in e for e in errors))
            self.assertTrue(any("identifiant en double : COM-Q-01" in e for e in errors))
        finally:
            copie.unlink(missing_ok=True)

    def test_sources_intactes(self):
        manifest = yaml.safe_load((ROOT / "sources/manifest.yml").read_text(encoding="utf-8"))
        for f in manifest["fichiers"]:
            data = (ROOT / "sources" / f["chemin"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), f["sha256"], f["chemin"])

    @unittest.skipUnless(shutil.which("pdftotext"), "poppler (pdftotext) absent")
    def test_integrite_face_au_v2(self):
        try:
            import check_integrity
        except ImportError as exc:  # lxml absent
            self.skipTest(str(exc))
        self.assertEqual(check_integrity.main(), 0)
        rapport = (ROOT / "docs/audit/rapport-integrite.md").read_text(encoding="utf-8")
        self.assertIn("| Clauses identiques au V2, rubrique par rubrique | 102 |", rapport)


if __name__ == "__main__":
    unittest.main()
