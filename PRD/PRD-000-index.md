---
id: PRD-000
title: "repomix-fork — Index des PRD"
repo: gerivdb/repomix-fork
status: active
created: 2026-06-10
author: gerivdb
---

# PRD-000 — repomix-fork · Index des PRD

> Index genere RSS-v2. Source de verite : fichiers individuels dans `PRD/`.
> Jamais editer manuellement — regenerer via `rss index rebuild`.

## PRD actifs

| ID | Slug | Titre | Statut | Date |
|----|------|-------|--------|------|
| PRD-001 | repomix-fork-cleanup | repomix-fork — Nettoyage, activation verse_detector et pipeline d'inventaire | accepted | 2026-06-10 |
| PRD-002 | architecture-diamant-verses | Architecture Diamant pour l'Organisation des Verses | accepted | 2026-05-07 |
| PRD-003 | urban-ontology-verse | URBAN ONTOLOGY VERSE (UrbanVerse) | draft | 2026-05-28 |
| PRD-004 | vague7 | Vague 7 — packaging, upstream sync, score emergence | accepted | 2026-06-11 |

## PRD archives / superseded

| ID ancien | Remplace par | Raison |
|-----------|-------------|--------|
| `PRD-REPOMIX-FORK-CLEANUP-2026-06-10.md` | PRD-001 | Migration RSS-v2 (nommage NNN-slug) |
| `PRD-Architecture-Diamant-Verses.md` | PRD-002 | Migration RSS-v2 (Phase 0) |
| `PRD_URBAN_ONTOLOGY_VERSE_V1.md` | PRD-003 | Migration RSS-v2 (Phase 0) |

## Statut

Phase 0 — Tous les PRD sont conformes RSS-v2 (nommage NNN-slug + frontmatter YAML).
Phase 1 — Nettoyage repo complete (.db, .coverage, __pycache__, .test_* untracked).
Phase 2 — Migration `.py` racine vers `src/repomix/` completee (18 fichiers).
Phase 3 — Activation `verse_detector.py` (pipeline d'inventaire local).
Phase 4 — STRATUM_RELAY activation (pont ENV1).
Phase 5 — Vague 5 : A1 ARGUS + A2 recall + CI/CD + tests unitaires.
Phase 6 — Vague 6 : A3→A10 cables (8/10), STRATUM_RELAY v6.
Phase 7 — Vague 7 : packaging v1.0.0, upstream sync, score 85% MATEURE.
Phase 8 — Vague 8 : PRD-002 P3+P4, VersesSyncManager + Marketplace API.

---

*Derniere mise a jour : 2026-06-11 — 4 PRD references (3 accepted, 1 draft).*
