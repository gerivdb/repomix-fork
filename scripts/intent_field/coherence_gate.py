"""CoherenceGate — EPIC-13 P1

Mesure la tension d'un IntentDraft avec les contraintes du champ :
- ADRs accepted (masses fortes)
- roadmaps / EPICs actives (masses moyennes)
- intents ratifiés existants (chevauchement)
- gate φ-CPS non négociable

Input  : IntentDraft + contexte du champ
Output : CoherenceScore
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .vibe_crystallizer import IntentDraft, PHI_CPS_HARD_THRESHOLD


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class FieldDocument:
    doc_id: str
    kind: str                 # adr | epic | intent
    title: str
    status: str
    phi_cps: Optional[float] = None
    spoke_scores: dict[str, float] = field(default_factory=dict)
    content: str = ""


@dataclass
class CoherenceScore:
    phi_cps_gate: str                 # OK | KO | WARNING
    tension_adr: float                # 0=aligné, 1=conflit
    tension_roadmap: float
    tension_intents: float
    overlap_ids: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    verdict: str = "REVISE"          # RATIFY | REVISE | REJECT
    coherence_score: float = 0.0      # score global 0→1

    def to_dict(self) -> dict:
        return {
            "phi_cps_gate": self.phi_cps_gate,
            "tension_adr": round(self.tension_adr, 3),
            "tension_roadmap": round(self.tension_roadmap, 3),
            "tension_intents": round(self.tension_intents, 3),
            "overlap_ids": self.overlap_ids,
            "suggestions": self.suggestions,
            "verdict": self.verdict,
            "coherence_score": round(self.coherence_score, 3),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = math.sqrt(sum(a.get(k, 0.0) ** 2 for k in keys))
    nb = math.sqrt(sum(b.get(k, 0.0) ** 2 for k in keys))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _extract_title(content: str) -> str:
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else "unknown"


def _extract_status(content: str) -> str:
    m = re.search(r"Statut[^:]*:[^`]*`([^`]+)`", content, re.IGNORECASE)
    if m:
        return m.group(1).strip().lower()
    m = re.search(r"Statut\s*:\s*([^\n]{2,40})", content, re.IGNORECASE)
    return m.group(1).strip().lower() if m else "unknown"


def _extract_phi_cps(content: str) -> Optional[float]:
    m = re.search(r"φ[-_]?CPS[^\d]*(\d+\.\d+)", content, re.IGNORECASE)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def _simple_spoke_scores(content: str) -> dict[str, float]:
    text = content.lower()
    keywords = {
        "AI": ["intent", "semantic", "agent", "memory", "skill", "llm", "rag"],
        "TECH": ["pipeline", "cli", "api", "git", "worktree", "acp", "emit", "dag"],
        "MATH": ["phi", "score", "graph", "vector", "cluster", "weight", "cosine"],
        "SCIENCE": ["research", "pattern", "signal", "trajectory"],
        "PHYSICS": ["field", "gravity", "mass", "flow"],
        "BIO": ["enzyme", "evolv", "adapt", "mutation"],
    }
    scores = {}
    for spoke, kws in keywords.items():
        hits = sum(1 for kw in kws if kw in text)
        scores[spoke] = min(hits / max(len(kws), 1), 1.0)
    return scores


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------

class CoherenceGate:
    """Mesure la cohérence d'un IntentDraft face au champ existant."""

    def __init__(self, adr_mass: float = 1.0, roadmap_mass: float = 0.7, intent_mass: float = 0.6):
        self.adr_mass = adr_mass
        self.roadmap_mass = roadmap_mass
        self.intent_mass = intent_mass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        draft: IntentDraft,
        adrs: list[FieldDocument],
        roadmaps: list[FieldDocument],
        ratified_intents: list[FieldDocument],
    ) -> CoherenceScore:
        phi_gate = self._phi_gate(draft)
        tension_adr = self._compute_mass_tension(draft, adrs, self.adr_mass)
        tension_roadmap = self._compute_mass_tension(draft, roadmaps, self.roadmap_mass)
        tension_intents, overlaps = self._compute_intent_overlap(draft, ratified_intents)
        suggestions = self._build_suggestions(phi_gate, tension_adr, tension_roadmap, tension_intents, overlaps)
        coherence_score = self._compute_global_score(phi_gate, tension_adr, tension_roadmap, tension_intents)
        verdict = self._verdict(phi_gate, coherence_score, tension_adr, tension_roadmap, tension_intents)
        return CoherenceScore(
            phi_cps_gate=phi_gate,
            tension_adr=tension_adr,
            tension_roadmap=tension_roadmap,
            tension_intents=tension_intents,
            overlap_ids=overlaps,
            suggestions=suggestions,
            verdict=verdict,
            coherence_score=coherence_score,
        )

    def load_field_documents(self, paths: list[Path]) -> list[FieldDocument]:
        docs: list[FieldDocument] = []
        for path in paths:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            kind = self._kind_from_path(path)
            title = _extract_title(content)
            status = _extract_status(content)
            phi = _extract_phi_cps(content)
            docs.append(FieldDocument(
                doc_id=path.stem,
                kind=kind,
                title=title,
                status=status,
                phi_cps=phi,
                spoke_scores=_simple_spoke_scores(content),
                content=content,
            ))
        return docs

    # ------------------------------------------------------------------
    # Core computations
    # ------------------------------------------------------------------

    @staticmethod
    def _phi_gate(draft: IntentDraft) -> str:
        if not draft.phi_cps_mentions:
            return "WARNING"
        if max(draft.phi_cps_mentions) >= PHI_CPS_HARD_THRESHOLD:
            return "OK"
        return "KO"

    def _compute_mass_tension(
        self,
        draft: IntentDraft,
        docs: list[FieldDocument],
        mass_weight: float,
    ) -> float:
        if not docs:
            return 0.35
        accepted_docs = [d for d in docs if d.status in {"accepted", "active"}]
        if not accepted_docs:
            accepted_docs = docs

        # Plus la similarité avec une masse est forte, plus la tension est basse
        sims = []
        for doc in accepted_docs:
            sim = cosine_similarity(draft.spoke_scores, doc.spoke_scores)
            sims.append(sim)
        best_sim = max(sims) if sims else 0.0
        tension = 1.0 - best_sim
        tension *= mass_weight
        return max(0.0, min(round(tension, 3), 1.0))

    def _compute_intent_overlap(
        self,
        draft: IntentDraft,
        intents: list[FieldDocument],
    ) -> tuple[float, list[str]]:
        if not intents:
            return 0.25, []
        overlaps: list[tuple[str, float]] = []
        sims = []
        for doc in intents:
            sim = cosine_similarity(draft.spoke_scores, doc.spoke_scores)
            sims.append(sim)
            if sim >= 0.65:
                overlaps.append((doc.doc_id, sim))
        tension = 1.0 - (max(sims) if sims else 0.0)
        tension *= self.intent_mass
        overlaps_sorted = [doc_id for doc_id, _ in sorted(overlaps, key=lambda x: x[1], reverse=True)]
        return max(0.0, min(round(tension, 3), 1.0)), overlaps_sorted[:5]

    @staticmethod
    def _build_suggestions(
        phi_gate: str,
        tension_adr: float,
        tension_roadmap: float,
        tension_intents: float,
        overlaps: list[str],
    ) -> list[str]:
        suggestions: list[str] = []
        if phi_gate == "KO":
            suggestions.append("Ajouter ou relever un φ-CPS explicite au-dessus du seuil 4.559 avant ratification.")
        elif phi_gate == "WARNING":
            suggestions.append("Documenter un φ-CPS explicite pour éviter une ratification aveugle.")

        if tension_adr > 0.4:
            suggestions.append("Relire les ADRs accepted : divergence significative avec une masse forte du champ.")
        if tension_roadmap > 0.45:
            suggestions.append("Rattacher l'intent à un EPIC/roadmap active ou expliciter pourquoi il ouvre une nouvelle branche de champ.")
        if overlaps:
            suggestions.append(f"Fusion/synergie possible avec : {', '.join(overlaps[:3])}.")
        elif tension_intents > 0.5:
            suggestions.append("Intent très isolé : vérifier qu'il ne réinvente pas un pattern déjà latent ailleurs dans le metacluster.")
        return suggestions

    @staticmethod
    def _compute_global_score(
        phi_gate: str,
        tension_adr: float,
        tension_roadmap: float,
        tension_intents: float,
    ) -> float:
        base = 1.0 - ((tension_adr * 0.4) + (tension_roadmap * 0.35) + (tension_intents * 0.25))
        if phi_gate == "OK":
            base += 0.08
        elif phi_gate == "KO":
            base -= 0.35
        score = max(0.0, min(base, 1.0))
        return round(score, 3)

    @staticmethod
    def _verdict(
        phi_gate: str,
        coherence_score: float,
        tension_adr: float,
        tension_roadmap: float,
        tension_intents: float,
    ) -> str:
        if phi_gate == "KO":
            return "REJECT"
        if coherence_score >= 0.85 and tension_adr <= 0.4 and tension_roadmap <= 0.45:
            return "RATIFY"
        if coherence_score >= 0.55:
            return "REVISE"
        return "REJECT"

    @staticmethod
    def _kind_from_path(path: Path) -> str:
        s = str(path).lower()
        if "/adr/" in s or s.startswith("adr/"):
            return "adr"
        if "epic" in path.name.lower() or "/prd/" in s:
            return "epic"
        return "intent"
