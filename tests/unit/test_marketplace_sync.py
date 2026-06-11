"""tests/unit/test_marketplace_sync.py — PRD-011 EPIC-11"""
import json
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "repomix"))

from sync.verses_sync_manager import VersesSyncManager, VerseEntry


@pytest.fixture
def tmp_registry(tmp_path):
    """Crée un registry temporaire pour les tests."""
    reg_path = tmp_path / "test_ontology_registry.json"
    reg_path.write_text(json.dumps({"verses": [], "version": "1.0"}))
    return reg_path


@pytest.fixture
def sample_verse():
    return VerseEntry(
        id="test-verse-001",
        name="Test Verse",
        domain="TEST",
        version="1.0.0",
        dependencies=["dep-1", "dep-2"],
        quality_score=85.0,
    )


class TestMarketplaceSync:
    def test_push_creates_registry(self, tmp_path, sample_verse):
        """push_to_marketplace crée ontology_registry.json s'il n'existe pas."""
        reg_path = tmp_path / "new_registry.json"
        mgr = VersesSyncManager(repo_path=tmp_path,
                                registry_path=tmp_path / "dummy.json")
        result = mgr.push_to_marketplace(sample_verse, registry_path=reg_path)
        assert reg_path.exists()
        assert result["status"] == "pushed"

    def test_push_updates_existing(self, tmp_registry, sample_verse):
        """push_to_marketplace met à jour un verse existant."""
        mgr = VersesSyncManager(repo_path=tmp_registry.parent,
                                registry_path=tmp_registry)
        # Premier push
        mgr.push_to_marketplace(sample_verse, registry_path=tmp_registry)
        # Update
        updated_verse = VerseEntry(
            id="test-verse-001", name="Test Verse Updated",
            domain="TEST", version="2.0.0", dependencies=[], quality_score=90.0,
        )
        result = mgr.push_to_marketplace(updated_verse, registry_path=tmp_registry)
        assert result["status"] == "updated"

        data = json.loads(tmp_registry.read_text(encoding="utf-8"))
        verse = next(v for v in data["verses"] if v["id"] == "test-verse-001")
        assert verse["version"] == "2.0.0"
        assert verse["quality_score"] == 90.0

    def test_push_persists_to_json(self, tmp_registry, sample_verse):
        """Le registry JSON contient le verse après push."""
        mgr = VersesSyncManager(repo_path=tmp_registry.parent,
                                registry_path=tmp_registry)
        mgr.push_to_marketplace(sample_verse, registry_path=tmp_registry)

        data = json.loads(tmp_registry.read_text(encoding="utf-8"))
        assert data["count"] == 1
        assert len(data["verses"]) == 1
        assert data["verses"][0]["id"] == "test-verse-001"
        assert data["verses"][0]["name"] == "Test Verse"
        assert "last_updated" in data

    def test_push_updates_in_memory_registry(self, tmp_registry, sample_verse):
        """push_to_marketplace met aussi à jour le registry en mémoire."""
        mgr = VersesSyncManager(repo_path=tmp_registry.parent,
                                registry_path=tmp_registry)
        mgr.push_to_marketplace(sample_verse, registry_path=tmp_registry)
        assert "test-verse-001" in mgr._registry
        assert mgr._registry["test-verse-001"].name == "Test Verse"

    def test_push_multiple_verses(self, tmp_registry):
        """Plusieurs pushes ajoutent plusieurs verses."""
        mgr = VersesSyncManager(repo_path=tmp_registry.parent,
                                registry_path=tmp_registry)
        for i in range(5):
            verse = VerseEntry(
                id="verse-{:03d}".format(i), name="Verse {}".format(i),
                domain="TEST", version="1.0.0", dependencies=[], quality_score=50.0 + i,
            )
            mgr.push_to_marketplace(verse, registry_path=tmp_registry)

        data = json.loads(tmp_registry.read_text(encoding="utf-8"))
        assert data["count"] == 5
        assert len(data["verses"]) == 5

    def test_push_ttl_not_expired(self, tmp_registry, sample_verse):
        """Le registry a un last_updated récent (TTL concept)."""
        import time
        mgr = VersesSyncManager(repo_path=tmp_registry.parent,
                                registry_path=tmp_registry)
        mgr.push_to_marketplace(sample_verse, registry_path=tmp_registry)

        data = json.loads(tmp_registry.read_text(encoding="utf-8"))
        # last_updated doit être < 5s
        assert time.time() - data["last_updated"] < 5.0

    def test_push_conflict_same_id_different_version(self, tmp_registry):
        """Deux pushes avec même id mais versions différentes → update, pas doublon."""
        mgr = VersesSyncManager(repo_path=tmp_registry.parent,
                                registry_path=tmp_registry)
        v1 = VerseEntry(id="conflict-v1", name="V1", domain="TEST", version="1.0",
                        dependencies=[], quality_score=50.0)
        v2 = VerseEntry(id="conflict-v1", name="V2", domain="TEST", version="2.0",
                        dependencies=[], quality_score=60.0)
        mgr.push_to_marketplace(v1, registry_path=tmp_registry)
        mgr.push_to_marketplace(v2, registry_path=tmp_registry)

        data = json.loads(tmp_registry.read_text(encoding="utf-8"))
        assert data["count"] == 1, "Doublon détecté — le verse devrait être mis à jour, pas dupliqué"
        assert data["verses"][0]["version"] == "2.0"
