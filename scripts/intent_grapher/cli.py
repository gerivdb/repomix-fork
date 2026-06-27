"""CLI INTENT-GRAPHER — EPIC-12 P0 (stub)

Usage:
    python -m scripts.intent_grapher.cli --repo gerivdb/Gitnote [--mode remote|local] [--output DIR]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import click
except ImportError:
    print("[intent-grapher] 'click' requis : pip install click", file=sys.stderr)
    sys.exit(1)

from .repo_scanner import RepoScanner


@click.group()
def cli():
    """INTENT-GRAPHER — Vectorisation du thought commit pipeline (EPIC-12)"""
    pass


@cli.command("scan")
@click.option("--repo", required=True, help="owner/repo ou chemin local")
@click.option(
    "--mode",
    default="remote",
    type=click.Choice(["local", "remote"]),
    show_default=True,
    help="Mode de lecture du repo",
)
@click.option("--output", default=None, help="Dossier de sortie pour les JSON")
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "table", "llm-pack"]), show_default=True)
def scan(repo: str, mode: str, output: str | None, fmt: str):
    """Scanne un repo et affiche le score de complétude du pipeline."""
    click.echo(f"[intent-grapher] Scanning {repo!r} (mode={mode})...")

    scanner = RepoScanner(repo=repo, mode=mode)
    result = scanner.scan()
    data = result.to_dict()

    if fmt == "json":
        output_str = json.dumps(data, indent=2, ensure_ascii=False)
        click.echo(output_str)
    elif fmt == "table":
        _print_table(data)
    elif fmt == "llm-pack":
        _print_llm_pack(data)

    if output:
        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "scan_result.json"
        out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        click.echo(f"[intent-grapher] → {out_file}")


@cli.command("diff")
@click.option("--repos", required=True, help="Liste CSV : gerivdb/Gitnote,gerivdb/KRONOS")
@click.option("--mode", default="remote", type=click.Choice(["local", "remote"]), show_default=True)
def diff(repos: str, mode: str):
    """[P4] Diff transversal de plusieurs repos — non implémenté en P0."""
    click.echo("[intent-grapher] diff — disponible à partir de P4 (EPIC-12).")


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def _print_table(data: dict) -> None:
    repo = data["repo"]
    score = data["global_score"]
    pip_idx = "✅" if data["pipeline_index_present"] else "❌"
    click.echo(f"\n📁  {repo}  (PIPELINE_INDEX: {pip_idx})")
    click.echo(f"   Global score : {score:.1f} / 5.0")
    click.echo("")
    click.echo(f"   {'Couche':<12} {'Présent':<10} {'Fichiers':<10} {'IntentHash':<12} {'Score'}")
    click.echo("   " + "-" * 56)
    for layer, info in data["layers"].items():
        present = "✅" if info["present"] else "❌"
        ih = "✅" if info["has_intent_hash"] else "❌"
        click.echo(
            f"   {layer:<12} {present:<10} {info['file_count']:<10} {ih:<12} {info['score']:.2f}"
        )
    click.echo("")


def _print_llm_pack(data: dict) -> None:
    """Produit un pack sémantique lisible LLM (Markdown)."""
    lines = [
        f"# INTENT-GRAPHER — {data['repo']}",
        f"",
        f"**Score pipeline global** : {data['global_score']:.1f} / 5.0",
        f"**PIPELINE_INDEX.md** : {'présent' if data['pipeline_index_present'] else 'absent'}",
        f"",
        f"## Couches détectées",
        f"",
        f"| Couche | Présent | Fichiers | Score |",
        f"|---|:---:|:---:|:---:|",
    ]
    for layer, info in data["layers"].items():
        p = "✅" if info["present"] else "❌"
        lines.append(f"| `{layer}` | {p} | {info['file_count']} | {info['score']:.2f} |")
    lines += [
        "",
        "## Fichiers pipeline détectés",
        "",
    ]
    for layer, info in data["layers"].items():
        if info["files"]:
            lines.append(f"### `{layer}`")
            for f in info["files"]:
                lines.append(f"- `{f}`")
            lines.append("")
    click.echo("\n".join(lines))


if __name__ == "__main__":
    cli()
