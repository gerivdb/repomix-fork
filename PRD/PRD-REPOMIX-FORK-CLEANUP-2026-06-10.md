# PRD — repomix-fork : nettoyage, activation verse_detector et intégration pipeline d'inventaire

**Version** : 1.0
**Date** : 2026-06-10
**Statut** : DRAFT
**Auteur** : Kilo Agent (ENV1)
**IntentHash** : `0xPRD_REPOMIX_FORK_CLEANUP_V1_20260610`
**Dépôt canon** : `gerivdb/repomix-fork` (PRD/)
**Repos concernés** : `gerivdb/repomix-fork`, `gerivdb/DevTools`

---

## Résumé Exécutif

`gerivdb/repomix-fork` est le repo de l'écosystème le plus riche en **capacités potentielles d'inventaire et de parsing** (`verse_detector.py`, `verse_auto_projection.py`, `neuro_symbolic_verse_engine.py`, `STRATUM_RELAY.md`). Cependant, le repo souffre de **pollution structurelle significative** qui l'empêche d'être utilisé efficacement :

- ~15 fichiers `.py` à la racine (violation règle NEXUS)
- Fichiers `.db` committés (`cache.db`, `beta_testing.db`, `llm_catalog.db`, `verses_marketplace.db`)
- Confusion historique avec le repo `VERSUS` (purge effectuée)
- `verse_detector.py` non branché sur `known_repositories.yaml`

Ce PRD définit le plan de nettoyage et d'activation de `repomix-fork` comme **pipeline d'inventaire local** de l'écosystème.

---

## 1. Diagnostic (2026-06-10)

### 1.1 Pollution structurelle identifiée

| Problème | Fichiers concernés | Violation |
|---------|-------------------|----------|
| `.py` à la racine | `brain_bypass_verse.py`, `fluence_bypass_verse.py`, `marketplace_phase4_week*.py`, `migration_phase*.py`, `neuro_symbolic_verse_engine.py`, `physic_verse.py`, `verse-template-generator.py`, `verse_auto_projection.py`, `verse_detector.py`, `verse_spiral_implementations.py`, `verses_creative_foundation.py`, `verses_library.py`, `world_verse.py` | Règle NEXUS : scripts .py à la racine → migrer vers `src/` ou `BRAIN` |
| `.db` committés | `cache.db`, `beta_testing.db`, `llm_catalog.db`, `verses_marketplace.db` | Données binéaires → `.gitignore` + `git rm --cached` |
| `.coverage` committé | `.coverage` (53 Ko) | Artefact de test → `.gitignore` |
| Dossiers `*_verse` en vrac | 10+ dossiers à la racine | Structure non conforme RSS-v1 |
| `*_bypass_verse.py` | `brain_bypass_verse.py`, `fluence_bypass_verse.py`, `wazaa_bypass_verse.js` | Bypasses actifs non documentés |

### 1.2 Actifs valorisables

| Fichier | Taille | Valeur potentielle |
|---------|--------|-------------------|
| `verse_detector.py` | 7 Ko | Détection structures verse — **cœur du pipeline** |
| `verse_auto_projection.py` | 3 Ko | Projection/mapping automatique de repos |
| `neuro_symbolic_verse_engine.py` | 13 Ko | Analyse symbolique de contenu |
| `verse-template-generator.py` | 17 Ko | Génération templates depuis structure |
| `verses_library.py` + `.json` | 14+21 Ko | Bibliothèque indexée de verses |
| `STRATUM_RELAY.md` | 3.5 Ko | **Pont ENV1 — pièce pivot** |
| `repomix-verse.yaml` | 1 Ko | Config repomix spécifique verses |
| `src/` | — | Structure cible pour migration |
| `scripts/` | — | Scripts auxiliaires |

### 1.3 État du pipeline d'inventaire

```
[❌ NON BRANCHÉ] known_repositories.yaml (GOVERNANCE-HUB)
       ↓
[⚠️ PARTIEL]  verse_detector.py (racine repomix-fork)
       ↓
[❌ MANQUANT]  audit_prd.py (DevTools/scripts/)
       ↓
[❌ INACTIF]   STRATUM_RELAY.md → ENV1
```

---

## 2. Architecture cible

### 2.1 Structure post-nettoyage

```
repomix-fork/
├── src/                          # Code Python migré depuis racine
│   ├── core/
│   │   ├── verse_detector.py       ← migré depuis racine
│   │   ├── verse_auto_projection.py ← migré
│   │   └── neuro_symbolic_engine.py ← migré (renommé)
│   ├── marketplace/
│   │   └── marketplace_phase*.py    ← migrés
│   └── migration/
│       └── migration_phase*.py      ← migrés
├── scripts/                      # Scripts auxiliaires (déjà présent)
├── verses/                       # Verses métier (déjà présent)
├── data/                         # Données JSON/YAML (déjà présent)
├── STRATUM_RELAY.md              ✅ conserver à la racine
├── PRD/                          ✅ ce document
├── EPICS/                        ✅ déjà présent
├── repomix-verse.yaml            ✅ conserver
├── pyproject.toml                ✅ conserver
└── .gitignore                    ← mettre à jour (.db, .coverage)
```

### 2.2 Pipeline d'inventaire activé

```
known_repositories.yaml (GOVERNANCE-HUB, 176+ repos)
  ↓ lu par
DevTools/scripts/inventory_repos.py
  ↓ appelle pour chaque repo
  ├── repomix-fork/src/core/verse_detector.py   [si repo type verse]
  └── DevTools/scripts/audit_prd.py             [si PRD/ présent]
       ↓
  rapport JSON consolidé
       ↓
  STRATUM_RELAY.md → ENV1 (Perplexity MCP)
```

---

## 3. Plan de réalisation

### Phase 1 — Nettoyage `.gitignore` + `.db` (P0 — 30 min)

| Tâche | Commande | Validation |
|-------|----------|------------|
| Ajouter au `.gitignore` | `*.db`, `*.coverage`, `.coverage`, `__pycache__/` | `cat .gitignore` |
| Supprimer `.db` du tracking | `git rm --cached *.db .coverage` | `git status` → 0 .db trackés |
| Commit + push | `git commit -m "chore: untrack .db and .coverage files"` | Remote propre |

### Phase 2 — Migration `.py` racine vers `src/` (P0 — 1h)

| Tâche | Fichiers source | Destination |
|-------|----------------|-------------|
| Migrer core | `verse_detector.py`, `verse_auto_projection.py`, `neuro_symbolic_verse_engine.py` | `src/core/` |
| Migrer marketplace | `marketplace_phase*.py`, `verses_creative_foundation.py`, `verses_library.py`, `verse_spiral_implementations.py` | `src/marketplace/` |
| Migrer migration | `migration_phase*.py` | `src/migration/` |
| Migrer utilitaires | `physic_verse.py`, `world_verse.py`, `verse-template-generator.py` | `src/utils/` |
| Documenter bypasses | `brain_bypass_verse.py`, `fluence_bypass_verse.py`, `wazaa_bypass_verse.js` | Commenter intent ou déplacer `src/bypass/` |

### Phase 3 — Activation `verse_detector.py` (P1 — 2h)

| Tâche | Détail | Validation |
|-------|--------|------------|
| Adapter `verse_detector.py` | Accepter `known_repositories.yaml` en entrée | Tests unitaires |
| Créer `src/core/pipeline.py` | Orchestration : yaml → detect → audit → rapport | `python pipeline.py --dry-run` |
| Lier avec `DevTools/scripts/audit_prd.py` | Appel subprocess ou import | Rapport consolidé généré |

### Phase 4 — STRATUM_RELAY activation (P2 — 2h)

| Tâche | Détail |
|-------|--------|
| Lire `STRATUM_RELAY.md` complet | Comprendre le protocole de relay existant |
| Ajouter payload JSON au STRATUM_RELAY | Format : `{repo, audit_result, timestamp}` |
| Tester boucle complète | Local → rapport → relay → ENV1 confirmation |

---

## 4. KPI et critères de succès

| Métrique | Avant (2026-06-10) | Cible |
|----------|--------------------|-------|
| Fichiers `.py` à la racine | ~15 | 0 |
| Fichiers `.db` trackés | 4 | 0 |
| `verse_detector.py` branché sur known_repositories.yaml | Non | Oui |
| Pipeline d'inventaire local fonctionnel | Non | Oui (dry-run pass) |
| STRATUM_RELAY actif | Non | Oui (payload → ENV1) |
| Confusion avec VERSUS | Résolue (purge effectuée) | ✅ Maintenu |

---

## 5. Risques et mitigations

| Risque | P | Impact | Mitigation |
|--------|:-:|--------|------------|
| Migration `.py` casse des imports existants | Moyen | Haut | Mettre à jour `__init__.py` + tests avant migration |
| `git rm --cached .db` perte de données de test | Faible | Moyen | Backup local avant `rm --cached` |
| `verse_detector.py` incompatible YAML GOVERNANCE-HUB | Inconnu | Haut | Analyser format attendu vs `known_repositories.yaml` avant adaptation |
| `STRATUM_RELAY.md` protocole obsète | Inconnu | Moyen | Lire complètement avant Phase 4 |

---

## 6. Références

| Document | Localisation | Type |
|----------|-------------|------|
| Ce PRD | `repomix-fork/PRD/PRD-REPOMIX-FORK-CLEANUP-2026-06-10.md` | PRD |
| PRD DevTools (lié) | `DevTools/PRD/PRD-AUDIT-PRD-ENGINE-2026-06-10.md` | PRD lié |
| STRATUM_RELAY | `repomix-fork/STRATUM_RELAY.md` | Pont ENV1 |
| known_repositories.yaml | `GOVERNANCE-HUB/known_repositories.yaml` | SOT repos |
| Règles NEXUS | Superstructure L0→L9 | Gouvernance |
| EPIC parent | `GOVERNANCE-HUB/EPICS/EPIC-2026-06-10-PRD-RESTRUCTURATION.md` | EPIC parent |

---

*PRD repomix-fork cleanup v1.0 — Nettoyage et activation pipeline d'inventaire local.*
*Couvre : pollution structurelle, migration src/, activation verse_detector, STRATUM_RELAY.*
*IntentHash: 0xPRD_REPOMIX_FORK_CLEANUP_V1_20260610*
*[À_VALIDER_NEXUS] [DÉRIVÉ — diagnostic ENV1 2026-06-10]*
