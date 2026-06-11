# DATA-MINER Interface — repomix-fork (A9)

Spec d'interface pour le pipeline de mining de bundles XML.

## Commande

```bash
# Mining d'un bundle complet
python scripts/mine_bundle.py --input bundle_001.xml --output mining_report.json

# Mining filtré par repo
python scripts/mine_bundle.py --input bundle.xml --repo-filter NEXUS --repo-filter BRAIN

# Mining d'un bundle P0 (41 repos)
python scripts/mine_bundle.py --input data/bundles/bundle_001.xml --output data/mining_p0.json
```

## Format rapport JSON

```json
{
  "bundle": "path/to/bundle.xml",
  "repos_count": 41,
  "repos": [
    {
      "name": "NEXUS",
      "files_count": 12,
      "languages": {".py": 8, ".md": 2, ".yaml": 2},
      "total_lines": 450,
      "imports": ["os", "sys", "pathlib"],
      "functions": ["main", "process", "validate"],
      "classes": ["NexusCore"],
      "todos": [{"type": "TODO", "text": "implement validation"}],
      "strings": ["Result: {}", "Error: invalid input"],
      "has_tests": true,
      "has_config": true,
      "metadata": {
        "strate": "L1",
        "tier": "P0",
        "phi_cps": "3.697",
        "intent_hash": "0xREPOMIX_INTENT_20260611",
        "vague_deployee": "12",
        "layer": "L1_CAUSALITY"
      }
    }
  ],
  "summary": {
    "total_files": 480,
    "total_lines": 15230,
    "languages": {".py": 320, ".md": 80, ".yaml": 40, ".js": 40},
    "has_tests": true,
    "has_config": true,
    "elapsed_s": 0.05
  }
}
```

## Champs garantis

| Champ | Type | Description |
|-------|------|-------------|
| `name` | str | Nom du repo |
| `files_count` | int | Nombre de fichiers dans le repo |
| `languages` | dict | Comptage par extension |
| `total_lines` | int | Nombre total de lignes |
| `imports` | list | Modules importés (max 30) |
| `functions` | list | Fonctions définies (max 30) |
| `classes` | list | Classes définies (max 20) |
| `todos` | list | TODO/FIXME/HACK détectés (max 20) |
| `strings` | list | Strings courts extraits (max 20) |
| `has_tests` | bool | Présence de fichiers test |
| `has_config` | bool | Présence de fichiers config |
| `metadata` | dict | Métadonnées UrbanVerse du header XML |

## KPI

| Métrique | Cible |
|----------|-------|
| Bundle P0 (41 repos) | < 30s |
| Bundle ALL (190 repos) | < 60s |
| Métadonnées extraites | 100% des repos avec balises UrbanVerse |
| Tests unitaires | 5 tests passent |

## Intégration

- **DATA-MINER** : lit le rapport JSON pour analyse de patterns
- **LYCOS** : ingère le corpus d'indexation via bundle XML
- **FLUENCE** : consomme les métadonnées phi-CPS et strate
- **ARGUS** : utilise les rapports pour détection de drift

## Tests

```bash
pytest tests/unit/test_mine_bundle.py -v
# 5 tests: basic, json format, repo filter, functions/classes/todos, performance, metadata
```
