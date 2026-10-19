# Correspondances entre le V2 et le classeur de préparation

Méthode : `scripts/audit_compare.py` aligne les 102 lignes de tableaux de l'ODT et les
101 lignes du classeur, puis compare chaque cellule. Le détail ligne par ligne est dans
`build/audit/comparaison.json` (régénérable) et dans l'en-tête de chaque clause
(`excel_preparation`).

## Matrice par élément

| Élément | V2 (ODT/PDF) | Classeur | Action retenue |
|---|---|---|---|
| Identifiant | Absent | Absent | **Créé** : convention `SEG-P-NN` (voir `docs/modele-documentaire.md`) |
| Intitulé | 1ʳᵉ colonne du tableau | Critère | Texte du V2 conservé ; 2 écarts consignés |
| Commentaires / descriptions | En-têtes variables selon le tableau | Commentaire ou Exigences | Rubrique Markdown au nom de l'en-tête du V2 ; colonne Excel selon `data/colonnes.yml` |
| Questions, Livrables, Niveaux 1 et 2 | Présents selon le tableau | Mêmes colonnes | Texte du V2 conservé |
| Segment | Titre de niveau 1 | Segment (libellé court) | Champ `segment` ; libellé court du classeur pour l'affichage |
| Sous-segment | Titres 5.1, 5.2, 6.3–6.5 | Sous segment | Repris ; Matériels : classement du classeur |
| Phase | Partie questionnaire ou exigences | Phase | Partie du V2 ; 3 écarts consignés |
| Ordre | Ordre des lignes | Ordre des lignes | Champ `ordre`, distinct de l'identifiant |
| Page | Pagination PDF | — | Champ `source.page_pdf` |
| Mise en forme (gras, italique, listes) | Présente | Perdue | Conservée en Markdown |
| Notes de bas de page | 5 dans les cellules | Perdues | Notes Markdown |
| Références | Section Sources documentaires | Absentes | `data/references.yml` |
| Lexique | 93 termes, 9 catégories | 92 termes | Lexique du V2 ; 2 écarts consignés |

## Correspondance des colonnes

| En-tête du V2 | Colonne du classeur | Tableaux |
|---|---|---|
| Critères / Critère / Exigences (1ʳᵉ colonne) | Critère | tous |
| Commentaires | Commentaire | 1.1, 2.1, 5.1.1, 5.1.2, 5.2.1, 6.3–6.5 |
| Commentaires | **Exigences** | 3.3 |
| Exigence | Exigences | 3.2 |
| Exigences (2ᵉ colonne) | Exigences | 2.2 |
| Description / Spécifications de l'exigence | Exigences | 1.2 |
| Questions | Questions | questionnaires |
| Livrables | Livrables | exigences |
| Niveau 1 (Must have) | Niveau 1 | tous |
| Niveau 2 (Nice to have) | Niveau 2 | tous |

Le classeur range la colonne « Commentaires » du tableau 3.3 dans « Exigences », et celle
du tableau 5.1.2 dans « Commentaire ». Le classeur généré applique une règle unique
(« Commentaires » → « Commentaire »), signalée en D-03.

## Écarts de contenu, ligne par ligne

| Clause | Ligne du classeur | V2 | Classeur |
|---|---|---|---|
| COM-Q-06 | 8 | Niveau 2 : « … CDP⁷ et / ou ADEME⁸ » | exposants absents (forme) |
| MAT-Q-12 | 41 | Intitulé « Emballages écoconçu » | « Emballages écoconçus » |
| CLD-Q-10 | 63 | Niveau 2 « Plan d'action opposables » | « Plan d'action opposable » |
| LOG-E-02 | 79 | Niveau 2 « Fourniture de scripts de configuration automatisés (profils "éco") pour le déploiement. » | **Niveau 2 vide** |
| DEV-Q-02 | 84 | Intitulé « Écoconception » | « Formation écoconception », commentaire « Coquille dans la source » |
| DEV-E-04, DEV-E-05, DEV-E-06 | 88–90 | Partie 5.1.2 Exigences | Phase « RFI/RFP » |
| IA-Q-06 | — | « Sobriété du Modèle » (6.4) | **Ligne absente** |
