"""Tests EPIC-13 P2 — MetaClusterProjector"""
from scripts.intent_field.vibe_crystallizer import VibeCrystallizer
from scripts.intent_field.coherence_gate import FieldDocument
from scripts.intent_field.metacluster_projector import (
    MetaClusterProjector,
    IntentPoint,
    MetaClusterMap,
    SPOKES,
)


# --- fixtures inline -------------------------------------------------------

VIBE_INTENT_FIELD = """
# INT-1301 — Intent Field
Statut : active
> φ-CPS : 4.71
intent semantic agent field gravity cluster vector metacluster
pipeline dag roadmap graph
gerivdb/BRAIN gerivdb/NEXUS gerivdb/ECOYSTEM
"""

VIBE_HERMES = """
# HERMES — memory skills acp
Statut : draft
agent memory skills acp emit persistent fts5 trajectory
pipeline cli bus
gerivdb/BRAIN gerivdb/EMIT
"""

VIBE_TOC = """
# TOC — task orchestration citizen
Statut : draft
worktree dag parallel executor verifier circuit phi cps
agent cli asyncio pipeline
gerivdb/ECOYSTEM gerivdb/NEXUS
"""

VIBE_MATH = """
# INT-MATH — formalisation mathématique
Statut : active
graph score vector matrix cosine threshold confidence weight
phi cps metric cluster gradient
"""

ADR_DOC = FieldDocument(
    doc_id="ADR-0001",
    kind="adr",
    title="Intent Grapher Pipeline",
    status="accepted",
    phi_cps=4.62,
    spoke_scores={"AI": 0.6, "TECH": 0.7, "MATH": 0.5, "SCIENCE": 0.1, "PHYSICS": 0.2, "BIO": 0.05},
    content="adr intent grapher pipeline",
)

EPIC_DOC = FieldDocument(
    doc_id="EPIC-13",
    kind="epic",
    title="Intent Field",
    status="active",
    phi_cps=4.71,
    spoke_scores={"AI": 0.7, "TECH": 0.6, "MATH": 0.6, "SCIENCE": 0.2, "PHYSICS": 0.5, "BIO": 0.1},
    content="intent field metacluster roadmap emergent",
)


def _make_inputs(tmp_path):
    vc = VibeCrystallizer()
    files = {
        "Gitnote":  (VIBE_INTENT_FIELD, "int1301.md"),
        "Gitnote":  (VIBE_HERMES,       "hermes.md"),   # noqa: F601 même repo
        "ECOYSTEM": (VIBE_TOC,          "toc.md"),
        "BRAIN":    (VIBE_MATH,         "math.md"),
    }
    inputs = []
    for repo, (content, fname) in [
        ("Gitnote",  (VIBE_INTENT_FIELD, "int1301.md")),
        ("Gitnote",  (VIBE_HERMES,       "hermes.md")),
        ("ECOYSTEM", (VIBE_TOC,          "toc.md")),
        ("BRAIN",    (VIBE_MATH,         "math.md")),
    ]:
        f = tmp_path / fname
        f.write_text(content, encoding="utf-8")
        draft = vc.crystallize(f)
        inputs.append((repo, draft))
    return inputs


# --- tests -----------------------------------------------------------------

def test_project_returns_metacluster_map(tmp_path):
    inputs = _make_inputs(tmp_path)
    result = MetaClusterProjector().project(inputs)
    assert isinstance(result, MetaClusterMap)


def test_repos_detected(tmp_path):
    inputs = _make_inputs(tmp_path)
    result = MetaClusterProjector().project(inputs)
    assert "Gitnote" in result.repos
    assert "ECOYSTEM" in result.repos or "BRAIN" in result.repos


def test_intent_cloud_non_empty(tmp_path):
    inputs = _make_inputs(tmp_path)
    result = MetaClusterProjector().project(inputs)
    assert len(result.intent_cloud) >= 4


def test_gravity_centers_from_adr(tmp_path):
    inputs = _make_inputs(tmp_path)
    result = MetaClusterProjector().project(inputs, gravity_docs=[ADR_DOC])
    gravity_ids = [p.point_id for p in result.gravity_centers]
    assert "ADR-0001" in gravity_ids


def test_gravity_centers_is_gravity_flag(tmp_path):
    inputs = _make_inputs(tmp_path)
    result = MetaClusterProjector().project(inputs, gravity_docs=[ADR_DOC, EPIC_DOC])
    for gp in result.gravity_centers:
        assert gp.is_gravity is True


def test_clusters_non_empty(tmp_path):
    inputs = _make_inputs(tmp_path)
    result = MetaClusterProjector(n_clusters=3).project(inputs)
    assert len(result.clusters) >= 1


def test_cluster_labels_known_spoke(tmp_path):
    inputs = _make_inputs(tmp_path)
    result = MetaClusterProjector(n_clusters=2).project(inputs)
    known_labels = {
        "intelligence_agentique", "infrastructure_pipeline", "formalisation_graphes",
        "recherche_patterns", "champ_flux", "systemes_adaptatifs",
    }
    for c in result.clusters:
        assert c.label_emergent in known_labels


def test_density_map_all_spokes(tmp_path):
    inputs = _make_inputs(tmp_path)
    result = MetaClusterProjector().project(inputs)
    for spoke in SPOKES:
        assert spoke in result.density_map
        assert 0.0 <= result.density_map[spoke] <= 1.0


def test_void_zones_detected_on_sparse_input(tmp_path):
    # Un seul intent très mono-spoke → doit détecter des zones vides
    vc = VibeCrystallizer()
    f = tmp_path / "mono.md"
    f.write_text("# Mono\nStatut: draft\nllm agent intent semantic memory", encoding="utf-8")
    draft = vc.crystallize(f)
    result = MetaClusterProjector(void_threshold=0.15).project([("TestRepo", draft)])
    assert len(result.void_zones) >= 1
    for v in result.void_zones:
        assert v.dominant_spoke in SPOKES


def test_summary_contains_repos_and_clusters(tmp_path):
    inputs = _make_inputs(tmp_path)
    result = MetaClusterProjector(n_clusters=2).project(inputs, gravity_docs=[ADR_DOC])
    summary = result.summary()
    assert "MetaClusterMap" in summary
    assert "Densité" in summary


def test_to_dict_shape(tmp_path):
    inputs = _make_inputs(tmp_path)
    result = MetaClusterProjector(n_clusters=2).project(inputs)
    data = result.to_dict()
    assert "repos" in data
    assert "cluster_count" in data
    assert "density_map" in data
    assert "void_zones" in data
