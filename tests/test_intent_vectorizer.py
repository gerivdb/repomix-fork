"""Tests EPIC-12 P1 — IntentVectorizer"""
import json
from pathlib import Path

import pytest

from scripts.intent_grapher.intent_vectorizer import (
    IntentParser,
    IntentVectorizer,
    SPOKE_KEYWORDS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

INTENT_1211_CONTENT = """
# INTENT-1211 — MoE-Router : Dispatch Enzymatique

> **IntentHash**: `0xINT_MOE_ROUTER_ENZYME_DISPATCH_φ1.211`
> **Statut**: `active`

## Signal
Le dispatch enzymatique est aveugle au type de source.

## Vecteur d'intent

```yaml
intent_id: INT-1211
dimension_principale: routing_intelligence
source_pain: dispatch_naif_premier_match
cible: enzyme_specialisation_par_source_type
contrainte_hard: retrocompat_commit_enzyme
resultat_attendu: router_confidence_dans_chaque_packet
```

## Traçabilité
- `INT-1211` → `EPIC-1211` → `ADR-001`
"""

INTENT_EMPTY_CONTENT = """
# INTENT-0000 — Test vide
Aucun vecteur YAML ici.
"""


@pytest.fixture
def intents_dir(tmp_path: Path) -> Path:
    d = tmp_path / "intents"
    d.mkdir()
    (d / "INT-1211-moe-router.md").write_text(INTENT_1211_CONTENT, encoding="utf-8")
    return d


@pytest.fixture
def empty_intents_dir(tmp_path: Path) -> Path:
    d = tmp_path / "intents"
    d.mkdir()
    (d / "INT-0000-empty.md").write_text(INTENT_EMPTY_CONTENT, encoding="utf-8")
    return d


# ---------------------------------------------------------------------------
# Tests IntentParser
# ---------------------------------------------------------------------------

class TestIntentParser:

    def test_parse_intent_hash(self, tmp_path):
        f = tmp_path / "INT-1211.md"
        f.write_text(INTENT_1211_CONTENT, encoding="utf-8")
        parser = IntentParser()
        iv = parser.parse_file(f)
        assert iv.intent_hash == "0xINT_MOE_ROUTER_ENZYME_DISPATCH_φ1.211"

    def test_parse_yaml_fields(self, tmp_path):
        f = tmp_path / "INT-1211.md"
        f.write_text(INTENT_1211_CONTENT, encoding="utf-8")
        parser = IntentParser()
        iv = parser.parse_file(f)
        assert iv.intent_id == "INT-1211"
        assert iv.dimension_principale == "routing_intelligence"
        assert iv.source_pain == "dispatch_naif_premier_match"
        assert iv.cible == "enzyme_specialisation_par_source_type"
        assert iv.resultat_attendu == "router_confidence_dans_chaque_packet"

    def test_epic_ref_extracted(self, tmp_path):
        f = tmp_path / "INT-1211.md"
        f.write_text(INTENT_1211_CONTENT, encoding="utf-8")
        parser = IntentParser()
        iv = parser.parse_file(f)
        assert iv.epic_ref == "1211"

    def test_adr_ref_extracted(self, tmp_path):
        f = tmp_path / "INT-1211.md"
        f.write_text(INTENT_1211_CONTENT, encoding="utf-8")
        parser = IntentParser()
        iv = parser.parse_file(f)
        assert iv.adr_ref == "001"

    def test_empty_content_no_crash(self, tmp_path):
        f = tmp_path / "INT-0000.md"
        f.write_text(INTENT_EMPTY_CONTENT, encoding="utf-8")
        parser = IntentParser()
        iv = parser.parse_file(f)
        assert iv.intent_id is not None   # fallback filename
        assert iv.intent_hash is None
        assert iv.dimension_principale is None

    def test_guess_id_from_filename(self):
        assert IntentParser._guess_id_from_filename("INT-1212-dag-rag.md") == "INT-1212"
        assert IntentParser._guess_id_from_filename("INT_1213_safety.md") == "INT-1213"


# ---------------------------------------------------------------------------
# Tests IntentVectorizer
# ---------------------------------------------------------------------------

class TestIntentVectorizer:

    def test_vectorize_returns_repo_vector(self, intents_dir):
        vect = IntentVectorizer(repo="test/repo", intents_dir=intents_dir)
        rv = vect.vectorize()
        assert rv.repo == "test/repo"
        assert len(rv.intents) == 1
        assert rv.repo_vector["dimensions"] == ["routing_intelligence"]
        assert rv.repo_vector["epic_refs"] == ["1211"]

    def test_spoke_scores_ai_dominant(self, intents_dir):
        vect = IntentVectorizer(repo="test/repo", intents_dir=intents_dir)
        rv = vect.vectorize()
        iv = rv.intents[0]
        # routing_intelligence + enzyme + dispatch → AI et TECH dominants
        assert iv.spoke_scores["AI"] > 0 or iv.spoke_scores["TECH"] > 0
        assert iv.dominant_spoke in ("AI", "TECH", "MATH")

    def test_aggregate_spokes_keys(self, intents_dir):
        vect = IntentVectorizer(repo="test/repo", intents_dir=intents_dir)
        rv = vect.vectorize()
        for spoke in SPOKE_KEYWORDS:
            assert spoke in rv.ontology_spokes

    def test_vectorize_to_file(self, intents_dir, tmp_path):
        vect = IntentVectorizer(repo="test/repo", intents_dir=intents_dir)
        out = tmp_path / "output" / "intent_vector.json"
        rv = vect.vectorize_to_file(out)
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["repo"] == "test/repo"
        assert "intents" in data
        assert "ontology_spokes" in data
        assert "repo_vector" in data

    def test_empty_intents_no_crash(self, empty_intents_dir):
        vect = IntentVectorizer(repo="test/repo", intents_dir=empty_intents_dir)
        rv = vect.vectorize()
        assert len(rv.intents) == 1
        # Pas de crash même sans YAML
        assert rv.repo_vector["dimensions"] == []

    def test_to_dict_complete(self, intents_dir):
        vect = IntentVectorizer(repo="test/repo", intents_dir=intents_dir)
        rv = vect.vectorize()
        d = rv.to_dict()
        assert d["intent_count"] == 1
        assert isinstance(d["intents"][0]["spoke_scores"], dict)
        assert isinstance(d["ontology_spokes"], dict)
