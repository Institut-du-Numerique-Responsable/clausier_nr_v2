# -*- coding: utf-8 -*-
"""Chargement du référentiel Markdown : clauses, pages, segments, données.

Module partagé par validate.py, check_integrity.py, build_excel.py et build_site.py.
Il ne dépend que de PyYAML.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
DATA = ROOT / "data"

FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
NOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$", re.M)


@dataclass
class Clause:
    path: Path
    meta: dict
    titre_corps: str            # titre « # » du corps
    rubriques: list             # [(titre de rubrique, markdown)]
    notes: dict = field(default_factory=dict)  # appel -> texte

    @property
    def id(self):
        return self.meta.get("id")

    def __getitem__(self, key):
        return self.meta.get(key)

    def rubrique(self, titre):
        for t, md in self.rubriques:
            if t == titre:
                return md
        return ""


def split_front(text):
    m = FRONT_RE.match(text)
    if not m:
        raise ValueError("en-tête YAML absent ou mal délimité (---)")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def parse_clause(path):
    meta, body = split_front(path.read_text(encoding="utf-8"))
    notes = {m.group(1): m.group(2).strip() for m in NOTE_DEF_RE.finditer(body)}
    body = NOTE_DEF_RE.sub("", body).strip()
    titre, rubriques, cur = "", [], None
    for line in body.split("\n"):
        if line.startswith("# ") and not titre and cur is None:
            titre = line[2:].strip()
        elif line.startswith("## "):
            cur = [line[3:].strip(), []]
            rubriques.append(cur)
        elif cur is not None:
            cur[1].append(line)
        elif line.strip():
            raise ValueError(f"texte hors rubrique : {line[:60]!r}")
    rubriques = [(t, "\n".join(lines).strip()) for t, lines in rubriques]
    return Clause(path, meta, titre, rubriques, notes)


def load_yaml(name):
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8"))


def segments():
    return load_yaml("segments.yml")


def section_order():
    """Ordre de tri des sections, tel que défini dans segments.yml."""
    order = []
    for seg in segments()["segments"]:
        order += [s["numero"] for s in seg["sections"]]
    return {num: i for i, num in enumerate(order)}


def load_clauses(include_archived=True):
    clauses = [parse_clause(p) for p in sorted((CONTENT / "clauses").rglob("*.md"))]
    order = section_order()
    clauses.sort(key=lambda c: (order.get(c["section"], 999), c["ordre"] or 0, c.id or ""))
    if not include_archived:
        clauses = [c for c in clauses if c["statut"] != "archivee"]
    return clauses


def load_page(path):
    meta, body = split_front(path.read_text(encoding="utf-8"))
    return meta, body.strip()


def published(clauses):
    """Clauses publiées dans les livrables : validées uniquement."""
    return [c for c in clauses if c["statut"] == "validee"]


def md_to_plain(md, notes=None):
    """Markdown d'une rubrique -> texte brut (Excel, export texte)."""
    s = md
    s = re.sub(r"<sup>([^<]*)</sup>", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: m.group(1) if m.group(1) == m.group(2)
               else f"{m.group(1)} ({m.group(2)})", s)
    used = re.findall(r"\[\^([^\]]+)\]", s)
    s = re.sub(r"\[\^([^\]]+)\]", r"[\1]", s)
    s = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", s)
    s = s.replace("**", "")
    s = re.sub(r"^(\s*)- ", lambda m: m.group(1) + "• ", s, flags=re.M)
    if notes and used:
        s += "\n" + "\n".join(f"[{n}] {notes[n]}" for n in dict.fromkeys(used) if n in notes)
    return s.strip()
