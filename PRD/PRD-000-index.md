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
| PRD-003 | urban-ontology-verse | URBAN ONTOLOGY VERSE (UrbanVerse) | accepted | 2026-05-28 |
| PRD-004 | vague7 | Vague 7 — packaging, upstream sync, score emergence | accepted | 2026-06-11 |
| PRD-005 | engines-citizens | Activation moteurs internes | draft (annule) | 2026-06-11 |
| PRD-006 | nexus-bridge | Bridge NEXUS | draft (annule) | 2026-06-11 |
| PRD-007 | ecosystem-190 | Mode ecosystem 190 repos | accepted | 2026-06-11 |
| PRD-008 | ecos-cli-bundle | ECOS-CLI A5 implementation | accepted | 2026-06-11 |
| PRD-009 | a9-a7 | A9 DATA-MINER + A7 GeriCode | accepted | 2026-06-11 |
| PRD-010 | urbanverse-vague2-3 | UrbanVerse Vague 2+3 | accepted | 2026-06-11 |
| PRD-011 | marketplace-pypi | VERSES marketplace + PyPI publish | accepted | 2026-06-11 |

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
Phase 9 — Vague 9 : PRD-003 P1+P2, UrbanVerse structure + 10 pilotes + upstream sync.
Phase 10 — Vague 10 : PRD-003 P3+P4, Karpathy Recall + Fibre/Economie.
Phase 11 — Vague 11 : PRD-007+008 accepted — 190 repos, cli_contract A5, bundle_corpus v2, 54 tests.
Phase 12 — Vague 12 : PRD-009+010 accepted — mine_bundle v2, relay v2+v3, cadastre 190, 77 tests.
Phase 13 — Vague 13 : PRD-011 accepted — marketplace sync v2, PyPI publish.yml, CHANGELOG v1.0.0, 84 tests.
Phase 14 — Vague 14 : EPIC-04 deploye — Karpathy Recall v4, transit_map v2, recall_coherence_check v4, 92 tests.
Phase 15 — Vague 15 : PyPI v1.0.0 publie, corrections residuelles STRATUM_RELAY, ADR GOVERNANCE-HUB propose, cadastre_v2 VERSES.
Phase 16 — Vague 16 : GOVERNANCE-HUB consolidation — known_repos v2.1, nettoyage NEXUS racine, ADR-042 accepted, LLM-BOOT GATE-4 synced.

---

*Derniere mise a jour : 2026-06-11 — 11 PRD references (9 accepted, 2 annules).*
