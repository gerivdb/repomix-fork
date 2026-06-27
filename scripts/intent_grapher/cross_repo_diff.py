"""CrossRepoDiff — EPIC-12 P4

Diff transversal entre N repos partageant des problématiques communes.
Compare : scores de complétude, vecteurs d'intent, EPICs parents, gaps.

Sortie : cross_repo_diff.json
    {
      "repos": [...],
      "dimensions_union": [...],
      "diff_matrix": { dim: {repo: value} },
      "spoke_divergence": { spoke: { repo: score } },
      "shared_epics": [ {epic_id, repos} ],
      "completeness_ranking": [ {repo, score, maturity} ],
      "divergences": [ {type, description, repos} ]
    }
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .completeness_scorer import CompletenessReport
from .intent_vectorizer import RepoIntentVector
from .pipeline_dag_builder import PipelineDAG


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RepoDiffEntry:
    """Toutes les données d’un repo pour le diff."""
    repo: str
    completeness: Optional[CompletenessReport] = None
    intent_vector: Optional[RepoIntentVector] = None
    dag: Optional[PipelineDAG] = None


@dataclass
class DivergenceRecord:
    dtype: str          # "intent_gap" | "spoke_divergence" | "missing_layer" | "epic_only_in"
    description: str
    repos: list[str] = field(default_factory=list)
    severity: str = "info"   # "info" | "warning" | "critical"

    def to_dict(self) -> dict:
        return {
            "type": self.dtype,
            "description": self.description,
            "repos": self.repos,
            "severity": self.severity,
        }


@dataclass
class CrossRepoDiffResult:
    repos: list[str]
    generated_at: str
    diff_matrix: dict[str, dict[str, object]] = field(default_factory=dict)
    spoke_divergence: dict[str, dict[str, float]] = field(default_factory=dict)
    shared_epics: list[dict] = field(default_factory=list)
    completeness_ranking: list[dict] = field(default_factory=list)
    dimension_union: list[str] = field(default_factory=list)
    divergences: list[DivergenceRecord] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "repos": self.repos,
            "generated_at": self.generated_at,
            "dimension_union": self.dimension_union,
            "diff_matrix": self.diff_matrix,
            "spoke_divergence": {
                spoke: {repo: round(v, 3) for repo, v in scores.items()}
                for spoke, scores in self.spoke_divergence.items()
            },
            "shared_epics": self.shared_epics,
            "completeness_ranking": self.completeness_ranking,
            "divergences": [d.to_dict() for d in self.divergences],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Cross-Repo Diff — INTENT-GRAPHER",
            "",
            f"**Repos analysés** : {', '.join(f'`{r}`' for r in self.repos)}",
            f"**Généré** : {self.generated_at}",
            "",
            "## Classement de complétude",
            "",
            "| # | Repo | Score | Maturité |",
            "|---|---|:---:|---|",
        ]
        for i, entry in enumerate(self.completeness_ranking, 1):
            lines.append(
                f"| {i} | `{entry['repo']}` | "
                f"`{entry['score']:.2f}/5.0` | {entry['maturity']} |"
            )

        if self.dimension_union:
            lines += [
                "",
                "## Dimensions d’intent (union)",
                "",
                "| Dimension | " + " | ".join(f"`{r}`" for r in self.repos) + " |",
                "|---" * (len(self.repos) + 1) + "|",
            ]
            for dim in self.dimension_union:
                row = f"| `{dim}` |"
                for repo in self.repos:
                    val = self.diff_matrix.get("dimensions", {}).get(dim, {}).get(repo, "❌")
                    row += f" {val} |"
                lines.append(row)

        if self.spoke_divergence:
            lines += [
                "",
                "## Divergence ontologique (spokes)",
                "",
                "| Spoke | " + " | ".join(f"`{r}`" for r in self.repos) + " |",
                "|---" * (len(self.repos) + 1) + "|",
            ]
            for spoke, scores in self.spoke_divergence.items():
                row = f"| `{spoke}` |"
                for repo in self.repos:
                    s = scores.get(repo, 0.0)
                    bar = "█" * round(s * 5) + "░" * (5 - round(s * 5))
                    row += f" {bar} `{s:.2f}` |"
                lines.append(row)

        if self.shared_epics:
            lines += [
                "",
                "## EPICs partagés",
                "",
            ]
            for entry in self.shared_epics:
                lines.append(
                    f"- `{entry['epic_id']}` — présent dans : "
                    + ", ".join(f"`{r}`" for r in entry["repos"])
                )

        if self.divergences:
            lines += [
                "",
                f"## Divergences détectées ({len(self.divergences)})",
                "",
            ]
            icons = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴"}
            for div in self.divergences:
                icon = icons.get(div.severity, "ℹ️")
                lines.append(
                    f"- {icon} **{div.dtype}** — {div.description} "
                    f"({', '.join(div.repos)})"
                )

        lines += ["", "---", "*[CONFORME_NEXUS] — EPIC-12 INTENT-GRAPHER*"]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Differ
# ---------------------------------------------------------------------------

class CrossRepoDiff:
    """Compare N repos et produit un CrossRepoDiffResult."""

    def __init__(self, entries: list[RepoDiffEntry]):
        if len(entries) < 2:
            raise ValueError("CrossRepoDiff nécessite au moins 2 repos.")
        self.entries = entries
        self._repos = [e.repo for e in entries]

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def diff(self) -> CrossRepoDiffResult:
        now = datetime.now(timezone.utc).isoformat()
        result = CrossRepoDiffResult(repos=self._repos, generated_at=now)

        result.completeness_ranking = self._rank_completeness()
        result.dimension_union, result.diff_matrix = self._diff_dimensions()
        result.spoke_divergence = self._diff_spokes()
        result.shared_epics = self._find_shared_epics()
        result.divergences = self._detect_divergences(result)
        return result

    def diff_to_files(
        self, output_dir: Path, write_json: bool = True, write_md: bool = True
    ) -> CrossRepoDiffResult:
        result = self.diff()
        output_dir.mkdir(parents=True, exist_ok=True)
        if write_json:
            (output_dir / "cross_repo_diff.json").write_text(
                json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        if write_md:
            (output_dir / "cross_repo_diff.md").write_text(
                result.to_markdown(), encoding="utf-8"
            )
        return result

    # ------------------------------------------------------------------
    # Classement de complétude
    # ------------------------------------------------------------------

    def _rank_completeness(self) -> list[dict]:
        ranking = []
        for entry in self.entries:
            score = entry.completeness.global_score if entry.completeness else 0.0
            maturity = entry.completeness.maturity_label if entry.completeness else "Inconnu"
            ranking.append({"repo": entry.repo, "score": round(score, 3), "maturity": maturity})
        return sorted(ranking, key=lambda x: x["score"], reverse=True)

    # ------------------------------------------------------------------
    # Diff des dimensions d’intent
    # ------------------------------------------------------------------

    def _diff_dimensions(self) -> tuple[list[str], dict]:
        """Union des dimensions principales de tous les repos."""
        all_dims: set[str] = set()
        repo_dims: dict[str, set[str]] = {}

        for entry in self.entries:
            dims: set[str] = set()
            if entry.intent_vector:
                dims = set(entry.intent_vector.repo_vector.get("dimensions", []))
            repo_dims[entry.repo] = dims
            all_dims |= dims

        dim_union = sorted(all_dims)
        matrix: dict[str, dict[str, object]] = {"dimensions": {}}
        for dim in dim_union:
            matrix["dimensions"][dim] = {
                repo: ("✅" if dim in repo_dims.get(repo, set()) else "❌")
                for repo in self._repos
            }
        return dim_union, matrix

    # ------------------------------------------------------------------
    # Divergence de spokes
    # ------------------------------------------------------------------

    def _diff_spokes(self) -> dict[str, dict[str, float]]:
        """Score par spoke par repo — utile pour identifier des spécialisations."""
        spokes: dict[str, dict[str, float]] = {}
        for entry in self.entries:
            if not entry.intent_vector:
                continue
            for spoke, score in entry.intent_vector.ontology_spokes.items():
                if spoke not in spokes:
                    spokes[spoke] = {}
                spokes[spoke][entry.repo] = score
        return spokes

    # ------------------------------------------------------------------
    # EPICs partagés
    # ------------------------------------------------------------------

    def _find_shared_epics(self) -> list[dict]:
        """EPICs numériquement identiques dans ≥ 2 repos."""
        epic_repos: dict[str, list[str]] = {}
        for entry in self.entries:
            if not entry.dag:
                continue
            for node in entry.dag.nodes:
                if node.layer in ("prd", "epic") and not node.gap:
                    epic_repos.setdefault(node.id, []).append(entry.repo)
        return [
            {"epic_id": eid, "repos": repos}
            for eid, repos in epic_repos.items()
            if len(repos) >= 2
        ]

    # ------------------------------------------------------------------
    # Détection des divergences
    # ------------------------------------------------------------------

    def _detect_divergences(self, result: CrossRepoDiffResult) -> list[DivergenceRecord]:
        divs: list[DivergenceRecord] = []

        # 1. Score très différent entre repos
        scores = [e["score"] for e in result.completeness_ranking]
        if scores and (max(scores) - min(scores)) > 1.5:
            divs.append(DivergenceRecord(
                dtype="score_gap",
                description=(
                    f"Ecart de score élevé : "
                    f"{result.completeness_ranking[0]['repo']} ({max(scores):.2f}) "
                    f"vs {result.completeness_ranking[-1]['repo']} ({min(scores):.2f})"
                ),
                repos=self._repos,
                severity="warning",
            ))

        # 2. Dimensions présentes dans 1 seul repo
        for dim, repo_map in result.diff_matrix.get("dimensions", {}).items():
            present_in = [r for r, v in repo_map.items() if v == "✅"]
            if len(present_in) == 1:
                divs.append(DivergenceRecord(
                    dtype="intent_gap",
                    description=f"Dimension `{dim}` absente des autres repos",
                    repos=present_in,
                    severity="info",
                ))

        # 3. Couche absente dans certains repos
        for entry in self.entries:
            if not entry.completeness:
                continue
            for layer, ls in entry.completeness.layer_scores.items():
                if ls.raw_score == 0.0:
                    divs.append(DivergenceRecord(
                        dtype="missing_layer",
                        description=f"Couche `{layer}` absente",
                        repos=[entry.repo],
                        severity="warning" if layer in ("intents", "prd") else "info",
                    ))

        # 4. Spokes très divergents (Δ > 0.3)
        for spoke, scores_map in result.spoke_divergence.items():
            vals = list(scores_map.values())
            if len(vals) >= 2 and (max(vals) - min(vals)) > 0.3:
                high = max(scores_map, key=lambda k: scores_map[k])
                low  = min(scores_map, key=lambda k: scores_map[k])
                divs.append(DivergenceRecord(
                    dtype="spoke_divergence",
                    description=(
                        f"Spoke `{spoke}` diverge : "
                        f"`{high}` ({scores_map[high]:.2f}) vs `{low}` ({scores_map[low]:.2f})"
                    ),
                    repos=[high, low],
                    severity="info",
                ))

        return divs
