# Gouvernance éditoriale

## Rôles

| Rôle | Qui | Droits |
|---|---|---|
| Comité de pilotage | Désigné par la FTCC et l'INR | Tranche les questions de fond : seuils, classement Must have ou Nice to have, périmètre commande publique, nouvelles clauses |
| Mainteneurs | Guillaume Gallon, Richard Bury, Vincent Courboulay, Paul Saulnier (fichier `.github/CODEOWNERS`) | Relisent et fusionnent les pull requests, publient les versions |
| Contributeurs | Toute personne | Ouvrent des issues et des pull requests |

Un mainteneur approuve chaque pull request avant sa fusion dans `main`. GitHub l'impose
depuis le 19 octobre 2026 : protection de `main`, une approbation d'un CODEOWNER, contrôles de
la CI au vert, ni push forcé ni suppression. Les administrateurs peuvent passer outre en cas de
besoin ; ils le signalent dans la pull request.

## Statuts d'une clause

| Statut | Sens | Publiée dans le site et le classeur |
|---|---|---|
| `brouillon` | Proposition en cours de rédaction | Non |
| `en_revision` | Proposition complète, soumise au comité | Non |
| `validee` | Texte officiel | Oui |
| `archivee` | Retirée ; l'identifiant n'est jamais réattribué | Non |

## Processus

1. **Signalement** : une issue décrit le problème ou la proposition, avec l'identifiant de la
   clause et une source.
2. **Proposition** : une pull request modifie le fichier Markdown. Si le texte d'une clause
   validée change, la clause reçoit une entrée dans `modifications` (date, description,
   référence de l'issue).
3. **Contrôles automatiques** : validation, tests, génération des livrables.
4. **Relecture** : au moins un mainteneur. Pour une question de fond, renvoi au comité de
   pilotage ; la décision est consignée dans l'issue.
5. **Fusion** puis **publication** : les livrables sont régénérés ; une version est taguée
   (`v2.0.1`, `v2.1.0`…) et décrite dans `CHANGELOG.md`.

## Versions

- Correctif (2.0.**x**) : coquilles, liens, mise en forme, sans changement de sens.
- Mineure (2.**x**) : clauses ajoutées, modifiées ou archivées.
- Majeure (**x**.0) : refonte de la structure ou du périmètre.
