---
id: PRD-001
title: "repomix-fork — Nettoyage, activation verse_detector et pipeline d'inventaire"
repo: gerivdb/repomix-fork
status: draft
created: 2026-06-10
author: gerivdb
intent_hash: 0xREPOMIXFORK_CLEANUP_PIPELINE_V1_20260610
related:
  - gerivdb/DevTools/PRD/PRD-001-audit-prd-engine.md
---

# PRD-001 — repomix-fork · Nettoyage, activation verse_detector et pipeline d'inventaire

> `gerivdb/repomix-fork` est le repo le plus riche en capacités d'inventaire de l'écosystème.
> Il souffre cependant d'une pollution structurelle qui l'empêche d'être utilisé efficacement.
> Ce PRD formalise le nettoyage et l'activation de `verse_detector.py` comme pipeline local.

## Problème

`repomix-fork` possède des actifs valorisables (`verse_detector.py`, `verse_auto_projection.py`, `neuro_symbolic_verse_engine.py`, `STRATUM_RELAY.md`) mais ne peut pas être intégré dans un pipeline d'inventaire local tant que :

- ~15 fichiers `.py` sont à la racine (violation règle NEXUS)
- 4 fichiers `.db` sont committés dans git
- `.coverage` (53 Ko) est tracké
- `verse_detector.py` n'est pas branché sur `known_repositories.yaml`
- La confusion historique avec VERSUS (purge effectuée) a laissé des traces

## Objectif

Nettoyer `repomix-fork` et activer son pipeline d'inventaire local, en coordination avec `DevTools/scripts/audit_prd.py` (PRD-001 DevTools) et la boucle `STRATUM_RELAY → ENV1`.

## Diagnostic structurel (2026-06-10)

### Pollution identifiée

| Type | Fichiers | Violation |
|------|----------|-----------|
| `.py` à la racine | `brain_bypass_verse.py`, `fluence_bypass_verse.py`, `marketplace_phase4_week*.py`, `migration_phase*.py`, `neuro_symbolic_verse_engine.py`, `physic_verse.py`, `verse-template-generator.py`, `verse_auto_projection.py`, `verse_detector.py`, `verse_spiral_implementations.py`, `verses_creative_foundation.py`, `verses_library.py`, `world_verse.py` | Règle NEXUS : `.py` racine → `src/` |
| `.db` committés | `cache.db`, `beta_testing.db`, `llm_catalog.db`, `verses_marketplace.db` | Binaires → `.gitignore` + `git rm --cached` |
| `.coverage` tracké | `.coverage` (53 Ko) | Artefact test → `.gitignore` |

### PRD existants dans `PRD/` (non conformes RSS-v2)

| Fichier | Problème |
|---------|----------|
| `PRD-Architecture-Diamant-Verses.md` | Nommage non RSS-v2, pas de frontmatter `id:` |
| `PRD_URBAN_ONTOLOGY_VERSE_V1.md` | Nommage non RSS-v2 (`_` au lieu de `-`, suffixe `_V1`) |

Ces fichiers doivent être migrés en Phase 0.

### Actifs valorisables

| Fichier | Taille | Rôle dans le pipeline |
|---------|--------|----------------------|
| `verse_detector.py` | 7 Ko | Détection structures verse — **cœur du pipeline** |
| `verse_auto_projection.py` | 3 Ko | Projection/mapping automatique de repos |
| `neuro_symbolic_verse_engine.py` | 13 Ko | Analyse symbolique de contenu |
| `verse-template-generator.py` | 17 Ko | Génération templates depuis structure |
| `verses_library.py` + `.json` | 14+21 Ko | Bibliothèque indexée |
| `STRATUM_RELAY.md` | 3.5 Ko | **Pont ENV1 — pièce pivot** |

## Architecture cible

```
repomix-fork/
├── src/
│   ├── core/
│   │   ├── verse_detector.py        ← migré depuis racine
│   │   ├── verse_auto_projection.py  ← migré
│   │   └── neuro_symbolic_engine.py  ← migré + renommé
│   ├── marketplace/
│   │   └── marketplace_phase*.py     ← migrés
│   ├── migration/
│   │   └── migration_phase*.py       ← migrés
│   └── utils/
│       └── physic_verse.py, world_verse.py, verse-template-generator.py
├── scripts/            ✅ existant
├── verses/             ✅ existant
├── data/               ✅ existant
├── STRATUM_RELAY.md    ✅ conserver à la racine
├── PRD/                ✅ ce document + index
├── EPICS/              ✅ existant
├── repomix-verse.yaml  ✅ conserver
└── pyproject.toml      ✅ conserver
```

## Pipeline d'inventaire activé

```
known_repositories.yaml (GOVERNANCE-HUB, 176+ repos)
  ↓
DevTools/scripts/inventory_repos.py
  ├── repomix-fork/src/core/verse_detector.py   [repos type verse]
  └── DevTools/scripts/audit_prd.py             [repos avec PRD/]
         ↓
  rapport JSON consolidé
         ↓
  STRATUM_RELAY.md → ENV1
```

## Plan de réalisation

### Phase 0 — Migration RSS-v2 des PRD existants (P0 — 15min)

| Tâche | Détail |
|-------|--------|
| Renommer `PRD-Architecture-Diamant-Verses.md` | → `PRD-002-architecture-diamant-verses.md` + ajout frontmatter |
| Renommer `PRD_URBAN_ONTOLOGY_VERSE_V1.md` | → `PRD-003-urban-ontology-verse.md` + ajout frontmatter |

### Phase 1 — Nettoyage `.gitignore` + `.db` (P0 — 30min)

| Tâche | Commande |
|-------|----------|
| Ajouter au `.gitignore` | `*.db`, `.coverage`, `__pycache__/` |
| Supprimer tracking | `git rm --cached *.db .coverage` |
| Commit + push | `chore: untrack .db and .coverage files` |

### Phase 2 — Migration `.py` racine → `src/` (P0 — 1h)

| Destination | Fichiers |
|-------------|----------|
| `src/core/` | `verse_detector.py`, `verse_auto_projection.py`, `neuro_symbolic_verse_engine.py` |
| `src/marketplace/` | `marketplace_phase*.py`, `verses_creative_foundation.py`, `verses_library.py`, `verse_spiral_implementations.py` |
| `src/migration/` | `migration_phase*.py` |
| `src/utils/` | `physic_verse.py`, `world_verse.py`, `verse-template-generator.py` |
| `src/bypass/` | `brain_bypass_verse.py`, `fluence_bypass_verse.py`, `wazaa_bypass_verse.js` |

### Phase 3 — Activation `verse_detector.py` (P1 — 2h)

| Tâche | Détail |
|-------|--------|
| Adapter `verse_detector.py` | Accepter `known_repositories.yaml` en entrée |
| Créer `src/core/pipeline.py` | Orchestration : yaml → detect → audit → rapport |
| Lier avec `DevTools/scripts/audit_prd.py` | Subprocess ou import |

### Phase 4 — STRATUM_RELAY activation (P2 — 2h)

| Tâche | Détail |
|-------|--------|
| Lire `STRATUM_RELAY.md` complet | Comprendre le protocole de relay |
| Ajouter payload JSON | Format : `{repo, audit_result, timestamp}` |
| Tester boucle complète | Local → rapport → relay → ENV1 confirmation |

## KPI

| Métrique | Avant (2026-06-10) | Cible |
|----------|--------------------|-------|
| Fichiers `.py` à la racine | ~15 | 0 |
| Fichiers `.db` trackés | 4 | 0 |
| PRD conformes RSS-v2 dans `PRD/` | 0/3 | 3/3 |
| `verse_detector.py` branché | Non | Oui |
| Pipeline d'inventaire local | Non | Oui |
| STRATUM_RELAY actif | Non | Oui |

## Risques

| Risque | P | Impact | Mitigation |
|--------|:-:|--------|------------|
| Migration `.py` casse imports existants | Moyen | Haut | `__init__.py` + tests avant migration |
| `git rm --cached .db` perte données test | Faible | Moyen | Backup local avant |
| `verse_detector.py` incompatible YAML | Inconnu | Haut | Analyser format attendu avant Phase 3 |

## Références

| Document | Localisation | Type |
|----------|-------------|------|
| PRD DevTools lié | `DevTools/PRD/PRD-001-audit-prd-engine.md` | PRD lié |
| RSS-v2 standard | `REPO-STANDARDS/PRD/PRD-001-rss-v2-artifact-policy.md` | Standard |
| ADR-001 local-first | `REPO-STANDARDS/ADR/ADR-001-local-first-artifact-authority.md` | ADR |
| STRATUM_RELAY | `repomix-fork/STRATUM_RELAY.md` | Pont ENV1 |
| known_repositories.yaml | `GOVERNANCE-HUB/known_repositories.yaml` | SOT repos |

---

*[À_VALIDER_NEXUS] — Conforme RSS-v2 (P1 local-first, P2 NNN-slug, P3 frontmatter, P4 index).*
