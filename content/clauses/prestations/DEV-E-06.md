---
id: DEV-E-06
titre: Inclusion (compatibilité terminaux anciens / faible connectivité)
segment: prestations
sous_segment: developpement-integration-tma
phase: exigences
section: 5.1.2
ordre: 6
statut: validee
version: '2.0'
source:
  document: clausier-numerique-responsable-v2.odt
  section: 5.1.2
  tableau: Table27
  ligne: 6
  page_pdf: 30
  colonnes:
  - Exigences
  - Commentaires
  - Livrables
  - Niveau 1 (Must have)
  - Niveau 2 (Nice to have)
excel_preparation:
  ligne: 90
  segment: Prestations
  sous_segment: Développement / Intégration / TMA logiciels
  phase: RFI/RFP
  ecarts_de_forme:
  - Livrables
  - Niveau 2 (Nice to have)
  ecarts:
  - Phase « RFI/RFP » dans le classeur ; la clause figure dans la partie exigences de l'ODT.
---

# Inclusion (compatibilité terminaux anciens / faible connectivité)

## Commentaires

Inclusion et Sobriété Technique : Le Titulaire s'engage à concevoir une SOLUTION universellement accessible, garantissant une expérience utilisateur fluide quel que soit l'équipement ou la qualité de la connexion réseau.

- **Compatibilité Matérielle** : La SOLUTION doit être optimisée pour fonctionner sur des terminaux anciens. Le Titulaire doit garantir une compatibilité ascendante avec les navigateurs et systèmes d'exploitation datant d'au moins cinq (5) ans.
- **Performance en connectivité dégradée** : La SOLUTION doit rester fonctionnelle et utilisable sur des réseaux à faible débit (type 3G ou 4G instable). Le Titulaire s'engage à minimiser le poids des pages et le nombre de requêtes serveurs pour permettre un affichage rapide en toutes circonstances.

## Livrables

Pour justifier de la robustesse de la solution :

- **Note de cadrage technique** : Définition précise du parc de terminaux et navigateurs cibles, basée si possible sur l'analyse de l'audience existante.
- **Rapport d'Audit de Performance et Compatibilité (Avant MEP)** : Rapport de tests incluant des mesures de temps de chargement en conditions de "Throttling" (simulation de bas débit) et tests sur navigateurs anciens.
- **Spécifications d'écoconception technique** : Document listant les choix faits pour réduire le poids des ressources (images compressées, lazy-loading, minification du code).

## Niveau 1 (Must have)

- **Seuil de compatibilité 90%** : Garantie de bon fonctionnement sur 90% des navigateurs du marché datant de 5 ans ou plus.
- **Performance "Bas Débit"** : Temps de chargement inférieur à un seuil défini (ex: < 5 secondes) sur une connexion simulée 3G.
- **Dégradation élégante** : Si une fonctionnalité avancée ne fonctionne pas sur un vieux terminal, le service de base doit rester accessible et lisible.

## Niveau 2 (Nice to have)

- **Mode Hors-Ligne** : capacité de la solution à stocker certaines données localement pour permettre une consultation sans réseau.
- **Engagement sur un poids moyen de page inférieur à 1 Mo** (hors vidéo).
- **Compatibilité > 7 ans** : support de terminaux encore plus anciens pour maximiser la durée de vie des équipements des utilisateurs.
- Réalisation des tests sur des appareils réels (vieux smartphones/tablettes) et non uniquement via des émulateurs.
