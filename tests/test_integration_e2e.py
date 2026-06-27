"""Tests intégration end-to-end EPIC-12 — P0→P5

Vérifie la chaîne complète sur un repo local fictif.
"""
from pathlib import Path
import json

import pytest

from scripts.intent_grapher import (
    RepoScanner,
    IntentVectorizer,
    PipelineDAGBuilder,
    CompletenessScorer,
    CrossRepoDiff,
    LLMPack,
)
from scripts.intent_grapher.cross_repo_diff import RepoDiffEntry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

INT_FULL = """
# INTENT-1211
> **IntentHash**: `0xINT_E2E_1211`

```yaml
intent_id: INT-1211
dimension_principale: routing_intelligence
source_pain: dispatch_naif_premier_match
cible: enzyme_specialisation_par_source_type
contrainte_hard: retrocompat_commit_enzyme
resultat_attendu: router_confidence_dans_chaque_packet
```

- `INT-1211` → `EPIC-1211` → `ADR-1211`
"""

INT_B_FULL = """
# INTENT-1212
> **IntentHash**: `0xINT_E2E_1212`

```yaml
intent_id: INT-1212
dimension_principale: semantic_depth
source_pain: truncation_100chars
cible: dag_4passes
contrainte_hard: max_confidence_0.30
resultat_attendu: causal_edges_ok
```
"""


@pytest.fixture
def repo_a(tmp_path) -> tuple[Path, str]:
    """Repo A : pipeline complet avec ADR."""
    d = tmp_path / "repo_a"
    d.mkdir()
    (d / "intents").mkdir()
    (d / "intents" / "INT-1211.md").write_text(INT_FULL, encoding="utf-8")
    (d / "PRD").mkdir()
    (d / "PRD" / "EPIC-1211.md").write_text(
        "# EPIC-1211\n> **IntentHash**: `0xEPIC_1211`\n", encoding="utf-8"
    )
    (d / "ADR").mkdir()
    (d / "ADR" / "ADR-1211.md").write_text("# ADR-1211\n", encoding="utf-8")
    return d, "test/repo-A"


@pytest.fixture
def repo_b(tmp_path) -> tuple[Path, str]:
    """Repo B : intents + PRD seulement."""
    d = tmp_path / "repo_b"
    d.mkdir()
    (d / "intents").mkdir()
    (d / "intents" / "INT-1212.md").write_text(INT_B_FULL, encoding="utf-8")
    (d / "PRD").mkdir()
    (d / "PRD" / "EPIC-1212.md").write_text(
        "# EPIC-1212\n> **IntentHash**: `0xEPIC_1212`\n", encoding="utf-8"
    )
    return d, "test/repo-B"


def _full_pipeline(repo_path: Path, repo_name: str) -> RepoDiffEntry:
    scan = RepoScanner(repo_name, mode="local", base_path=repo_path).scan()
    intents_dir = repo_path / "intents"
    iv = IntentVectorizer(repo_name, intents_dir).vectorize()
    dag = PipelineDAGBuilder(repo_name, scan, iv).build()
    completeness = CompletenessScorer(repo_name, scan, dag).score()
    return RepoDiffEntry(
        repo=repo_name, completeness=completeness, intent_vector=iv, dag=dag
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestE2EPipeline:

    def test_p0_scan_result(self, repo_a):
        path, name = repo_a
        scan = RepoScanner(name, mode="local", base_path=path).scan()
        assert scan.layers["intents"].present
        assert scan.layers["prd"].present
        assert scan.layers["adr"].present

    def test_p1_intent_vector(self, repo_a):
        path, name = repo_a
        scan = RepoScanner(name, mode="local", base_path=path).scan()
        iv = IntentVectorizer(name, path / "intents").vectorize()
        assert iv.intents[0].intent_id == "INT-1211"
        assert iv.intents[0].intent_hash == "0xINT_E2E_1211"
        assert "routing_intelligence" in iv.repo_vector["dimensions"]

    def test_p2_dag_nodes_and_edges(self, repo_a):
        path, name = repo_a
        scan = RepoScanner(name, mode="local", base_path=path).scan()
        iv = IntentVectorizer(name, path / "intents").vectorize()
        dag = PipelineDAGBuilder(name, scan, iv).build()
        layers = {n.layer for n in dag.nodes if not n.gap}
        assert "intent" in layers
        assert "prd" in layers
        assert "adr" in layers
        assert len(dag.edges) >= 2

    def test_p3_completeness_score(self, repo_a):
        path, name = repo_a
        entry = _full_pipeline(path, name)
        # intent(1.0) + prd(1.0) + adr(1.0) = 3.0 minimum
        assert entry.completeness.global_score >= 3.0
        assert entry.completeness.maturity_label in ["Structuré", "Maturé", "Complet"]

    def test_p4_cross_diff_two_repos(self, repo_a, repo_b, tmp_path):
        entry_a = _full_pipeline(*repo_a)
        entry_b = _full_pipeline(*repo_b)
        result = CrossRepoDiff([entry_a, entry_b]).diff()
        assert len(result.repos) == 2
        assert result.completeness_ranking[0]["repo"] == "test/repo-A"
        assert len(result.divergences) >= 1

    def test_p5_llm_pack_content(self, repo_a):
        path, name = repo_a
        entry = _full_pipeline(path, name)
        pack = LLMPack(
            repo=name,
            completeness=entry.completeness,
            intent_vector=entry.intent_vector,
            dag=entry.dag,
        )
        content = pack.build()
        assert "# LLM-PACK" in content
        assert "routing_intelligence" in content
        assert "CONFORME_NEXUS" in content
        assert "v0.1.0-p5" in content

    def test_p5_llm_pack_write_file(self, repo_a, tmp_path):
        path, name = repo_a
        entry = _full_pipeline(path, name)
        pack = LLMPack(
            repo=name,
            completeness=entry.completeness,
            intent_vector=entry.intent_vector,
            dag=entry.dag,
        )
        out = tmp_path / "llm_pack.md"
        pack.write(out)
        assert out.exists()
        assert len(out.read_text()) > 200

    def test_full_chain_no_crash(self, repo_a, repo_b, tmp_path):
        """Smoke test : P0→P4 sans exception."""
        entry_a = _full_pipeline(*repo_a)
        entry_b = _full_pipeline(*repo_b)
        result = CrossRepoDiff([entry_a, entry_b]).diff_to_files(tmp_path / "out")
        assert (tmp_path / "out" / "cross_repo_diff.json").exists()
        data = json.loads((tmp_path / "out" / "cross_repo_diff.json").read_text())
        assert data["repos"] == ["test/repo-A", "test/repo-B"]
