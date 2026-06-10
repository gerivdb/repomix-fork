#!/usr/bin/env python3
"""
A3 — Corpus d'indexation multi-repo → ingestion CodeDB-E5620 / LYCOS / FLUENCE.

Produit des bundles XML/MD pour un ou plusieurs tiers de repos
(known_repositories.yaml). Chaque repo est bundlé via npx repomix.
Les bundles sont déposés dans corpus/ (gitignore) avec un manifeste JSON.

Usage:
    python scripts/bundle_corpus.py --tier P0
    python scripts/bundle_corpus.py --tier P0 --tier P1 --format md
    python scripts/bundle_corpus.py --tier P2 --dry-run
"""
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

import yaml

DEFAULT_YAML = Path("D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB/known_repositories.yaml")
DEFAULT_OUTPUT = Path(__file__).parent.parent / "corpus"

TIER_MAP = {
    "P0": "P0_CONSTITUTIONAL",
    "P1": "P1_STRATEGIC",
    "P2": "P2_SUPPORT",
}

SKIP_STATUS = {"archived"}
SKIP_LIFECYCLE = {"DEPRECATED", "DORMANT"}
SKIP_NAME_PREFIXES = ("geri-cms-", "gericms")
CONFIG_PATH = Path(__file__).parent.parent / "repomix.config.json"


def is_inactive(repo: dict) -> bool:
    if repo.get("status") in SKIP_STATUS:
        return True
    if repo.get("lifecycle") in SKIP_LIFECYCLE:
        return True
    if repo.get("archived_at"):
        return True
    name = repo.get("name", "")
    if any(name.lower().startswith(p) for p in SKIP_NAME_PREFIXES):
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="A3 — Corpus multi-repo pour CodeDB/LYCOS/FLUENCE"
    )
    parser.add_argument("--tier", action="append", default=[],
                        choices=["P0", "P1", "P2"],
                        help="Tier a traiter (repetable). Defaut: P0")
    parser.add_argument("--yaml", type=Path, default=DEFAULT_YAML)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--format", default="xml", choices=["xml", "md", "txt"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = yaml.safe_load(args.yaml.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "generated_at": datetime.now().isoformat(),
        "tiers": args.tier,
        "format": args.format,
        "bundles": [],
    }
    errors = []

    for tier in args.tier:
        section = TIER_MAP[tier]
        repos = data.get(section, [])
        print(f"\n[{tier}] {len(repos)} repos dans {section}")

        for repo in repos:
            name = repo.get("name", "")
            full_name = repo.get("full_name", "")

            if is_inactive(repo):
                print(f"  SKIP {name} (inactif)")
                continue

            slug = full_name.replace("/", "__")
            ts = datetime.now().strftime("%Y%m%d")
            out_file = args.output_dir / f"{slug}__{ts}.{args.format}"

            cmd = [
                "npx", "repomix",
                "--remote", full_name,
                "--output", str(out_file),
                "--style", args.format,
                "--config", str(CONFIG_PATH),
            ]

            if args.dry_run:
                print(f"  [DRY] {full_name} -> {out_file.name}")
                manifest["bundles"].append({
                    "repo": full_name, "tier": tier,
                    "file": str(out_file), "status": "dry_run"
                })
                continue

            print(f"  Bundling {full_name}...", end=" ", flush=True)
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=120, shell=True)
            if r.returncode == 0:
                kb = out_file.stat().st_size // 1024 if out_file.exists() else 0
                print(f"OK ({kb}K)")
                manifest["bundles"].append({
                    "repo": full_name, "tier": tier,
                    "file": str(out_file), "kb": kb, "status": "ok"
                })
            else:
                print(f"ECHEC")
                err_msg = r.stderr[:200] if r.stderr else "unknown"
                errors.append({"repo": full_name, "error": err_msg})
                manifest["bundles"].append({
                    "repo": full_name, "tier": tier,
                    "status": "error", "error": err_msg
                })

    # Ecriture manifeste
    manifest_path = args.output_dir / "corpus_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    total = len(manifest["bundles"])
    ok = sum(1 for b in manifest["bundles"] if b.get("status") == "ok")
    print(f"\n{total} repos traites | {ok} OK | {len(errors)} erreurs")
    print(f"Manifeste: {manifest_path}")
    if errors:
        print(f"Erreurs: {[e['repo'] for e in errors]}")


if __name__ == "__main__":
    main()
