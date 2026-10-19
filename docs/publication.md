# Publication et archivage

## Où se trouve quoi

| Ressource | Emplacement |
|---|---|
| Page officielle (point d'entrée public) | https://institutnr.org/clausier-numerique-ecoresponsable (WordPress de l'INR) |
| Sources, issues, pull requests, Releases | https://github.com/Institut-du-Numerique-Responsable/clausier_nr_v2 |
| Site de consultation | https://clausier.institutnr.org/ : hébergement OVH mutualisé de l'INR (`ovh-cluster127`), dossier `~/clausier` (Multisite créé le 19/10/2026, avec `www.clausier`) |
| Classeur Excel, PDF du V2, archive du site | Releases GitHub, noms de fichiers fixes |

## Liens à mettre sur la page WordPress

| Lien | Adresse |
|---|---|
| Consulter le clausier en ligne | `https://clausier.institutnr.org/` |
| Télécharger le classeur Excel | `https://github.com/Institut-du-Numerique-Responsable/clausier_nr_v2/releases/latest/download/Clausier-Numerique-Responsable-V2.xlsx` |
| Télécharger le PDF | `https://github.com/Institut-du-Numerique-Responsable/clausier_nr_v2/releases/latest/download/clausier-numerique-responsable-v2.pdf` |
| Contribuer sur GitHub | `https://github.com/Institut-du-Numerique-Responsable/clausier_nr_v2` |

Les adresses `releases/latest/download/…` existent dès la première Release (tag `v…`).
Elles pointent toujours vers la dernière version : la page WordPress n'a pas à changer.
**Ne pas renommer ces fichiers** ; pour un V3, créer de nouveaux noms et mettre à jour la page.
Le site sert aussi les mêmes fichiers dans `telechargements/`.

Le site renvoie vers la page WordPress et vers le dépôt en pied de page
(`data/metadata.yml`, bloc `liens`).

## Déployer le site sur OVH

```sh
make deploy-essai   # construit puis montre ce que rsync enverrait ou supprimerait
make deploy         # construit, teste, publie dans ovh-cluster127:~/clausier/
```

Première mise en ligne (une seule fois, dans l'espace client OVH) :

1. Multisite : créer le sous-domaine, dossier racine `clausier`.
2. Certificats SSL : commander le certificat du sous-domaine. Tant que
   `openssl s_client -servername <sous-domaine> -connect <sous-domaine>:443` renvoie
   `CN=cluster127.hosting.ovh.net`, le site reste inaccessible : institutnr.org envoie
   HSTS `includeSubDomains`. Compter 15 à 60 minutes après le passage en « Actif ».
3. Activer ensuite les redirections HTTPS et `www` de `site/htaccess`, reconstruire, redéployer (fait le 19/10/2026).
4. Renseigner `liens.site` dans `data/metadata.yml`.

Le `.htaccess` applique une CSP stricte (`script-src 'self'`, `style-src 'self'`) : le site
n'a aucun script ni style inline (contrôlé par les tests). CSS et JS sont mis en cache
7 jours ; leurs adresses portent une empreinte (`style.css?v=…`), donc chaque publication est
prise en compte immédiatement.

## Publier une version

1. Mettre à jour `CHANGELOG.md` et `data/metadata.yml` (version).
2. Fusionner sur `main`, puis créer un tag : `git tag v2.0.1 && git push origin v2.0.1`.
3. Le workflow `publication.yml` crée la Release avec le classeur, le PDF et l'archive du site.
4. `make deploy` pour mettre le site à jour sur OVH.

## Archivage

Un dépôt GitHub archivé passe en lecture seule : plus de push, d'issues ni de pull requests ;
ses Releases restent téléchargeables. Avant d'archiver :

- publier une dernière Release, pour que les liens `releases/latest/download/…` de la page
  WordPress restent valides ;
- vérifier que `LICENSE` porte CC BY 4.0 (fait dans ce dépôt) ;
- ne pas y verser les commentaires de relecture nominatifs (`old/sources/*.docx`,
  `docs/commentaires-relecture.json` du répertoire de travail) sans l'accord des relecteurs.

Les documents d'origine utiles (ODT, PDF, classeur de préparation) sont déjà dans
`sources/originaux/` avec leurs empreintes ; les fichiers de travail du répertoire local
(`old/`, `outils/`, notes de refonte) peuvent être ajoutés dans un dossier `archives/` si
l'INR souhaite les conserver dans le dépôt.
