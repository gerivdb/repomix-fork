#!/usr/bin/env python3
"""
A4 — Packs recall auto-generes pour LLM-REPO/TRAINING/.

Produit un bundle XML avec metadonnées de versioning (version, SHA256, timestamp).
Chaque pack est optimise LLM : XML avec en-tete UrbanVerse etragu.

Usage:
    python scripts/pack_recall.py --repo gerivdb/BRAIN
    python scripts/pack_recall.py --repo gerivdb/NEXUS --version v2
"""
import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

DEFAULT_OUTPUT = Path("D:/DO/WEB/TOOLS/L1-INFRA/LLM-REPO/TRAINING/packs")
CONFIG_PATH = Path(__file__).parent.parent / "repomix.config.json"


def main():
    parser = argparse.ArgumentParser(
        description="A4 — Packs recall pour LLM-REPO/TRAINING/"
    )
    parser.add_argument("--repo", required=True, help="Ex: gerivdb/BRAIN")
    parser.add_argument("--version", default="v1", help="Version du pack")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    slug = args.repo.replace("/", "__")
    out_file = args.output_dir / f"recall__{slug}__{args.version}__{ts}.xml"

    env = os.environ.copy()
    env["REPOMIX_RECALL_VERSION"] = args.version
    env["REPOMIX_RECALL_GENERATED_AT"] = ts

    cmd = [
        "npx", "repomix",
        "--remote", args.repo,
        "--output", str(out_file),
        "--style", "xml",
        "--config", str(CONFIG_PATH),
    ]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, shell=True, env=env, encoding="utf-8", errors="replace")

    if r.returncode != 0:
        print(f"ERREUR: {r.stderr[:300]}", file=__import__("sys").stderr)
        raise SystemExit(1)

    # Calcul SHA256
    content = out_file.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()[:12]
    kb = len(content) // 1024

    # Manifeste JSON
    meta = {
        "repo": args.repo,
        "version": args.version,
        "generated_at": ts,
        "sha256_short": sha256,
        "kb": kb,
        "file": str(out_file),
    }
    meta_file = out_file.with_suffix(".json")
    meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Pack recall: {out_file.name}")
    print(f"  {kb}K | SHA256: {sha256} | meta: {meta_file.name}")


if __name__ == "__main__":
    main()
