"""Tests unitaires VersesSyncManager — sans dependance reseau (R3)."""
import json, time, pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "repomix"))

from sync.verses_sync_manager import VersesSyncManager, VerseEntry


def _make_manager(tmp_path, verses):
    registry = {"verses": verses}
    reg_path = tmp_path / "registry.json"
    reg_path.write_text(json.dumps(registry))
    return VersesSyncManager(repo_path=tmp_path, registry_path=reg_path)


def test_sync_empty(tmp_path):
    mgr = _make_manager(tmp_path, [])
    result = mgr.sync_selective([])
    assert result["elapsed_s"] < mgr.SYNC_TIMEOUT_S
    assert result["under_kpi"] is True


def test_sync_known_verse(tmp_path):
    mgr = _make_manager(tmp_path, [{
        "id": "physics-v1", "name": "Physics Verse", "domain": "PHYSICS",
        "version": "1.0.0", "dependencies": [], "quality_score": 80.0
    }])
    result = mgr.sync_selective(["physics-v1"])
    assert "physics-v1" in result["cached"]
    assert result["under_kpi"] is True


def test_sync_skips_cached(tmp_path):
    mgr = _make_manager(tmp_path, [{
        "id": "math-v1", "name": "Math Verse", "domain": "MATH",
        "version": "1.0.0", "dependencies": [], "quality_score": 75.0
    }])
    mgr.sync_selective(["math-v1"])
    result = mgr.sync_selective(["math-v1"])
    assert "math-v1" in result["skipped"]


def test_dependency_resolution(tmp_path):
    mgr = _make_manager(tmp_path, [
        {"id": "A", "name": "A", "domain": "X", "version": "1.0", "dependencies": ["B"], "quality_score": 50},
        {"id": "B", "name": "B", "domain": "X", "version": "2.0", "dependencies": [], "quality_score": 50},
    ])
    deps = mgr._resolve_dependencies(["A"])
    assert "A" in deps and "B" in deps


def test_sync_under_kpi(tmp_path):
    verses = [{"id": "v{}".format(i), "name": "Verse {}".format(i), "domain": "TEST",
               "version": "1.0", "dependencies": [], "quality_score": 50.0}
              for i in range(50)]
    mgr = _make_manager(tmp_path, verses)
    t0 = time.time()
    mgr.sync_selective(["v{}".format(i) for i in range(50)])
    assert time.time() - t0 < mgr.SYNC_TIMEOUT_S


def test_invalidate_cache(tmp_path):
    mgr = _make_manager(tmp_path, [{
        "id": "z1", "name": "Z", "domain": "TEST", "version": "1.0",
        "dependencies": [], "quality_score": 50.0
    }])
    mgr.sync_selective(["z1"])
    count = mgr.invalidate_cache("z1")
    assert count == 1


def test_list_available_domain_filter(tmp_path):
    mgr = _make_manager(tmp_path, [
        {"id": "p1", "name": "Physics", "domain": "PHYSICS", "version": "1.0", "dependencies": [], "quality_score": 80.0},
        {"id": "m1", "name": "Math", "domain": "MATH", "version": "1.0", "dependencies": [], "quality_score": 70.0},
    ])
    physics = mgr.list_available(domain="PHYSICS")
    assert len(physics) == 1
    assert physics[0].id == "p1"


def test_pin_versions_latest(tmp_path):
    mgr = _make_manager(tmp_path, [{
        "id": "v1", "name": "V", "domain": "X", "version": "2.5.0",
        "dependencies": [], "quality_score": 50.0
    }])
    deps = {"v1": "latest"}
    pinned = mgr._pin_versions(deps)
    assert pinned["v1"] == "2.5.0"
