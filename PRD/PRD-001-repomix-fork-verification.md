---
id: PRD-001
title: "Vérification & Tests repomix-fork — Diagnostic Réel"
repo: gerivdb/repomix-fork
status: accepted
created: 2026-06-10
author: gerivdb
---

# PRD-001 — Vérification & Tests repomix-fork

**Diagnostic réel de l'état du repo vs hypothèses initiales.**

---

## Résumé Exécutif

Le diagnostic initial (rédigé sur base d'une lecture MCP de la racine) contenait **des hypothèses incorrectes** sur la structure du repo. Ce document corrige le diagnostic sur base d'un audit live complet.

---

## Delta : Hypothèses initiales vs Réalité

| Élément | Hypothèse initiale | Réalité constatée |
|---------|-------------------|-------------------|
| `src/repomix/` existe | ✅ Oui, avec `engines/`, `marketplace/`, `migrations/` | ❌ **N'existe pas**. Aucun répertoire `src/` dans le repo |
| `verse_detector.py` à la racine | Présent racine | ✅ **Confirmé** — 7 Ko, seule version existante |
| `verse_detector.py` dans `src/repomix/` | Déjà migré | ❌ **N'existe pas** |
| `verses_library.py` à la racine | Présent racine | ✅ **Confirmé** — 14.5 Ko |
| `verses_library.py` dans `src/repomix/` | Version migrée | ❌ **N'existe pas** — mais existe dans `verses/` (18 Ko, version plus complète) |
| `verses_library.json` | Non mentionné | ✅ Existe — 21 Ko (données JSON) |
| Rôle de repomix-fork | Pipeline d'inventaire RSS-v2 | ❌ **Incorrect** — C'est un bundler souverain (fork yamadashy/repomix v1.14.1), pas un auditeur |
| `.py` à la racine | ~15 fichiers à migrer | **19 fichiers** — ce sont des verses UrbanVerse, pas du code repomix |
| `package.json` | Non mentionné | ❌ **Absent** — le code Node.js du bundler n'est pas dans ce repo |
| `scripts/register-repo.py` | Référencé dans README | ❌ **N'existe pas** |

---

## Décisions d'Architecture (BLOC D)

### D1 — `verse_detector.py` canonique
- **Décision** : La version racine (7 Ko, hash `C2B3F6BE...`) est la seule et unique version canonique.
- **Action** : Aucune migration nécessaire.

### D2 — `verses_library.py` canonique
- **Décision** : La version dans `verses/` (18 Ko, hash `401645C9...`) est plus complète que la racine (14.5 Ko, hash `880CE3EC...`).
- **Action** : La version `verses/verses_library.py` doit remplacer la version racine. La version racine est un stub/ancienne version.

### D3 — Rôle de repomix-fork
- **Décision** : Le repo contient deux couches distinctes :
  1. **Verses UrbanVerse** (19 `.py` à la racine + 27 fichiers dans `verses/`) — logique métier NEXUS
  2. **Configuration repomix** (`repomix-verse.yaml`, `STRATUM_RELAY.md`) — métadonnées du bundler
- **Action** : Ne PAS migrer les `.py` vers `src/repomix/`. Ils sont à leur place (verses à la racine + dans `verses/`).

### D4 — `.db` trackés
- **Décision** : 4 fichiers `.db` + `.coverage` étaient trackés dans git.
- **Action** : Retirés du tracking (Phase 1 complétée).

---

## Résultats du Nettoyage (Phase 1)

| Fichier | Action | Statut |
|---------|--------|--------|
| `beta_testing.db` | `git rm --cached` | ✅ Fait |
| `cache.db` | `git rm --cached` | ✅ Fait |
| `llm_catalog.db` | `git rm --cached` | ✅ Fait |
| `verses_marketplace.db` | `git rm --cached` | ✅ Fait |
| `.coverage` | `git rm --cached` | ✅ Fait |

### `.gitignore` mis à jour
Ajouté :
```
# RSS-v2 - Base de données locales (non trackées)
*.db

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
```

---

## Résultats des Tests (BLOC B)

### B1 — Imports Python
- `import verse_detector` : ✅ OK
- `import verses_library` : ✅ OK

### B2 — Interface verse_detector
- Classe principale : `UniversalVerseDetector`
- Types exportés : `VerseObservation`, `VerseStatus` (Enum)
- Module fonctionnel avec interface complète

### B3 — repomix-verse.yaml
- Version : 5.0.0
- Intent hash : `0xREPOMIX_INTENT_20260530`
- Mode ecosystem activé (multi-repo, XML)
- 4 intégrations configurées (argus, recall_coherence, codedb, llm_training)

### B4 — Module repomix (Node.js)
- ❌ `repomix` non installé comme module Python (normal — c'est un package npm)
- ❌ Pas de `package.json` dans ce repo (le code Node.js du bundler n'est pas ici)
- **Note** : Le bundler repomix est un outil externe. Ce repo contient les verses et la config UrbanVerse.

### B5 — Suite de tests pytest
- **985 tests collectés**
- **28 erreurs** — tous des `ModuleNotFoundError` (dépendances externes : `NEXUS`, `src.*`, etc.)
- **5 skipped**
- **0 test exécuté** (bloqué par les erreurs d'import)
- **Diagnostic** : La suite de tests est conçue pour un environnement complet avec tous les repos gerivdb montés (NEXUS, src/citizens, etc.). Elle ne peut pas tourner isolément dans ce repo.

---

## Conformité RSS-v2 (BLOC C)

### PRD renommés avec frontmatter

| Ancien nom | Nouveau nom | Statut |
|------------|-------------|--------|
| `PRD/PRD-Architecture-Diamant-Verses.md` | `PRD/PRD-002-architecture-diamant-verses.md` | ✅ Renommé + frontmatter ajouté |
| `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md` | `PRD/PRD-003-urban-ontology-verse.md` | ✅ Renommé + frontmatter ajouté |

### Frontmatter format
```yaml
---
id: PRD-002
title: "..."
repo: gerivdb/repomix-fork
status: draft
created: YYYY-MM-DD
author: gerivdb
---
```

---

## Structure finale du repo (fichiers racine)

```
repomix-fork/
├── .gitignore                    # ✅ Mis à jour (*.db, __pycache__, etc.)
├── .coverage                     # ✅ Untracked (reste local)
├── *.db (4 fichiers)             # ✅ Untracked (restent local)
├── STRATUM_RELAY.md              # Identité strate L4
├── repomix-verse.yaml            # Config UrbanVerse
├── README.md                     # Doc du fork
├── ontology_registry.json        # Registre local des verses
├── verses_library.py             # Stub (14.5 Ko) — verses/ est plus complet
├── verse_detector.py             # ✅ Canonique (7 Ko)
├── [17 autres .py]              # Verses UrbanVerse (à leur place)
├── PRD/
│   ├── PRD-002-architecture-diamant-verses.md  # ✅ Renommé + frontmatter
│   └── PRD-003-urban-ontology-verse.md         # ✅ Renommé + frontmatter
├── EPICS/                        # 6 EPICS + INDEX
├── verses/                       # 27 fichiers verses (incl. verses_library.py 18 Ko)
├── tests/                        # ~985 tests (dépendances externes requises)
└── [15 répertoires verses_*]     # Verses spécialisés
```

---

## Recommandations

1. **Ne PAS créer `src/repomix/`** — les verses sont à leur place à la racine et dans `verses/`
2. **Remplacer `verses_library.py` racine** par la version `verses/verses_library.py` (plus complète)
3. **Installer repomix via npm** si le bundler est nécessaire : `npx repomix@latest`
4. **Les tests nécessitent l'environnement complet** gerivdb (NEXUS, src/citizens, etc.) pour tourner
5. **Créer `scripts/register-repo.py`** si l'enregistrement automatique est nécessaire (actuellement référencé dans README mais absent)

---

*Document généré par OWL (Kilo) — 2026-06-10*
*IntentHash: 0xREPOMIX_PRD001_DIAGNOSTIC_20260610*
