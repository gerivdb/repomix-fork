# EPIC-09 — A9 DATA-MINER × A7 GeriCode : Activation apports passifs

---

**EPIC** : EPIC-09
**Titre** : Validation et tests des apports A9 (DATA-MINER) et A7 (GeriCode/KiloCode)
**PRD parent** : `PRD/PRD-009-a9-data-miner-a7-gericode.md`
**Version** : 1.0.0
**Date** : 2026-06-11
**Statut** : 🟡 À DÉMARRER
**Priorité** : P1 — Dépend EPIC-07

---

## Objectif

Transformer les apports A9 (mining bundle XML sans git clone) et A7 (injection
métadonnées UrbanVerse dans GeriCode/KiloCode) de l'état "passif/non testé" à
"validé par tests automatisés". `mine_bundle.py` et `test_bundle_a7.py` existent
déjà — les formaliser et les câbler dans la suite de tests.

## User Stories

| ID | Story | Critères d'acceptation |
|----|-------|----------------------|
| US-09-1 | En tant qu'agent DATA-MINER, je peux miner un bundle XML sans cloner les 190 repos | `mine_bundle.py --input bundle.xml --output mining_report.json` produit un rapport structuré |
| US-09-2 | En tant que dev, le mining extrait : imports, fonctions, classes, strings, todos par repo | Rapport JSON contient sections `imports`, `functions`, `classes`, `todos` par repo |
| US-09-3 | En tant que dev GeriCode, les métadonnées `strate`, `phi_cps`, `intent_hash` sont lisibles dans le XML | `test_bundle_a7.py` parse le XML et assert la présence des 4 champs UrbanVerse |
| US-09-4 | En tant que dev, les deux scripts sont intégrés dans `pytest` (pas seulement exécutables manuellement) | `tests/unit/test_mine_bundle.py` + `tests/unit/test_a7_metadata.py` passent en CI |

## Tâches techniques

- [ ] `scripts/mine_bundle.py` v2 — formaliser CLI (`--input`, `--output`, `--repo-filter`)
- [ ] `tests/unit/test_mine_bundle.py` — 5 tests (extraction, format JSON, filtre repo, performance < 10s/bundle)
- [ ] `scripts/test_bundle_a7.py` → migrer vers `tests/unit/test_a7_metadata.py`
- [ ] Assert 4 champs UrbanVerse : `strate`, `phi_cps`, `intent_hash`, `vague_deployee`
- [ ] Fixture `tests/fixtures/sample_bundle_p0.xml` — bundle XML minimal pour tests reproductibles
- [ ] Documenter `docs/data-miner-interface.md` — format rapport + champs garantis

## Structure cible

```
scripts/
└── mine_bundle.py                ← v2, CLI formalisée
tests/
├── unit/
│   ├── test_mine_bundle.py       ← 5 tests A9
│   └── test_a7_metadata.py       ← 4 tests A7
└── fixtures/
    └── sample_bundle_p0.xml      ← fixture reproductible
docs/
└── data-miner-interface.md
```

## Définition de "Done"

- [ ] 9 nouveaux tests passent (5 A9 + 4 A7)
- [ ] `mine_bundle.py --help` fonctionne avec `--input`, `--output`, `--repo-filter`
- [ ] Fixture XML reproductible disponible pour les tests downstream
- [ ] Total tests actifs ≥ 59
