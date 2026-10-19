# Architecture

## Principe

Le Markdown est la seule source éditoriale. Les livrables sont générés, reproductibles et
jamais modifiés à la main.

```
sources/originaux/  ──(migration unique : scripts/migrate.py)──►  content/ + data/
                                                                       │
                       scripts/validate.py  ◄──────────────────────────┤
                       scripts/check_integrity.py (face au V2) ◄───────┤
                                                                       ├──► scripts/build_excel.py ──► dist/excel/*.xlsx
                                                                       └──► scripts/build_site.py  ──► dist/site/
```

`scripts/clausier.py` lit le référentiel (clauses, pages, données) pour tous les autres
scripts. Il ne dépend que de PyYAML.

## Décisions

| Décision | Choix | Raison |
|---|---|---|
| Source de référence | Markdown + en-tête YAML, un fichier par clause | Lisible, modifiable dans le navigateur GitHub, diff ligne à ligne, aucun outil propriétaire |
| Référence textuelle de la migration | ODT V2, pas le PDF ni le classeur | Structure exacte des tableaux, fusions, gras ; le classeur porte des altérations de copier-coller (voir audit) |
| Outillage | Python seul | Un seul langage pour validation, Excel et site ; 5 dépendances figées |
| Générateur de site | Script Python maison (~400 lignes) plutôt qu'Astro | Astro ajouterait Node et plusieurs centaines de paquets npm pour 120 pages simples ; le script n'a que PyYAML et Markdown comme dépendances et reste lisible par un contributeur Python |
| Base de données, back-end | Aucun | 102 fichiers suffisent ; la sélection est stockée dans le navigateur |
| Classeur | openpyxl, formules INDEX/MATCH, aucune macro | Compatible Excel 2007+ et LibreOffice ; pas de FILTER (Excel 365 seulement) |
| Hébergement | OVH mutualisé de l'INR (cluster127), par `rsync` | Infrastructure déjà utilisée par l'INR (esr.institutnr.org) ; `.htaccess` avec CSP stricte ; GitHub garde les sources et les Releases |

## Site

- 122 pages HTML statiques. Adresses relatives : le site fonctionne à la racine d'un
  domaine, dans un sous-dossier ou ouvert en local.
- Adresse stable par clause : `clausier/clauses/<ID>/`.
- Un seul fichier CSS (~10 Ko) et un seul script (~11 Ko), aucune police téléchargée,
  aucune ressource externe, aucun cookie, aucun traceur.
- Amélioration progressive : sans JavaScript, le catalogue et toutes les fiches restent
  consultables ; filtres, recherche et sélection demandent JavaScript.
- Recherche plein texte : `donnees/clauses.json` (~100 Ko) chargé seulement à la première
  recherche ou sur la page « Ma sélection ».
- Sélection : identifiants dans `localStorage` ; exports Markdown, CSV (séparateur `;`,
  BOM UTF-8 pour Excel), texte, impression PDF par le navigateur.

## Classeur

Feuilles : Présentation, Catalogue, Sélection, Clauses retenues, Lexique, Références,
Crédits. La colonne « Retenir » de la feuille Sélection (liste Oui/Non) alimente un rang
(`COUNTIF`), que la feuille Clauses retenues lit par `INDEX/MATCH`. Le fichier est
reproductible octet pour octet (dates figées dans l'archive).

## PDF (phase ultérieure)

Non réalisé. Option recommandée : une page « clausier complet » du site, mise en forme pour
l'impression (CSS paged media), convertie en PDF par Chrome sans tête
(`--print-to-pdf`) dans la CI. Alternatives : WeasyPrint (dépendances système Pango), ou
génération d'un ODT puis conversion LibreOffice, plus proche de la mise en page d'origine
mais plus lourde à maintenir. En attendant, la page « Ma sélection » s'imprime en PDF et le
PDF V2 d'origine est proposé au téléchargement.

## Écoconception

Mesures en place, contrôlées par `tests/test_livrables.py` :

| Contrôle | Seuil |
|---|---|
| Poids d'une page HTML | ≤ 60 Ko (catalogue : 46 Ko ; fiche : ~5 Ko) |
| CSS | ≤ 15 Ko |
| JavaScript | ≤ 15 Ko, aucune bibliothèque |
| Données JSON | ≤ 200 Ko, chargées à la demande |
| Ressources externes | aucune |

Ces chiffres ne prouvent pas à eux seuls l'écoconception du service. Points à instruire
avec le RGESN (référentiel général d'écoconception de services numériques, Arcep/Arcom/ADEME)
et le RGAA 4.1 pour l'accessibilité : audit RGAA complet par une personne qualifiée,
déclaration d'accessibilité, mesure EcoIndex ou GreenIT-Analysis sur le site publié,
déclaration d'écoconception RGESN. Les versions de ces référentiels sont à vérifier au moment
de l'audit.
