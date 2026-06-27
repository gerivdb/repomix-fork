"""CompletenessScorer — EPIC-12 P3

Consolide ScanResult (P0) + PipelineDAG (P2) en un score structuré 0→5.
Produit completeness_score.json + rapport Markdown.

Score par couche (0.0 – 1.0) :
  intents  : présence (0.4) + IntentHash (0.3) + YAML front-matter (0.3)
  prd      : présence (0.4) + ≥ 1 EPIC avec IntentHash (0.6)
  epics    : présence (0.4) + ≥ 1 EPIC avec critères d’accept. (0.6)
  adr      : présence (0.3) + ≥ 1 ADR accepted (0.7)
  issues   : présence (0.5) + ≥ 1 issue liée à EPIC (0.5)

Global = somme des scores couches (0.0 – 5.0)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .repo_scanner import ScanResult
from .pipeline_dag_builder import PipelineDAG


# ---------------------------------------------------------------------------
# Pondération par couche
# ---------------------------------------------------------------------------

LAYER_WEIGHTS: dict[str, dict[str, float]] = {
    "intents": {
        "presence":     0.4,
        "intent_hash":  0.3,
        "yaml_block":   0.3,   # approxié par has_intent_hash (P0 ne lit pas YAML en remote)
    },
    "prd": {
        "presence":     0.4,
        "intent_hash":  0.6,
    },
    "epics": {
        "presence":     0.4,
        "has_content":  0.6,   # file_count > 0 et non scaffold seul
    },
    "adr": {
        "presence":     0.3,
        "has_real_adr": 0.7,   # au moins 1 ADR non-README, non-.gitkeep
    },
    "issues": {
        "presence":     0.5,
        "linked":       0.5,   # au moins 1 fichier template ou issue connue
    },
}

MAX_SCORE = float(len(LAYER_WEIGHTS))  # 5.0

# Labels de maturité
MATURITY_LABELS = [
    (0.0,  1.0,  "Vide",         "Aucune couche pipeline"),
    (1.0,  2.0,  "Initialisé",   "Signal d’intent existant"),
    (2.0,  3.0,  "Formalisé",    "Intent + PRD couverts"),
    (3.0,  4.0,  "Structuré",    "Intent + PRD + EPIC/ADR partiels"),
    (4.0,  4.75, "Maturé",       "Pipeline presque complet"),
    (4.75, 5.01, "Complet",      "Pipeline INTENT→Issue couvert"),
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class LayerScore:
    layer: str
    raw_score: float          # 0.0 – 1.0
    max_score: float = 1.0
    breakdown: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    @property
    def pct(self) -> float:
        return round(self.raw_score / self.max_score * 100, 1)

    def to_dict(self) -> dict:
        return {
            "score": round(self.raw_score, 3),
            "max": self.max_score,
            "pct": self.pct,
            "breakdown": {k: round(v, 3) for k, v in self.breakdown.items()},
            "notes": self.notes,
        }


@dataclass
class CompletenessReport:
    repo: str
    generated_at: str
    layer_scores: dict[str, LayerScore] = field(default_factory=dict)
    global_score: float = 0.0
    maturity_label: str = ""
    maturity_desc: str = ""
    gap_summary: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "repo": self.repo,
            "generated_at": self.generated_at,
            "global_score": round(self.global_score, 3),
            "max_score": MAX_SCORE,
            "maturity": {
                "label": self.maturity_label,
                "description": self.maturity_desc,
            },
            "layers": {k: v.to_dict() for k, v in self.layer_scores.items()},
            "gaps": self.gap_summary,
        }

    def to_markdown(self) -> str:
        lines = [
            f"# Completeness Report — `{self.repo}`",
            f"",
            f"**Score global** : `{self.global_score:.2f} / {MAX_SCORE:.1f}`  ",
            f"**Maturité** : `{self.maturity_label}` — {self.maturity_desc}  ",
            f"**Généré** : {self.generated_at}",
            f"",
            f"## Score par couche",
            f"",
            f"| Couche | Score | % | Notes |",
            f"|---|:---:|:---:|---|",
        ]
        icons = {
            "intents": "📌",
            "prd":     "📄",
            "epics":   "📚",
            "adr":     "⚖️",
            "issues":  "🔗",
        }
        for layer, ls in self.layer_scores.items():
            bar = self._bar(ls.raw_score)
            icon = icons.get(layer, "")
            note = " / ".join(ls.notes[:2]) if ls.notes else "—"
            lines.append(
                f"| {icon} `{layer}` | {bar} `{ls.raw_score:.2f}` | {ls.pct}% | {note} |"
            )
        if self.gap_summary:
            lines += [
                f"",
                f"## Gaps détectés ({len(self.gap_summary)})",
                f"",
            ]
            for gap in self.gap_summary:
                lines.append(f"- {gap}")
        lines += [
            f"",
            f"---",
            f"*[CONFORME_NEXUS] — EPIC-12 INTENT-GRAPHER*",
        ]
        return "\n".join(lines)

    @staticmethod
    def _bar(score: float, width: int = 5) -> str:
        filled = round(score * width)
        return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------

class CompletenessScorer:
    """Calcule le score de complétude pipeline d’un repo."""

    def __init__(
        self,
        repo: str,
        scan_result: ScanResult,
        dag: Optional[PipelineDAG] = None,
    ):
        self.repo = repo
        self.scan = scan_result
        self.dag = dag

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def score(self) -> CompletenessReport:
        now = datetime.now(timezone.utc).isoformat()
        report = CompletenessReport(repo=self.repo, generated_at=now)

        for layer in ["intents", "prd", "epics", "adr", "issues"]:
            ls = self._score_layer(layer)
            report.layer_scores[layer] = ls
            report.global_score += ls.raw_score

        report.global_score = round(report.global_score, 3)
        report.maturity_label, report.maturity_desc = self._maturity(report.global_score)
        report.gap_summary = self._build_gap_summary(report)
        return report

    def score_to_files(
        self,
        output_dir: Path,
        write_json: bool = True,
        write_md: bool = True,
    ) -> CompletenessReport:
        report = self.score()
        output_dir.mkdir(parents=True, exist_ok=True)
        if write_json:
            (output_dir / "completeness_score.json").write_text(
                json.dumps(report.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        if write_md:
            (output_dir / "completeness_report.md").write_text(
                report.to_markdown(), encoding="utf-8"
            )
        return report

    # ------------------------------------------------------------------
    # Scoring par couche
    # ------------------------------------------------------------------

    def _score_layer(self, layer: str) -> LayerScore:
        weights = LAYER_WEIGHTS.get(layer, {})
        scan_layer = self.scan.layers.get(layer)
        ls = LayerScore(layer=layer, raw_score=0.0, breakdown={})

        if not scan_layer or not scan_layer.present:
            ls.notes.append(f"Dossier {layer.upper()} absent")
            return ls

        # --- Présence ---
        ls.breakdown["presence"] = weights.get("presence", 0.0)
        ls.raw_score += ls.breakdown["presence"]

        if layer == "intents":
            ls = self._score_intents(ls, scan_layer, weights)
        elif layer == "prd":
            ls = self._score_prd(ls, scan_layer, weights)
        elif layer == "epics":
            ls = self._score_epics(ls, scan_layer, weights)
        elif layer == "adr":
            ls = self._score_adr(ls, scan_layer, weights)
        elif layer == "issues":
            ls = self._score_issues(ls, scan_layer, weights)

        ls.raw_score = min(round(ls.raw_score, 3), 1.0)
        return ls

    def _score_intents(self, ls, scan_layer, weights) -> LayerScore:
        if scan_layer.has_intent_hash:
            ls.breakdown["intent_hash"] = weights.get("intent_hash", 0.0)
            ls.raw_score += ls.breakdown["intent_hash"]
            # proxy YAML : si IntentHash présent, YAML bloc probable
            ls.breakdown["yaml_block"] = weights.get("yaml_block", 0.0)
            ls.raw_score += ls.breakdown["yaml_block"]
            ls.notes.append(f"{scan_layer.file_count} intent(s) avec IntentHash")
        else:
            ls.notes.append("Intents présents mais sans IntentHash")
        return ls

    def _score_prd(self, ls, scan_layer, weights) -> LayerScore:
        if scan_layer.has_intent_hash:
            ls.breakdown["intent_hash"] = weights.get("intent_hash", 0.0)
            ls.raw_score += ls.breakdown["intent_hash"]
            ls.notes.append(f"{scan_layer.file_count} PRD/EPIC(s) avec IntentHash")
        else:
            ls.notes.append("PRD présent sans IntentHash")
        return ls

    def _score_epics(self, ls, scan_layer, weights) -> LayerScore:
        real_files = [
            f for f in scan_layer.files
            if not f.endswith(".gitkeep") and "README" not in f
        ]
        if real_files:
            ls.breakdown["has_content"] = weights.get("has_content", 0.0)
            ls.raw_score += ls.breakdown["has_content"]
            ls.notes.append(f"{len(real_files)} EPIC(s) rédigé(s)")
        else:
            ls.notes.append("EPICS/ scaffold uniquement (vide)")
        return ls

    def _score_adr(self, ls, scan_layer, weights) -> LayerScore:
        real_adrs = [
            f for f in scan_layer.files
            if not f.endswith(".gitkeep") and "README" not in f
        ]
        if real_adrs:
            ls.breakdown["has_real_adr"] = weights.get("has_real_adr", 0.0)
            ls.raw_score += ls.breakdown["has_real_adr"]
            ls.notes.append(f"{len(real_adrs)} ADR(s) rédigé(s)")
        else:
            ls.notes.append("ADR/ scaffold uniquement (0 ADR rédigé)")
        return ls

    def _score_issues(self, ls, scan_layer, weights) -> LayerScore:
        if scan_layer.file_count > 0:
            ls.breakdown["linked"] = weights.get("linked", 0.0)
            ls.raw_score += ls.breakdown["linked"]
            ls.notes.append(f"{scan_layer.file_count} template(s) issue détecté(s)")
        else:
            ls.notes.append("Issues non liées")
        return ls

    # ------------------------------------------------------------------
    # Gap summary (depuis DAG si disponible)
    # ------------------------------------------------------------------

    def _build_gap_summary(self, report: CompletenessReport) -> list[str]:
        gaps: list[str] = []
        # Gaps depuis le DAG
        if self.dag:
            for gap in self.dag.gaps:
                gaps.append(f"`{gap.missing_id}` ({gap.layer}) — {gap.reason}")
        # Gaps depuis les scores
        for layer, ls in report.layer_scores.items():
            if ls.raw_score == 0.0:
                gaps.append(f"Couche `{layer}` absente ou vide (score 0)")
            elif ls.raw_score < 0.5:
                gaps.append(f"Couche `{layer}` partielle ({ls.pct}%)")
        return gaps

    # ------------------------------------------------------------------
    # Maturité
    # ------------------------------------------------------------------

    @staticmethod
    def _maturity(score: float) -> tuple[str, str]:
        for lo, hi, label, desc in MATURITY_LABELS:
            if lo <= score < hi:
                return label, desc
        return "Complet", "Pipeline INTENT→Issue couvert"
