"""
test_bundle_generator.py — Tests unitaires pour bundle_generator (EPIC-239 Phase 3)
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ajouter le path de repomix-fork
sys.path.insert(0, r"D:\DO\WEB\TOOLS\L4-TOOLS\REPOMIX-FORK\src")

from repomix.core.bundle.bundle_generator import BundleGenerator, BundleComponent


class TestBundleComponent:
    """Tests pour BundleComponent."""

    def test_create_component(self):
        comp = BundleComponent(
            name="test-service",
            path="services/test",
            kind="service",
            entry_point="main.py",
            dependencies=["requests", "flask"],
        )
        assert comp.name == "test-service"
        assert comp.kind == "service"
        assert comp.entry_point == "main.py"
        assert len(comp.dependencies) == 2

    def test_to_dict(self):
        comp = BundleComponent(name="lib", path="libs/lib", kind="library")
        d = comp.to_dict()
        assert d["name"] == "lib"
        assert d["kind"] == "library"
        assert d["entry_point"] is None
        assert d["dependencies"] == []

    def test_defaults(self):
        comp = BundleComponent(name="x", path="y/z")
        assert comp.kind == "service"
        assert comp.dependencies == []
        assert comp.metadata == {}


class TestBundleGenerator:
    """Tests pour BundleGenerator."""

    def test_detect_strate_by_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Créer une structure simulée
            repo_path = Path(tmp) / "L4-TOOLS" / "test-repo"
            repo_path.mkdir(parents=True)

            gen = BundleGenerator(str(repo_path))
            assert gen._detect_strate() == "L4-TOOLS"

    def test_detect_strate_l0(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = Path(tmp) / "L0-CANON" / "nexus"
            repo_path.mkdir(parents=True)

            gen = BundleGenerator(str(repo_path))
            assert gen._detect_strate() == "L0-CANON"

    def test_detect_strate_l3(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = Path(tmp) / "L3-CITIZENS" / "fluence"
            repo_path.mkdir(parents=True)

            gen = BundleGenerator(str(repo_path))
            assert gen._detect_strate() == "L3-CITIZENS"

    def test_detect_strate_auto_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = Path(tmp) / "unknown-path" / "myrepo"
            repo_path.mkdir(parents=True)

            gen = BundleGenerator(str(repo_path))
            assert gen._detect_strate() == "L4-TOOLS"  # Défaut

    def test_scan_subrepos(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = Path(tmp) / "L4-TOOLS" / "mono-repo"
            repo_path.mkdir(parents=True)

            # Créer un sous-repo
            sub = repo_path / "sub-service"
            sub.mkdir()
            (sub / ".git").mkdir()  # Simuler un repo git
            (sub / "main.py").write_text("# main", encoding="utf-8")

            gen = BundleGenerator(str(repo_path))
            gen.analyze()

            assert len(gen.components) >= 1
            assert gen.components[0].name == "sub-service"

    def test_generate_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = Path(tmp) / "L4-TOOLS" / "test-bundle"
            repo_path.mkdir(parents=True)

            # Créer un fichier pour simuler un repo
            (repo_path / "README.md").write_text("# Test", encoding="utf-8")

            gen = BundleGenerator(str(repo_path))
            gen.analyze()
            bundle = gen.generate(actor="test:user")

            assert bundle["schema_version"] == "1.0.0"
            assert bundle["source_repo"] == str(repo_path.resolve())
            assert bundle["target_strate"] == "L4-TOOLS"
            assert bundle["actor"] == "test:user"
            assert bundle["component_count"] >= 1
            assert bundle["intent_hash"].startswith("0xBUNDLE_")
            assert len(bundle["bundle_id"]) == 16

    def test_write_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = Path(tmp) / "L4-TOOLS" / "test-write"
            repo_path.mkdir(parents=True)
            (repo_path / "README.md").write_text("# Test", encoding="utf-8")

            output = Path(tmp) / "output" / "test.bundle.kiva.json"

            gen = BundleGenerator(str(repo_path))
            gen.analyze()
            result_path = gen.write(output_path=str(output), actor="test:user")

            assert result_path.exists()
            with open(result_path, "r", encoding="utf-8") as f:
                bundle = json.load(f)
            assert bundle["schema_version"] == "1.0.0"
            assert bundle["component_count"] >= 1

    def test_detect_component_kind_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            comp_path = Path(tmp) / "my-lib"
            comp_path.mkdir()
            (comp_path / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
            (comp_path / "src").mkdir()

            gen = BundleGenerator(tmp)
            assert gen._detect_component_kind(comp_path) == "library"

    def test_detect_component_kind_service(self):
        with tempfile.TemporaryDirectory() as tmp:
            comp_path = Path(tmp) / "my-svc"
            comp_path.mkdir()
            (comp_path / "package.json").write_text('{"name":"test"}', encoding="utf-8")

            gen = BundleGenerator(tmp)
            assert gen._detect_component_kind(comp_path) == "service"

    def test_find_entry_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            comp_path = Path(tmp) / "my-svc"
            comp_path.mkdir()
            (comp_path / "src").mkdir()
            (comp_path / "src" / "main.py").write_text("# main", encoding="utf-8")

            gen = BundleGenerator(tmp)
            entry = gen._find_entry_point(comp_path)
            assert entry == "src/main.py"

    def test_extract_dependencies_pyproject(self):
        with tempfile.TemporaryDirectory() as tmp:
            comp_path = Path(tmp) / "my-lib"
            comp_path.mkdir()
            (comp_path / "pyproject.toml").write_text(
                '[project]\ndependencies = ["requests>=2.0", "flask"]\n',
                encoding="utf-8",
            )

            gen = BundleGenerator(tmp)
            deps = gen._extract_dependencies(comp_path)
            assert "requests>=2.0" in deps
            assert "flask" in deps

    def test_extract_dependencies_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            comp_path = Path(tmp) / "my-lib"
            comp_path.mkdir()
            (comp_path / "requirements.txt").write_text(
                "requests==2.28.0\nflask>=2.0\n# comment\nnumpy\n",
                encoding="utf-8",
            )

            gen = BundleGenerator(tmp)
            deps = gen._extract_dependencies(comp_path)
            assert "requests" in deps
            assert "flask" in deps
            assert "numpy" in deps
            assert "# comment" not in deps

    def test_nonexistent_path_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_path = Path(tmp) / "nonexistent"
            gen = BundleGenerator(str(fake_path))
            with pytest.raises(FileNotFoundError):
                gen.analyze()

    def test_bundle_has_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = Path(tmp) / "L4-TOOLS" / "test-fields"
            repo_path.mkdir(parents=True)
            (repo_path / "README.md").write_text("# Test", encoding="utf-8")

            gen = BundleGenerator(str(repo_path))
            gen.analyze()
            bundle = gen.generate(actor="test:user")

            required = [
                "schema_version", "bundle_id", "created_at", "actor",
                "source_repo", "target_strate", "intent_hash",
                "component_count", "components", "metadata",
            ]
            for field in required:
                assert field in bundle, f"Missing required field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
