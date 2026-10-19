---
id: MAT-Q-07
titre: Performance énergétique - Efficacité énergétique
segment: materiels
sous_segment: datacenter
phase: questionnaire
section: '2.1'
ordre: 7
statut: validee
version: '2.0'
source:
  document: clausier-numerique-responsable-v2.odt
  section: '2.1'
  tableau: Table12
  ligne: 7
  page_pdf: 15
  colonnes:
  - Critères
  - Commentaires
  - Questions
  - Niveau 1 (Must have)
  - Niveau 2 (Nice to have)
excel_preparation:
  ligne: 36
  segment: Matériels
  sous_segment: Data centers
  phase: RFI/RFP
  ecarts_de_forme:
  - Niveau 1 (Must have)
---

# Performance énergétique - Efficacité énergétique

## Commentaires

Équipements en datacenter

## Questions

- Pour chaque type d'équipement mobilisé (serveurs, stockage, réseau), pouvez-vous fournir une matrice de consommation électrique détaillée incluant les trois états suivants : Pleine charge (100%), Charge nominale (50%) et Mode veille (Idle/Standby) ?
- Quel est le ratio entre la consommation en mode veille et la consommation en charge maximale pour vos équipements ? Comment ce ratio se compare-t-il aux standards de l'état de l'art (ex: Code de conduite européen sur les centres de données) ?
- Quel est le niveau de certification 80 PLUS des blocs d'alimentation (PSU) utilisés dans vos serveurs ? (Note : Le niveau Titanium est ici la cible d'excellence).
- Quelle est votre politique de renouvellement du matériel ? Comment garantissez-vous que les processeurs (CPU) utilisés offrent le meilleur ratio Performance/Watt disponible au moment de la mise en production ?
- Quelles sont les fonctionnalités de Power Management (gestion de l'énergie) activées nativement sur vos infrastructures pour réduire la consommation lors des phases de faible sollicitation ?
- Disposez-vous d'outils d'orchestration permettant la mise hors tension automatique ou la mise en sommeil profonde des nœuds de calcul non sollicités (lutte contre les "serveurs fantômes") ? Si oui, décrivez le fonctionnement.

## Niveau 1 (Must have)

- Fourniture obligatoire des valeurs de consommation pleine charge / veille pour chaque équipement.
- Certification 80 PLUS Bronze ou équivalent au minimum pour tous les équipements datacenter.
- Présence de fonctionnalités natives de gestion d'énergie (mise en veille automatique des composants non sollicités).

## Niveau 2 (Nice to have)

- Alimentations certifiées 80 PLUS PLATINIUM ou TITANIUM, ou équivalent (rendement > 94%).
- Utilisation de processeurs de dernière génération avec un rapport performance/watt supérieur de 20% à la génération précédente.
- Engagement sur une consommation en veille ne dépassant pas 10% de la consommation en pleine charge.
- Équipements conçus pour fonctionner à des températures ambiantes plus élevées (permettant de réduire le besoin en climatisation du datacenter).
