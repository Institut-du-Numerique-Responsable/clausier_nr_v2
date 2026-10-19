# Recommandations

## Décisions à prendre avant publication

| N° | Décision | Qui | Référence |
|---|---|---|---|
| 1 | ~~Licence des contenus~~ : CC BY 4.0 (INR, 19/10/2026) ; **accord de la FTCC à obtenir** | FTCC | D-01 |
| 2 | Licence du code (proposition : EUPL-1.2 ou MIT) | INR | `LICENSE.md` |
| 3 | ~~Dépôt cible~~ : `clausier_nr_v2` (INR, 19/10/2026) | INR | inventaire |
| 4 | Markdown source de référence, ODT archivé | Pilotage | D-02 |
| 5 | ~~Adresse de contact unique~~ : `contact@institutnr.org` (décidé le 19/10/2026) | INR | D-04 |
| 6 | ~~Mainteneurs~~ : G. Gallon, R. Bury, V. Courboulay, P. Saulnier ; identifiants GitHub de R. Bury et P. Saulnier à fournir | INR | `.github/CODEOWNERS` |
| 7 | Mentions légales du site (éditeur, directeur de publication, hébergeur) | INR | `content/site/mentions-legales.md` |
| 9 | Répartition entre dépôt archivé et dépôt actif ; adresse du site (sous-domaine sur l'hébergement OVH) ; adresse de la page WordPress | INR | `docs/publication.md` |
| 8 | Usage du logo INR et du logo FTCC sur le site et dans le classeur | INR, FTCC | `docs/charte-graphique.md` |

## Corrections éditoriales proposées (version 2.0.1 ou 2.1)

À traiter par pull request, une par point, avec journal `modifications` dans la clause :
D-03 (DEV-Q-02, DEV-E-04 à 06), D-05, D-06, D-07, D-08.

Les 83 commentaires de relecture (`docs/commentaires-relecture.json` du répertoire de
travail) et les propositions de `docs/refonte-redactionnelle.md` n'ont pas été importés :
ils contiennent des noms de relecteurs et des arbitrages en cours. Proposition : les
transformer en issues GitHub après accord des auteurs, une issue par sujet.

## Enrichissements possibles

Aucun n'a été réalisé : ils ajoutent de l'information absente du V2.

- Références structurées par clause (RGESN, RGAA, AI Act…), avec version du référentiel.
- Mots-clés (environnement, social, accessibilité, éthique, souveraineté) pour filtrer.
- Sous-intitulés explicites pour les clauses à intitulé partagé (D-13).
- Indication « applicable / non applicable en commande publique » : le texte en contient
  déjà (« Hors commande publique »), une donnée structurée faciliterait le filtrage.
- Vérification périodique des 6 adresses de `data/references.yml` et des notes (lien mort).

## Classeur Excel

- Les segments (slicers) du classeur de préparation ne peuvent pas être produits par
  openpyxl. Le classeur généré utilise des filtres automatiques. Si les slicers sont
  jugés indispensables, deux options : les ajouter à la main après génération (perdus à
  chaque régénération), ou post-traiter le fichier en injectant le XML des slicers.
  À évaluer avec les utilisateurs.

## Site

- Hébergement OVH mutualisé de l'INR (cluster127), déploiement par `scripts/deploy_ovh.sh`.
  À fournir : sous-domaine (ex. clausier.institutnr.org) et mentions légales.
