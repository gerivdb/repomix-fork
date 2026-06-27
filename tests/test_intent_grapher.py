"""Tests EPIC-12 P0 — RepoScanner mode local"""
import json
import tempfile
from pathlib import Path

import pytest

from scripts.intent_grapher.repo_scanner import RepoScanner, PIPELINE_LAYERS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_repo(tmp_path: Path) -> Path:
    """Repo vide — aucune couche pipeline."""
    return tmp_path


@pytest.fixture
def partial_repo(tmp_path: Path) -> Path:
    """Repo avec intents + PRD seulement (score attendu = 2.0)."""
    (tmp_path / "intents").mkdir()
    (tmp_path / "intents" / "INT-001-test.md").write_text(
        "# Intent\n> **IntentHash**: `0xINT_TEST`\n"
    )
    (tmp_path / "PRD").mkdir()
    (tmp_path / "PRD" / "EPIC-001.md").write_text(
        "# EPIC-001\n> **IntentHash**: `0xEPIC_TEST`\n"
    )
    return tmp_path


@pytest.fixture
def full_repo(tmp_path: Path) -> Path:
    """Repo avec toutes les couches remplies (score attendu = 5.0)."""
    for layer_dir in ["intents", "PRD", "EPICS", "ADR", ".github/ISSUE_TEMPLATE"]:
        d = tmp_path / layer_dir
        d.mkdir(parents=True, exist_ok=True)
        (d / "sample.md").write_text("# Sample\n> **IntentHash**: `0xTEST`\n")
    return tmp_path


# ---------------------------------------------------------------------------
# Tests — mode local
# ---------------------------------------------------------------------------

class TestRepoScannerLocal:

    def test_empty_repo_score_zero(self, empty_repo):
        scanner = RepoScanner(str(empty_repo), mode="local", base_path=empty_repo)
        result = scanner.scan()
        assert result.global_score == 0.0
        assert all(not lr.present for lr in result.layers.values())

    def test_partial_repo_score_two(self, partial_repo):
        scanner = RepoScanner(str(partial_repo), mode="local", base_path=partial_repo)
        result = scanner.scan()
        assert result.layers["intents"].present is True
        assert result.layers["intents"].has_intent_hash is True
        assert result.layers["prd"].present is True
        assert result.layers["epics"].present is False
        assert result.layers["adr"].present is False
        # Score = 1.0 (intents) + 1.0 (prd) = 2.0
        assert result.global_score == pytest.approx(2.0, abs=0.1)

    def test_full_repo_score_five(self, full_repo):
        scanner = RepoScanner(str(full_repo), mode="local", base_path=full_repo)
        result = scanner.scan()
        assert result.global_score == pytest.approx(5.0, abs=0.1)
        assert all(lr.present for lr in result.layers.values())

    def test_gitkeep_not_counted(self, tmp_path):
        (tmp_path / "intents").mkdir()
        (tmp_path / "intents" / ".gitkeep").write_text("")
        scanner = RepoScanner(str(tmp_path), mode="local", base_path=tmp_path)
        result = scanner.scan()
        # .gitkeep seul → file_count == 0 → score == 0
        assert result.layers["intents"].file_count == 0
        assert result.layers["intents"].score == 0.0

    def test_to_dict_structure(self, partial_repo):
        scanner = RepoScanner(str(partial_repo), mode="local", base_path=partial_repo)
        result = scanner.scan()
        d = result.to_dict()
        assert "repo" in d
        assert "global_score" in d
        assert "layers" in d
        for layer in PIPELINE_LAYERS:
            assert layer in d["layers"]
            layer_d = d["layers"][layer]
            assert "present" in layer_d
            assert "score" in layer_d
            assert "file_count" in layer_d

    def test_pipeline_index_detected(self, partial_repo):
        (partial_repo / "PIPELINE_INDEX.md").write_text("# PIPELINE_INDEX\n")
        scanner = RepoScanner(str(partial_repo), mode="local", base_path=partial_repo)
        result = scanner.scan()
        assert result.pipeline_index_present is True
