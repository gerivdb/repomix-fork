"""tests/unit/test_mine_bundle.py — PRD-009 A9"""
import json
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.mine_bundle import mine_bundle


# ── Fixture: bundle XML minimal ─────────────────────────────────────

SAMPLE_BUNDLE_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
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
  <layer>L1_CAUSALITY</layer>
  <file path="src/nexus/core.py">
import os
import sys
from pathlib import Path

class NexusCore:
    def __init__(self):
        pass

    def process(self, data):
        # TODO: implement validation
        return data

def main():
    core = NexusCore()
    result = core.process({})
    print("Result: {}".format(result))
  </file>
  <file path="tests/test_core.py">
import pytest
from src.nexus.core import NexusCore

class TestNexusCore:
    def test_process(self):
        core = NexusCore()
        assert core.process({}) == {}
  </file>
  <file path="config.yaml">
database:
  host: localhost
  port: 5432
  </file>
</repo>
<repo name="BRAIN">
  <strate>L2</strate>
  <tier>P0</tier>
  <phi_cps>4.092</phi_cps>
  <vague_deployee>12</vague_deployee>
  <layer>L3_EMERGENCE</layer>
  <file path="src/brain/agent.py">
import json
import logging

class BrainAgent:
    def __init__(self, name):
        self.name = name

    def think(self, input_data):
        # FIXME: add reasoning chain
        return {"output": input_data}

def create_agent(name):
    return BrainAgent(name)
  </file>
</repo>
"""


@pytest.fixture
def sample_bundle(tmp_path):
    f = tmp_path / "sample_bundle.xml"
    f.write_text(SAMPLE_BUNDLE_XML, encoding="utf-8")
    return f


class TestMineBundle:
    def test_basic_extraction(self, sample_bundle):
        result = mine_bundle(sample_bundle)
        assert result["repos_count"] == 2
        assert result["summary"]["total_files"] == 4

    def test_json_output_format(self, sample_bundle, tmp_path):
        out = tmp_path / "report.json"
        result = mine_bundle(sample_bundle)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert loaded["repos_count"] == 2
        assert "summary" in loaded

    def test_repo_filter(self, sample_bundle):
        result = mine_bundle(sample_bundle, repo_filter=["NEXUS"])
        assert result["repos_count"] == 1
        assert result["repos"][0]["name"] == "NEXUS"

    def test_extracts_functions_classes_todos(self, sample_bundle):
        result = mine_bundle(sample_bundle)
        nexus = next(r for r in result["repos"] if r["name"] == "NEXUS")
        assert "NexusCore" in nexus["classes"]
        assert "main" in nexus["functions"]
        assert any(t["type"] == "TODO" for t in nexus["todos"])
        assert nexus["has_tests"] is True
        assert nexus["has_config"] is True

    def test_performance_under_10s(self, sample_bundle):
        import time
        t0 = time.perf_counter()
        mine_bundle(sample_bundle)
        elapsed = time.perf_counter() - t0
        assert elapsed < 10.0, "Mining took {:.2f}s > 10s".format(elapsed)

    def test_urbanverse_metadata_extracted(self, sample_bundle):
        result = mine_bundle(sample_bundle)
        nexus = next(r for r in result["repos"] if r["name"] == "NEXUS")
        assert nexus["metadata"].get("strate") == "L1"
        assert nexus["metadata"].get("tier") == "P0"
        assert nexus["metadata"].get("vague_deployee") == "12"
