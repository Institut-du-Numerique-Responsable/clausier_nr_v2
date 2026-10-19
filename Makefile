# Commandes du projet. Prérequis : Python 3.10+ ; poppler (pdftotext) et LibreOffice
# sont facultatifs (contrôle d'intégrité face au PDF, test de recalcul du classeur).
PY ?= .venv/bin/python

.PHONY: install validate integrity excel site build test serve visuels deploy-essai deploy indexnow clean

install:            ## crée l'environnement Python et installe les dépendances
	python3 -m venv .venv
	$(PY) -m pip install -r requirements.txt

validate:           ## vérifie les fichiers Markdown (schéma, identifiants, rubriques, notes)
	$(PY) scripts/validate.py

integrity:          ## compare le Markdown au document V2 et écrit docs/audit/rapport-integrite.md
	$(PY) scripts/check_integrity.py

excel:              ## génère dist/excel/Clausier-Numerique-Responsable-V2.xlsx
	$(PY) scripts/build_excel.py

site: excel         ## génère le site dans dist/site/
	$(PY) scripts/build_site.py

build: validate site ## valide puis génère tous les livrables

test:               ## lance tous les tests
	$(PY) -m unittest discover -s tests -v

serve: site         ## sert le site sur http://127.0.0.1:8000/
	cd dist/site && python3 -m http.server 8000 --bind 127.0.0.1

visuels: build      ## visuels de présentation dans dist/visuels/ (requirements-visuels.txt)
	$(PY) scripts/build_visuels.py

deploy-essai: build  ## montre ce que le déploiement OVH enverrait (aucune modification)
	sh scripts/deploy_ovh.sh

deploy: build test  ## publie dist/site sur ovh-cluster127 (après validation)
	sh scripts/deploy_ovh.sh --appliquer

indexnow:           ## signale les URL du site en ligne à Bing et aux moteurs IndexNow
	$(PY) scripts/indexnow.py --envoyer

clean:              ## supprime les livrables générés
	rm -rf dist build
