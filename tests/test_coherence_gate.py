"""Tests EPIC-13 P1 — CoherenceGate"""
from pathlib import Path

from scripts.intent_field.vibe_crystallizer import VibeCrystallizer
from scripts.intent_field.coherence_gate import CoherenceGate, FieldDocument


VIBE_INT1301 = """
# INT-1301 — Intent Field : Méta-vectorisation & Cohérence Metacluster

> **IntentHash** : `0xINT_FIELD_METACLUSTER_COHERENCE_φ1.301`
> **Statut** : `active`
> **Date** : 2026-06-27
> **EPIC** : EPIC-13
> **φ-CPS delta estimé** : +1.247

## Problème fondamental
Il n'existe pas de couche qui donne aux intents individuels leur cohérence commune
avant qu'ils ne s'exécutent.

## Architecture cible — Intent Field
Le champ metacluster mesure la tension vs ADRs, roadmaps, intents ratifiés.
Projection 6D, clustering, gravité sémantique, roadmap émergente.

gerivdb/NEXUS gerivdb/BRAIN gerivdb/ECOYSTEM gerivdb/ONTOLOGY
Priorité : P0
"""

ADR_0001 = """
# ADR-0001 — Intent Grapher Pipeline

> **IntentHash** : `0xADR_INTENT_GRAPHER_PIPELINE_φ1.001`
> **Statut** : `accepted`
> **φ-CPS** : `4.62`

## Décision
Pipeline Python modulaire : scanner, vectorizer, DAG, scorer, diff, llm_pack.
Intent, semantic depth, constitutional safety, graph, pipeline.
"""

EPIC_13 = """
# EPIC-13 — Intent Field : Méta-vectorisation & Cohérence Metacluster

> **IntentHash** : `0xEPIC_INTENT_FIELD_METACLUSTER_φ1.301`
> **Statut** : `active`
> **φ-CPS** : `4.71`

## P1 — CoherenceGate
Input : IntentDraft + contexte champ (ADRs + roadmap + intents ratifiés)
Output : CoherenceScore
Contraintes comme masses gravitationnelles, roadmap active, champ metacluster.
"""

INT_1211 = """
# INT-1211 — moe router enzyme dispatch

Statut : active
routing intelligence, dispatch, semantic, intent router, agent.
"""

BAD_VIBE = """
# Vibe chaotique

Statut : draft
Juste une idée floue sans phi cps, sans lien roadmap, sans champ commun.
"""


def _mk_doc(doc_id: str, kind: str, status: str, content: str) -> FieldDocument:
    gate = CoherenceGate()
    path = Path(f"{doc_id}.md")
    path.write_text if False else None
    return FieldDocument(
        doc_id=doc_id,
        kind=kind,
        title=doc_id,
        status=status,
        phi_cps=4.62 if "4.62" in content else (4.71 if "4.71" in content else None),
        spoke_scores={
            "AI": 0.7 if "intent" in content.lower() or "semantic" in content.lower() else 0.1,
            "TECH": 0.7 if "pipeline" in content.lower() or "dag" in content.lower() else 0.1,
            "MATH": 0.6 if "phi" in content.lower() or "graph" in content.lower() else 0.1,
            "SCIENCE": 0.2,
            "PHYSICS": 0.6 if "field" in content.lower() or "grav" in content.lower() else 0.1,
            "BIO": 0.1,
        },
        content=content,
    )


def test_phi_gate_ok(tmp_path):
    vibe = tmp_path / "int1301.md"
    vibe.write_text(VIBE_INT1301, encoding="utf-8")
    draft = VibeCrystallizer().crystallize(vibe)
    score = CoherenceGate().evaluate(draft, [], [], [])
    assert score.phi_cps_gate == "OK"


def test_phi_gate_warning_when_missing(tmp_path):
    vibe = tmp_path / "bad.md"
    vibe.write_text(BAD_VIBE, encoding="utf-8")
    draft = VibeCrystallizer().crystallize(vibe)
    score = CoherenceGate().evaluate(draft, [], [], [])
    assert score.phi_cps_gate == "WARNING"


def test_coherence_int1301_vs_adr_and_epic_is_high(tmp_path):
    vibe = tmp_path / "int1301.md"
    vibe.write_text(VIBE_INT1301, encoding="utf-8")
    draft = VibeCrystallizer().crystallize(vibe)

    adr = _mk_doc("ADR-0001", "adr", "accepted", ADR_0001)
    epic = _mk_doc("EPIC-13", "epic", "active", EPIC_13)
    intent = _mk_doc("INT-1211", "intent", "active", INT_1211)

    score = CoherenceGate().evaluate(draft, [adr], [epic], [intent])
    assert score.coherence_score >= 0.55
    assert score.tension_adr <= 0.6
    assert score.tension_roadmap <= 0.6
    assert score.verdict in {"RATIFY", "REVISE"}


def test_overlap_ids_detected(tmp_path):
    vibe = tmp_path / "int1301.md"
    vibe.write_text(VIBE_INT1301, encoding="utf-8")
    draft = VibeCrystallizer().crystallize(vibe)
    similar_intent = _mk_doc("INT-1211", "intent", "active", "intent semantic agent routing field graph")
    score = CoherenceGate().evaluate(draft, [], [], [similar_intent])
    assert "INT-1211" in score.overlap_ids or score.tension_intents < 0.5


def test_bad_vibe_not_ratified(tmp_path):
    vibe = tmp_path / "bad.md"
    vibe.write_text(BAD_VIBE, encoding="utf-8")
    draft = VibeCrystallizer().crystallize(vibe)
    adr = _mk_doc("ADR-0001", "adr", "accepted", ADR_0001)
    epic = _mk_doc("EPIC-13", "epic", "active", EPIC_13)
    score = CoherenceGate().evaluate(draft, [adr], [epic], [])
    assert score.verdict in {"REVISE", "REJECT"}


def test_suggestions_include_phi_when_missing(tmp_path):
    vibe = tmp_path / "bad.md"
    vibe.write_text(BAD_VIBE, encoding="utf-8")
    draft = VibeCrystallizer().crystallize(vibe)
    score = CoherenceGate().evaluate(draft, [], [], [])
    joined = " ".join(score.suggestions).lower()
    assert "φ-cps" in joined or "phi-cps" in joined


def test_load_field_documents(tmp_path):
    adr_path = tmp_path / "ADR-0001.md"
    epic_path = tmp_path / "EPIC-13.md"
    intent_path = tmp_path / "INT-1211.md"
    adr_path.write_text(ADR_0001, encoding="utf-8")
    epic_path.write_text(EPIC_13, encoding="utf-8")
    intent_path.write_text(INT_1211, encoding="utf-8")

    docs = CoherenceGate().load_field_documents([adr_path, epic_path, intent_path])
    assert len(docs) == 3
    kinds = {d.kind for d in docs}
    assert "intent" in kinds


def test_to_dict_shape(tmp_path):
    vibe = tmp_path / "int1301.md"
    vibe.write_text(VIBE_INT1301, encoding="utf-8")
    draft = VibeCrystallizer().crystallize(vibe)
    score = CoherenceGate().evaluate(draft, [], [], [])
    data = score.to_dict()
    assert "phi_cps_gate" in data
    assert "coherence_score" in data
    assert "verdict" in data
