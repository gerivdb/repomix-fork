"""Tests unitaires pour known_repos_adapter — sans dependance externe."""
import networkx as nx
import pytest
import yaml
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "repomix"))

from adapters.known_repos_adapter import load_known_repos_graph, _is_active, _get_layer

# ── Fixtures ────────────────────────────────────────────────────────────────

MINIMAL_YAML = """\
metadata:
  version: '2.0'
  total_repos: 5
P0_CONSTITUTIONAL:
- name: NEXUS
  layer: L1_CAUSALITY
  phi_cps: 3.697
  status: active
- name: KIVA
  layer: L1_CAUSALITY
  phi_cps: 3.697
  status: active
P1_STRATEGIC:
- name: BRAIN
  layer: L3_EMERGENCE
  phi_cps: 3.697
  status: active
- name: KEEL
  layer: L1b
  status: design
P3_DORMANT:
- name: OLD-REPO
  layer: L3_EMERGENCE
  lifecycle: DORMANT
"""

FULL_YAML = """\
metadata:
  version: '2.0'
  total_repos: 8
P0_CONSTITUTIONAL:
- name: NEXUS
  layer: L1_CAUSALITY
  phi_cps: 3.697
  status: active
- name: KIVA
  layer: L1_CAUSALITY
  phi_cps: 3.697
  status: active
P1_STRATEGIC:
- name: BRAIN
  layer: L3_EMERGENCE
  phi_cps: 3.697
  status: active
  triade: T1
- name: FLUENCE
  layer: L3_EMERGENCE
  phi_cps: 3.697
  status: active
  triade: T1
- name: KEEL
  layer: L1b
  status: design
P2_SUPPORT:
- name: DevTools
  layer: L3_TOOLS
  phi_cps: 3.697
  status: active
- name: email-sender-1
  layer: L3_EMERGENCE
  status: active
P3_DORMANT:
- name: TOOL-FACTORY-1
  layer: L3_EMERGENCE
  lifecycle: DORMANT
ARCHIVE_GERI_CMS:
- name: geri-cms-old
  layer: L3_EMERGENCE
  status: archived
"""


@pytest.fixture
def minimal_yaml(tmp_path):
    f = tmp_path / "known.yaml"
    f.write_text(MINIMAL_YAML, encoding="utf-8")
    return f


@pytest.fixture
def full_yaml(tmp_path):
    f = tmp_path / "known_full.yaml"
    f.write_text(FULL_YAML, encoding="utf-8")
    return f


# ── Tests _is_active ─────────────────────────────────────────────────────────

class TestIsActive:
    def test_active_repo(self):
        assert _is_active({"name": "FOO", "status": "active"}) is True

    def test_dormant_repo(self):
        assert _is_active({"name": "FOO", "lifecycle": "DORMANT"}) is False

    def test_deprecated_repo(self):
        assert _is_active({"name": "FOO", "lifecycle": "DEPRECATED"}) is False

    def test_archived_status(self):
        assert _is_active({"name": "FOO", "status": "archived"}) is False

    def test_geri_cms_prefix(self):
        assert _is_active({"name": "geri-cms-old", "status": "active"}) is False

    def test_gericms_prefix(self):
        assert _is_active({"name": "gericms-xyz", "status": "active"}) is False

    def test_design_status_is_active(self):
        assert _is_active({"name": "FOO", "status": "design"}) is True


# ── Tests _get_layer ─────────────────────────────────────────────────────────

class TestGetLayer:
    def test_known_layer(self):
        assert _get_layer({"layer": "L1_CAUSALITY"}) == "L1_CAUSALITY"

    def test_missing_layer(self):
        assert _get_layer({}) == "L3_EMERGENCE"

    def test_none_layer(self):
        assert _get_layer({"layer": None}) == "L3_EMERGENCE"


# ── Tests load_known_repos_graph ─────────────────────────────────────────────

class TestLoadGraph:
    def test_returns_graph(self, minimal_yaml):
        G = load_known_repos_graph(minimal_yaml)
        assert isinstance(G, nx.Graph)

    def test_minimal_nodes(self, minimal_yaml):
        G = load_known_repos_graph(minimal_yaml)
        # 5 repos total - 1 DORMANT = 4 actifs
        assert G.number_of_nodes() == 4

    def test_dormant_excluded(self, minimal_yaml):
        G = load_known_repos_graph(minimal_yaml)
        assert "OLD-REPO" not in G.nodes

    def test_active_included(self, minimal_yaml):
        G = load_known_repos_graph(minimal_yaml)
        assert "NEXUS" in G.nodes
        assert "KIVA" in G.nodes
        assert "BRAIN" in G.nodes

    def test_node_attributes(self, minimal_yaml):
        G = load_known_repos_graph(minimal_yaml)
        nexus = G.nodes["NEXUS"]
        assert nexus["layer"] == "L1_CAUSALITY"
        assert nexus["phi_cps"] == 3.697
        assert nexus["layer_order"] == 1

    def test_edges_same_layer(self, minimal_yaml):
        G = load_known_repos_graph(minimal_yaml)
        # NEXUS et KIVA sont tous les deux L1_CAUSALITY
        assert G.has_edge("NEXUS", "KIVA")

    def test_no_edges_different_layers(self, minimal_yaml):
        G = load_known_repos_graph(minimal_yaml)
        # NEXUS (L1) et BRAIN (L3) pas de direct edge
        # (sauf si meme strate)
        assert not G.has_edge("NEXUS", "BRAIN")

    def test_full_yaml_excludes_archive(self, full_yaml):
        G = load_known_repos_graph(full_yaml)
        assert "geri-cms-old" not in G.nodes

    def test_full_yaml_excludes_dormant(self, full_yaml):
        G = load_known_repos_graph(full_yaml)
        assert "TOOL-FACTORY-1" not in G.nodes

    def test_full_yaml_counts(self, full_yaml):
        G = load_known_repos_graph(full_yaml)
        # 8 repos - 1 DORMANT - 1 ARCHIVE (pas de champ name) = 6 actifs
        # En fait ARCHIVE_GERI_CMS a structure differente (pas de name)
        # Donc: 8 - 1 DORMANT = 7 (l'archive est exclue via name vide)
        assert G.number_of_nodes() == 7

    def test_triade_edges(self, full_yaml):
        G = load_known_repos_graph(full_yaml)
        # BRAIN et FLUENCE partagent triade T1
        assert G.has_edge("BRAIN", "FLUENCE")
        edge_data = G.edges["BRAIN", "FLUENCE"]
        assert edge_data["reason"] == "same_triade"
        assert edge_data["weight"] == 2.0

    def test_empty_yaml(self, tmp_path):
        f = tmp_path / "empty.yaml"
        f.write_text("metadata:\n  version: '2.0'\n", encoding="utf-8")
        G = load_known_repos_graph(f)
        assert G.number_of_nodes() == 0

    def test_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_known_repos_graph(Path("/nonexistent/path.yaml"))


# ── Tests verse_detector integration ─────────────────────────────────────────

class TestVerseDetectorIntegration:
    def test_score_from_graph(self, full_yaml):
        from verse_detector import VERSE_DETECTOR
        G = load_known_repos_graph(full_yaml)
        score = VERSE_DETECTOR.score_emergence(G)
        assert 0.0 <= score <= 1.0

    def test_observe_from_graph(self, full_yaml):
        from verse_detector import VERSE_DETECTOR, VerseStatus
        G = load_known_repos_graph(full_yaml)
        obs = VERSE_DETECTOR.observe("test_ecosystem", G)
        assert obs.name == "test_ecosystem"
        assert isinstance(obs.status, VerseStatus)
        assert obs.nodes == G.number_of_nodes()
        assert obs.edges == G.number_of_edges()

    def test_score_with_empty_graph(self):
        from verse_detector import VERSE_DETECTOR
        G = nx.Graph()
        score = VERSE_DETECTOR.score_emergence(G)
        assert score == 0.0

    def test_score_with_small_graph(self):
        from verse_detector import VERSE_DETECTOR
        G = nx.path_graph(5)  # 5 nodes < 7 minimum
        score = VERSE_DETECTOR.score_emergence(G)
        assert score == 0.0

    def test_score_with_large_graph(self):
        from verse_detector import VERSE_DETECTOR
        G = nx.complete_graph(20)
        score = VERSE_DETECTOR.score_emergence(G)
        assert score > 0.5  # Complete graph should score high
