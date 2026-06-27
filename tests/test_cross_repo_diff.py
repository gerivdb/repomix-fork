"""Tests EPIC-12 P4 — CrossRepoDiff"""
from pathlib import Path

import pytest

from scripts.intent_grapher.repo_scanner import RepoScanner
from scripts.intent_grapher.intent_vectorizer import IntentVectorizer
from scripts.intent_grapher.pipeline_dag_builder import PipelineDAGBuilder
from scripts.intent_grapher.completeness_scorer import CompletenessScorer
from scripts.intent_grapher.cross_repo_diff import CrossRepoDiff, RepoDiffEntry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

INT_A = """
# INTENT-1211
> **IntentHash**: `0xINT_A`
```yaml
intent_id: INT-1211
dimension_principale: routing_intelligence
source_pain: dispatch_naif
cible: enzyme_router
contrainte_hard: retrocompat
resultat_attendu: router_ok
```
"""

INT_B = """
# INTENT-1212
> **IntentHash**: `0xINT_B`
```yaml
intent_id: INT-1212
dimension_principale: semantic_depth
source_pain: truncation
cible: dag_multipass
contrainte_hard: max_confidence_0.30
resultat_attendu: causal_edges
```
"""


def _make_repo(tmp_path: Path, name: str, intent_content: str, with_adr: bool = False) -> Path:
    d = tmp_path / name
    d.mkdir()
    (d / "intents").mkdir()
    (d / "intents" / f"INT-{'1211' if 'A' in name else '1212'}.md").write_text(
        intent_content, encoding="utf-8"
    )
    (d / "PRD").mkdir()
    (d / "PRD" / f"EPIC-{'1211' if 'A' in name else '1212'}.md").write_text(
        "# EPIC\n> **IntentHash**: `0xEPIC`\n", encoding="utf-8"
    )
    if with_adr:
        (d / "ADR").mkdir()
        (d / "ADR" / "ADR-1211.md").write_text("# ADR-1211\n", encoding="utf-8")
    return d


def _entry(repo_path: Path, repo_name: str) -> RepoDiffEntry:
    scan = RepoScanner(repo_name, mode="local", base_path=repo_path).scan()
    intents_dir = repo_path / "intents"
    iv = IntentVectorizer(repo_name, intents_dir).vectorize()
    dag = PipelineDAGBuilder(repo_name, scan, iv).build()
    completeness = CompletenessScorer(repo_name, scan, dag).score()
    return RepoDiffEntry(
        repo=repo_name,
        completeness=completeness,
        intent_vector=iv,
        dag=dag,
    )


@pytest.fixture
def two_repos(tmp_path):
    """Repo A (avec ADR) vs Repo B (sans ADR)."""
    path_a = _make_repo(tmp_path, "repo-A", INT_A, with_adr=True)
    path_b = _make_repo(tmp_path, "repo-B", INT_B, with_adr=False)
    return [
        _entry(path_a, "test/repo-A"),
        _entry(path_b, "test/repo-B"),
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCrossRepoDiff:

    def test_requires_at_least_two_repos(self, tmp_path):
        path_a = _make_repo(tmp_path, "solo", INT_A)
        entry = _entry(path_a, "test/solo")
        with pytest.raises(ValueError, match="au moins 2"):
            CrossRepoDiff([entry])

    def test_diff_returns_result(self, two_repos):
        result = CrossRepoDiff(two_repos).diff()
        assert len(result.repos) == 2
        assert result.generated_at

    def test_completeness_ranking_ordered(self, two_repos):
        result = CrossRepoDiff(two_repos).diff()
        scores = [e["score"] for e in result.completeness_ranking]
        assert scores == sorted(scores, reverse=True)
        # Repo A (avec ADR) doit scorer plus haut
        assert result.completeness_ranking[0]["repo"] == "test/repo-A"

    def test_dimension_union_contains_both(self, two_repos):
        result = CrossRepoDiff(two_repos).diff()
        assert "routing_intelligence" in result.dimension_union
        assert "semantic_depth" in result.dimension_union

    def test_diff_matrix_dimensions(self, two_repos):
        result = CrossRepoDiff(two_repos).diff()
        dims = result.diff_matrix.get("dimensions", {})
        # routing_intelligence : présent A, absent B
        routing = dims.get("routing_intelligence", {})
        assert routing.get("test/repo-A") == "✅"
        assert routing.get("test/repo-B") == "❌"

    def test_spoke_divergence_keys(self, two_repos):
        result = CrossRepoDiff(two_repos).diff()
        assert len(result.spoke_divergence) > 0
        for spoke_scores in result.spoke_divergence.values():
            assert "test/repo-A" in spoke_scores or "test/repo-B" in spoke_scores

    def test_divergences_detected(self, two_repos):
        result = CrossRepoDiff(two_repos).diff()
        # Au moins 1 divergence (score gap ou intent gap ou missing layer)
        assert len(result.divergences) >= 1

    def test_markdown_output(self, two_repos):
        result = CrossRepoDiff(two_repos).diff()
        md = result.to_markdown()
        assert "# Cross-Repo Diff" in md
        assert "test/repo-A" in md
        assert "test/repo-B" in md
        assert "CONFORME_NEXUS" in md

    def test_diff_to_files(self, two_repos, tmp_path):
        out = tmp_path / "diff_out"
        CrossRepoDiff(two_repos).diff_to_files(out)
        assert (out / "cross_repo_diff.json").exists()
        assert (out / "cross_repo_diff.md").exists()
