# Rapport d'intégrité documentaire

Généré le 2026-10-19 par `scripts/check_integrity.py`. Ne pas modifier à la main.

Référence : **le PDF V2 fait foi** (`sources/originaux/clausier-numerique-responsable-v2.pdf`, 44 pages). L'ODT dont il est le rendu (`clausier-numerique-responsable-v2.odt`) sert à extraire la structure des tableaux ; les deux sont comparés au Markdown.

## Synthèse

| Contrôle | Résultat |
|---|---|
| Lignes de tableaux du V2 | 102 |
| Clauses Markdown | 102 (validee : 102) |
| Clauses identiques au V2, rubrique par rubrique | 102 |
| Clauses modifiées avec journal de modifications | 0 |
| Pertes ou écarts non consignés | 0 |
| Clauses sans équivalent dans le V2 | 0 |
| Paragraphes hors tableaux du V2 | 144 |
| Paragraphes ou titres introuvables dans content/ | 0 |
| Clauses dont un mot manque dans le texte du PDF | 1 |
| Segments de 20 lettres comparés au PDF | 2668 |
| … retrouvés tels quels | 2626 |
| … séparés dans le PDF par du texte voisin (mise en page) | 30 |
| … à relire visuellement (début ou fin de cellule) | 12 |

## Segments à relire dans le PDF

Début ou fin de cellule non retrouvé tel quel : en général un appel de note collé au mot (« CDP7 »), une cellule coupée entre deux pages ou une colonne voisine intercalée. Relecture du 19 octobre 2026 : tous ces cas relèvent de la mise en page, aucune différence de texte. Toute nouvelle ligne ici doit être relue.

| Clause | Page | Rubrique | Segment |
|---|---|---|---|
| COM-Q-06 | 10 | Niveau 2 (Nice to have) | `eformecdpetouademe` |
| COM-Q-13 | 10 | Niveau 2 (Nice to have) | `auniveaueuropeen` |
| COM-E-07 | 12 | titre | `tesocialeetethiquede` |
| MAT-Q-01 | 15 | Niveau 1 (Must have) | `epeatouenergystaroue` |
| MAT-Q-02 | 15 | Niveau 1 (Must have) | `epeatouenergystaroue` |
| MAT-Q-03 | 15 | Niveau 1 (Must have) | `blueangelouenergysta` |
| CLD-Q-12 | 21 | titre | `cycledeviedesdonnees` |
| CLD-Q-12 | 21 | Exigence | `serlesvolumesdedonne` |
| DEV-E-03 | 28 | Niveau 2 (Nice to have) | `sdansledomaineordina` |
| IA-Q-08 | 36 | Commentaires | `analysedelaperforman` |
| IA-Q-08 | 36 | Niveau 1 (Must have) | `publicationdesdonnee` |
| IA-Q-08 | 36 | Niveau 2 (Nice to have) | `garantiedunratioperf` |

## Contrôle du rendu PDF (mots)

Mots présents dans le Markdown mais absents du texte extrait du PDF. Les césures avec tiret sont recollées. Un mot coupé sans tiret dans une colonne étroite (ex. « applic » / « atifs ») apparaît ici sans qu'il y ait de perte : vérifier à l'œil à la page indiquée.

- COM-E-06 (page 12) : applicatifs
