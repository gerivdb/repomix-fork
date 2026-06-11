"""tests/unit/test_relay_propagator_v2.py — PRD-10 (Vague 2+3)"""
import json
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.relay_propagator import (
    propagate, _render_relay, _render_relay_v2, _render_relay_v3,
    PILOT_REPOS, FIBRE_REPOS, LOCAL_RULES, KARPATHY_5Q, KARPATHY_10Q
)


class TestVague2:
    def test_vague2_10_pilots(self, tmp_path):
        """Vague 2 couvre les 10 repos pilotes."""
        results = propagate(dry_run=False, output_dir=tmp_path, vague=2)
        assert results["vague"] == 2
        assert len(results["generated"]) == 10

    def test_vague2_has_local_rules(self, tmp_path):
        """Chaque relay Vague 2 a 5 règles locales spécifiques."""
        results = propagate(dry_run=False, output_dir=tmp_path, vague=2)
        for repo_name in results["generated"]:
            f = tmp_path / "{}__STRATUM_RELAY_v2.md".format(repo_name)
            content = f.read_text(encoding="utf-8")
            assert "Regles locales (structurees)" in content
            # Vérifier que les 5 règles sont présentes
            rules = LOCAL_RULES.get(repo_name, [])
            for rule in rules:
                rule_short = rule.split(" — ")[1] if " — " in rule else rule
                assert rule_short in content or rule[:20] in content, \
                    "Regle manquante pour {}: {}".format(repo_name, rule[:40])

    def test_vague2_has_5q_karpathy(self, tmp_path):
        """Chaque relay Vague 2 a 5Q Karpathy spécifiques."""
        results = propagate(dry_run=False, output_dir=tmp_path, vague=2)
        for repo_name in results["generated"]:
            f = tmp_path / "{}__STRATUM_RELAY_v2.md".format(repo_name)
            content = f.read_text(encoding="utf-8")
            assert "Karpathy-Recall local (5Q specifiques)" in content
            qa = KARPATHY_5Q.get(repo_name, [])
            # Vérifier que la première question est présente
            if qa:
                assert qa[0][0] in content, \
                    "Q1 manquante pour {}".format(repo_name)

    def test_vague2_connectivite_dsl_plus(self, tmp_path):
        """Vague 2 a connectivite DSL+ (pas FIBRE comme connectivité active)."""
        results = propagate(dry_run=False, output_dir=tmp_path, vague=2)
        f = tmp_path / "{}__STRATUM_RELAY_v2.md".format(results["generated"][0])
        content = f.read_text(encoding="utf-8")
        # La connectivité active est DSL, pas FIBRE (FIBRE est mentionnée comme "prochaine vague")
        assert "Connectivite** : DSL" in content
        assert "Connectivite** : FIBRE" not in content


class TestVague3:
    def test_vague3_fibre_5_repos(self, tmp_path):
        """Vague 3 fibre-only couvre exactement 5 repos."""
        results = propagate(dry_run=False, output_dir=tmp_path, vague=3, fibre_only=True)
        assert results["vague"] == 3
        assert len(results["generated"]) == 5
        assert set(results["generated"]) == set(FIBRE_REPOS)

    def test_vague3_has_fibre_flag(self, tmp_path):
        """Vague 3 a la connectivité FIBRE."""
        results = propagate(dry_run=False, output_dir=tmp_path, vague=3, fibre_only=True)
        for repo_name in results["generated"]:
            f = tmp_path / "{}__STRATUM_RELAY_v3.md".format(repo_name)
            content = f.read_text(encoding="utf-8")
            assert "FIBRE (Full Interconnect Bundle for Repository Emergence)" in content

    def test_vague3_has_10q_karpathy(self, tmp_path):
        """Vague 3 a 10Q Karpathy (5 de V2 + 5 supplémentaires)."""
        results = propagate(dry_run=False, output_dir=tmp_path, vague=3, fibre_only=True)
        for repo_name in results["generated"]:
            f = tmp_path / "{}__STRATUM_RELAY_v3.md".format(repo_name)
            content = f.read_text(encoding="utf-8")
            assert "Karpathy-Recall local (10Q specifiques)" in content
            # Compter les questions (format "N. question")
            import re
            questions = re.findall(r'^\d+\. ', content, re.MULTILINE)
            assert len(questions) == 10, \
                "Attendu 10Q pour {}, trouvé {}".format(repo_name, len(questions))

    def test_vague3_has_dependencies(self, tmp_path):
        """Vague 3 a la section Dépendances."""
        results = propagate(dry_run=False, output_dir=tmp_path, vague=3, fibre_only=True)
        for repo_name in results["generated"]:
            f = tmp_path / "{}__STRATUM_RELAY_v3.md".format(repo_name)
            content = f.read_text(encoding="utf-8")
            assert "## Dependances" in content

    def test_vague3_has_fibre_connectivity(self, tmp_path):
        """Vague 3 a la section Connectivité FIBRE avec les 4 sous-sections."""
        results = propagate(dry_run=False, output_dir=tmp_path, vague=3, fibre_only=True)
        f = tmp_path / "{}__STRATUM_RELAY_v3.md".format(results["generated"][0])
        content = f.read_text(encoding="utf-8")
        assert "Connectivite FIBRE" in content
        assert "Recall packs" in content
        assert "Cadastre" in content
        assert "Score emergence" in content

    def test_vague3_manifest(self, tmp_path):
        """Le manifeste Vague 3 a les bons champs."""
        propagate(dry_run=False, output_dir=tmp_path, vague=3, fibre_only=True)
        manifest = json.loads((tmp_path / "relay_manifest_v3.json").read_text())
        assert manifest["vague"] == 3
        assert manifest["connectivite"] == "FIBRE"
        assert manifest["fibre_only"] is True
        assert manifest["count"] == 5
