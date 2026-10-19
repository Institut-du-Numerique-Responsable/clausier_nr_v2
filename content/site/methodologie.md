---
titre: Méthodologie
description: D'où viennent les textes, comment ils sont tenus à jour.
---

## Une source unique

L'INR tient le texte des clauses dans des fichiers Markdown, un par clause, sur le dépôt du
projet. Des scripts en tirent le site, le classeur Excel et les exports. Pour changer un
livrable, on modifie le fichier source puis on relance la génération.

## Reprise du document V2

Un script a converti le Clausier Numérique Responsable V2 (août 2026, 44 pages) en
Markdown, sans réécrire une ligne. Il conserve le gras, l'italique, les listes, les notes et
les liens. Chaque clause indique sa section, son tableau et sa page dans le PDF V2, qui fait
foi.

Un contrôle compare chaque clause au V2, rubrique par rubrique, puis cherche son texte dans le
PDF. Il vérifie aussi la reprise des textes hors tableaux. Résultat : 102 clauses sur 102
identiques au V2.

Le classeur de préparation de Paul Saulnier a fourni le modèle de colonnes, le classement par
segment, sous-segment et phase, et le lexique. L'audit liste les écarts entre ce classeur et
le V2 ; le comité les arbitre, et le texte des clauses reste celui du V2 en attendant.

## Évolutions

Pour modifier une clause, vous déposez une proposition publique ; les mainteneurs désignés
par l'INR la relisent et la valident. Chaque clause modifiée garde la trace de ses
changements depuis le V2. Voir [Contribuer](../contribuer/) et
l'[historique des versions](../versions/).
