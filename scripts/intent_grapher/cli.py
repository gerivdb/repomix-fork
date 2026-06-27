"""CLI intent_grapher — EPIC-12 P5 (orchestrateur complet)

Usage:
    python -m scripts.intent_grapher.cli scan   --repo OWNER/REPO [options]
    python -m scripts.intent_grapher.cli diff   --repos A B [options]
    python -m scripts.intent_grapher.cli report --repo OWNER/REPO [options]
    python -m scripts.intent_grapher.cli llm-pack --repo OWNER/REPO [options]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import click
except ImportError:
    print("[intent_grapher] click requis : pip install click", file=sys.stderr)
    sys.exit(1)

from . import __version__
from .repo_scanner import RepoScanner
from .intent_vectorizer import IntentVectorizer
from .pipeline_dag_builder import PipelineDAGBuilder
from .completeness_scorer import CompletenessScorer
from .cross_repo_diff import CrossRepoDiff, RepoDiffEntry
from .llm_pack import LLMPack


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_entry(
    repo: str,
    mode: str,
    base_path: Path | None,
    token: str | None,
) -> RepoDiffEntry:
    """Construit un RepoDiffEntry complet (P0→P4) pour un repo."""
    scan = RepoScanner(
        repo, mode=mode, base_path=base_path, github_token=token
    ).scan()

    intents_dir = (base_path or Path(repo.split("/")[-1])) / "intents"
    iv = None
    if intents_dir.exists():
        iv = IntentVectorizer(repo, intents_dir).vectorize()

    dag = PipelineDAGBuilder(repo, scan, iv).build()
    completeness = CompletenessScorer(repo, scan, dag).score()

    return RepoDiffEntry(
        repo=repo,
        completeness=completeness,
        intent_vector=iv,
        dag=dag,
    )


def _print_table(entry: RepoDiffEntry) -> None:
    c = entry.completeness
    click.echo(f"\n📁  {entry.repo}")
    click.echo(f"   Score global : {c.global_score:.2f} / 5.0  [{c.maturity_label}]")
    click.echo(f"   {'Couche':<12} {'Score':>6}  Notes")
    click.echo("   " + "-" * 52)
    for layer, ls in c.layer_scores.items():
        bar = "█" * round(ls.raw_score * 5) + "░" * (5 - round(ls.raw_score * 5))
        note = ls.notes[0] if ls.notes else ""
        click.echo(f"   {layer:<12} {bar} {ls.raw_score:.2f}  {note}")
    if c.gap_summary:
        click.echo(f"\n   Gaps ({len(c.gap_summary)}) :")
        for gap in c.gap_summary[:6]:
            click.echo(f"     • {gap}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(__version__, prog_name="intent_grapher")
def cli():
    """INTENT-GRAPHER — EPIC-12 — Analyse de pipeline intent→issue."""


# ---- scan ----------------------------------------------------------------

@cli.command()
@click.option("--repo", required=True, help="owner/repo (ex: gerivdb/Gitnote)")
@click.option("--mode", default="remote", type=click.Choice(["local", "remote"]),
              show_default=True)
@click.option("--base-path", default=None, type=click.Path(), help="Chemin local (mode=local)")
@click.option("--token", envvar="GITHUB_TOKEN", default=None, help="GitHub token")
@click.option("--format", "fmt", default="table",
              type=click.Choice(["table", "json", "llm-pack"]), show_default=True)
@click.option("--output", "-o", default=None, type=click.Path(), help="Dossier de sortie")
def scan(repo, mode, base_path, token, fmt, output):
    """Scan un repo et affiche le score de complétude (P0→P3)."""
    base = Path(base_path) if base_path else None
    entry = _build_entry(repo, mode, base, token)

    if fmt == "table":
        _print_table(entry)

    elif fmt == "json":
        data = entry.completeness.to_dict()
        if output:
            out = Path(output)
            out.mkdir(parents=True, exist_ok=True)
            (out / "completeness_score.json").write_text(
                json.dumps(data, indent=2, ensure_ascii=False
            ), encoding="utf-8")
            click.echo(f"✅ completeness_score.json → {out}")
        else:
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))

    elif fmt == "llm-pack":
        pack = LLMPack(
            repo=repo,
            completeness=entry.completeness,
            intent_vector=entry.intent_vector,
            dag=entry.dag,
        )
        content = pack.build()
        if output:
            out = Path(output)
            pack.write(out / "llm_pack.md")
            click.echo(f"✅ llm_pack.md → {out}")
        else:
            click.echo(content)


# ---- diff ----------------------------------------------------------------

@cli.command()
@click.option("--repos", required=True, multiple=True,
              help="owner/repo (répéter : --repos A --repos B)")
@click.option("--mode", default="remote", type=click.Choice(["local", "remote"]),
              show_default=True)
@click.option("--base-path", default=None, type=click.Path())
@click.option("--token", envvar="GITHUB_TOKEN", default=None)
@click.option("--format", "fmt", default="table",
              type=click.Choice(["table", "json", "md"]), show_default=True)
@click.option("--output", "-o", default=None, type=click.Path())
def diff(repos, mode, base_path, token, fmt, output):
    """Diff transversal entre N repos (P4)."""
    if len(repos) < 2:
        click.echo("❌ diff nécessite au moins 2 repos.", err=True)
        sys.exit(1)

    entries: list[RepoDiffEntry] = []
    for repo in repos:
        base = Path(base_path) / repo.split("/")[-1] if base_path else None
        click.echo(f"🔍 Scan {repo}...", err=True)
        entries.append(_build_entry(repo, mode, base, token))

    result = CrossRepoDiff(entries).diff()

    if fmt == "table":
        click.echo("\n📊 Cross-Repo Diff")
        click.echo(f"   Repos : {', '.join(result.repos)}")
        for entry in result.completeness_ranking:
            click.echo(
                f"   {entry['repo']:<35} {entry['score']:.2f}/5.0  [{entry['maturity']}]"
            )
        if result.divergences:
            click.echo(f"\n   Divergences ({len(result.divergences)}) :")
            for div in result.divergences[:5]:
                click.echo(f"     • [{div.severity.upper()}] {div.description}")

    elif fmt == "json":
        data = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        if output:
            out = Path(output)
            CrossRepoDiff(entries).diff_to_files(out, write_md=False)
            click.echo(f"✅ cross_repo_diff.json → {out}")
        else:
            click.echo(data)

    elif fmt == "md":
        md = result.to_markdown()
        if output:
            out = Path(output)
            out.mkdir(parents=True, exist_ok=True)
            (out / "cross_repo_diff.md").write_text(md, encoding="utf-8")
            click.echo(f"✅ cross_repo_diff.md → {out}")
        else:
            click.echo(md)


# ---- report ---------------------------------------------------------------

@cli.command()
@click.option("--repo", required=True)
@click.option("--mode", default="remote", type=click.Choice(["local", "remote"]))
@click.option("--base-path", default=None, type=click.Path())
@click.option("--token", envvar="GITHUB_TOKEN", default=None)
@click.option("--output", "-o", required=True, type=click.Path())
def report(repo, mode, base_path, token, output):
    """Génère le rapport complet (JSON + MD + Mermaid + llm-pack)."""
    base = Path(base_path) if base_path else None
    entry = _build_entry(repo, mode, base, token)
    out = Path(output)

    # Completeness
    CompletenessScorer(
        repo, entry.completeness.layer_scores,  # déjà calculé
    ) if False else None  # skip re-score
    entry.completeness.to_dict()  # sécurité

    out.mkdir(parents=True, exist_ok=True)
    (out / "completeness_score.json").write_text(
        json.dumps(entry.completeness.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (out / "completeness_report.md").write_text(
        entry.completeness.to_markdown(), encoding="utf-8"
    )

    # DAG
    if entry.dag:
        (out / "pipeline_dag.json").write_text(
            json.dumps(entry.dag.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (out / "pipeline_dag.mmd").write_text(entry.dag.mermaid(), encoding="utf-8")

    # Intent vector
    if entry.intent_vector:
        (out / "intent_vector.json").write_text(
            json.dumps(entry.intent_vector.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # llm-pack
    LLMPack(
        repo=repo,
        completeness=entry.completeness,
        intent_vector=entry.intent_vector,
        dag=entry.dag,
    ).write(out / "llm_pack.md")

    click.echo(f"✅ Rapport complet généré dans : {out}")
    click.echo(f"   completeness_score.json")
    click.echo(f"   completeness_report.md")
    click.echo(f"   pipeline_dag.json")
    click.echo(f"   pipeline_dag.mmd")
    click.echo(f"   intent_vector.json")
    click.echo(f"   llm_pack.md")
    _print_table(entry)


# ---- llm-pack -------------------------------------------------------------

@cli.command(name="llm-pack")
@click.option("--repo", required=True)
@click.option("--mode", default="remote", type=click.Choice(["local", "remote"]))
@click.option("--base-path", default=None, type=click.Path())
@click.option("--token", envvar="GITHUB_TOKEN", default=None)
@click.option("--output", "-o", default=None, type=click.Path())
def llm_pack_cmd(repo, mode, base_path, token, output):
    """Génère un bundle context compact pour LLM."""
    base = Path(base_path) if base_path else None
    entry = _build_entry(repo, mode, base, token)
    pack = LLMPack(
        repo=repo,
        completeness=entry.completeness,
        intent_vector=entry.intent_vector,
        dag=entry.dag,
    )
    if output:
        path = Path(output)
        if path.is_dir() or not path.suffix:
            path = path / "llm_pack.md"
        pack.write(path)
        click.echo(f"✅ llm_pack.md → {path}")
    else:
        click.echo(pack.build())


if __name__ == "__main__":
    cli()
