"""tests/unit/test_relay_propagator.py — PRD-003 Phase 2"""
import json, pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "repomix"))

from scripts.relay_propagator import propagate, _render_relay, PILOT_REPOS
from scripts.cadastre_builder import build_cadastre, validate_parcel


def test_dry_run_no_write(tmp_path):
    results = propagate(dry_run=True, output_dir=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_10_pilots_selected():
    assert len(PILOT_REPOS) == 10


def test_relay_content_valid():
    content = _render_relay(PILOT_REPOS[0])
    for section in ["Identite stratique", "Navigation rapide", "Regles locales",
                    "Karpathy-Recall", "Vague de mise a jour"]:
        assert section in content


def test_strate_coverage():
    strates = {r["strate"] for r in PILOT_REPOS}
    assert "L0" in strates
    assert "L3" in strates
    assert "L8" in strates


def test_commit_mode_writes(tmp_path):
    results = propagate(dry_run=False, output_dir=tmp_path)
    files = list(tmp_path.glob("*.md"))
    assert len(files) == 10
    assert (tmp_path / "relay_manifest_v1.json").exists()


def test_manifest_structure(tmp_path):
    propagate(dry_run=False, output_dir=tmp_path)
    manifest = json.loads((tmp_path / "relay_manifest_v1.json").read_text())
    assert manifest["vague"] == 1
    assert manifest["count"] == 10
    assert manifest["connectivite"] == "DSL"


def test_cadastre_schema_valid():
    parcelles = build_cadastre(vague=1)
    for p in parcelles:
        errors = validate_parcel(p)
        assert errors == [], "{}: {}".format(p["repo_name"], errors)


def test_cadastre_vague_default():
    parcelles = build_cadastre()
    for p in parcelles:
        assert p["vague_courante"] == 1
        assert p["connectivite"] == "DSL"
