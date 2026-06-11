"""tests/unit/test_ecosystem_190.py — PRD-007 Phase D"""
import json
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "repomix"))

from adapters.known_repos_adapter import (
    KnownReposAdapterV3, TIER_MAP, EXCLUDED_STATUSES, RepoNode
)
from scripts.bundle_corpus import chunk_repos, stream_xml_bundle, generate_bundles


# ── Fixture repos de test ──────────────────────────────────────────

SAMPLE_REPOS = [
    {"name": "repo-{:03d}".format(i), "layer": "L0" if i < 5 else "L3",
     "status": "ACTIVE", "tier": "P0" if i < 5 else "P1"}
    for i in range(120)
]


# ── known_repos_adapter v3 ─────────────────────────────────────────

def test_lazy_load_not_triggered_at_init(tmp_path):
    """Le graphe n'est PAS charge a l'instanciation."""
    adapter = KnownReposAdapterV3(yaml_path=tmp_path / "fake.yaml")
    assert adapter._nodes is None


def test_tier_resolution():
    assert KnownReposAdapterV3._resolve_tier("L0") == "P0"
    assert KnownReposAdapterV3._resolve_tier("L4") == "P1"
    assert KnownReposAdapterV3._resolve_tier("L8") == "P3"
    assert KnownReposAdapterV3._resolve_tier("UNKNOWN") == "P3"


def test_excluded_statuses():
    for s in EXCLUDED_STATUSES:
        node = RepoNode("test", "L0", "P0", status=s)
        assert not node.is_active()


# ── bundle_corpus v2 — chunking ────────────────────────────────────

def test_chunk_repos_size():
    chunks = chunk_repos(SAMPLE_REPOS, max_per_chunk=50)
    assert len(chunks) == 3          # 120 repos / 50 = 3 chunks
    assert len(chunks[0]) == 50
    assert len(chunks[2]) == 20


def test_stream_xml_has_urbanverse_metadata():
    xml_fragments = list(stream_xml_bundle(SAMPLE_REPOS[:5], chunk_idx=1))
    full_xml = "".join(xml_fragments)
    for field in ["intent_hash", "urbanverse_version", "strate", "tier"]:
        assert field in full_xml, "Champ manquant dans XML : {}".format(field)


def test_generate_bundles_creates_manifest(tmp_path):
    manifest = generate_bundles(
        SAMPLE_REPOS, output_dir=tmp_path,
        chunk_size_mb=80, max_per_chunk=50, tier_filter="ALL"
    )
    assert (tmp_path / "bundle_manifest.json").exists()
    assert manifest["total_repos"] == 120
    assert len(manifest["chunks"]) == 3
    assert manifest["kpi_ok"] is True


def test_tier_filter_p0_only(tmp_path):
    manifest = generate_bundles(
        SAMPLE_REPOS, output_dir=tmp_path,
        chunk_size_mb=80, max_per_chunk=50, tier_filter="P0"
    )
    assert manifest["total_repos"] == 5    # seuls les 5 repos L0
    assert manifest["tier_filter"] == "P0"
