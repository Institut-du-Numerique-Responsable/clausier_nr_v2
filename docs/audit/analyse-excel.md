# Analyse du classeur de préparation (Paul Saulnier)

Fichier : `prepa excell/Clausier NR V2.xlsx`, dernière modification le 30 septembre 2026.
Auteur selon les propriétés du fichier : Paul SAULNIER.

## Feuilles

| Feuille | Contenu |
|---|---|
| **Notice** | Texte « Comment lire » du V2 (deux parties, niveaux Must have / Nice to have), mention de licence CC BY-NC-ND 4.0, adresse `clausier_nr@institutnr.org`, une image |
| **Clausier** | Tableau structuré `Tableau1` (A2:J103), 101 lignes, volets figés en B3 |
| **Lexique** | Tableau structuré `Tableau2` (A3:C95), 92 termes : Terme, Définition, Catégorie |

## Feuille Clausier

Colonnes : **Critère, Commentaire, Exigences, Livrables, Questions, Niveau 1, Niveau 2,
Segment, Sous segment, Phase.**

- Une ligne par clause, dans l'ordre du document.
- Les sept premières colonnes unifient les en-têtes variables des tableaux du V2 en un
  modèle unique. Exemple : « Description / Spécifications de l'exigence » (1.2) et
  « Exigence » (3.2) vont dans « Exigences » ; l'intitulé des tableaux d'exigences va
  dans « Critère ».
- Trois colonnes de classement, absentes du V2 sous cette forme :
  - **Segment** : `- Transverse -`, `Matériels`, `Services cloud`, `Logiciels`,
    `Prestations`, `IA` ;
  - **Sous segment** : pour Matériels, `Bureautiques`, `Data centers`, `- Transverse -`
    (**classement propre au classeur**, le V2 ne distingue pas ces sous-segments) ;
    pour Prestations et IA, l'intitulé des sous-sections du V2 ;
  - **Phase** : `RFI/RFP` ou `CCAP & CCTP`.
- **Quatre segments (slicers)** connectés aux tableaux : Segment, Sous segment, Phase
  (feuille Clausier) et Catégorie (feuille Lexique). C'est le mécanisme de sélection du
  classeur : l'utilisateur filtre par segment et par phase.
- Aucune formule, aucune validation de données, aucune colonne de sélection individuelle.
- Les quatre noms définis `Segment_*` valent `#N/A` : artefact normal des segments Excel.
- Un commentaire de cellule (A84, « SAULNIER : Coquille dans la source ») accompagne le
  renommage de l'intitulé « Écoconception » en « Formation écoconception ».

## Qualité du texte

Comparaison automatique cellule par cellule avec l'ODT (`scripts/audit_compare.py`) :

| Résultat | Cellules |
|---|---|
| Identique | 393 |
| Différence de forme seulement | 73 (52 lignes) |
| Différence de contenu | 5 |
| Ligne absente | 1 clause |

Les différences de forme viennent d'un copier-coller depuis le PDF :

- traits d'union de césure perdus : « fait-elle » → « faitelle », « non-discrimination » →
  « nondiscrimination », « sous-traitants » → « soustraitants » ;
- espaces parasites en milieu de mot : « environnementale » → « environnement ale »,
  « Responsable » → « Responsab le » ;
- puces devenues tirets dans le texte, retours à la ligne du PDF conservés ;
- quelques points finaux perdus ou ajoutés.

Ces altérations touchent le texte. Le classeur ne peut donc pas servir de source textuelle ;
l'ODT reste la référence. Les écarts de contenu sont détaillés dans
[correspondances.md](correspondances.md) et [divergences.md](divergences.md).

## Apports repris dans le projet

| Apport du classeur | Reprise |
|---|---|
| Modèle de sept colonnes unifiées | Colonnes du classeur généré (`data/colonnes.yml`) |
| Colonnes Segment / Sous segment / Phase | Champs `segment`, `sous_segment`, `phase` ; libellés courts dans `data/segments.yml` |
| Sous-segments Bureautiques / Data centers / Transverse | Repris pour les 24 clauses Matériels, attribués au classeur (`origine: excel-preparation`) |
| Filtrage par segment et phase | Filtres automatiques du tableau structuré généré ; filtres du site |
| Feuille Notice | Feuille « Présentation » du classeur généré |
| Feuille Lexique avec catégories | Feuille « Lexique » du classeur généré |
| Tableaux structurés, volets figés | Repris |
| Slicers | Non reproductibles avec openpyxl : remplacés par les filtres automatiques (voir recommandations) |
