# EPIC-11 — VERSES Marketplace Sync + Publication PyPI

---

**EPIC** : EPIC-11
**Titre** : Synchronisation marketplace VERSES ↔ VersesSyncManager + publication PyPI gerivdb-repomix
**PRD parent** : `PRD/PRD-011-marketplace-pypi.md`
**Version** : 1.0.0
**Date** : 2026-06-11
**Statut** : 🔵 PLANIFIÉ
**Priorité** : P2 — Dépend EPIC-07, EPIC-08

---

## Objectif

Deux finalités distinctes couplées : (1) synchroniser la marketplace FastAPI locale
(port 8742) avec `VERSES/verses-marketplace/` en bidirectionnel via VersesSyncManager ;
(2) publier `gerivdb-repomix` v1.0.0 sur PyPI avec workflow GitHub Actions.

## User Stories

| ID | Story | Critères d'acceptation |
|----|-------|----------------------|
| US-11-1 | En tant que dev, `POST /publish` sur la marketplace enregistre le verse dans VERSES/ontology_registry.json | `ontology_registry.json` mis à jour après appel API |
| US-11-2 | En tant que dev, `GET /search?q=urban` retourne les verses correspondant depuis l'état VERSES courant | Résultats cohérents avec `verses_library.json` de VERSES |
| US-11-3 | En tant qu'agent, `VersesSyncManager.sync()` pousse les deltas vers VERSES/verses-marketplace/ via git commit | Commit automatique avec message standardisé `sync(marketplace): delta vX` |
| US-11-4 | En tant que dev, `pip install gerivdb-repomix` installe la version fork depuis PyPI | Package disponible sur PyPI, `import repomix` fonctionne post-install |
| US-11-5 | En tant que mainteneur, le tag `v1.0.0` déclenche automatiquement la publication PyPI via GitHub Actions | Workflow `.github/workflows/publish.yml` fonctionnel sur push tag `v*` |

## Tâches techniques

**Marketplace sync :**
- [ ] `src/repomix/marketplace/marketplace_api.py` v2 — endpoint `/publish` écrit dans `VERSES/ontology_registry.json` (via git API ou fichier local monté)
- [ ] `src/repomix/sync/verses_sync_manager.py` v2 — méthode `push_to_marketplace(verse_entry)` avec commit auto
- [ ] `tests/unit/test_marketplace_sync.py` — 5 tests (publish, search, sync delta, TTL, conflit)

**PyPI :**
- [ ] `pyproject.toml` — vérifier `name = "gerivdb-repomix"`, `version = "1.0.0"`, classifiers complets
- [ ] `.github/workflows/publish.yml` — trigger `on: push: tags: ["v*"]`, étapes build + twine upload
- [ ] `CHANGELOG.md` v1.0.0 — entrée de release avec résumé Vagues 4→10
- [ ] Test local : `python -m build && twine check dist/*` sans erreur

## Définition de "Done"

- [ ] `/publish` + `/search` cohérents avec VERSES (test E2E)
- [ ] `VersesSyncManager.push_to_marketplace()` commit dans VERSES sans intervention manuelle
- [ ] `twine check dist/*` retourne 0 erreur
- [ ] Workflow `publish.yml` validé en dry-run (`act` local ou push sur branche feature/)
- [ ] 5 nouveaux tests passent — total actifs ≥ 64
