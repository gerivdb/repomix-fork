"""CLI field — EPIC-13 P3

Orchestre le pipeline EPIC-13 complet :
  field crystallize <path>       — cristallise une vibe
  field gate <path> --adr <adr>  — évalue la cohérence
  field project <dir>            — projette le metacluster
  field roadmap <dir>            — roadmap émergente complète

Usage :
  python -m scripts.intent_field.cli_field roadmap ./intents-dir --output ./reports
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import click
    _CLICK = True
except ImportError:
    _CLICK = False

from .vibe_crystallizer import VibeCrystallizer
from .coherence_gate import CoherenceGate
from .metacluster_projector import MetaClusterProjector
from .emergent_roadmap import EmergentRoadmapBuilder


def _load_gravity(adr_paths: list[Path]) -> list:
    gate = CoherenceGate()
    return gate.load_field_documents(adr_paths) if adr_paths else []


def _crystallize_dir(directory: Path) -> list[tuple[str, object]]:
    vc = VibeCrystallizer()
    inputs: list[tuple[str, object]] = []
    for md in sorted(directory.rglob("*.md")):
        if md.name.startswith("README") or md.name == ".gitkeep":
            continue
        draft = vc.crystallize(md)
        repo = md.parent.name if md.parent != directory else directory.name
        inputs.append((repo, draft))
    return inputs


if _CLICK:
    @click.group()
    def cli():
        """intent-field — EPIC-13 pipeline"""
        pass

    @cli.command()
    @click.argument("path", type=click.Path(exists=True))
    @click.option("--output", "-o", default=None, help="Fichier JSON de sortie")
    def crystallize(path: str, output: str | None):
        """Cristallise une vibe .md → IntentDraft JSON."""
        p = Path(path)
        vc = VibeCrystallizer()
        draft = vc.crystallize(p)
        data = json.dumps(draft.to_dict(), indent=2, ensure_ascii=False)
        if output:
            Path(output).write_text(data, encoding="utf-8")
            click.echo(f"IntentDraft → {output}")
        else:
            click.echo(data)
        icon = "✅" if draft.ratification_ready else "⚠️"
        click.echo(f"\n{icon} cristallisation={draft.crystallization_score:.2f}  parle_dominant={draft.dominant_spoke}  ready={draft.ratification_ready}")

    @cli.command()
    @click.argument("path", type=click.Path(exists=True))
    @click.option("--adr", "adr_paths", multiple=True, type=click.Path(exists=True), help="Chemin(s) ADR .md")
    @click.option("--epic", "epic_paths", multiple=True, type=click.Path(exists=True), help="Chemin(s) EPIC .md")
    @click.option("--output", "-o", default=None, help="Fichier JSON de sortie")
    def gate(path: str, adr_paths, epic_paths, output: str | None):
        """Evalue la cohérence d'une vibe face aux masses du champ."""
        vc = VibeCrystallizer()
        cg = CoherenceGate()
        draft = vc.crystallize(Path(path))
        adrs = cg.load_field_documents([Path(p) for p in adr_paths])
        epics = cg.load_field_documents([Path(p) for p in epic_paths])
        score = cg.evaluate(draft, adrs, epics, [])
        data = json.dumps(score.to_dict(), indent=2, ensure_ascii=False)
        if output:
            Path(output).write_text(data, encoding="utf-8")
            click.echo(f"CoherenceScore → {output}")
        else:
            click.echo(data)
        verdict_icon = {"✅": "RATIFY", "⚠️": "REVISE", "❌": "REJECT"}
        icon = "✅" if score.verdict == "RATIFY" else ("❌" if score.verdict == "REJECT" else "⚠️")
        click.echo(f"\n{icon} verdict={score.verdict}  cohérence={score.coherence_score:.2f}  φ-CPS={score.phi_cps_gate}")

    @cli.command()
    @click.argument("directory", type=click.Path(exists=True))
    @click.option("--adr", "adr_paths", multiple=True, type=click.Path(exists=True))
    @click.option("--clusters", "-k", default=5, help="Nombre de clusters")
    @click.option("--output", "-o", default=None)
    def project(directory: str, adr_paths, clusters: int, output: str | None):
        """Projette les intents du dossier dans l'espace 6D."""
        inputs = _crystallize_dir(Path(directory))
        gravity = _load_gravity([Path(p) for p in adr_paths])
        projector = MetaClusterProjector(n_clusters=clusters)
        cluster_map = projector.project(inputs, gravity_docs=gravity)
        click.echo(cluster_map.summary())
        if output:
            Path(output).write_text(
                json.dumps(cluster_map.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            click.echo(f"\nMetaClusterMap → {output}")

    @cli.command()
    @click.argument("directory", type=click.Path(exists=True))
    @click.option("--adr", "adr_paths", multiple=True, type=click.Path(exists=True))
    @click.option("--clusters", "-k", default=5)
    @click.option("--output", "-o", default="./field-roadmap")
    def roadmap(directory: str, adr_paths, clusters: int, output: str):
        """Roadmap émergente complète depuis un dossier d'intents."""
        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        inputs = _crystallize_dir(Path(directory))
        gravity = _load_gravity([Path(p) for p in adr_paths])
        projector = MetaClusterProjector(n_clusters=clusters)
        cluster_map = projector.project(inputs, gravity_docs=gravity)
        rm = EmergentRoadmapBuilder().build(cluster_map)

        (out_dir / "cluster_map.json").write_text(
            json.dumps(cluster_map.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (out_dir / "roadmap.json").write_text(
            json.dumps(rm.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (out_dir / "roadmap.mmd").write_text(rm.mermaid_roadmap, encoding="utf-8")
        reading_md = f"# Lecture du champ\n\n{rm.coherence_reading}\n\n{rm.mermaid_roadmap}\n"
        (out_dir / "roadmap.md").write_text(reading_md, encoding="utf-8")

        click.echo(f"\n{rm.coherence_reading}")
        click.echo(f"\n\ud83d\udcc1 {out_dir}/")
        click.echo(f"   cluster_map.json | roadmap.json | roadmap.mmd | roadmap.md")
        click.echo(f"\n⏳ Timeline :")
        for cohort in ("now", "next", "later"):
            items = rm.timeline.get(cohort, [])
            icon = {"now": "🔴", "next": "🟡", "later": "⚪"}.get(cohort, "")
            click.echo(f"  {icon} {cohort.upper():6} : {', '.join(items) or '(vide)'}")

    if __name__ == "__main__":
        cli()
