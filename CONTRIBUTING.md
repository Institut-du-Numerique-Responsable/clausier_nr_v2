# Contribuer au Clausier Numérique Responsable

Merci de votre aide. Ce guide ne suppose aucune connaissance de Git.

## 1. Signaler une erreur ou proposer une idée (5 minutes)

Il suffit d'un compte GitHub gratuit.

1. Ouvrez l'onglet **Issues** du dépôt, puis **New issue**.
2. Choisissez un modèle : *Erreur dans une clause*, *Proposition de modification*,
   *Nouvelle clause* ou *Référence à ajouter*.
3. Remplissez le formulaire. Indiquez l'**identifiant de la clause** (par exemple
   `CLD-Q-01`, visible sur le site et dans le classeur) et, si possible, une source.

Sans compte GitHub : écrivez à `contact@institutnr.org`.

## 2. Modifier une clause directement dans le navigateur

1. Ouvrez le fichier de la clause : `content/clauses/<segment>/<ID>.md`
   (ex. `content/clauses/cloud/CLD-Q-01.md`).
2. Cliquez sur l'icône crayon (**Edit this file**). GitHub crée une copie à votre nom.
3. Modifiez le texte sous les titres `##`. Ne touchez pas à l'en-tête entre les `---`,
   sauf pour ajouter une entrée `modifications` (voir plus bas).
4. En bas de page, décrivez votre changement, puis **Propose changes** et
   **Create pull request**.

Les contrôles automatiques s'exécutent. Une coche verte signifie que le fichier reste
valide ; une croix rouge renvoie au détail de l'erreur.

### Règles de rédaction

- Une clause = un fichier. Le titre `#` reprend le champ `titre` de l'en-tête.
- Rubriques autorisées (titres `##`) : `Commentaires`, `Exigence`, `Exigences`,
  `Description / Spécifications de l'exigence`, `Questions`, `Livrables`,
  `Niveau 1 (Must have)`, `Niveau 2 (Nice to have)`.
- Listes avec `- `, gras avec `**…**`, notes avec `[^1]` et une ligne `[^1]: …` en fin de
  fichier.
- Toute modification du texte d'une clause validée s'accompagne d'une entrée :

  ```yaml
  modifications:
    - date: "2026-11-02"
      description: "Correction : « comptabilité » remplacé par « compatibilité »."
      rubrique: "titre"
      reference: "#12"
  ```

### Proposer une nouvelle clause

Copiez une clause de la même section, changez l'identifiant (numéro libre suivant, jamais
celui d'une clause archivée), mettez `statut: brouillon`, donnez un `ordre` libre dans la
section, supprimez les blocs `source` et `excel_preparation`. Le comité de pilotage décide de sa validation.

## 3. Travailler en local

```sh
git clone <adresse du dépôt>
cd clausier_nr_v2
make install
make validate test
make build serve    # site sur http://127.0.0.1:8000/
```

## Ce qui se passe ensuite

Un mainteneur relit la proposition. Les questions de fond (seuils, niveaux, périmètre) sont
soumises au comité de pilotage. Une proposition peut être acceptée, amendée ou refusée ; la
décision est motivée dans la pull request. Voir [GOVERNANCE.md](GOVERNANCE.md).

## Licence des contributions

En contribuant, vous acceptez que votre contribution soit diffusée sous licence
CC BY 4.0, comme le reste du clausier (voir [LICENSE.md](LICENSE.md)).

## Code de conduite

Voir [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
