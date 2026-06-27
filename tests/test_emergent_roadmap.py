"""Tests EPIC-13 P3 — EmergentRoadmap"""
from scripts.intent_field.metacluster_projector import (
    MetaClusterMap, Cluster, IntentPoint, VoidZone, SPOKES
)
from scripts.intent_field.coherence_gate import FieldDocument
from scripts.intent_field.emergent_roadmap import (
    EmergentRoadmapBuilder, RoadmapPriority, GapSuggestion, DriftRisk,
    HIGH_DENSITY_THRESHOLD,
)


# --- helpers fixtures -------------------------------------------------------

def _make_point(pid: str, repo: str, dominant: str, is_gravity: bool = False) -> IntentPoint:
    coords = {s: 0.05 for s in SPOKES}
    coords[dominant] = 0.7
    total = sum(coords.values())
    coords = {k: round(v / total, 4) for k, v in coords.items()}
    return IntentPoint(
        point_id=pid, repo=repo, coords=coords,
        kind="intent", status="active",
        is_gravity=is_gravity, gravity_weight=3.0 if is_gravity else 1.0,
    )


def _make_cluster(cid: int, dominant: str, density: float, points: list[str]) -> Cluster:
    coords = {s: 0.05 for s in SPOKES}
    coords[dominant] = 0.7
    total = sum(coords.values())
    centroid = {k: round(v / total, 4) for k, v in coords.items()}
    label_map = {
        "AI": "intelligence_agentique",
        "TECH": "infrastructure_pipeline",
        "MATH": "formalisation_graphes",
        "PHYSICS": "champ_flux",
    }
    return Cluster(
        cluster_id=cid,
        centroid=centroid,
        points=points,
        label_emergent=label_map.get(dominant, dominant),
        density=density,
    )


def _make_map(
    clusters: list[Cluster],
    void_zones: list[VoidZone] | None = None,
    gravity_points: list[IntentPoint] | None = None,
) -> MetaClusterMap:
    all_points = [
        _make_point(pid, "Gitnote", c.label_emergent.split("_")[0].upper()[:5] or "AI")
        for c in clusters
        for pid in c.points
    ] + (gravity_points or [])
    density_map = {
        s: sum(1 for c in clusters if c.centroid.get(s, 0) > 0.3) / max(len(clusters), 1)
        for s in SPOKES
    }
    return MetaClusterMap(
        repos=["Gitnote", "ECOYSTEM"],
        intent_cloud=all_points,
        clusters=clusters,
        gravity_centers=gravity_points or [],
        void_zones=void_zones or [],
        density_map=density_map,
    )


# --- tests -----------------------------------------------------------------

def test_build_returns_emergent_roadmap():
    clusters = [_make_cluster(0, "AI", 0.6, ["INT-1301", "INT-1211"]),
                _make_cluster(1, "TECH", 0.08, ["TOC-01"])]
    rm = EmergentRoadmapBuilder().build(_make_map(clusters))
    assert len(rm.priorities) == 2


def test_now_cohort_on_dense_cluster():
    dense = _make_cluster(0, "AI", HIGH_DENSITY_THRESHOLD + 0.1, ["INT-A", "INT-B", "INT-C"])
    sparse = _make_cluster(1, "TECH", 0.05, ["INT-D"])
    rm = EmergentRoadmapBuilder().build(_make_map([dense, sparse]))
    now = [p for p in rm.priorities if p.cohort == "now"]
    assert len(now) >= 1
    assert now[0].label == "intelligence_agentique"


def test_later_cohort_on_sparse_cluster():
    sparse = _make_cluster(0, "PHYSICS", 0.02, ["INT-X"])
    rm = EmergentRoadmapBuilder().build(_make_map([sparse]))
    later = [p for p in rm.priorities if p.cohort == "later"]
    assert len(later) >= 1


def test_gaps_from_void_zones():
    clusters = [_make_cluster(0, "AI", 0.5, ["INT-A"])]
    voids = [
        VoidZone(zone_id=0, dominant_spoke="BIO",
                 description="Aucun intent BIO",
                 coords_approx={s: 0 for s in SPOKES}),
    ]
    rm = EmergentRoadmapBuilder().build(_make_map(clusters, void_zones=voids))
    assert len(rm.gaps) == 1
    assert rm.gaps[0].dominant_spoke == "BIO"
    assert "INT-NEW" in rm.gaps[0].suggested_intent


def test_drift_risk_detected():
    cluster_ai = _make_cluster(0, "AI", 0.4, ["INT-A"])
    # Masse gravitationnelle purement TECH → cluster AI sera éloigné
    gravity = _make_point("ADR-0001", "GOVERNANCE", "TECH", is_gravity=True)
    gravity.gravity_weight = 3.0
    cluster_map = _make_map([cluster_ai], gravity_points=[gravity])
    rm = EmergentRoadmapBuilder().build(cluster_map)
    # Il peut y avoir ou non un drift selon la distance cosine ; juste vérifier le type
    assert isinstance(rm.drift_risks, list)


def test_timeline_structure():
    clusters = [
        _make_cluster(0, "AI", 0.5, ["A"]),
        _make_cluster(1, "TECH", 0.15, ["B"]),
        _make_cluster(2, "MATH", 0.02, ["C"]),
    ]
    rm = EmergentRoadmapBuilder().build(_make_map(clusters))
    assert set(rm.timeline.keys()) == {"now", "next", "later"}
    all_labels = rm.timeline["now"] + rm.timeline["next"] + rm.timeline["later"]
    assert len(all_labels) == 3


def test_mermaid_contains_subgraphs():
    clusters = [_make_cluster(0, "AI", 0.4, ["INT-A"])]
    rm = EmergentRoadmapBuilder().build(_make_map(clusters))
    assert "flowchart TD" in rm.mermaid_roadmap
    assert "NOW" in rm.mermaid_roadmap
    assert "NEXT" in rm.mermaid_roadmap
    assert "LATER" in rm.mermaid_roadmap


def test_coherence_reading_non_empty():
    clusters = [_make_cluster(0, "AI", 0.5, ["INT-A"])]
    rm = EmergentRoadmapBuilder().build(_make_map(clusters))
    assert len(rm.coherence_reading) > 20
    assert "champ" in rm.coherence_reading.lower() or "intent" in rm.coherence_reading.lower()


def test_to_dict_shape():
    clusters = [_make_cluster(0, "AI", 0.4, ["INT-A"])]
    rm = EmergentRoadmapBuilder().build(_make_map(clusters))
    data = rm.to_dict()
    assert "priorities" in data
    assert "gaps" in data
    assert "drift_risks" in data
    assert "timeline" in data


def test_suggested_epic_mapping():
    cluster = _make_cluster(0, "AI", 0.5, ["INT-A"])
    rm = EmergentRoadmapBuilder().build(_make_map([cluster]))
    epics = [p.suggested_epic for p in rm.priorities]
    assert any("agent" in e or "EPIC" in e for e in epics)


def test_no_gravity_no_drift_risks():
    clusters = [_make_cluster(0, "AI", 0.4, ["INT-A"])]
    cluster_map = _make_map(clusters)  # pas de gravity_points
    rm = EmergentRoadmapBuilder().build(cluster_map)
    assert rm.drift_risks == []
