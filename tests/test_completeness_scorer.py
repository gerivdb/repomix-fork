"""Tests EPIC-12 P3 — CompletenessScorer"""
from pathlib import Path

import pytest

from scripts.intent_grapher.repo_scanner import RepoScanner
from scripts.intent_grapher.intent_vectorizer import IntentVectorizer
from scripts.intent_grapher.pipeline_dag_builder import PipelineDAGBuilder
from scripts.intent_grapher.completeness_scorer import (
    CompletenessScorer,
    MAX_SCORE,
    MATURITY_LABELS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

INTENT_MD = """
# INTENT-1211
> **IntentHash**: `0xINT_TEST`
```yaml
intent_id: INT-1211
dimension_principale: routing_intelligence
source_pain: dispatch_naif
cible: enzyme_router
contrainte_hard: retrocompat
resultat_attendu: router_ok
```
"""


@pytest.fixture
def repo_intents_prd(tmp_path):
    """Score attendu ~2.0 : intents (1.0) + prd (1.0)."""
    (tmp_path / "intents").mkdir()
    (tmp_path / "intents" / "INT-1211.md").write_text(INTENT_MD, encoding="utf-8")
    (tmp_path / "PRD").mkdir()
    (tmp_path / "PRD" / "EPIC-1211.md").write_text(
        "# EPIC-1211\n> **IntentHash**: `0xEPIC`\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def repo_full_pipeline(tmp_path):
    """Score attendu ~4.0+ : intents + PRD + EPICS + ADR (issues absentes)."""
    (tmp_path / "intents").mkdir()
    (tmp_path / "intents" / "INT-1211.md").write_text(INTENT_MD, encoding="utf-8")
    (tmp_path / "PRD").mkdir()
    (tmp_path / "PRD" / "EPIC-1211.md").write_text(
        "# EPIC\n> **IntentHash**: `0xEPIC`\n", encoding="utf-8"
    )
    (tmp_path / "EPICS").mkdir()
    (tmp_path / "EPICS" / "EPIC-01.md").write_text("# EPIC-01\n", encoding="utf-8")
    (tmp_path / "ADR").mkdir()
    (tmp_path / "ADR" / "ADR-1211.md").write_text("# ADR-1211\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def repo_scaffold_only(tmp_path):
    """ADR/ et EPICS/ scaffolds vides — scores partiels."""
    (tmp_path / "intents").mkdir()
    (tmp_path / "intents" / "INT-1211.md").write_text(INTENT_MD, encoding="utf-8")
    (tmp_path / "PRD").mkdir()
    (tmp_path / "PRD" / "EPIC-1211.md").write_text(
        "# EPIC\n> **IntentHash**: `0xEPIC`\n", encoding="utf-8"
    )
    (tmp_path / "ADR").mkdir()
    (tmp_path / "ADR" / ".gitkeep").write_text("", encoding="utf-8")
    (tmp_path / "ADR" / "README.md").write_text("# ADR README\n", encoding="utf-8")
    return tmp_path


def _scan(p, name="test/repo"):
    return RepoScanner(name, mode="local", base_path=p).scan()


def _dag(p, scan, name="test/repo"):
    intents_dir = p / "intents"
    iv = IntentVectorizer(name, intents_dir).vectorize() if intents_dir.exists() else None
    return PipelineDAGBuilder(name, scan, iv).build()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCompletenessScorer:

    def test_intents_prd_score_approx_two(self, repo_intents_prd):
        scan = _scan(repo_intents_prd)
        scorer = CompletenessScorer("test/repo", scan)
        report = scorer.score()
        assert 1.8 <= report.global_score <= 2.2

    def test_full_pipeline_score_above_three(self, repo_full_pipeline):
        scan = _scan(repo_full_pipeline)
        scorer = CompletenessScorer("test/repo", scan)
        report = scorer.score()
        assert report.global_score >= 3.0

    def test_scaffold_only_adr_partial(self, repo_scaffold_only):
        scan = _scan(repo_scaffold_only)
        scorer = CompletenessScorer("test/repo", scan)
        report = scorer.score()
        # ADR présent mais scaffold uniquement → score < 1.0
        assert report.layer_scores["adr"].raw_score < 1.0
        assert report.layer_scores["adr"].raw_score > 0.0

    def test_maturity_label_formalise(self, repo_intents_prd):
        scan = _scan(repo_intents_prd)
        scorer = CompletenessScorer("test/repo", scan)
        report = scorer.score()
        assert report.maturity_label in ["Formalisé", "Initialisé", "Structuré"]

    def test_gap_summary_populated(self, repo_intents_prd):
        scan = _scan(repo_intents_prd)
        dag = _dag(repo_intents_prd, scan)
        scorer = CompletenessScorer("test/repo", scan, dag)
        report = scorer.score()
        assert len(report.gap_summary) >= 1

    def test_markdown_report_structure(self, repo_intents_prd):
        scan = _scan(repo_intents_prd)
        scorer = CompletenessScorer("test/repo", scan)
        report = scorer.score()
        md = report.to_markdown()
        assert "# Completeness Report" in md
        assert "Score global" in md
        assert "intents" in md
        assert "prd" in md
        assert "CONFORME_NEXUS" in md

    def test_score_to_files(self, repo_intents_prd, tmp_path):
        scan = _scan(repo_intents_prd)
        scorer = CompletenessScorer("test/repo", scan)
        out = tmp_path / "out"
        scorer.score_to_files(out)
        assert (out / "completeness_score.json").exists()
        assert (out / "completeness_report.md").exists()

    def test_to_dict_structure(self, repo_intents_prd):
        scan = _scan(repo_intents_prd)
        scorer = CompletenessScorer("test/repo", scan)
        d = scorer.score().to_dict()
        assert "global_score" in d
        assert "maturity" in d
        assert "layers" in d
        assert "gaps" in d
        for layer in ["intents", "prd", "epics", "adr", "issues"]:
            assert layer in d["layers"]

    def test_max_score_constant(self):
        assert MAX_SCORE == 5.0
