---
id: PRD-000
title: "repomix-fork — Index des PRD"
repo: gerivdb/repomix-fork
status: active
created: 2026-06-10
author: gerivdb
---

# PRD-000 — repomix-fork · Index des PRD

> Index généré RSS-v2. Source de vérité : fichiers individuels dans `PRD/`.
> Ne jamais éditer manuellement — regénérer via `rss index rebuild`.

## PRD actifs

| ID | Slug | Titre | Statut | Date |
|----|------|-------|--------|------|
| PRD-001 | repomix-fork-cleanup | repomix-fork — Nettoyage, activation verse_detector et pipeline d'inventaire | draft | 2026-06-10 |
| PRD-002 | architecture-diamant-verses | Architecture Diamant pour l'Organisation des Verses | draft | 2026-05-07 |
| PRD-003 | urban-ontology-verse | URBAN ONTOLOGY VERSE (UrbanVerse) | draft | 2026-05-28 |

## PRD archivés / superseded

| ID ancien | Remplacé par | Raison |
|-----------|-------------|--------|
| `PRD-REPOMIX-FORK-CLEANUP-2026-06-10.md` | PRD-001 | Migration RSS-v2 (nommage NNN-slug) |
| `PRD-Architecture-Diamant-Verses.md` | PRD-002 | Migration RSS-v2 (Phase 0) |
| `PRD_URBAN_ONTOLOGY_VERSE_V1.md` | PRD-003 | Migration RSS-v2 (Phase 0) |

## Statut

Phase 0 ✅ — Tous les PRD sont conformes RSS-v2 (nommage NNN-slug + frontmatter YAML).
Phase 1 ✅ — Nettoyage repo complété (.db, .coverage, __pycache__, .test_* untracked).
Phase 2 ✅ — Migration `.py` racine → `src/repomix/` complétée (18 fichiers).
Phase 3 ⏳ — Activation `verse_detector.py` (pipeline d'inventaire local).
Phase 4 ⏳ — STRATUM_RELAY activation (pont ENV1).

---

*Dernière mise à jour : 2026-06-10 — 3 PRD référencés (3 conformes RSS-v2).*
