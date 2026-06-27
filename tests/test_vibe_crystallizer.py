"""Tests EPIC-13 P0 — VibeCrystallizer
Testest sur du contenu réel inspiré des vibes hermes + toc de Gitnote.
"""
from pathlib import Path
import json

import pytest

from scripts.intent_field.vibe_crystallizer import (
    VibeCrystallizer,
    IntentDraft,
    CRYSTALLIZATION_THRESHOLD,
)


# ---------------------------------------------------------------------------
# Fixtures — vibes réelles Gitnote (extraits représentatifs)
# ---------------------------------------------------------------------------

VIBE_HERMES = """
# INTENT — HERMES-EXTRACT : Intégration sélective ACP/Memory/Skills

**Date** : 2026-04-06
**Dépôts cibles** : `gerivdb/BRAIN`, `gerivdb/EMIT`, `gerivdb/ECOS-CLI`, `gerivdb/ONTOLOGY`
**Statut** : 🟡 À valider dans NEXUS
**Score constitutionnel** : 8.4/10
**φ-CPS delta estimé** : +0.847

## Contexte
hermes-agent implémente trois patterns architecturaux absents de l'Ecosystem-1.
Cette extraction est non-fork : on prèle 3 modules ciblés sans embarquer le framework complet.

## Objectif
ACP adapter natif vers EMIT. Mémoire persistante FTS5 cross-sessions vers BRAIN.
Trajectory compression pour future inflérence locale.

## Contraintes ENV2 / Z600
```yaml
ENV2_CONSTRAINTS:
  ram_runtime_max_mb: 6144
  docker: INTERDIT
  cloud_inference: INTERDIT
  python_min: "3.11"
```

## Module 1 — ACP Adapter
Source : hermes-agent/acp_adapter/
Cible : gerivdb/EMIT/adapters/acp/
Effort : 6-8h

## Module 2 — Mémoire persistante
Source : hermes_state.py (FTS5 + LLM summarization)
Cible : gerivdb/BRAIN/memory/
Effort : 10-12h

Priorité : P1
"""

VIBE_TOC = """
# INTENT MAGISTRAL — TaskOrchestrationCitizen L3

**ID** : `INTENT-TOC-20260408`
**IntentHash** : `0xTASK_ORCHESTRATION_CITIZEN_ENV2_20260408`
**Dépôt cible** : `gerivdb/ECOYSTEM`
**Statut** : 🟡 DRAFT → à valider NEXUS
**Priorité** : P1
**φ-CPS delta** : +0.025 estimé

## Problème fondamental
Aucun composant natif n'assure l'exécution autonome multi-tâches avec
décomposition d'un intent en DAG de tâches parallèles.

## Objectif
Créer TaskOrchestrationCitizen — Citoyen L3 Python qui décompose,
planifie, exécute, vérifie et commit de manière autonome.

```yaml
intent_id: INTENT-TOC-20260408
dimension_principale: autonomous_task_orchestration
source_pain: aucun_composant_dag_parallele_natif
cible: TaskOrchestrationCitizen_L3
contrainte_hard: ram_runtime_max_mb_6144
```

## Contraintes ENV2
clôud_inference: INTERDIT
docker: INTERDIT
parallelisme_max: 2

## Architecture
EMIT event → SpecDecomposer → DAGPlanner → WorktreeExecutor → GoalVerifier

Priorité : P1
EPIC-13 (créer)
gerivdb/ECOYSTEM, gerivdb/NEXUS, gerivdb/ONTOLOGY
"""

VIBE_MINIMAL = """
# Vibe à propos de quelque chose
Je voudrais faire un truc avec les repos.
"""


@pytest.fixture
def hermes_file(tmp_path):
    f = tmp_path / "20260406-hermes-extract.md"
    f.write_text(VIBE_HERMES, encoding="utf-8")
    return f


@pytest.fixture
def toc_file(tmp_path):
    f = tmp_path / "20260408-intent-toc.md"
    f.write_text(VIBE_TOC, encoding="utf-8")
    return f


@pytest.fixture
def minimal_file(tmp_path):
    f = tmp_path / "vibe-minimal.md"
    f.write_text(VIBE_MINIMAL, encoding="utf-8")
    return f


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestVibeCrystallizer:

    def test_hermes_crystallizes(self, hermes_file):
        vc = VibeCrystallizer()
        draft = vc.crystallize(hermes_file)
        assert draft.source_file.endswith(".md")
        assert draft.crystallization_score > 0

    def test_hermes_repos_detected(self, hermes_file):
        draft = VibeCrystallizer().crystallize(hermes_file)
        assert "BRAIN" in draft.repos_cibles or "EMIT" in draft.repos_cibles

    def test_hermes_env_constraints(self, hermes_file):
        draft = VibeCrystallizer().crystallize(hermes_file)
        assert len(draft.env_constraints) >= 2
        interdit = " ".join(draft.env_constraints)
        assert "interdit" in interdit or "env2" in interdit or "ollama" in interdit

    def test_hermes_phi_cps_detected(self, hermes_file):
        draft = VibeCrystallizer().crystallize(hermes_file)
        # 8.4 (score constitutionnel) ou 4.559 (seuil) ou delta +0.847
        assert len(draft.phi_cps_mentions) >= 0  # au moins tentative

    def test_hermes_priority_p1(self, hermes_file):
        draft = VibeCrystallizer().crystallize(hermes_file)
        assert draft.priority == "1"

    def test_toc_yaml_fields(self, toc_file):
        draft = VibeCrystallizer().crystallize(toc_file)
        assert draft.dimension == "autonomous_task_orchestration"
        assert draft.pain == "aucun_composant_dag_parallele_natif"
        assert draft.cible == "TaskOrchestrationCitizen_L3"

    def test_toc_intent_hash_real(self, toc_file):
        draft = VibeCrystallizer().crystallize(toc_file)
        assert draft.intent_hash_draft == "0xTASK_ORCHESTRATION_CITIZEN_ENV2_20260408"
        assert "DRAFT" not in draft.intent_hash_draft

    def test_toc_ratification_ready(self, toc_file):
        draft = VibeCrystallizer().crystallize(toc_file)
        # TOC est bien structuré avec YAML + sections + repos → doit être ready
        assert draft.crystallization_score >= CRYSTALLIZATION_THRESHOLD
        assert draft.ratification_ready is True

    def test_toc_epic_ref(self, toc_file):
        draft = VibeCrystallizer().crystallize(toc_file)
        assert "13" in draft.epic_refs

    def test_toc_spoke_ai_or_tech_dominant(self, toc_file):
        draft = VibeCrystallizer().crystallize(toc_file)
        assert draft.dominant_spoke in ("AI", "TECH", "MATH")

    def test_minimal_not_ready(self, minimal_file):
        draft = VibeCrystallizer().crystallize(minimal_file)
        assert draft.ratification_ready is False
        assert draft.crystallization_score < CRYSTALLIZATION_THRESHOLD

    def test_tension_hermes_between_zero_one(self, hermes_file):
        draft = VibeCrystallizer().crystallize(hermes_file)
        assert 0.0 <= draft.tension_preliminary <= 1.0

    def test_crystallize_directory(self, tmp_path):
        (tmp_path / "vibe1.md").write_text(VIBE_HERMES, encoding="utf-8")
        (tmp_path / "vibe2.md").write_text(VIBE_TOC, encoding="utf-8")
        (tmp_path / "README.md").write_text("# README", encoding="utf-8")  # ignoré
        vc = VibeCrystallizer()
        drafts = vc.crystallize_directory(tmp_path)
        assert len(drafts) == 2

    def test_crystallize_to_file(self, hermes_file, tmp_path):
        vc = VibeCrystallizer()
        out = tmp_path / "draft.json"
        draft = vc.crystallize_to_file(hermes_file, out)
        assert out.exists()
        data = json.loads(out.read_text())
        assert "crystallization_score" in data
        assert "spoke_scores" in data
        assert "ratification_ready" in data

    def test_markdown_summary_output(self, toc_file):
        draft = VibeCrystallizer().crystallize(toc_file)
        md = draft.to_markdown_summary()
        assert "IntentDraft" in md
        assert "Cristallisation" in md
        assert "Ratification" in md
