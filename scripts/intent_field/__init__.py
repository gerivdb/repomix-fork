"""intent_field — EPIC-13 Intent Field / Méta-vectorisation metacluster

Pipeline :
  P0 VibeCrystallizer    — prose libre → IntentDraft vectorisé
  P1 CoherenceGate       — tension vs ADRs + roadmap + φ-CPS gate
  P2 MetaClusterProjector— carte 6D tous repos
  P3 EmergentRoadmap     — roadmap bottom-up depuis le champ

Dépend de : scripts/intent_grapher (EPIC-12)
"""

__version__ = "0.1.0-p0"
__all__ = ["VibeCrystallizer", "IntentDraft"]

from .vibe_crystallizer import VibeCrystallizer, IntentDraft
