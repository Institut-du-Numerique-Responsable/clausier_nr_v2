# Analyse du document V2 (PDF et ODT)

**Le PDF V2 fait foi.** Pour en extraire la structure (tableaux, cellules fusionnées, gras,
listes), on lit l'ODT dont il est le rendu direct (même date de génération, 11 août 2026) :
l'extraction depuis un PDF en colonnes mélange les cellules. Le texte obtenu est ensuite
recherché dans le PDF, segment par segment (`scripts/check_integrity.py`) : aucune différence
de texte constatée.

## Plan du document (44 pages)

| Pages | Partie | Contenu |
|---|---|---|
| 1 | Couverture | Titre, « Version 2.0 », « Aout 2026 », mention de licence |
| 2 | Remerciements | Pilotage EDF, coordination FTCC/INR, une cinquantaine d'organisations contributrices |
| 3 | Sommaire | Généré |
| 4–5 | Enjeux et objectifs | Texte, 5 notes de bas de page (Arcep, Shift Project, AIE, CSRD, INR) |
| 6 | L'approche | Principes, périmètre de la V2 (social, éthique, accessibilité, IA) |
| 7 | Comment lire le clausier | Étapes d'un appel d'offres, deux parties par segment, niveaux Must have / Nice to have |
| 8–13 | 1. Exigences communes | 1.1 questionnaire (17), 1.2 exigences CCAP & CCTP (10) |
| 14–19 | 2. Matériels bureautiques et datacenter | 2.1 questionnaire (17), 2.2 exigences (7) |
| 20–24 | 3. Services cloud | 3.1 définitions IaaS/PaaS/SaaS, 3.2 questionnaire (15), 3.3 exigences (3) |
| 25–26 | 4. Logiciels | 4.1 questionnaire (6), 4.2 exigences (5) |
| 27–33 | 5. Prestations | 5.1 Dév./intégration/TMA : 5.1.1 (2), 5.1.2 (6) ; 5.2 Infogérance : 5.2.1 (5), 5.2.2 renvoi |
| 34–37 | 6. Achats IA/IAg | 6.1 définitions, 6.2 cinq segments d'achat, 6.3 (3), 6.4 (3), 6.5 (3) |
| 38 | Sources documentaires | 6 références avec adresses |
| 39–44 | Lexique | 93 termes en 9 catégories, mentions de licence et contact |

**Total : 102 lignes de tableaux, soit 102 clauses**, réparties en 16 tableaux.

## Structure d'une clause

Chaque clause est une ligne de tableau. Les colonnes varient selon le tableau :

| Tableaux | 1ʳᵉ colonne | Colonnes suivantes |
|---|---|---|
| 1.1, 2.1, 5.1.1, 5.2.1, 6.3–6.5 | Critères | Commentaires, Questions, Niveau 1, Niveau 2 |
| 3.2 | Critères | **Exigence**, Questions, Niveau 1, Niveau 2 |
| 4.1 | Critères | Questions, Niveau 1, Niveau 2 |
| 1.2 | Exigences | Description / Spécifications de l'exigence, Livrables, Niveau 1, Niveau 2 |
| 2.2 | Critère | Exigences, Livrables, Niveau 1, Niveau 2 |
| 3.3, 5.1.2 | Exigences | Commentaires, Livrables, Niveau 1, Niveau 2 |
| 4.2 | Exigences | Livrables, Niveau 1, Niveau 2 |

« Niveau 1 » porte la mention « (Must have) », « Niveau 2 » la mention « (Nice to have) ».

Informations **présentes** pour chaque clause : intitulé, segment, partie (questionnaire
ou exigences), texte des colonnes ci-dessus, page.

Informations **absentes** du document : identifiant, statut, date, auteur de la clause,
références réglementaires structurées, mots-clés. Aucune n'a été inventée. L'identifiant
est créé selon la convention de `docs/modele-documentaire.md` ; les autres restent des
enrichissements possibles (voir [recommandations.md](recommandations.md)).

## Particularités relevées

- **Cellules fusionnées verticalement** : « Écolabels/certification de produits » (6 lignes,
  intitulé et questions communs), « MCO & Réparabilité » (2), « Accessibilité Numérique »
  en 5.1.2 (2), « Infogérance à distance » (2). Chaque ligne devient une clause ; le texte
  fusionné est recopié dans chacune et la fusion est consignée (`source.cellules_fusionnees`).
- **Notes de bas de page dans les cellules** : 5 notes (adresses Energy Star, TCO Certified,
  Blauer Engel, EPEAT) dans le tableau 2.1, reprises en notes Markdown.
- **Exposants sans note** : « CDP⁷ » et « ADEME⁸ » (critère « Transparence sur l'empreinte
  environnementale de l'entreprise ») n'ont pas de note correspondante, ni dans l'ODT ni dans
  le PDF. Conservés tels quels en `<sup>`.
- **Mise en forme porteuse de sens** : gras et italique dans les cellules (« **Indicateurs
  légaux** : … »), conservés en Markdown.
- **Notes 18 à 20** (définitions PUE, WUE, CUE) placées comme paragraphes après le premier
  tableau 3.2 ; reprises dans `content/segments/cloud.md`.
- **Section 5.2.2** sans tableau : renvoi « Se reporter aux exigences transverses dans la
  partie 1.1 », lien interne vers un signet.
- **Section 6** : uniquement des questionnaires ; aucune partie « exigences ».
- **Illustrations** : 7 images dans l'ODT (logos et visuels de couverture, image du lexique
  au texte alternatif généré automatiquement). Non reprises : leurs conditions de
  réutilisation ne sont pas établies.

## Références réglementaires et normatives

Les références figurent dans le texte des clauses (RGESN, RGAA 4.1, WCAG, EN 301 549,
ISO 14001, ISO 14064, ISO 14024, ISO/IEC 21031, CSRD, CS3D, AI Act, REACH, RoHS, AGEC,
REEN, SecNumCloud, Energy Star, EPEAT, TCO Certified, Blauer Engel…) et dans la section
« Sources documentaires » (6 références). Seules ces 6 références structurées sont reprises
dans `data/references.yml`. Les références citées dans le corps des clauses restent dans
leur texte ; leur extraction en données structurées est un enrichissement proposé.
