# Inventaire des sources

Audit réalisé le 19 octobre 2026 sur le répertoire de travail `clausier_v2/`.

## Fichiers examinés

| Fichier (répertoire de travail) | Nature | Date | Taille | Rôle retenu |
|---|---|---|---|---|
| `odt/clausier-numerique-responsable-v2.odt` | Document maître V2, OpenDocument | 11 août 2026 | 347 Ko | **Référence textuelle de la migration** |
| `pdf/clausier-numerique-responsable-v2.pdf` | Rendu LibreOffice du maître, 44 pages A4, PDF balisé | 11 août 2026 | 1,3 Mo | Référence de pagination et contrôle du rendu |
| `prepa excell/Clausier NR V2.xlsx` | Classeur de préparation, Paul Saulnier | 30 sept. 2026 | 131 Ko | Référence fonctionnelle et ergonomique du classeur |
| `old/sources/20260515-clausier-relecture-commentee.docx` | Copie de relecture, 83 commentaires | 15 mai 2026 | 1,3 Mo | Non reprise (a divergé du maître, voir README d'origine) |
| `old/sources/202606-clausier-interne-v1-relecture.pdf` | PDF de relecture V1 interne | juin 2026 | 1,2 Mo | Non reprise |
| `old/versions/202606-clausier-interne-v1-original.odt` | Version antérieure | juin 2026 | — | Non reprise |
| `docs/commentaires-relecture.json` | 83 commentaires extraits du .docx | 10 août 2026 | 31 Ko | Signalé dans les recommandations |
| `docs/refonte-redactionnelle.md` | Propositions de refonte, non appliquées | 10 août 2026 | 17 Ko | Signalé dans les recommandations |
| `outils/*.py` | Scripts de mise en page de l'ODT (lxml) | 10 août 2026 | — | Non repris ; `extract_texte.py` a inspiré `scripts/odt_extract.py` |

Le PDF et l'ODT portent le même horodatage (11 août 2026, 10:47) : le PDF est le rendu
LibreOffice 26.2 de l'ODT. Les métadonnées du PDF indiquent « FARES Sirine » comme auteur
du fichier et « Writer » comme créateur.

## Copies dans le projet

Les trois sources de référence sont copiées, à l'identique, dans `sources/originaux/`.
Aucun fichier du répertoire de travail n'a été modifié.

| Copie | SHA-256 |
|---|---|
| `clausier-numerique-responsable-v2.odt` | `298a7c997cb732da0306ac4b7ac89beb125031a4ce77d5e45cff15065f54af24` |
| `clausier-numerique-responsable-v2.pdf` | `ba578c21017b08ea630a10a914a84669771349267fcad1ecd49e4c81b26f1153` |
| `clausier-nr-v2-prepa-excel-paul-saulnier.xlsx` | `28912b4acfb3e72b92e4b4b015748da8a9eafca8f93f618c6adf22904d02394f` |

Le classeur a été renommé en ASCII, sans espace, selon la convention du README d'origine.
Les empreintes sont reprises dans `sources/manifest.yml` et contrôlées par les tests.

## Dépôts GitHub existants

Vérifications en lecture seule dans l'organisation `Institut-du-Numerique-Responsable` :

- `clausier-numerique-responsable` : **libre** (réponse 404).
- `clausier_nr_v2` : **existe déjà**, public, créé le 10 août 2026. Il contient un README
  d'une ligne, un `CODEOWNERS` et un fichier `LICENSE` **CC BY-SA 4.0** (PR #2 du
  28 août 2026). Cette licence contredit la mention CC BY-NC-ND 4.0 des documents
  (voir [divergences.md](divergences.md), D-01).

## Propriété intellectuelle et crédits relevés

- Mention portée par la couverture, la dernière page du PDF et la feuille « Notice » du
  classeur : « Clausier Numérique Responsable © 2026 by French Tech Corporate Community
  (FTCC) & Institut du Numérique Responsable (INR) is licensed under CC BY-NC-ND 4.0 ».
- Pilotage : Richard BURY (Groupe EDF) et Claire LARDIERE (EDF SA), page 2.
- Coordination : FTCC et INR.
- 51 mentions d'organisations contributrices et de leurs représentants, page 2 (une cinquantaine d'organisations). Paul SAULNIER y figure
  pour la MACIF.
- Classeur de préparation : propriétés du fichier « créateur » et « dernière modification »
  au nom de Paul SAULNIER ; un commentaire de cellule signé « SAULNIER ». Ces éléments
  corroborent l'attribution du classeur à Paul Saulnier.
