---
id: PRD-011
title: "VERSES marketplace + PyPI publish"
repo: gerivdb/repomix-fork
status: draft
created: 2026-06-11
author: gerivdb
intent_hash: 0xREPOMIX_MARKETPLACE_PYPI_20260611
---

# PRD-011 — VERSES marketplace + PyPI publish

## Partie 1 : Marketplace VERSES

### Objet

Integrer le marketplace local FastAPI (port 8742) avec `gerivdb/VERSES/verses-marketplace/`.

### Livrables

- Synchronisation bidirectionnelle `VersesSyncManager` <-> `VERSES/ontology_registry.json`
- Endpoints marketplace operationnels sur VERSES
- Tests d'integration marketplace

## Partie 2 : PyPI publish

### Objet

Publier `gerivdb-repomix` sur PyPI.

### Livrables

1. `pyproject.toml` finalise (deja fait en v1.0.0)
2. Build : `python -m build` -> wheel + sdist
3. Test : `twine check dist/*`
4. Publish : `twine upload dist/*` (test.pypi.org d'abord)
5. GitHub Actions workflow : tag v1.0.0 -> release + publish
6. Verification : `pip install gerivdb-repomix` fonctionne

### KPI

- Package publie sur PyPI
- `pip install gerivdb-repomix` fonctionne
- 7 entrypoints CLI installes
- GitHub release v1.0.0 creee

## Dependances

- Compte PyPI avec token API
- `gerivdb/VERSES` accessible
- Permissions GitHub Actions pour publish
