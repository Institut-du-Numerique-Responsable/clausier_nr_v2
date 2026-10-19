# Divergences et points à arbitrer

Aucune de ces divergences n'a été tranchée dans le texte des clauses. Le Markdown reprend
le V2 à l'identique ; chaque point attend une décision des responsables du clausier.
Les identifiants D-xx servent de référence dans les issues et les pull requests.

Légende : **Bloquant** = empêche la publication ; **Éditorial** = touche le sens ou la
formulation d'une clause ; **Mineur** = coquille ou mise en forme.

## Licence et gouvernance

### D-01 — Licence des contenus — **tranché par l'INR, accord FTCC à confirmer**

- Le V2 (couverture, page 44) et le classeur portaient **CC BY-NC-ND 4.0**, au nom de la
  FTCC et de l'INR ; le dépôt public `clausier_nr_v2` déclare **CC BY-SA 4.0**.
- **Décision de l'INR (19 octobre 2026) : CC BY 4.0.** Le clausier peut être repris et
  modifié, y compris commercialement ; la source doit être citée.
- Reste à faire : obtenir l'accord écrit de la FTCC, co-titulaire des droits ; aligner le
  fichier `LICENSE` de `clausier_nr_v2` avant son archivage ; porter la nouvelle mention
  dans une version 2.0.1 du PDF. Les documents d'origine de `sources/originaux/` gardent
  leur mention historique.

## Écarts entre le V2 et le classeur de préparation

### D-03 — Écarts de contenu du classeur (Éditorial)

| Clause | Constat | Proposition |
|---|---|---|
| IA-Q-06 « Sobriété du Modèle » | Absente du classeur | Reprise depuis le V2 (fait) |
| LOG-E-02 | Niveau 2 vide dans le classeur | Texte du V2 conservé (fait) |
| DEV-Q-02 | Intitulé « Écoconception » renommé « Formation écoconception » (« Coquille dans la source ») | **À arbitrer** : le contenu porte sur la formation ; le renommage paraît fondé |
| MAT-Q-12 | « écoconçu » corrigé en « écoconçus » | Correction à valider (voir D-08) |
| CLD-Q-10 | « opposables » corrigé en « opposable » | Correction à valider (voir D-08) |
| DEV-E-04, DEV-E-05, DEV-E-06 | Phase « RFI/RFP » dans le classeur, partie 5.1.2 « Exigences » dans le V2 | Partie du V2 conservée ; **à confirmer** |
| CLD-E-01 à 03 | « Commentaires » rangé en colonne « Exigences » dans le classeur, en « Commentaire » ailleurs | Règle unique « Commentaires » → « Commentaire » ; à confirmer |

Les 73 écarts de forme (césures perdues, espaces parasites) ne sont pas repris.

### D-15 — Lexique (Mineur)

- Le classeur range IaaS, PaaS et SaaS dans « Intelligence Artificielle (IA) » ; le V2 les
  place dans une catégorie « Modèles de Services Cloud ». Catégorie du V2 conservée.
- Le terme « IA Générative (IAg) » du V2 manque dans le classeur. Repris.

## Incohérences internes au V2

### D-04 — Deux adresses de contact (Éditorial) — **tranché**

Page 6 : `contact@institutnr.org`. Page 44 et classeur de préparation :
`clausier_nr@institutnr.org`.

**Décision (19 octobre 2026) : `contact@institutnr.org`.** Le site, le classeur généré et la
documentation du dépôt utilisent cette adresse. Le texte de la page 44 reprise du V2
(`content/pages/licence.md`) reste inchangé ; sa correction relève d'une version 2.0.1.

### D-05 — Renvoi erroné en 5.2.2 (Éditorial)

« Se reporter aux exigences transverses dans la partie 1.1 » : la partie 1.1 est le
questionnaire ; les exigences transverses sont en 1.2. Le lien pointe vers un signet
de l'ODT (`#_bookmark0`) qui n'existe plus dans le Markdown. Proposition : « partie 1.2 »,
lien vers la liste COM-E.

### D-06 — Renvoi erroné en 6.2.4 (Éditorial)

« Renvoie directement à la section 3.1 (Infrastructures & Datacenters) pour les enjeux de
PUE et de WUE. » La section 3.1 contient les définitions cloud. Les critères PUE et WUE
sont en 3.2 (CLD-Q-01, CLD-Q-02) ; les équipements de datacenter en 2. À corriger après
arbitrage.

### D-07 — Appels de note incohérents (Mineur)

- « Enjeux et objectifs » : le texte appelle les notes 1 à 7, la page n'en définit que
  5 (Arcep, Shift Project, AIE, CSRD, INR). « CSRD⁶ » et « INR⁷ » correspondent aux notes
  4 et 5 ; les appels 4 (SBTi) et 5 (Nations Unies) n'ont pas de source.
- COM-Q-06 : « CDP⁷ » et « ADEME⁸ » sans note.
- Page 44 : « Propositions d'actualisation : »²¹ sans note.

### D-08 — Coquilles (Mineur)

Conservées à l'identique, à corriger par le comité éditorial :

| Emplacement | Texte du V2 | Proposition |
|---|---|---|
| Couverture | « Aout 2026 » | « Août 2026 » |
| Couverture | « Numérique Responsable © 2026 by… » | « Clausier Numérique Responsable © 2026 by… » (comme page 44) |
| Enjeux et objectifs | « la FCC et l'INR » | « la FTCC et l'INR » |
| Titre 6.3 | « chabot » | « chatbot » |
| MAT-Q-12 | « Emballages écoconçu » | « Emballages écoconçus » |
| CLD-Q-08 | « Management de Efficacité énergétique » | « Management de l'efficacité énergétique » |
| CLD-Q-10 | « Plan d'action opposables » | « Plans d'action opposables » ou « Plan d'action opposable » |
| DEV-E-02 | « garantir la comptabilité du SERVICE » | « la compatibilité du SERVICE » |
| Section 3.2, note 20 | « Carbon Usage Effectivenes » | « Effectiveness » |
| Lexique | « **ESS (Économie Sociale et Solidair**e) » | gras à corriger (sans effet sur le texte) |
| Dernière page | Paragraphe « dUne image contenant cercle, capture d’écran, Graphique, Police Description générée automatiquement » | Texte alternatif d'image généré automatiquement, sorti dans le corps du texte : à supprimer |

### D-09 — Questions rédigées comme des engagements (Éditorial)

Plusieurs cellules « Questions » des questionnaires sont rédigées comme des obligations
contractuelles (« Le Prestataire s'engage à… »), par exemple DEV-Q-02. Ce défaut est
documenté dans `docs/refonte-redactionnelle.md` du répertoire de travail (section 2),
avec des propositions non appliquées.

### D-10 — En-têtes de colonnes hétérogènes

Une même information porte des noms différents selon les tableaux (« Exigence »,
« Exigences », « Description / Spécifications de l'exigence », « Commentaires »). Le
Markdown conserve l'en-tête de chaque tableau. Une harmonisation est possible ; elle
modifierait la présentation, pas le texte des clauses.

### D-13 — Lignes à intitulé partagé

Six clauses « Écolabels/certification de produits » (MAT-Q-01 à 06), deux « MCO &
Réparabilité », deux « Accessibilité Numérique » (DEV-E-04, 05), deux « Infogérance à
distance » partagent leur intitulé, issu d'une cellule fusionnée. Chacune reste une clause
distincte, comme dans le classeur. La rubrique « Commentaires » porte la précision
(« Ordinateurs », « Écran », « Durée de la MCO »…). Le site et le classeur l'affichent à
côté de l'intitulé lorsque celui-ci est partagé, sans modifier le texte. Un sous-intitulé
explicite serait plus simple à citer : à décider.
