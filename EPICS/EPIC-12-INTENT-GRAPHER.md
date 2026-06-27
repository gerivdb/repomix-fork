# EPIC-12 — INTENT-GRAPHER : Vectorisation Cross-Repo du Thought Commit Pipeline

> **IntentHash**: `0xEPIC_INTENT_GRAPHER_VECTORISATION_PIPELINE_φ1.214`
> **Statut**: `draft`
> **Priorité**: P1
> **Repo cible**: gerivdb/repomix-fork
> **Strate**: L3 (DevTools / méta-outillage)
> **EPIC parent**: EPIC-07 (Ecosystem 190 repos)
> **Repos consommés**: tout repo gerivdb/* ayant INTENTS/ ou intents/ + PRD/ + EPICS/ + ADR/

---

## Problème actuel

Chaque repo de l'écosystème gerivdb formalise ses intentions différemment :
- KRONOS : `INTENTS/` + `PRD/` — EPICS et ADR absents
- Gitnote : `intents/` + `PRD/` + `ADR/` scaffold — issues non liées
- repomix-fork : `EPICS/` + `PRD/` — pas d'INTENTS/
- 170+ autres repos : structure inconnue ou absente

Il n'existe **aucun outil** capable de :
1. Lire la structure d'un repo et identifier quelles couches du pipeline sont présentes
2. Reconstruire le *propos* du repo à partir de ces fichiers (sans lire le code)
3. Mesurer la complétude du pipeline INTENT→Commit
4. Comparer des repos entre eux sur une même problématique (transversalité)

---

## Objectif

Créer **INTENT-GRAPHER** : un méta-outil qui, donné un repo cible (ou une liste), produit :

1. **`intent_vector.json`** — vecteur sémantique du repo (propos, dimension principale, contraintes)
2. **`pipeline_dag.json`** — DAG de traçabilité INTENT→PRD→EPIC→ADR→Issue→Commit
3. **`completeness_score.json`** — score 0→5 par couche + score global
4. **`cross_repo_diff.json`** — diff transversal entre repos partageant des EPICs parents communs

---

## Inspiration directe

### repomix-fork
repomix pack un repo en un fichier XML/MD lisible par LLM. INTENT-GRAPHER fait la même chose
mais **filtré sur les artefacts de pipeline** (INTENTS/, PRD/, EPICS/, ADR/, issues) plutôt que
sur le code source — produisant un "pack" sémantique-intentionnel.

### Roadmap fractale / méta-roadmap
Comme la roadmap fractale décompose une vision en niveaux emboîstés,
INTENT-GRAPHER remonte la chaîne inverse : des commits vers les intents,
reconstruisant la hiérarchie de sens.

### ontology_registry.json (repomix-fork)
Sert d'espace sémantique de référence pour normaliser les vecteurs d'intent
entre repos (termes métier communs).

---

## Architecture

```
INTENT-GRAPHER
    │
    ├── [1] RepoScanner
    │       Parcourt INTENTS/ + PRD/ + EPICS/ + ADR/ + .github/issues
    │       Détecte les couches présentes
    │       Extrait les IntentHash + EPIC parents + ADR statuses
    │
    ├── [2] IntentVectorizer
    │       Parse chaque fichier d'intent (YAML front-matter)
    │       Projette sur ontology_registry.json
    │       Produit intent_vector.json
    │
    ├── [3] PipelineDAGBuilder
    │       Construit le DAG INTENT→PRD→EPIC→ADR→Issue→Commit
    │       Identifie les nœuds manquants (gaps)
    │       Produit pipeline_dag.json
    │
    ├── [4] CompletenessScorer
    │       Score 0→1 par couche (pondéré par nombre de fichiers)
    │       Score global 0→5
    │       Produit completeness_score.json
    │
    └── [5] CrossRepoDiff (optionnel)
            Comparer N repos sur EPIC parent commun
            Identifier divergences d'intent sur même problématique
            Produit cross_repo_diff.json
```

---

## Périmètre technique

### Fichiers à créer
```
scripts/intent_grapher/
    ├── __init__.py
    ├── repo_scanner.py        # détection couches, listing fichiers pipeline
    ├── intent_vectorizer.py   # parse YAML front-matter + projection ontologie
    ├── pipeline_dag_builder.py # construction DAG + détection gaps
    ├── completeness_scorer.py  # scoring 0→5 par couche
    ├── cross_repo_diff.py      # diff transversal cross-repos
    └── cli.py                 # point d'entrée CLI
```

### CLI interface
```bash
# Analyser un repo
python -m intent_grapher --repo gerivdb/Gitnote --output intent_grapher_output/

# Comparer plusieurs repos
python -m intent_grapher --repos gerivdb/Gitnote,gerivdb/KRONOS --diff --epic-parent EPIC-1139

# Mode repomix-style : produire un pack sémantique lisible LLM
python -m intent_grapher --repo gerivdb/Gitnote --format llm-pack
```

### Format `intent_vector.json`
```json
{
  "repo": "gerivdb/Gitnote",
  "generated_at": "2026-06-27T09:47:00Z",
  "intent_vector": {
    "dimension_principale": "knowledge_digestion_pipeline",
    "source_pain": "fragmentation_signaux_git_repos",
    "cible": "enzyme_enzymatique_multi_source",
    "contraintes_hard": ["max_confidence_0.30", "hitl_validation"],
    "ontologie_terms": ["enzyme", "invariant", "signal", "digestion", "causality"]
  },
  "pipeline_completeness": {
    "intents": 1.0,
    "prd": 1.0,
    "epics": 1.0,
    "adr": 0.0,
    "issues": 0.0,
    "global_score": 2.0
  }
}
```

### Format `pipeline_dag.json`
```json
{
  "nodes": [
    {"id": "INT-1211", "layer": "intent", "file": "intents/INT-1211-...md"},
    {"id": "EPIC-1211", "layer": "epic", "file": "PRD/EPIC-1211-...md"},
    {"id": "ADR-1211", "layer": "adr", "file": null, "gap": true}
  ],
  "edges": [
    {"from": "INT-1211", "to": "EPIC-1211", "type": "derives"},
    {"from": "EPIC-1211", "to": "ADR-1211", "type": "requires", "gap": true}
  ]
}
```

---

## Scoring de complétude (détail)

| Couche | Points | Condition |
|---|---|---|
| `INTENTS/` ou `intents/` présent et non vide | 1.0 | ≥ 1 fichier `.md` avec front-matter YAML |
| `PRD/` présent et non vide | 1.0 | ≥ 1 PRD avec IntentHash |
| `EPICS/` présent et non vide | 1.0 | ≥ 1 EPIC avec critères d'acceptation |
| `ADR/` présent et non vide | 1.0 | ≥ 1 ADR `accepted` |
| Issues GitHub liées | 1.0 | ≥ 1 issue référençant un EPIC |
| **Max** | **5.0** | |

---

## Lien avec repomix-fork

INTENT-GRAPHER est une **Verse** spécialisée : là où repomix pack le code,
INTENT-GRAPHER pack la **sémantique intentionnelle**. Les deux peuvent s'enchaîner :

```
repomix --repo gerivdb/Gitnote > code_pack.xml
intent_grapher --repo gerivdb/Gitnote > intent_pack.json
# → LLM reçoit les deux : code + intention = compréhension système complète
```

L'`ontology_registry.json` existant dans repomix-fork sert de **pont sémantique** commun.

---

## Création d'une Verse dédiée

Il est recommandé de créer une Verse `intent_grapher_verse/` dans repomix-fork
avéc sa propre `repomix-verse.yaml` pour isoler le contenu sémantique-pipeline
des Verses de domaine (urban, lecun, etc.).

---

## Critères d'acceptation

- [ ] `intent_grapher --repo gerivdb/Gitnote` produit un `intent_vector.json` valide
- [ ] `pipeline_dag.json` contient les 3 intents 1211/1212/1213 et leurs EPICs
- [ ] `completeness_score` == 2.0 pour Gitnote (intents + PRD présents, ADR/Issues absents)
- [ ] `completeness_score` == 2.0 pour KRONOS (INTENTS + PRD présents)
- [ ] `--diff` entre Gitnote et KRONOS produit un `cross_repo_diff.json` non vide
- [ ] Mode `--format llm-pack` produit un fichier `.md` lisible directement par un LLM
- [ ] Tests dans `tests/test_intent_grapher.py`
- [ ] Aucune dépendance externe autre que `PyYAML`, `networkx`, `mcp-github` (optionnel)

---

## Dépendances

- `ontology_registry.json` — existant dans repomix-fork ✅
- `scripts/` — existant dans repomix-fork ✅
- SKILL `reposcope-*` (gerivdb/SKILLS) — [À_VALIDER_NEXUS] réutilisation possible
- MCP GitHub API — pour accès remote (mode cloud vs local)

---

## Ordonnancement

```
P0 — repo_scanner.py + CLI stub (2h) — pas de blocant
P1 — intent_vectorizer.py (3h) — besoin YAML front-matter dans les intents ✅ (Gitnote)
P2 — pipeline_dag_builder.py (3h) — besoin P0+P1
P3 — completeness_scorer.py (1h) — besoin P2
P4 — cross_repo_diff.py (2h) — besoin P3 + ≥ 2 repos scaffolodés ✅
P5 — tests + llm-pack format (2h) — besoin P0–P4
```

---

*Créé 2026-06-27 — [CONFORME_NEXUS]*
