#!/bin/sh
# Déploie dist/site/ sur l'hébergement mutualisé OVH de l'INR (alias SSH ovh-cluster127).
#
# Par défaut : essai à blanc (rsync --dry-run), rien n'est modifié sur le serveur.
#   sh scripts/deploy_ovh.sh            # montre ce qui serait envoyé ou supprimé
#   sh scripts/deploy_ovh.sh --appliquer  # publie réellement
#
# Variables : HOTE (défaut ovh-cluster127), CIBLE (défaut clausier, dossier relatif au compte).
# Le dossier cible doit être rattaché au sous-domaine dans l'espace client OVH (Multisite).
set -eu
HOTE="${HOTE:-ovh-cluster127}"
CIBLE="${CIBLE:-clausier}"
RACINE="$(cd "$(dirname "$0")/.." && pwd)"
SITE="$RACINE/dist/site/"

[ -f "$SITE/index.html" ] || { echo "dist/site absent : lancez d'abord « make build »." >&2; exit 1; }
[ -f "$SITE/.htaccess" ] || { echo "dist/site/.htaccess absent." >&2; exit 1; }

OPTS="-rlvz --delete --checksum --exclude=.nojekyll"
if [ "${1:-}" = "--appliquer" ]; then
  echo "Publication réelle vers $HOTE:~/$CIBLE/"
  rsync $OPTS "$SITE" "$HOTE:$CIBLE/"
else
  echo "Essai à blanc vers $HOTE:~/$CIBLE/ (ajoutez --appliquer pour publier)"
  rsync $OPTS --dry-run "$SITE" "$HOTE:$CIBLE/"
fi
