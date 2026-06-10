# Interface ECOS-CLI — repomix-fork (A5)

Spec d'interface pour le cote ECOS-CLI (`gerivdb/ECOS-CLI`).
Les scripts appartiennent a repomix-fork, ECOS-CLI les appelle en subprocess.

## Commande attendue

```bash
ecos bundle <repo>              # Bundle mono-repo -> ARGUS
ecos bundle --tier P0           # Corpus tier P0 complet
ecos bundle --recall <repo>     # Pack recall LLM-REPO
ecos bundle --argus <repo>      # Bundle ARGUS (alias)
ecos bundle --corpus --tier P0  # Corpus multi-repo
```

## Contrat entree/sortie

| Commande ECOS-CLI | Script repomix-fork | Sortie |
|-------------------|---------------------|--------|
| `ecos bundle <repo>` | `scripts/bundle_for_argus.py --repo <repo>` | XML dans `data/argus/bundles/` |
| `ecos bundle --tier P0` | `scripts/bundle_corpus.py --tier P0` | XMLs dans `corpus/` + manifeste |
| `ecos bundle --recall <repo>` | `scripts/pack_recall.py --repo <repo>` | XML + meta JSON dans LLM-REPO/TRAINING/packs/ |
| `ecos bundle --argus <repo>` | `scripts/bundle_for_argus.py --repo <repo>` | idem bundle |

## Chemin d'appel (depuis ECOS-CLI)

```python
import subprocess
REPOMIX_ROOT = "D:/DO/WEB/TOOLS/L4-TOOLS/REPOMIX-FORK"
result = subprocess.run([
    "python",
    f"{REPOMIX_ROOT}/scripts/bundle_for_argus.py",
    "--repo", repo_name
], capture_output=True, text=True, encoding="utf-8", errors="replace")
```

## Variables d'environnement

| Variable | Defaut | Usage |
|----------|--------|-------|
| `REPOMIX_OUTPUT_DIR` | `D:/DO/WEB/TOOLS/L4-TOOLS/repomix/` | Repertoire de sortie global |
| `REPOMIX_YAML_PATH` | `D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB/known_repositories.yaml` | SOT repos |
| `REPOMIX_RECALL_VERSION` | `v1` | Version des packs recall |
