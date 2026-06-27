"""LLMPack — EPIC-12 P5

Assemble un bundle context compact pour LLM à partir des outputs P0→P4.
Format : Markdown structuré, optimisé pour token budget réduit.

Sortie : llm_pack.md
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .completeness_scorer import CompletenessReport
from .intent_vectorizer import RepoIntentVector
from .pipeline_dag_builder import PipelineDAG
from .cross_repo_diff import CrossRepoDiffResult


@dataclass
class LLMPack:
    """Construit un context bundle compact pour LLM."""

    repo: str
    completeness: Optional[CompletenessReport] = None
    intent_vector: Optional[RepoIntentVector] = None
    dag: Optional[PipelineDAG] = None
    cross_diff: Optional[CrossRepoDiffResult] = None

    def build(self) -> str:
        """Retourne le bundle Markdown."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        sections: list[str] = [
            f"# LLM-PACK — `{self.repo}`",
            f"*Généré : {now} — EPIC-12 INTENT-GRAPHER v0.1.0-p5*",
            "",
        ]

        # --- Complétude ---
        if self.completeness:
            c = self.completeness
            sections += [
                "## Complétude pipeline",
                f"- **Score** : `{c.global_score:.2f}/5.0` — `{c.maturity_label}`",
                "- **Couches** :",
            ]
            for layer, ls in c.layer_scores.items():
                icon = "✅" if ls.raw_score >= 0.8 else ("⚠️" if ls.raw_score > 0 else "❌")
                sections.append(f"  - {icon} `{layer}` : {ls.raw_score:.2f} — {' / '.join(ls.notes[:1])}")
            if c.gap_summary:
                sections.append(f"- **Gaps** ({len(c.gap_summary)}) : "
                                 + ", ".join(f"`{g.split(' —')[0].strip('`- ')}`"
                                             for g in c.gap_summary[:5]))
            sections.append("")

        # --- Intent vector ---
        if self.intent_vector:
            iv = self.intent_vector
            rv = iv.repo_vector
            dominant_spokes = sorted(
                iv.ontology_spokes.items(), key=lambda x: x[1], reverse=True
            )[:3]
            sections += [
                "## Intent vector",
                f"- **Dimensions** : {', '.join(f'`{d}`' for d in rv.get('dimensions', []))}",
                f"- **Pains** : {', '.join(f'`{p}`' for p in rv.get('source_pains', []))}",
                f"- **Cibles** : {', '.join(f'`{c}`' for c in rv.get('cibles', []))}",
                f"- **Spokes dominants** : "
                + ", ".join(f"`{s}` ({v:.2f})" for s, v in dominant_spokes),
                f"- **EPICs référencés** : "
                + ", ".join(f"`EPIC-{e}`" for e in rv.get('epic_refs', [])),
                "",
            ]

        # --- DAG summary ---
        if self.dag:
            d = self.dag.to_dict()["summary"]
            sections += [
                "## Pipeline DAG",
                f"- **Noeuds réels** : {d['nodes_real']} | **Gaps** : {d['nodes_gap']}",
                f"- **Arêtes** : {d['edges_total']}",
                f"- **Couches couvertes** : {', '.join(f'`{l}`' for l in d['layers_covered'])}",
                "",
            ]
            # Mermaid compact (15 noeuds max)
            if d["nodes_total"] <= 15:
                sections.append("```mermaid")
                sections.append(self.dag.mermaid())
                sections.append("```")
                sections.append("")

        # --- Cross diff ---
        if self.cross_diff:
            cd = self.cross_diff
            sections += [
                "## Cross-repo diff",
                f"- **Repos** : {', '.join(f'`{r}`' for r in cd.repos)}",
            ]
            for entry in cd.completeness_ranking:
                sections.append(
                    f"  - `{entry['repo']}` : `{entry['score']:.2f}/5.0` ({entry['maturity']})"
                )
            if cd.divergences:
                critical = [d for d in cd.divergences if d.severity == "critical"]
                warnings = [d for d in cd.divergences if d.severity == "warning"]
                sections.append(
                    f"- **Divergences** : {len(cd.divergences)} total "
                    f"({len(critical)} critical, {len(warnings)} warning)"
                )
            sections.append("")

        sections += ["---", "*[CONFORME_NEXUS] — intent_grapher v0.1.0-p5*"]
        return "\n".join(sections)

    def write(self, output_path: Path) -> str:
        content = self.build()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        return content
