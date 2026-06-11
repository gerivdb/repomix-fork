"""tests/unit/test_recall_coherence.py — EPIC-04 Karpathy Recall × UrbanVerse"""
from pathlib import Path
import pytest
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "repomix"))

from tools.recall_coherence_check import (
    check_bundle_xml,
    check_transit_map,
    check_relay_coherence,
    check_full_coherence,
)


# ── Fixtures ─────────────────────────────────────────────────────────

SAMPLE_BUNDLE_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<bundle chunk="1" repos="2">
  <metadata>
    <generated_by>gerivdb-repomix</generated_by>
    <urbanverse_version>5.0.0</urbanverse_version>
    <intent_hash>0xREPOMIX_INTENT_20260611</intent_hash>
  </metadata>
  <repo name="NEXUS">
    <strate>L1</strate>
    <tier>P0</tier>
    <phi_cps>3.697</phi_cps>
    <vague_deployee>12</vague_deployee>
    <file path="src/nexus/core.py">
import os
from pathlib import Path

class NexusCore:
    def __init__(self):
        pass
    def process(self, data):
        return data
    </file>
  </repo>
  <repo name="BRAIN">
    <strate>L2</strate>
    <tier>P0</tier>
    <phi_cps>4.092</phi_cps>
    <vague_deployee>12</vague_deployee>
    <file path="src/brain/agent.py">
import json
class BrainAgent:
    def __init__(self, name):
        self.name = name
    </file>
  </repo>
</bundle>
"""

SAMPLE_BUNDLE_NO_METADATA = """\
<?xml version="1.0" encoding="UTF-8"?>
<bundle chunk="1" repos="1">
  <repo name="UNKNOWN">
    <file path="README.md"># Unknown</file>
  </repo>
</bundle>
"""

SAMPLE_TRANSIT_YAML = """\
lines:
  - id: M1
    name: "Ligne Cognitive Principale"
    type: metro
    recall_pack: true
    stops:
      - id: L0
        name: "Gouvernance"
        repo: "GOVERNANCE-HUB"
        recall_pack: "L0_governance_recall"
        recall_questions: 5
      - id: L1b
        name: "Substrat Cognitif"
        repo: "LLM-REPO"
        recall_pack: "L1b_llm_substrate_recall"
        recall_questions: 5
  - id: RER-A
    name: "Transversale"
    type: rer
    stops: [L0, L3]
    recall_pack: false
"""

SAMPLE_RELAY_V2 = """\
# STRATUM RELAY - GOVERNANCE-HUB (L0)

VAGUE: 2 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Karpathy-Recall local (5Q specifiques)
1. Quel est le role canonique de GOVERNANCE-HUB ?
   -> Constitution de l'ecosysteme.
2. Quelle strate amont alimente GOVERNANCE-HUB ?
   -> Aucune -- L0 est la strate racine.
3. Quelle strate aval GOVERNANCE-HUB alimente-t-il ?
   -> L1 (SOT operationnel) et L1b (substrat cognitif LLM).
4. Quelle est la regle R1 de GOVERNANCE-HUB ?
   -> Fichiers proteges : ADR/, STRATUM_RELAY.md.
5. Comment verifier l'integrite du cadastre ?
   -> Lire known_repositories.yaml (GATE-0).
"""

SAMPLE_RELAY_V2_INSUFFICIENT = """\
# STRATUM RELAY — BRAIN (L2)

VAGUE: 2 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Karpathy-Recall local (5Q specifiques)
1. Quel est le role canonique de BRAIN ?
   -> Couche IA -- agents cognitifs.
2. Quelle strate amont alimente BRAIN ?
   -> L1 (ECOYSTEM, NEXUS).
"""

SAMPLE_RELAY_V2_INSUFFICIENT = """\
# STRATUM RELAY - BRAIN (L2)

VAGUE: 2 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Karpathy-Recall local (5Q specifiques)
1. Quel est le role canonique de BRAIN ?
   -> Couche IA - agents cognitifs.
2. Quelle strate amont alimente BRAIN ?
   -> L1 (ECOYSTEM, NEXUS).
"""


@pytest.fixture
def sample_bundle(tmp_path):
    f = tmp_path / "sample_bundle.xml"
    f.write_text(SAMPLE_BUNDLE_XML, encoding="utf-8")
    return f


@pytest.fixture
def sample_bundle_no_metadata(tmp_path):
    f = tmp_path / "sample_bundle_no_meta.xml"
    f.write_text(SAMPLE_BUNDLE_NO_METADATA, encoding="utf-8")
    return f


@pytest.fixture
def sample_transit(tmp_path):
    f = tmp_path / "transit_map.yaml"
    f.write_text(SAMPLE_TRANSIT_YAML, encoding="utf-8")
    return f


@pytest.fixture
def sample_relay_dir(tmp_path):
    """Crée un répertoire avec des relays Vague 2 valides."""
    relay_dir = tmp_path / "relays_v2"
    relay_dir.mkdir()
    (relay_dir / "GOVERNANCE-HUB__STRATUM_RELAY_v2.md").write_text(
        SAMPLE_RELAY_V2, encoding="utf-8")
    (relay_dir / "BRAIN__STRATUM_RELAY_v2.md").write_text(
        SAMPLE_RELAY_V2_INSUFFICIENT, encoding="utf-8")
    return relay_dir


# ── Tests check_transit_map ──────────────────────────────────────────

class TestCheckTransitMap:
    def test_valid_transit_no_errors(self, sample_transit):
        """Un transit_map valide ne produit pas d'erreurs."""
        errors = check_transit_map(sample_transit)
        assert errors == {}

    def test_nonexistent_transit(self, tmp_path):
        """Un transit_map inexistant produit une erreur."""
        errors = check_transit_map(tmp_path / "nonexistent.yaml")
        assert "file_not_found" in errors


# ── Tests check_relay_coherence ──────────────────────────────────────

class TestCheckRelayCoherence:
    def test_relay_with_insufficient_questions(self, sample_relay_dir):
        """Un relay avec < 5 questions est signalé."""
        errors = check_relay_coherence(sample_relay_dir, expected_vague=2)
        assert "insufficient_questions" in errors
        # BRAIN a seulement 2 questions au lieu de 5
        assert any("BRAIN" in e for e in errors["insufficient_questions"])

    def test_relay_dir_missing(self, tmp_path):
        """Un répertoire inexistant produit une erreur."""
        errors = check_relay_coherence(tmp_path / "nonexistent")
        assert "file_not_found" in errors

    def test_valid_relay_has_5_questions(self, tmp_path):
        """Un relay avec 5 questions ne produit pas d'erreur."""
        relay_dir = tmp_path / "relays_valid"
        relay_dir.mkdir()
        (relay_dir / "GOVERNANCE-HUB__STRATUM_RELAY_v2.md").write_text(
            SAMPLE_RELAY_V2, encoding="utf-8")
        errors = check_relay_coherence(relay_dir, expected_vague=2)
        assert "insufficient_questions" not in errors


# ── Tests check_full_coherence ───────────────────────────────────────

class TestCheckFullCoherence:
    def test_full_coherence_with_valid_data(self, sample_transit, tmp_path):
        """La cohérence complète valide des données transit + relays valides."""
        relay_dir = tmp_path / "relays_full"
        relay_dir.mkdir()
        # Créer un relay pour GOVERNANCE-HUB (L0)
        (relay_dir / "GOVERNANCE-HUB__STRATUM_RELAY_v2.md").write_text(
            SAMPLE_RELAY_V2, encoding="utf-8")
        errors = check_full_coherence(sample_transit, relay_dir)
        # Pas d'erreur de type missing_relay_for_stop pour L0
        missing = errors.get("missing_relay_for_stop", [])
        assert not any("L0" in m for m in missing)

    def test_full_coherence_missing_relay(self, sample_transit, tmp_path):
        """Un arrêt M1 sans relay correspondant est signalé."""
        relay_dir = tmp_path / "relays_empty"
        relay_dir.mkdir()
        errors = check_full_coherence(sample_transit, relay_dir)
        assert "missing_relay_for_stop" in errors

    def test_full_coherence_missing_transit(self, tmp_path):
        """Un transit_map manquant produit une erreur."""
        errors = check_full_coherence(tmp_path / "nonexistent.yaml", tmp_path)
        assert "transit_missing" in errors
