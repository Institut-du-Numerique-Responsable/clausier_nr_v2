# Clausier Numérique Responsable

Clauses types « numérique responsable » à intégrer dans les consultations et marchés IT :
questionnaires d'évaluation des soumissionnaires (RFI/RFP) et exigences pour le cahier des
charges (CCAP & CCTP), en deux niveaux, *Must have* et *Nice to have*.

Le clausier est coordonné par la French Tech Corporate Community (FTCC) et l'Institut du
Numérique Responsable (INR). Sa version 2.0 (août 2026) compte 102 clauses réparties en six
segments d'achat.

## Accéder au clausier

| | Lien |
|---|---|
| Page officielle | https://institutnr.org/clausier-numerique-ecoresponsable |
| Document PDF (V2, 44 pages) | [clausier-numerique-responsable-v2.pdf](https://institutnr.org/wp-content/uploads/2026/09/clausier-numerique-responsable-v2.pdf) |
| Classeur Excel (catalogue, sélection, clauses retenues) | [Clausier-Numerique-Responsable-V2.xlsx](https://github.com/Institut-du-Numerique-Responsable/clausier_nr_v2/releases/latest/download/Clausier-Numerique-Responsable-V2.xlsx) (disponible à la première version publiée) |
| Site de consultation (recherche, sélection, exports) | en cours de mise en ligne sur l'hébergement de l'INR |
| Clauses au format texte | dossier [`content/clauses/`](content/clauses/) |

## Le principe d'un clausier

Un clausier n'est pas un cahier des charges à reprendre en bloc. C'est une **bibliothèque de
clauses prérédigées** dans laquelle chaque organisation **prend ce qu'elle estime nécessaire**
et l'intègre à son propre processus d'achat :

- dans une **consultation** ou un **sourcing**, pour interroger le marché ;
- dans un **RFI ou un RFP**, avec les questionnaires d'évaluation des soumissionnaires ;
- dans le **cahier des charges** (CCAP, CCTP) ou le **contrat**, avec les exigences suivies
  pendant l'exécution ;
- dans un avenant, une convention de service ou une politique d'achat interne.

Les clauses sont **prêtes à l'emploi mais restent ajustables**. Chaque entreprise, collectivité
ou administration les adapte à son contexte : périmètre de l'achat, maturité du marché,
contraintes de la commande publique, stratégie RSE, poids accordé à chaque critère. Les deux
niveaux de chaque clause aident à calibrer l'ambition : le *Must have* comme socle, le
*Nice to have* pour valoriser les offres les plus avancées.

La licence CC BY 4.0 le permet expressément : reprenez, modifiez et intégrez les clauses,
y compris dans un cadre commercial, en citant la source.

## Le dépôt

Ce dépôt fait du clausier un référentiel ouvert et maintenable : **le texte des clauses est tenu en
Markdown, un fichier par clause**. Le classeur Excel et le site sont générés à partir de ces
fichiers ; on ne les modifie jamais à la main.

```
content/clauses/*.md  ──►  scripts/  ──►  dist/excel/   classeur Excel
     (source)                       └──►  dist/site/    site statique (recherche, sélection, exports)
```

## Démarrer

Prérequis : Python 3.10 ou plus. Facultatif : poppler (`pdftotext`) et LibreOffice pour
deux contrôles.

```sh
make install     # environnement .venv et dépendances
make validate    # contrôle des fichiers Markdown
make test        # tous les tests
make build       # validation, classeur Excel, site
make serve       # site sur http://127.0.0.1:8000/
```

| Commande | Effet |
|---|---|
| `make validate` | Schéma des en-têtes, identifiants, rubriques, notes, liens internes |
| `make integrity` | Compare le Markdown au document V2 ; écrit `docs/audit/rapport-integrite.md` |
| `make excel` | `dist/excel/Clausier-Numerique-Responsable-V2.xlsx` |
| `make site` | `dist/site/` (classeur inclus en téléchargement) |
| `make test` | Tests documentaires, classeur, site, cohérence entre formats |

## Organisation

| Dossier | Contenu |
|---|---|
| `content/clauses/<segment>/<ID>.md` | Une clause par fichier : en-tête YAML, rubriques du V2 |
| `content/segments/` | Introductions et définitions de chaque segment (texte du V2) |
| `content/pages/` | Pages du V2 hors clauses : enjeux, approche, comment lire, remerciements… |
| `content/site/` | Pages propres au site : mode d'emploi, méthodologie, contribuer, mentions légales |
| `data/` | Segments et phases, rubriques autorisées, lexique, références, métadonnées |
| `schemas/` | Schéma JSON de l'en-tête d'une clause |
| `scripts/` | Validation, intégrité, génération Excel et site, migration initiale |
| `site/assets/` | Feuille de style et script du site |
| `sources/` | Documents d'origine, copies figées et empreintes (`manifest.yml`) |
| `tests/` | Tests (`unittest`, aucune dépendance de test) |
| `docs/` | Architecture, modèle documentaire, maintenance, charte, audit |

## Une clause

```markdown
---
id: CLD-Q-01
titre: PUE
segment: cloud
sous_segment: null
phase: questionnaire
section: '3.2'
ordre: 1
statut: validee
version: '2.0'
source: {document: clausier-numerique-responsable-v2.odt, section: '3.2', page_pdf: 20, …}
---

# PUE

## Exigence
…
## Niveau 1 (Must have)
…
```

Le détail est dans [docs/modele-documentaire.md](docs/modele-documentaire.md).

## Publication

La page du clausier sur institutnr.org renvoie vers le site, le classeur, le PDF et ce
dépôt. Les livrables sont publiés en Release GitHub sous des noms fixes, pour des liens
stables même après archivage : voir [docs/publication.md](docs/publication.md).

## Contribuer

Signaler une erreur, proposer une correction ou une clause : voir
[CONTRIBUTING.md](CONTRIBUTING.md). Aucune connaissance de Git n'est nécessaire pour ouvrir
un signalement. Les modifications sont validées par les mainteneurs désignés par l'INR
([GOVERNANCE.md](GOVERNANCE.md)).

## Crédits

**Paul Saulnier** — Contribution initiale à la structuration et à la préparation du classeur
Excel du Clausier Numérique Responsable V2. Liste complète : [CONTRIBUTORS.md](CONTRIBUTORS.md).

## Licence

Contenu sous **CC BY 4.0** : réutilisation et modification libres, y compris commerciales,
à condition de citer la source (« Clausier Numérique Responsable, Institut du Numérique
Responsable (INR) et French Tech Corporate Community (FTCC), licence CC BY 4.0 ») et
d'indiquer les modifications. Licence du code à choisir. Détails : [LICENSE.md](LICENSE.md).

Page officielle : https://institutnr.org/clausier-numerique-ecoresponsable

Contact : `contact@institutnr.org`
