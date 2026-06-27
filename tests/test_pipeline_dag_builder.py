"""Tests EPIC-12 P2 — PipelineDAGBuilder"""
from pathlib import Path

import pytest

from scripts.intent_grapher.repo_scanner import RepoScanner, ScanResult, LayerResult
from scripts.intent_grapher.intent_vectorizer import IntentVectorizer
from scripts.intent_grapher.pipeline_dag_builder import (
    PipelineDAGBuilder,
    DAGNode,
    LAYER_ORDER,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

INTENT_CONTENT = """
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

- `INT-1211` → `EPIC-1211`
"""


@pytest.fixture
def full_local_repo(tmp_path: Path) -> Path:
    """Repo avec intents + PRD + ADR (pas d'issues)."""
    # intents
    (tmp_path / "intents").mkdir()
    (tmp_path / "intents" / "INT-1211-moe.md").write_text(INTENT_CONTENT, encoding="utf-8")

    # PRD
    (tmp_path / "PRD").mkdir()
    (tmp_path / "PRD" / "EPIC-1211-moe.md").write_text(
        "# EPIC-1211\n> **IntentHash**: `0xEPIC`\n", encoding="utf-8"
    )

    # ADR
    (tmp_path / "ADR").mkdir()
    (tmp_path / "ADR" / "ADR-1211-choice.md").write_text(
        "# ADR-1211\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def gap_repo(tmp_path: Path) -> Path:
    """Repo intents + PRD seulement — ADR manquant → gap attendu."""
    (tmp_path / "intents").mkdir()
    (tmp_path / "intents" / "INT-1212-dag.md").write_text(
        "# INTENT-1212\n```yaml\nintent_id: INT-1212\ndimension_principale: semantic_depth\n```\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD").mkdir()
    (tmp_path / "PRD" / "EPIC-1212-dag.md").write_text(
        "# EPIC-1212\n", encoding="utf-8"
    )
    return tmp_path


def _make_scan(repo_path: Path, repo_name: str = "test/repo") -> ScanResult:
    scanner = RepoScanner(repo_name, mode="local", base_path=repo_path)
    return scanner.scan()


def _make_iv(repo_path: Path, repo_name: str = "test/repo"):
    intents_dir = repo_path / "intents"
    if not intents_dir.exists():
        return None
    return IntentVectorizer(repo=repo_name, intents_dir=intents_dir).vectorize()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPipelineDAGBuilder:

    def test_full_repo_nodes_present(self, full_local_repo):
        scan = _make_scan(full_local_repo)
        iv = _make_iv(full_local_repo)
        builder = PipelineDAGBuilder("test/repo", scan, iv)
        dag = builder.build()
        layers = {n.layer for n in dag.nodes if not n.gap}
        assert "intent" in layers
        assert "prd" in layers
        assert "adr" in layers

    def test_intent_epic_edge_exists(self, full_local_repo):
        scan = _make_scan(full_local_repo)
        iv = _make_iv(full_local_repo)
        dag = PipelineDAGBuilder("test/repo", scan, iv).build()
        derives_edges = [e for e in dag.edges if e.edge_type == "derives"]
        assert len(derives_edges) >= 1
        assert derives_edges[0].from_id == "INT-1211"
        assert derives_edges[0].to_id == "EPIC-1211"

    def test_epic_adr_edge_exists(self, full_local_repo):
        scan = _make_scan(full_local_repo)
        iv = _make_iv(full_local_repo)
        dag = PipelineDAGBuilder("test/repo", scan, iv).build()
        requires_edges = [e for e in dag.edges if e.edge_type == "requires"]
        assert len(requires_edges) >= 1
        assert not requires_edges[0].gap

    def test_gap_detected_when_adr_missing(self, gap_repo):
        scan = _make_scan(gap_repo)
        iv = _make_iv(gap_repo)
        dag = PipelineDAGBuilder("test/repo", scan, iv).build()
        gap_nodes = [n for n in dag.nodes if n.gap]
        assert len(gap_nodes) >= 1
        assert any(n.layer == "adr" for n in gap_nodes)

    def test_gap_adr_edge_is_gap(self, gap_repo):
        scan = _make_scan(gap_repo)
        iv = _make_iv(gap_repo)
        dag = PipelineDAGBuilder("test/repo", scan, iv).build()
        gap_edges = [e for e in dag.edges if e.gap]
        assert len(gap_edges) >= 1
        assert gap_edges[0].edge_type == "requires"

    def test_gaps_record_populated(self, gap_repo):
        scan = _make_scan(gap_repo)
        iv = _make_iv(gap_repo)
        dag = PipelineDAGBuilder("test/repo", scan, iv).build()
        assert len(dag.gaps) >= 1
        gap_layers = [g.layer for g in dag.gaps]
        assert "adr" in gap_layers or "issue" in gap_layers

    def test_summary_counts(self, full_local_repo):
        scan = _make_scan(full_local_repo)
        iv = _make_iv(full_local_repo)
        dag = PipelineDAGBuilder("test/repo", scan, iv).build()
        d = dag.to_dict()
        assert d["summary"]["nodes_total"] >= 3
        assert d["summary"]["edges_total"] >= 2

    def test_mermaid_output(self, full_local_repo):
        scan = _make_scan(full_local_repo)
        iv = _make_iv(full_local_repo)
        dag = PipelineDAGBuilder("test/repo", scan, iv).build()
        mmd = dag.mermaid()
        assert mmd.startswith("flowchart TD")
        assert "INT-1211" in mmd
        assert "EPIC-1211" in mmd
        assert "-->" in mmd or "-.-" in mmd

    def test_build_to_file(self, full_local_repo, tmp_path):
        scan = _make_scan(full_local_repo)
        iv = _make_iv(full_local_repo)
        out = tmp_path / "out" / "pipeline_dag.json"
        dag = PipelineDAGBuilder("test/repo", scan, iv).build_to_file(out)
        import json
        data = json.loads(out.read_text())
        assert "nodes" in data
        assert "edges" in data
        assert "gaps" in data
        assert "summary" in data
