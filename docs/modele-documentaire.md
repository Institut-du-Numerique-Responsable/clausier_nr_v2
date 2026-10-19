# Modèle documentaire

## Une clause, un fichier

Chemin : `content/clauses/<segment>/<ID>.md`. Le fichier contient un en-tête YAML, un titre
`#` égal au champ `titre`, puis des rubriques `##`.

### En-tête

| Champ | Obligatoire | Contenu |
|---|---|---|
| `id` | oui | Identifiant stable (voir ci-dessous) |
| `titre` | oui | Intitulé, 1ʳᵉ colonne du tableau du V2 |
| `segment` | oui | `commun`, `materiels`, `cloud`, `logiciels`, `prestations`, `ia` |
| `sous_segment` | selon segment | Slug déclaré dans `data/segments.yml` ; obligatoire pour Matériels, Prestations, IA |
| `phase` | oui | `questionnaire` (RFI/RFP) ou `exigences` (CCAP & CCTP) |
| `section` | oui | Section du clausier (`1.1`, `5.1.2`…) |
| `ordre` | oui | Position dans la section, indépendante de l'identifiant |
| `statut` | oui | `brouillon`, `en_revision`, `validee`, `archivee` |
| `version` | oui | Version du clausier où le texte a été validé |
| `source` | migration | Document, section, tableau, ligne, page PDF, en-têtes de colonnes, cellules fusionnées |
| `excel_preparation` | migration | Ligne du classeur de Paul Saulnier, son classement, écarts constatés |
| `modifications` | si modifiée | Journal des modifications du texte depuis le V2 |
| `remplace` | facultatif | Identifiant d'une clause remplacée |
| `tags` | facultatif | Mots-clés (aucun dans le V2) |

Le schéma complet : `schemas/clause.schema.json`.

### Rubriques

Les titres `##` reprennent les en-têtes de colonnes du V2. Ces en-têtes varient d'un tableau
à l'autre (voir `docs/audit/analyse-pdf.md`) ; ils sont conservés. `data/colonnes.yml` liste
les rubriques autorisées et la colonne du classeur où chacune est publiée.

Une cellule vide du V2 ne donne pas de rubrique. `source.colonnes` garde la liste complète des
colonnes du tableau d'origine.

## Identifiants

Format : `SEG-P-NN`.

| Partie | Valeurs |
|---|---|
| `SEG` | `COM` exigences communes, `MAT` matériels, `CLD` services cloud, `LOG` logiciels, `DEV` développement / intégration / TMA, `INF` infogérance, `IA` IA/IAg |
| `P` | `Q` questionnaire (RFI/RFP), `E` exigences (CCAP & CCTP) |
| `NN` | Numéro attribué à la création, sur deux ou trois chiffres |

Règles :

- **Un identifiant ne change jamais**, même si la clause est déplacée ou reclassée. Le
  préfixe reflète le classement d'origine.
- **Un identifiant n'est jamais réattribué**. Une clause retirée passe au statut `archivee`
  et reste dans le dépôt.
- Une nouvelle clause prend le numéro libre suivant de son préfixe.
- L'ordre d'affichage vient de `section` et `ordre`, pas de l'identifiant.

Les numéros de la migration suivent l'ordre du V2 : COM-Q-01 est la première ligne du
tableau 1.1. Ils ne dépendent plus de cette position ensuite.

Le préfixe `DEV` (sous-segment 5.1) et `INF` (5.2) distinguent les deux sous-segments de
« Prestations », qui ont des tableaux séparés dans le V2. Les trois sous-segments IA
partagent `IA-Q`, numérotés à la suite (6.3, puis 6.4, puis 6.5), comme dans le classeur.

## Textes hors clauses

| Emplacement | Contenu |
|---|---|
| `content/pages/*.md` | Pages du V2 : couverture, remerciements, enjeux, approche, comment lire, sources, mentions finales |
| `content/segments/*.md` | Texte des sections de segment (définitions 3.1, 6.1, 6.2…) ; le marqueur `<!-- clauses section="2.1" -->` indique où le site insère la liste des clauses |
| `content/site/*.md` | Pages rédigées pour le site (hors V2) |
| `data/lexique.yml` | Lexique du V2, 93 termes |
| `data/references.yml` | Sources documentaires du V2 |

## Traçabilité

Pour chaque clause : document, section, tableau, ligne, page du PDF (`source`), ligne du
classeur de préparation et écarts (`excel_preparation`), modifications (`modifications`),
historique Git. `scripts/check_integrity.py` vérifie à chaque exécution que tout le V2 est
repris, rubrique par rubrique face à l'ODT et segment par segment face au PDF, qui fait foi :
rapport dans `docs/audit/rapport-integrite.md`.
