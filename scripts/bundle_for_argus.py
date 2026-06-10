#!/usr/bin/env python3
"""
A1 — Bundle unique repo → ARGUS scan.

Produit un bundle XML repomix pour un repo cible.
Le bundle est deposé dans data/argus/bundles/ (non committe, R3 offline).
Le manifeste data/argus_bundle_manifest.json est mis a jour automatiquement.

Usage:
    python scripts/bundle_for_argus.py --repo gerivdb/NEXUS [--output-dir PATH] [--dry-run]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

DEFAULT_OUTPUT = Path(__file__).parent.parent / "data" / "argus" / "bundles"
MANIFEST_PATH = Path(__file__).parent.parent / "data" / "argus_bundle_manifest.json"
REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = REPO_ROOT / "repomix.config.json"


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {
        "version": "1.0",
        "generated_at": None,
        "generator": "repomix-fork/scripts/bundle_for_argus.py",
        "bundles": [],
    }


def save_manifest(manifest: dict):
    manifest["generated_at"] = datetime.now().isoformat()
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="A1 — Bundle unique repo pour ARGUS scan"
    )
    parser.add_argument("--repo", required=True, help="Ex: gerivdb/NEXUS")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_slug = args.repo.replace("/", "__")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = args.output_dir / f"{repo_slug}__{timestamp}.xml"

    cmd = [
        "npx", "repomix",
        "--remote", args.repo,
        "--output", str(output_file),
        "--style", "xml",
        "--config", str(CONFIG_PATH),
    ]

    print(f"Bundle: {args.repo} -> {output_file.name}")

    if args.dry_run:
        print(f"[DRY RUN] {' '.join(cmd)}")
        sys.exit(0)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"ERREUR: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    size_kb = output_file.stat().st_size // 1024
    print(f"OK: {size_kb}Ko")

    # Update manifest
    manifest = load_manifest()
    manifest["bundles"].append({
        "repo": args.repo,
        "file": str(output_file.relative_to(REPO_ROOT)),
        "timestamp": timestamp,
        "size_kb": size_kb,
    })
    save_manifest(manifest)
    print(f"Manifeste mis a jour: {MANIFEST_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
