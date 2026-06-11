# Changelog — gerivdb-repomix

## [1.0.0] — 2026-06-11

### Résumé

Première release stable de `gerivdb-repomix`, fork souverain de yamadashy/repomix v1.14.1 avec customisations UrbanVerse. Couvre 190 repos gerivdb/* avec pipeline complet de bundling, mining, et synchronisation marketplace.

### Vagues de déploiement

| Vague | Contenu | Statut |
|-------|---------|--------|
| 4 | Fork + métadonnées XML + mode écosystème + agents | Déployé |
| 5 | CI/CD local + tests UrbanVerse + A1 ARGUS + A2 recall | Déployé |
| 6 | A3→A10 câblés, docs ECOS-CLI, scan secrets | Déployé |
| 7 | Packaging v1.0.0, upstream sync, score émergence > 72% | Déployé |
| 8 | PRD-002 P3+P4 : VersesSyncManager + Marketplace API | Déployé |
| 9 | PRD-003 P1+P2 : UrbanVerse structure + 10 pilotes + upstream sync | Déployé |
| 10 | PRD-003 P3+P4 : Karpathy Recall + Fibre/Économie | Déployé |
| 11 | PRD-007+008 : Ecosystem 190 repos + cli_contract A5 + bundle_corpus v2 | Déployé |
| 12 | PRD-009+010 : mine_bundle v2 + A7 tests + relay Vague 2+3 + cadastre 190 | Déployé |
| 13 | PRD-011 : Marketplace sync bidirectionnelle + publication PyPI | Déployé |

### Fonctionnalités principales

- **Bundle multi-repo** : `bundle_corpus.py v2` — streaming XML, chunking 80Mo/50 repos, KPI < 5min pour 190 repos
- **Adaptateur graphe** : `known_repos_adapter.py v3` — 190 nœuds, lazy loading, tier API, KPI < 5s
- **Mining** : `mine_bundle.py v2` — extraction imports, fonctions, classes, todos, strings depuis bundle XML
- **Contrat CLI** : `cli_contract.py v1.0.0` — BundleRequest/Result, bundle_repo(), CLI_SCHEMA A5
- **Relay propagator** : Vague 1 (DSL) + Vague 2 (5Q Karpathy + règles locales) + Vague 3 (FIBRE + 10Q)
- **Cadastre** : 190 parcelles (86 FIBRE + 104 DSL)
- **Marketplace** : API FastAPI locale (port 8742) avec push bidirectionnel vers VERSES/ontology_registry.json
- **Publication PyPI** : workflow GitHub Actions (tag v* → TestPyPI → PyPI → GitHub Release)

### Tests

- **77 tests unitaires** passent (pytest tests/unit/)
- Couverture : adapters, sync, marketplace, relay, mining, bundle, cli_contract, ecosystem 190

### Entrypoints CLI

| Commande | Script |
|----------|--------|
| `repomix-scan` | `scripts/scan_ecosystem.py` |
| `repomix-bundle` | `scripts/bundle_for_argus.py` |
| `repomix-corpus` | `scripts/bundle_corpus.py` |
| `repomix-recall` | `scripts/pack_recall.py` |
| `repomix-validate` | `scripts/validate_all.py` |
| `repomix-secrets` | `scripts/scan_secrets.py` |
| `repomix-graph` | `scripts/xml_to_graph.py` |

### Dépendances

- Python >= 3.11
- numpy, pydantic, httpx, networkx, pyyaml
- Optionnel : fastapi, uvicorn (marketplace)
- Dev : pytest, build, twine

### Métadonnées UrbanVerse injectées dans ch XML

- `strate` — strate du repo (L0→L9)
- `tier` — priorité (P0→P3)
- `phi_cps` — score cognitif
- `intent_hash` — identifiant unique
- `vague_deployee` — numéro de vague
- `layer` — layer détaillé

### Apports écosystème (A1→A10)

| ID | Bénéficiaire | Apport |
|----|-------------|--------|
| A1 | ARGUS | Bundle unique par repo → scan 7 pathologies |
| A2 | recall_coherence_check.py | Mode `--repomix` exhaustivité |
| A3 | CodeDB-E5620 / LYCOS | Corpus d'indexation multi-repo |
| A4 | LLM-REPO | Packs recall auto-générés, versionnés |
| A5 | ECOS-CLI | Commande `ecos bundle` via cli_contract |
| A6 | IRIS | Canal repomix complémentaire opensrc |
| A7 | GeriCode/KiloCode | Métadonnées UrbanVerse dans XML |
| A8 | ECOS-VISION | Bundle XML → graphes dépendances |
| A9 | DATA-MINER | Mining sur bundle complet sans git clone |
| A10 | TOPOS/Riddler | Scan secrets sur fichier unique |

| 17 | EPICs 01→11 statuts synchronisés, consolidations | Déployé |
| 18 | Nettoyage artefacts, README v1.0.0, upstream check, PyPI-ready | Déployé |

---

*Fork de yamadashy/repomix — UrbanVerse v5.0.0*
*IntentHash: 0xREPOMIX_INTENT_20260530*
*V1.0.0 — Cycle complet Vagues 1→18*
