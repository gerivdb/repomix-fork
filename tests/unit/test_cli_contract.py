"""tests/unit/test_cli_contract.py — PRD-008"""
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "repomix"))

from cli_contract import (
    BundleRequest, BundleResult, OutputFormat, Tier,
    bundle_repo, CLI_SCHEMA, CLI_ENTRYPOINT
)


def test_bundle_request_valid():
    req = BundleRequest(repo="GOVERNANCE-HUB", tier=Tier.P0)
    assert req.validate() == []


def test_bundle_request_empty_repo():
    req = BundleRequest(repo="   ")
    errors = req.validate()
    assert len(errors) == 1
    assert "repo" in errors[0]


def test_cli_schema_structure():
    """Le schema CLI expose les champs requis par ECOS-CLI."""
    assert CLI_SCHEMA["version"] == "1.0.0"
    assert "--repo" in CLI_SCHEMA["args"]
    assert "--tier" in CLI_SCHEMA["args"]
    assert CLI_SCHEMA["args"]["--repo"]["required"] is True
    assert "intent_hash" in CLI_SCHEMA


def test_bundle_result_unknown_repo():
    req = BundleResult(
        success=False, repo="INEXISTANT",
        output_path=None, error="Repo inconnu"
    )
    assert not req.success
    assert req.error is not None
