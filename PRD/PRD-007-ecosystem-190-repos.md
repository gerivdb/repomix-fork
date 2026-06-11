---
id: PRD-007
title: "repomix-fork — Mode ecosystem 190 repos"
repo: gerivdb/repomix-fork
status: draft
created: 2026-06-11
author: gerivdb
intent_hash: 0xREPOMIX_ECOSYSTEM_190_20260611
related:
  - PRD-001-repomix-fork-cleanup.md
  - gerivdb/GOVERNANCE-HUB/known_repositories.yaml
---

# PRD-007 — repomix-fork · Mode `--ecosystem` 190 repos

## Objectif

Porter l'adaptateur `known_repos_adapter.py` et le bundler `bundle_corpus.py` de 72 repos actuels à **190 repos** — couverture complète du métacluster gerivdb.

## Contexte

- `known_repositories.yaml` (GOVERNANCE-HUB) liste actuellement 81 repos (P0+P1+P2+P3)
- L'adaptateur charge 72 nœuds actifs (hors DORMANT/DEPRECATED/ARCHIVE)
- La cible est 190 repos actifs (tous les repos gerivdb/* non archivés)
- Le `bundle_corpus.py` (A3) doit supporter des bundles > 100Mo via chunking

## Livrables

### 1. `known_repos_adapter.py` v2

- Support de 190 nœuds dans le graphe
- Partitionnement par strate L0→L9 avec `LAYER_ORDER` étendu
- Chargement incrémental (lazy) pour éviter les timeouts sur gros graphe
- KPI : chargement 190 repos < 5s sur ENV1

### 2. `repomix-verse.yaml` v2

- Registry complet 190 repos pointant vers VERSES
- Configuration `max_repos_per_pack: 50` pour chunking
- Support mode `--ecosystem` avec tier P0/P1/P2

### 3. `bundle_corpus.py` v2

- Support chunking : bundles > 100Mo découpés en packs de 50 repos
- Gestion mémoire : streaming XML au lieu de chargement complet
- KPI : bundle 190 repos en < 5min sur ENV1

### 4. Tests

- `test_known_repos_adapter_190.py` : test de charge 190 nœuds
- `test_bundle_corpus_chunking.py` : test chunking 3 packs de 50

## KPI

| Métrique | Actuel | Cible |
|----------|--------|-------|
| Repos dans graphe | 72 | 190 |
| Temps chargement | < 1s | < 5s |
| Bundle mono-pack | 30 fichiers | 190 repos chunkés |
| Score émergence | 85% | > 90% |

## Phases

- Phase A : Étendre `known_repos_adapter.py` à 190 nœuds (2h)
- Phase B : Mettre à jour `repomix-verse.yaml` (1h)
- Phase C : Chunking `bundle_corpus.py` (2h)
- Phase D : Tests de charge (1h)

**Durée estimée : ~6h**
