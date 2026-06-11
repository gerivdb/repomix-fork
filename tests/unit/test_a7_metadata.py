"""tests/unit/test_a7_metadata.py — PRD-009 A7"""
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.test_bundle_a7 import extract_stratum_metadata, validate_bundle_metadata


# ── Fixture: bundle XML avec métadonnées UrbanVerse ──────────────────

URBANVERSE_BUNDLE_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<bundle chunk="1" repos="3">
  <metadata>
    <generated_by>gerivdb-repomix</generated_by>
    <urbanverse_version>5.0.0</urbanverse_version>
    <intent_hash>0xREPOMIX_INTENT_20260611</intent_hash>
  </metadata>
  <repo name="GOVERNANCE-HUB">
    <strate>L0</strate>
    <tier>P0</tier>
    <phi_cps>3.697</phi_cps>
    <vague_deployee>12</vague_deployee>
    <layer>L2_COMPOSITION</layer>
    <file path="README.md"># GOVERNANCE-HUB</file>
  </repo>
  <repo name="NEXUS">
    <strate>L1</strate>
    <tier>P0</tier>
    <phi_cps>3.697</phi_cps>
    <vague_deployee>12</vague_deployee>
    <layer>L1_CAUSALITY</layer>
    <file path="README.md"># NEXUS</file>
  </repo>
  <repo name="BRAIN">
    <strate>L2</strate>
    <tier>P0</tier>
    <phi_cps>4.092</phi_cps>
    <vague_deployee>12</vague_deployee>
    <layer>L3_EMERGENCE</layer>
    <file path="README.md"># BRAIN</file>
  </repo>
</bundle>
"""


@pytest.fixture
def urbanverse_bundle(tmp_path):
    f = tmp_path / "urbanverse_bundle.xml"
    f.write_text(URBANVERSE_BUNDLE_XML, encoding="utf-8")
    return f


class TestA7Metadata:
    def test_strate_present(self, urbanverse_bundle):
        fields = extract_stratum_metadata(urbanverse_bundle)
        assert fields["strate"] is not None

    def test_phi_cps_present(self, urbanverse_bundle):
        fields = extract_stratum_metadata(urbanverse_bundle)
        assert fields["phi_cps"] is not None

    def test_intent_hash_present(self, urbanverse_bundle):
        fields = extract_stratum_metadata(urbanverse_bundle)
        assert fields["intent_hash"] is not None

    def test_vague_deployee_present(self, urbanverse_bundle):
        fields = extract_stratum_metadata(urbanverse_bundle)
        assert fields["vague_deployee"] is not None

    def test_all_4_fields_present(self, urbanverse_bundle):
        """Les 4 champs UrbanVerse sont presents dans le bundle."""
        ok = validate_bundle_metadata(urbanverse_bundle)
        assert ok is True

    def test_layer_present(self, urbanverse_bundle):
        fields = extract_stratum_metadata(urbanverse_bundle)
        assert fields["layer"] is not None
