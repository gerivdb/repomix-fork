#!/usr/bin/env python3
"""
A6 — Bundle repos tiers upstream pour IRIS.

Produit des bundles XML pour des repos tiers (bun, claude-code, etc.)
que IRIS surveille. Complement du mode opensrc : bundle complet vs API partielle.

Usage:
    python scripts/bundle_upstream.py --repo oven-sh/bun
    python scripts/bundle_upstream.py --all-iris
    python scripts/bundle_upstream.py --all-iris --dry-run
"""
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Repos tiers suivis par IRIS
IRIS_UPSTREAM_REPOS = [
    "oven-sh/bun",
    "anthropics/claude-code",
    "PowerShell/PowerShell",
    "yamadashy/repomix",
    "microsoft/vscode",
    "neovim/neovim",
]

DEFAULT_OUTPUT = Path("D:/DO/WEB/TOOLS/L3-CITIZENS/IRIS/bundles/upstream")
CONFIG_PATH = Path(__file__).parent.parent / "repomix.config.json"


def main():
    parser = argparse.ArgumentParser(
        description="A6 — Bundle repos tiers upstream pour IRIS"
    )
    parser.add_argument("--repo", help="Repo tiers specifique (owner/repo)")
    parser.add_argument("--all-iris", action="store_true",
                        help="Bundler tous les repos IRIS connus")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.all_iris:
        repos = IRIS_UPSTREAM_REPOS
    elif args.repo:
        repos = [args.repo]
    else:
        parser.error("Fournir --repo ou --all-iris")
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for repo in repos:
        slug = repo.replace("/", "__")
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        out_file = args.output_dir / f"upstream__{slug}__{ts}.xml"

        cmd = [
            "npx", "repomix", "--remote", repo,
            "--output", str(out_file),
            "--style", "xml", "--config", str(CONFIG_PATH),
        ]

        if args.dry_run:
            print(f"[DRY] {repo} -> {out_file.name}")
            results.append({"repo": repo, "status": "dry_run"})
            continue

        print(f"IRIS upstream: {repo}...", end=" ", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, shell=True)

        if r.returncode == 0:
            kb = out_file.stat().st_size // 1024
            print(f"OK ({kb}K)")
            results.append({"repo": repo, "file": str(out_file), "kb": kb, "status": "ok"})
        else:
            print(f"ECHEC")
            results.append({"repo": repo, "status": "error", "error": r.stderr[:200]})

    # Manifeste IRIS
    manifest = {"generated_at": datetime.now().isoformat(), "bundles": results}
    manifest_file = args.output_dir / "iris_upstream_manifest.json"
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifeste IRIS: {manifest_file}")


if __name__ == "__main__":
    main()
