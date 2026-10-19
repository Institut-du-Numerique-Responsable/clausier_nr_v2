# Maintenance

## Installer

```sh
make install          # .venv + requirements.txt
```

Outils facultatifs : `pdftotext` (paquet poppler) pour `make integrity`, LibreOffice pour le
test de recalcul du classeur. Les tests concernés sont ignorés s'ils manquent.

## Cycle courant

```sh
make validate         # après toute modification de content/ ou data/
make test             # avant toute pull request
make build serve      # vérifier le rendu en local
```

## Tâches fréquentes

| Tâche | Où |
|---|---|
| Corriger une clause | `content/clauses/<segment>/<ID>.md`, avec une entrée `modifications` |
| Ajouter une clause | Copier une clause de la section ; nouvel `id`, `ordre`, `statut: brouillon` |
| Retirer une clause | `statut: archivee` ; ne pas supprimer le fichier |
| Ajouter un segment ou une section | `data/segments.yml` (préfixe d'identifiant, phase), puis `schemas/clause.schema.json` si nouveau préfixe |
| Ajouter une rubrique | `data/colonnes.yml` (titre et colonne Excel) |
| Modifier le lexique, les références | `data/lexique.yml`, `data/references.yml` |
| Modifier une page du site | `content/site/*.md` ; mise en page dans `scripts/build_site.py` |
| Changer le style | `site/assets/style.css` (budget 15 Ko) |
| Publier une version | `CHANGELOG.md`, `data/metadata.yml` (version), tag Git `vX.Y.Z` |

## Migration initiale

`scripts/migrate.py` a produit `content/` à partir de l'ODT V2. **Ne le relancez pas** sur un
dépôt où des clauses ont été modifiées : il refuse d'écrire si des clauses existent, sauf
`--force`, qui écraserait tout. `scripts/audit_compare.py` et `scripts/odt_extract.py`
restent utiles au contrôle d'intégrité.

## Contrôle d'intégrité

`make integrity` compare chaque clause au V2. Une clause modifiée sans entrée
`modifications` fait échouer le contrôle : c'est voulu. Toute modification du texte officiel
doit être consignée.

## Publication

La CI (`.github/workflows/ci.yml`) valide, teste et génère les livrables sur chaque pull
request. La publication (`.github/workflows/publication.yml`) ne se lance qu'à la main ou sur
un tag de version : elle déploie le site et, sur tag, crée une Release GitHub contenant le
classeur, le PDF du V2 et une archive du site, sous des noms fixes cités par la page WordPress
de l'INR. Détails, liens et archivage : [publication.md](publication.md).
