# Interface ECOS-CLI — repomix-fork (A5)

Spec d'interface pour le cote ECOS-CLI (`gerivdb/ECOS-CLI`).
Les scripts appartiennent a repomix-fork, ECOS-CLI les appelle en subprocess.

## Contrat d'interface v1.0.0

**Version** : 1.0.0
**IntentHash** : `0xECOS_CLI_CONTRACT_A5_20260611`
**Fichier source** : `src/repomix/cli_contract.py`

## Commande attendue

```bash
ecos bundle <repo>              # Bundle mono-repo -> ARGUS
ecos bundle --tier P0           # Corpus tier P0 complet
ecos bundle --recall <repo>     # Pack recall LLM-REPO
ecos bundle --argus <repo>      # Bundle ARGUS (alias)
ecos bundle --corpus --tier P0  # Corpus multi-repo
```

## BundleRequest / BundleResult — types

```python
from repomix.cli_contract import BundleRequest, BundleResult, Tier, OutputFormat

# Requete
req = BundleRequest(
    repo="GOVERNANCE-HUB",
    tier=Tier.P0,
    output_format=OutputFormat.XML,
    include_metadata=True,
)

# Resultat
result: BundleResult = bundle_repo(req)
# result.success: bool
# result.output_path: Path | None
# result.size_bytes: int
# result.elapsed_s: float
# result.chunks: int
# result.error: str | None
```

## Contrat garanti v1.0.0

- Signature stable : `BundleRequest -> BundleResult`
- Levee de `ValueError` si `request.validate()` retourne des erreurs
- Jamais de `sys.exit()` — toujours retourner `BundleResult(success=False, error=...)`

## CLI_SCHEMA — reference

| Argument | Type | Requis | Defaut | Choix |
|----------|------|--------|--------|-------|
| `--repo` | str | Oui | — | Nom du repo ou ALL |
| `--tier` | str | Non | ALL | P0, P1, P2, P3, ALL |
| `--output` | str | Non | xml | xml, md, text |
| `--out-dir` | Path | Non | data/bundles/ | Repertoire de sortie |

**Codes de sortie** :
- 0 : success
- 1 : validation_error
- 2 : repo_not_found
- 3 : bundle_failed

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
| `REPOMIX_YAML_PATH` | `data/known_repositories_190.yaml` | SOT repos v3 |
| `REPOMIX_RECALL_VERSION` | `v1` | Version des packs recall |

## Changelog

| Version | Date | Changement |
|---------|------|------------|
| 1.0.0 | 2026-06-11 | Contrat initial A5 — BundleRequest/Result, CLI_SCHEMA, bundle_repo() |
