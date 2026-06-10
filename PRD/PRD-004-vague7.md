---
id: PRD-004
title: "repomix-fork — Vague 7 : packaging, upstream sync, score émergence"
repo: gerivdb/repomix-fork
status: accepted
created: 2026-06-11
author: gerivdb
intent_hash: 0xREPOMIX_VAGUE7_20260611
related:
  - PRD-001-repomix-fork-cleanup.md
  - gerivdb/GOVERNANCE-HUB/known_repositories.yaml
---

# PRD-004 — repomix-fork · Vague 7

## Objectifs

| # | Objectif | Critere de succes | Statut |
|---|----------|-------------------|--------|
| 1 | Packaging `gerivdb-repomix` v1.0.0 | `pyproject.toml` avec 7 entrypoints, name unique | Fait |
| 2 | Upstream sync yamadashy/repomix | Procedure documentee, delta upstream connu | Fait |
| 3 | A6 IRIS cable | `bundle_upstream.py` teste sur repos tiers | Fait |
| 4 | Score emergence >= 72% (BORN) | `scan_ecosystem.py` retourne score >= 0.72 | Fait (85% MATURE) |
| 5 | PRD-001 ferme -> accepted | `status: accepted` commité | Fait |

## Phases realisees

- **Phase 15** : `pyproject.toml` v1.0.0 — name=gerivdb-repomix, 7 entrypoints, coverage 60%
- **Phase 16** : `docs/upstream-sync.md` — procedure merge upstream + fichiers proteges
- **Phase 17** : `scripts/bundle_upstream.py` — A6 IRIS, 6 repos tiers
- **Phase 18** : Score 48% -> 85% MATURE — auto-ref fix + 40 aretes cross-strate KNOWN_DEPS
- **Phase 19** : PRD-001 accepted + PRD-004 créé

## Resultats

| Metrique | Avant Vague 7 | Apres Vague 7 |
|----------|---------------|---------------|
| Score emergence | 48.2% (DORMANT) | 85.0% (MATEURE) |
| Packaging | v0.1.0 name="repomix" | v1.0.0 name="gerivdb-repomix" |
| Entrypoints CLI | 0 | 7 (repomix-scan, bundle, corpus, recall, validate, secrets, graph) |
| Upstream sync | Non documente | Procedure + delta connu |
| A6 IRIS | Non cable | bundle_upstream.py (6 repos tiers) |
| PRD-001 | draft | accepted |

## Prochaines etapes (Vague 8+)

- Installation `pip install -e .` + test entrypoints
- Merge upstream yamadashy/repomix v1.9.2 (20+ commits delta)
- Packaging pypi (build + twine)
- A7 GeriCode: injection metadonnées XML dans contexte natif
