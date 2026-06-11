#!/usr/bin/env python3
"""
bundle_corpus.py v2 — PRD-007 Phase C
Chunking automatique, streaming XML, KPI < 5min pour 190 repos.

Usage:
    python scripts/bundle_corpus.py --yaml data/known_repositories_190.yaml --tier ALL
    python scripts/bundle_corpus.py --yaml data/known_repositories_190.yaml --tier P0
    python scripts/bundle_corpus.py --yaml data/known_repositories_190.yaml --tier P0 --chunk-size-mb 80
"""
from __future__ import annotations
import time
import json
import sys
from pathlib import Path
from typing import Iterator

CHUNK_SIZE_MB = 80
REPOS_PER_PACK = 50

RepoChunk = list[dict]


def chunk_repos(repos: list[dict], max_per_chunk: int = REPOS_PER_PACK) -> list[RepoChunk]:
    """Decoupe la liste de repos en chunks de taille max_per_chunk."""
    return [repos[i:i + max_per_chunk] for i in range(0, len(repos), max_per_chunk)]


def estimate_bundle_size_mb(repos: list[dict]) -> float:
    """Estimation conservative : 500 Ko/repo en moyenne."""
    return len(repos) * 0.5


def stream_xml_bundle(repos: RepoChunk, chunk_idx: int) -> Iterator[str]:
    """Generateur XML — emet les elements un par un sans charger tout en RAM."""
    yield '<?xml version="1.0" encoding="UTF-8"?>\n'
    yield '<bundle chunk="{}" repos="{}">\n'.format(chunk_idx, len(repos))
    yield '  <metadata>\n'
    yield '    <generated_by>gerivdb-repomix</generated_by>\n'
    yield '    <urbanverse_version>5.0.0</urbanverse_version>\n'
    yield '    <intent_hash>0xREPOMIX_INTENT_20260611</intent_hash>\n'
    yield '  </metadata>\n'

    for repo in repos:
        name = repo.get("name", "unknown")
        layer = repo.get("layer", "UNKNOWN")
        tier = repo.get("tier", "P3")
        yield (
            '  <repo name="{}">\n'
            '    <strate>{}</strate>\n'
            '    <tier>{}</tier>\n'
            '    <phi_cps>4.559</phi_cps>\n'
            '    <vague_deployee>11</vague_deployee>\n'
            '    <!-- files omitted in index bundle -->\n'
            '  </repo>\n'.format(name, layer, tier)
        )

    yield '</bundle>\n'


def generate_bundles(
    repos: list[dict],
    output_dir: Path,
    chunk_size_mb: float = CHUNK_SIZE_MB,
    max_per_chunk: int = REPOS_PER_PACK,
    tier_filter: str = "ALL",
) -> dict:
    """
    Point d'entree principal.
    Retourne un manifeste JSON decrivant les chunks produits.
    """
    t0 = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Filtre tier
    if tier_filter != "ALL":
        repos = [r for r in repos if r.get("tier") == tier_filter]

    chunks = chunk_repos(repos, max_per_chunk)
    manifest: dict = {
        "version": "2.0",
        "total_repos": len(repos),
        "tier_filter": tier_filter,
        "chunks": [],
    }

    for idx, chunk in enumerate(chunks, start=1):
        fname = output_dir / "bundle_{:03d}.xml".format(idx)
        with fname.open("w", encoding="utf-8") as fh:
            for fragment in stream_xml_bundle(chunk, idx):
                fh.write(fragment)

        size_mb = fname.stat().st_size / (1024 * 1024)
        manifest["chunks"].append({
            "index": idx,
            "file": fname.name,
            "repos": len(chunk),
            "size_mb": round(size_mb, 3),
        })
        print("  OK Chunk {}/{} — {} repos — {:.2f} Mo".format(
            idx, len(chunks), len(chunk), size_mb))

    elapsed = time.perf_counter() - t0
    manifest["elapsed_s"] = round(elapsed, 2)
    manifest["kpi_ok"] = elapsed < 300.0  # KPI: < 5min

    # Manifeste JSON
    manifest_path = output_dir / "bundle_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("\n{} chunks — {} repos — {:.1f}s".format(len(chunks), len(repos), elapsed))
    if not manifest["kpi_ok"]:
        print("WARN: KPI FAILED: bundle > 5 min")

    return manifest


def main() -> None:
    import argparse
    import yaml as _yaml

    parser = argparse.ArgumentParser(description="bundle_corpus v2 — chunking 190 repos")
    parser.add_argument("--yaml", type=Path,
                        default=Path("data/known_repositories_190.yaml"))
    parser.add_argument("--output", type=Path,
                        default=Path("data/bundles/"))
    parser.add_argument("--tier", choices=["P0", "P1", "P2", "P3", "ALL"], default="ALL")
    parser.add_argument("--chunk-size-mb", type=float, default=CHUNK_SIZE_MB)
    args = parser.parse_args()

    raw = _yaml.safe_load(args.yaml.read_text(encoding="utf-8"))

    # Support both v2 (section-based) and v3 (flat repositories) formats
    if "repositories" in raw:
        repos = raw["repositories"]
    else:
        repos = []
        for section in ["P0_CONSTITUTIONAL", "P1_STRATEGIC", "P2_SUPPORT", "P3_DORMANT"]:
            repos.extend(raw.get(section, []))

    # Resolve tier for each repo
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from repomix.adapters.known_repos_adapter import KnownReposAdapterV3, TIER_MAP
    for repo in repos:
        if "tier" not in repo:
            layer = repo.get("layer", "UNKNOWN")
            repo["tier"] = "P3"
            for tier, layers in TIER_MAP.items():
                if layer in layers:
                    repo["tier"] = tier
                    break

    generate_bundles(repos, args.output, args.chunk_size_mb, REPOS_PER_PACK, args.tier)


if __name__ == "__main__":
    main()
