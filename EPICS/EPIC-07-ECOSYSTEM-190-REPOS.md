# EPIC-07 — Ecosystem 190 Repos

---

**EPIC** : EPIC-07
**Titre** : Mode --ecosystem étendu à 190 repos du métacluster
**PRD parent** : `PRD/PRD-007-ecosystem-190-repos.md`
**Version** : 1.0.0
**Date** : 2026-06-11
**Statut** : ✅ DÉPLOYÉ (Vague 11)
**Priorité** : P0 — Bloquant EPIC-08, EPIC-09, EPIC-11

---

## Objectif

Porter `known_repos_adapter.py` v2 (113 nœuds actuels) à 190 repos, mettre à jour
`repomix-verse.yaml` en conséquence, et garantir que `--ecosystem` génère un bundle
complet en < 5 min sur ENV1 avec chunking automatique au-delà de 100 Mo.

## User Stories

| ID | Story | Critères d'acceptation |
|----|-------|----------------------|
| US-07-1 | En tant que dev, je lance `repomix --ecosystem` et obtiens un bundle couvrant 190 repos | Bundle XML généré, 190 entrées dans le header |
| US-07-2 | En tant que dev, je peux filtrer par tier (P0/P1/P2) pour des bundles partiels | `--tier P0` produit uniquement les repos critiques (L0→L2) |
| US-07-3 | En tant qu'agent LLM, les métadonnées strate/phi_cps sont présentes dans chaque section XML | Chaque `<file>` contient `<strate>`, `<phi_cps>`, `<vague_deployee>` |
| US-07-4 | En tant que dev, le bundle > 100 Mo est splitté automatiquement en chunks numérotés | `bundle_001.xml`, `bundle_002.xml`, manifest de réassemblage |
| US-07-5 | En tant que dev, `known_repos_adapter.py` expose 190 nœuds et un score émergence recalculé | `adapter.get_stats()` retourne `{"nodes": 190, "edges": ≥1400}` |

## Tâches techniques

- [ ] `data/known_repositories_190.yaml` → compléter de 122 à 190 repos (strate + tier obligatoires)
- [ ] `src/repomix/adapters/known_repos_adapter.py` v3 — chargement 190 nœuds, recalcul score
- [ ] `repomix-verse.yaml` v3 — registry complet 190 VERSES avec tier P0/P1/P2
- [ ] `src/repomix/__main__.py` — argument `--tier {P0,P1,P2,ALL}` (défaut: ALL)
- [ ] `scripts/bundle_corpus.py` v2 — chunking automatique (seuil configurable, défaut 80 Mo)
- [ ] `tests/unit/test_ecosystem_190.py` — 6 tests (count nœuds, tier filter, chunking, métadonnées XML)
- [ ] `repomix.config.json` — section `ecosystem.repos` mise à jour

## Structure cible

```
data/
└── known_repositories_190.yaml   ← 190 repos, strate + tier
src/repomix/
├── adapters/
│   └── known_repos_adapter.py    ← v3, 190 nœuds
scripts/
└── bundle_corpus.py              ← v2, chunking
tests/unit/
└── test_ecosystem_190.py         ← 6 tests
```

## Définition de "Done"

- [ ] `known_repos_adapter.py` retourne 190 nœuds
- [ ] `--ecosystem --tier P0` produit un bundle < 30 Mo en < 60s
- [ ] `--ecosystem` complet termine en < 5 min (ENV1 D:\DO\WEB\)
- [ ] 6 nouveaux tests passent — total ≥ 50 tests actifs
- [ ] Score émergence ≥ 82% recalculé sur 190 repos
