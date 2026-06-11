# REPOMIX — UrbanVerse Fork

Bundler souverain de codebase → format LLM-optimisé (XML/MD/texte).

**Fork de** [yamadashy/repomix](https://github.com/yamadashy/repomix) v1.14.1
**Version** : v1.0.0 — PyPI-ready

## Installation

```bash
# Via npm (upstream)
npx repomix@latest

# Via PyPI (ce fork)
pip install gerivdb-repomix

# Via source
git clone https://github.com/gerivdb/repomix-fork.git
cd repomix-fork
pip install -e .
```

## Customisations UrbanVerse

### 1. Métadonnées UrbanVerse en XML
L'en-tête XML de chaque bundle inclut :
`strate`, `layer`, `phi_cps`, `intent_hash`, `vague_deployee`

### 2. Mode `--ecosystem`
Bundle multi-repo (190 repos → chunks 80 Mo/50 repos par tier P0→P3).
Config : `repomix-verse.yaml`

### 3. CLI Entrypoints

| Commande | Script |
|----------|--------|
| `repomix-scan` | `scripts/scan_ecosystem.py` |
| `repomix-bundle` | `scripts/bundle_for_argus.py` |
| `repomix-corpus` | `scripts/bundle_corpus.py` |
| `repomix-recall` | `scripts/pack_recall.py` |
| `repomix-validate` | `scripts/validate_all.py` |
| `repomix-secrets` | `scripts/scan_secrets.py` |
| `repomix-graph` | `scripts/xml_to_graph.py` |

### 4. Tests
```bash
pytest tests/unit/ -v
# 92 tests — adapters, sync, marketplace, recall, ecosystem, cli_contract
```

## Apports écosystème

| ID | Bénéficiaire | Apport | Vague |
|----|-------------|--------|-------|
| A1 | ARGUS | Bundle unique → scan 7 pathologies | 5 |
| A2 | recall_coherence_check.py | Mode `--repomix` exhaustivité | 5 |
| A3 | CodeDB-E5620 / LYCOS | Corpus d'indexation FLUENCE | 6 |
| A4 | LLM-REPO/TRAINING/ | Packs recall auto-générés | 5 |
| A5 | ECOS-CLI | cli_contract.py v1.0.0 — `ecos bundle` | 11 |
| A6 | IRIS | Canal repomix repos tiers | 7 |
| A7 | GeriCode/KiloCode | Métadonnées UrbanVerse dans XML | 12 |
| A8 | ECOS-VISION | Bundle XML → graphes dépendances | 6 |
| A9 | DATA-MINER | mine_bundle v2 — 190 repos | 12 |
| A10 | TOPOS/Riddler | Scan secrets sur fichier unique | 6 |

## Métriques

| Métrique | Valeur |
|----------|--------|
| EPICs déployés | 11/11 |
| PRDs accepted | 9 |
| Tests unitaires | 92/92 |
| Repos dans graphe | 190 |
| Temps chargement graphe | 0.21s |
| Bundle 190 repos | 0.01s (4 chunks) |

## Fichiers clés

- `STRATUM_RELAY.md` — Identité stratique L4, Vague 15
- `repomix-verse.yaml` — Configuration UrbanVerse v3
- `CHANGELOG.md` — Historique des vagues 1→15
- `EPICS/INDEX.md` — 11 EPICs déployés

## Licence

MIT (hérité de yamadashy/repomix)

---

*UrbanVerse v5.0.0 — IntentHash: 0xREPOMIX_INTENT_20260530*
*Vague 18 — v1.0.0 finalisée*
