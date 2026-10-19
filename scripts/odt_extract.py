# -*- coding: utf-8 -*-
"""Lecture structurée du document maître ODT du clausier.

Ce module ne modifie jamais le fichier source. Il renvoie :
- la suite des titres et paragraphes hors tableaux ;
- chaque tableau de clauses, rattaché à sa section, avec ses en-têtes de colonnes
  et ses lignes. Chaque cellule est convertie en Markdown (gras, italique, listes,
  liens, appels de note).

Utilisé par scripts/migrate.py (migration initiale) et par les tests d'intégrité,
qui comparent le texte des fichiers Markdown au texte de l'ODT.
"""
import re
import unicodedata
import zipfile

from lxml import etree

NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
}
T = "{%s}" % NS["text"]
TB = "{%s}" % NS["table"]
ST = "{%s}" % NS["style"]
FO = "{%s}" % NS["fo"]
XL = "{%s}" % NS["xlink"]
O = "{%s}" % NS["office"]


def _styles(root):
    """Renvoie (gras, italique, exposant) : noms des styles automatiques concernés."""
    bold, ital, sup = set(), set(), set()
    for s in root.iter(ST + "style"):
        tp = s.find(ST + "text-properties")
        if tp is None:
            continue
        if tp.get(FO + "font-weight") == "bold":
            bold.add(s.get(ST + "name"))
        if tp.get(FO + "font-style") == "italic":
            ital.add(s.get(ST + "name"))
        pos = (tp.get(ST + "text-position") or "0").split()[0]
        if pos == "super" or (pos.endswith("%") and float(pos[:-1]) > 0):
            sup.add(s.get(ST + "name"))
    return bold, ital, sup


def plain(s):
    """Texte comparable : NFC, espaces normalisés. Aucune autre transformation."""
    s = unicodedata.normalize("NFC", s).replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


class Converter:
    def __init__(self, root, styles_root=None):
        self.bold, self.ital, self.sup = _styles(root)
        self.notes = []  # (numéro, texte) des notes du bloc en cours
        # style de liste -> niveaux numérotés
        self.numbered = {}
        roots = [root] + ([styles_root] if styles_root is not None else [])
        for ls in (x for r in roots for x in r.iter(T + "list-style")):
            self.numbered[ls.get(ST + "name")] = {
                int(lv.get(T + "level")) for lv in ls if etree.QName(lv).localname == "list-level-style-number"}

    def is_numbered(self, el):
        level, name, a = 0, None, el
        while a is not None:
            if a.tag == T + "list":
                level += 1
                name = name or a.get(T + "style-name")
            a = a.getparent()
        return level in self.numbered.get(name, set())

    def inline(self, el):
        """Convertit le contenu en ligne d'un paragraphe en Markdown."""
        return _render(self.runs(el, False, False, False))

    def runs(self, el, b, i, sup):
        """Suite de segments (texte, gras, italique, exposant, brut)."""
        out = []
        if el.text:
            out.append((el.text, b, i, sup, False))
        for ch in el:
            tag = etree.QName(ch).localname
            if tag == "span":
                name = ch.get(T + "style-name")
                out += self.runs(ch, b or name in self.bold, i or name in self.ital,
                                 sup or name in self.sup)
            elif tag == "a":
                inner = _render(self.runs(ch, b, i, sup))
                href = ch.get(XL + "href") or ""
                out.append((f"[{inner}]({href})" if href and inner.strip() else inner,
                            False, False, False, True))
            elif tag == "s":
                out.append((" " * int(ch.get(T + "c", "1")), b, i, sup, False))
            elif tag == "tab":
                out.append((" ", b, i, sup, False))
            elif tag == "line-break":
                out.append(("\n", False, False, False, True))
            elif tag == "note":
                num = "".join(ch.find(T + "note-citation").itertext()).strip()
                body = plain(" ".join("".join(p.itertext()) for p in ch.find(T + "note-body")))
                self.notes.append((num, body))
                out.append((f"[^{num}]", False, False, False, True))
            elif tag in ("soft-page-break", "bookmark", "bookmark-start", "bookmark-end"):
                pass
            else:
                out += self.runs(ch, b, i, sup)
            if ch.tail:
                out.append((ch.tail, b, i, sup, False))
        return out

    def block(self, el, depth=0):
        """Convertit un paragraphe ou une liste en lignes Markdown."""
        tag = etree.QName(el).localname
        lines = []
        if tag in ("p", "h"):
            s = self.inline(el)
            for part in s.split("\n"):
                part = _tidy(part)
                if part:
                    lines.append(part)
        elif tag == "list":
            numbered, n = self.is_numbered(el), 0
            for item in el:
                if etree.QName(item).localname not in ("list-item", "list-header"):
                    continue
                if etree.QName(item).localname == "list-item":
                    n += 1
                marker = f"{n}. " if numbered else "- "
                first = True
                for sub in item:
                    for line in self.block(sub, depth + 1):
                        if first and not line.startswith("  "):
                            lines.append("  " * depth + marker + line)
                            first = False
                        else:
                            lines.append(line if line.startswith("  ") else "  " * (depth + 1) + line)
            if depth == 0:
                lines = _dedent(lines)
        return lines

    def cell(self, cell):
        """Markdown d'une cellule : blocs séparés par une ligne vide."""
        blocks = []
        for ch in cell:
            lines = self.block(ch)
            if lines:
                blocks.append(lines)
        out = []
        for lines in blocks:
            is_list = lines[0].lstrip().startswith("- ")
            if out and not (is_list and out[-1].lstrip().startswith("- ")):
                out.append("")
            out.extend(lines)
        return "\n".join(out).strip()


def _dedent(lines):
    """Retire l'indentation commune : l'ODT imbrique parfois des listes vides."""
    pad = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    pad -= pad % 2
    return [l[pad:] for l in lines]


def _render(runs):
    """Regroupe les segments contigus de même mise en forme, puis les balise.

    Les espaces seuls n'interrompent pas un groupe : « *EPEAT* *ou* » devient « *EPEAT ou* ».
    """
    groups = []  # [texte, gras, italique, exposant] ; brut -> exposant None
    for text, b, i, sup, raw in runs:
        if raw:
            groups.append([text, False, False, None])
        elif not text.strip() and groups and groups[-1][3] is not None:
            groups[-1][0] += text
        elif groups and groups[-1][3] is not None and groups[-1][1:] == [b, i, sup]:
            groups[-1][0] += text
        else:
            groups.append([text, b, i, sup])
    out = []
    for text, b, i, sup in groups:
        if sup and text.strip():
            lead, core, trail = _split(text)
            text = f"{lead}<sup>{core}</sup>{trail}"
        out.append(text if sup is None else _wrap(text, b, i))
    return "".join(out)


def _split(s):
    core = s.strip()
    return s[: len(s) - len(s.lstrip())], core, s[len(s.rstrip()):]


def _wrap(s, b, i):
    if not (b or i) or not s.strip():
        return s
    lead = s[: len(s) - len(s.lstrip())]
    trail = s[len(s.rstrip()):]
    core = s.strip()
    mark = ("**" if b else "") + ("*" if i else "")
    return f"{lead}{mark}{core}{mark[::-1]}{trail}"


def _tidy(s):
    s = s.replace(" ", " ")
    return re.sub(r"[ \t]+", " ", s).strip()


def read(path):
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read("content.xml"))
    conv = Converter(root, etree.fromstring(z.read("styles.xml")))
    body = root.find(O + "body").find(O + "text")

    heads = []        # pile des titres courants
    events = []       # ("h", niveau, texte) | ("p", texte) | ("table", dict)
    for el in _flatten(body):
        tag = etree.QName(el).localname
        if tag == "h":
            level = int(el.get(T + "outline-level", "1"))
            txt = plain("".join(el.itertext()))
            heads = heads[: level - 1] + [txt]
            events.append(("h", level, txt))
        elif tag in ("p", "list"):
            conv.notes = []
            lines = conv.block(el)
            if lines:
                events.append(("p", "\n".join(lines), conv.notes))
        elif tag == "table":
            events.append(("table", _table(el, conv, list(heads))))
    return events


def _flatten(container):
    """Enfants de premier niveau, en descendant dans les sections (mise en colonnes)."""
    for el in container:
        if etree.QName(el).localname == "section":
            yield from _flatten(el)
        else:
            yield el


def _table(el, conv, heads):
    name = el.get(TB + "name")
    hdr_el = el.find(TB + "table-header-rows")
    hdr_rows = hdr_el.findall(TB + "table-row") if hdr_el is not None else []
    body_rows = [r for r in el.iter(TB + "table-row") if r.getparent() is not hdr_el]
    headers = []
    if hdr_rows:
        headers = [plain("".join(c.itertext())) for c in hdr_rows[0] if c.tag == TB + "table-cell"]
    # grille avec propagation des cellules fusionnées verticalement
    spans = {}  # colonne -> (lignes restantes, valeur, fusion d'origine)
    rows = []
    for ri, r in enumerate(body_rows):
        vals, col = [], 0
        for c in r:
            if c.tag not in (TB + "table-cell", TB + "covered-table-cell"):
                continue
            if c.tag == TB + "covered-table-cell":
                left, v, origin = spans.get(col, (0, "", None))
                vals.append({"md": v, "covered_by_row": origin, "notes": []})
                if left > 1:
                    spans[col] = (left - 1, v, origin)
                else:
                    spans.pop(col, None)
            else:
                conv.notes = []
                v = conv.cell(c)
                n = int(c.get(TB + "number-rows-spanned", "1"))
                if n > 1:
                    spans[col] = (n - 1, v, ri)
                vals.append({"md": v, "rowspan": n, "notes": conv.notes})
            col += 1
        rows.append(vals)
    return {"name": name, "headings": heads, "headers": headers, "rows": rows}
