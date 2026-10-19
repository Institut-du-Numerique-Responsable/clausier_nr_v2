---
id: CLD-Q-12
titre: Cycle de Vie des Données
segment: cloud
sous_segment: null
phase: questionnaire
section: '3.2'
ordre: 12
statut: validee
version: '2.0'
source:
  document: clausier-numerique-responsable-v2.odt
  section: '3.2'
  tableau: Table20
  ligne: 5
  page_pdf: 21
  colonnes:
  - Critères
  - Exigence
  - Questions
  - Niveau 1 (Must have)
  - Niveau 2 (Nice to have)
excel_preparation:
  ligne: 65
  segment: Services cloud
  sous_segment: null
  phase: RFI/RFP
  ecarts_de_forme:
  - Critères
  - Exigence
---

# Cycle de Vie des Données

## Exigence

- Définir une date de fin de vie des données
- Fournir des outils pour minimiser les volumes de données

## Questions

Le Titulaire s’engage à intégrer les principes de sobriété des données dès la phase de conception de la SOLUTION.

- **Cycle de vie** : Le Titulaire doit définir, pour chaque catégorie de données traitées, une durée de conservation limitée et un mécanisme de purge automatique ou de d'archivage compressé en fin de vie.
- **Optimisation des volumes** : Le Titulaire met à disposition du Client des fonctionnalités et des outils d'administration permettant de monitorer et de réduire activement les volumes de données stockées (déduplication, compression, suppression assistée).

## Niveau 1 (Must have)

- Paramétrage manuel ou automatique de dates de péremption par dossier ou type de fichier.
- Utilisation de formats de fichiers compressés et algorithmes de déduplication standards
- Fourniture d'un indicateur global de volume stocké.

Limitation du nombre de versions sauvegardées (versioning raisonné).

## Niveau 2 (Nice to have)

- Purge automatique intelligente avec alertes préalables et rapport de gain de stockage associé.
- Déduplication à la source et optimisation dynamique des bases de données (sharding, indexing écoconçu).
- Analyse trimestrielle des données "mortes" et recommandations de nettoyage.
