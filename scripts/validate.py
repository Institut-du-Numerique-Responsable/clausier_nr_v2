# -*- coding: utf-8 -*-
"""Valide le référentiel Markdown. Code de sortie 1 en cas d'erreur.

Contrôles :
- en-tête YAML conforme à schemas/clause.schema.json ;
- identifiant unique, cohérent avec le nom du fichier, le dossier, le segment et la phase ;
- segment, sous-segment et section déclarés dans data/segments.yml ;
- rubriques autorisées (data/colonnes.yml), non dupliquées, non vides ;
- titre du corps identique au champ « titre » ;
- appels de note définis, notes définies utilisées ;
- emphases Markdown équilibrées ;
- liens internes des pages vers des clauses existantes ;
- ordre unique au sein d'une section.

Usage : python scripts/validate.py
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import fastjsonschema

sys.path.insert(0, str(Path(__file__).parent))
import clausier  # noqa: E402

ROOT = clausier.ROOT


def check():
    errors, warnings = [], []
    schema = json.loads((ROOT / "schemas/clause.schema.json").read_text(encoding="utf-8"))
    validate_meta = fastjsonschema.compile(schema)
    segs = clausier.segments()
    by_slug = {s["slug"]: s for s in segs["segments"]}
    rubriques = {r["titre"] for r in clausier.load_yaml("colonnes.yml")["rubriques"]}

    clauses = []
    for path in sorted((ROOT / "content/clauses").rglob("*.md")):
        rel = path.relative_to(ROOT)
        try:
            c = clausier.parse_clause(path)
        except Exception as exc:  # fichier illisible : on continue sur les autres
            errors.append(f"{rel}: {exc}")
            continue
        try:
            validate_meta(c.meta)
        except fastjsonschema.JsonSchemaException as exc:
            errors.append(f"{rel}: en-tête invalide : {exc.message}")
            continue
        clauses.append(c)
        e = lambda msg: errors.append(f"{rel}: {msg}")  # noqa: E731
        if path.stem != c.id:
            e(f"le nom du fichier doit être {c.id}.md")
        if path.parent.name != c["segment"]:
            e(f"le fichier doit être rangé dans content/clauses/{c['segment']}/")
        seg = by_slug[c["segment"]]
        sec = next((s for s in seg["sections"] if s["numero"] == c["section"]), None)
        if sec is None:
            e(f"section {c['section']} absente du segment {c['segment']} (data/segments.yml)")
        else:
            if sec["phase"] != c["phase"]:
                e(f"phase {c['phase']} incohérente avec la section {c['section']} ({sec['phase']})")
            if not c.id.startswith(sec["prefixe"] + "-"):
                e(f"l'identifiant d'une clause de la section {c['section']} commence par {sec['prefixe']}-")
        subs = {s["slug"] for s in seg["sous_segments"]}
        if c["sous_segment"] and c["sous_segment"] not in subs:
            e(f"sous-segment inconnu : {c['sous_segment']}")
        if subs and not c["sous_segment"]:
            e(f"sous-segment obligatoire pour le segment {c['segment']}")
        if c.titre_corps != c["titre"]:
            e(f"le titre « # » du corps diffère du champ titre : {c.titre_corps!r}")
        seen = Counter(t for t, _ in c.rubriques)
        for t, n in seen.items():
            if t not in rubriques:
                e(f"rubrique non autorisée : « ## {t} » (voir data/colonnes.yml)")
            if n > 1:
                e(f"rubrique en double : « ## {t} »")
        for t, md in c.rubriques:
            if not md:
                e(f"rubrique vide : « ## {t} » (supprimez-la)")
            for ln, line in enumerate(md.split("\n"), 1):
                stripped = re.sub(r"\[\^[^\]]+\]", "", line)
                if stripped.count("*") % 2:
                    warnings.append(f"{rel}: « {t} » ligne {ln} : emphase * déséquilibrée")
        if not c.rubriques:
            e("aucune rubrique")
        body = "\n".join(md for _, md in c.rubriques)
        calls = set(re.findall(r"\[\^([^\]]+)\]", body))
        for n in calls - set(c.notes):
            e(f"appel de note [^{n}] sans définition")
        for n in set(c.notes) - calls:
            e(f"note [^{n}] définie mais jamais appelée")

    ids = Counter(c.id for c in clauses)
    for i, n in ids.items():
        if n > 1:
            errors.append(f"identifiant en double : {i} ({n} fichiers)")
    pos = Counter((c["section"], c["ordre"]) for c in clauses if c["statut"] != "archivee")
    for (s, o), n in pos.items():
        if n > 1:
            errors.append(f"section {s} : ordre {o} attribué à {n} clauses")
    for c in clauses:
        if c["remplace"] and c["remplace"] not in ids:
            errors.append(f"{c.id}: remplace une clause inconnue : {c['remplace']}")

    # pages : liens vers des clauses et marqueurs de section
    known = set(ids)
    sections = {s["numero"] for seg in segs["segments"] for s in seg["sections"]}
    for path in sorted((ROOT / "content").glob("*/*.md")):
        if "clauses" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        try:
            _, body = clausier.load_page(path)
        except ValueError as exc:
            errors.append(f"{rel}: {exc}")
            continue
        for ref in re.findall(r"\(clause:([A-Z]+-[QE]-\d+)\)", body):
            if ref not in known:
                errors.append(f"{rel}: lien vers une clause inconnue : {ref}")
        for sec in re.findall(r'<!-- clauses section="([^"]+)" -->', body):
            if sec not in sections:
                errors.append(f"{rel}: marqueur de section inconnue : {sec}")
        for anchor in re.findall(r"\]\((#[^)]+)\)", body):
            warnings.append(f"{rel}: ancre interne héritée de l'ODT, sans cible : {anchor}")
    return clauses, errors, warnings


def main():
    clauses, errors, warnings = check()
    for w in warnings:
        print("AVERTISSEMENT", w)
    for e in errors:
        print("ERREUR", e)
    statuts = Counter(c["statut"] for c in clauses)
    print(f"{len(clauses)} clauses lues ({dict(statuts)}), "
          f"{len(errors)} erreur(s), {len(warnings)} avertissement(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
