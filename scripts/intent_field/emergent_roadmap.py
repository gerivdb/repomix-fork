"""EmergentRoadmap — EPIC-13 P3

Lit le MetaClusterMap et produit une roadmap bottom-up
non planifiée : priorités, gaps, risques de dérive, timeline now/next/later.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .metacluster_projector import MetaClusterMap, Cluster, VoidZone, SPOKES
from .coherence_gate import cosine_similarity

# Seuils
HIGH_DENSITY_THRESHOLD  = 0.25   # zone dense → priorité now
MED_DENSITY_THRESHOLD   = 0.12   # zone moyenne → next
DRIFT_DISTANCE_THRESHOLD = 0.55  # distance du centre gravitationnel → risque


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class RoadmapPriority:
    cluster_id: int
    label: str
    density: float
    cohort: str          # now | next | later
    suggested_epic: str
    point_ids: list[str] = field(default_factory=list)


@dataclass
class GapSuggestion:
    zone_id: int
    dominant_spoke: str
    description: str
    suggested_intent: str


@dataclass
class DriftRisk:
    cluster_id: int
    label: str
    distance_from_gravity: float
    repos: list[str] = field(default_factory=list)
    warning: str = ""


@dataclass
class EmergentRoadmap:
    priorities: list[RoadmapPriority]
    gaps: list[GapSuggestion]
    drift_risks: list[DriftRisk]
    timeline: dict[str, list[str]]   # now/next/later → [labels]
    mermaid_roadmap: str
    coherence_reading: str            # texte libre de lecture du champ

    def to_dict(self) -> dict:
        return {
            "priorities": [
                {"cluster_id": p.cluster_id, "label": p.label,
                 "density": p.density, "cohort": p.cohort,
                 "suggested_epic": p.suggested_epic}
                for p in self.priorities
            ],
            "gaps": [
                {"zone_id": g.zone_id, "spoke": g.dominant_spoke,
                 "suggested_intent": g.suggested_intent}
                for g in self.gaps
            ],
            "drift_risks": [
                {"cluster_id": d.cluster_id, "label": d.label,
                 "distance": round(d.distance_from_gravity, 3),
                 "repos": d.repos}
                for d in self.drift_risks
            ],
            "timeline": self.timeline,
        }


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class EmergentRoadmapBuilder:
    """Lit le MetaClusterMap → roadmap bottom-up."""

    def build(self, cluster_map: MetaClusterMap) -> EmergentRoadmap:
        priorities  = self._extract_priorities(cluster_map)
        gaps        = self._extract_gaps(cluster_map)
        drift_risks = self._extract_drift_risks(cluster_map)
        timeline    = self._build_timeline(priorities)
        mermaid     = self._build_mermaid(priorities, gaps, drift_risks)
        reading     = self._build_reading(priorities, gaps, drift_risks, cluster_map)
        return EmergentRoadmap(
            priorities=priorities,
            gaps=gaps,
            drift_risks=drift_risks,
            timeline=timeline,
            mermaid_roadmap=mermaid,
            coherence_reading=reading,
        )

    # ------------------------------------------------------------------
    # Priorités — lecture zones denses
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_priorities(cluster_map: MetaClusterMap) -> list[RoadmapPriority]:
        priorities: list[RoadmapPriority] = []
        gravity_centroids = [gp.coords for gp in cluster_map.gravity_centers] if cluster_map.gravity_centers else []

        for c in sorted(cluster_map.clusters, key=lambda x: x.density, reverse=True):
            cohort = "later"
            if c.density >= HIGH_DENSITY_THRESHOLD:
                cohort = "now"
            elif c.density >= MED_DENSITY_THRESHOLD:
                cohort = "next"

            # Bonus cohort si aligné avec une masse gravitationnelle
            if gravity_centroids:
                best_align = max(
                    cosine_similarity(c.centroid, g) for g in gravity_centroids
                )
                if best_align >= 0.85 and cohort == "later":
                    cohort = "next"

            # Suggérer un EPIC basé sur le label du cluster
            epic_map = {
                "intelligence_agentique": "EPIC-agent-cognition",
                "infrastructure_pipeline": "EPIC-pipeline-infra",
                "formalisation_graphes": "EPIC-graph-formalism",
                "recherche_patterns": "EPIC-research-patterns",
                "champ_flux": "EPIC-field-dynamics",
                "systemes_adaptatifs": "EPIC-adaptive-systems",
            }
            suggested_epic = epic_map.get(c.label_emergent, f"EPIC-{c.label_emergent}")

            # Récupérer les repos impliqués
            point_ids = list(c.points)

            priorities.append(RoadmapPriority(
                cluster_id=c.cluster_id,
                label=c.label_emergent,
                density=c.density,
                cohort=cohort,
                suggested_epic=suggested_epic,
                point_ids=point_ids,
            ))
        return priorities

    # ------------------------------------------------------------------
    # Gaps — lecture zones vides
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_gaps(cluster_map: MetaClusterMap) -> list[GapSuggestion]:
        gap_intent_map = {
            "AI":      "INT-NEW: agent cognitif ou layer sémantique manquant",
            "TECH":    "INT-NEW: pipeline ou infrastructure non couverte",
            "MATH":    "INT-NEW: formalisation graphe/score absente",
            "SCIENCE": "INT-NEW: patterns de recherche non capturés",
            "PHYSICS": "INT-NEW: dynamique de champ ou flux non modelée",
            "BIO":     "INT-NEW: mécanisme adaptatif ou évolutif absent",
        }
        return [
            GapSuggestion(
                zone_id=v.zone_id,
                dominant_spoke=v.dominant_spoke,
                description=v.description,
                suggested_intent=gap_intent_map.get(v.dominant_spoke, "INT-NEW: zone non couverte"),
            )
            for v in cluster_map.void_zones
        ]

    # ------------------------------------------------------------------
    # Risques de dérive — clusters loin des masses
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_drift_risks(cluster_map: MetaClusterMap) -> list[DriftRisk]:
        if not cluster_map.gravity_centers:
            return []
        risks: list[DriftRisk] = []
        gravity_centroids = [gp.coords for gp in cluster_map.gravity_centers]

        for c in cluster_map.clusters:
            best_sim = max(
                (cosine_similarity(c.centroid, g) for g in gravity_centroids),
                default=0.0
            )
            distance = 1.0 - best_sim
            if distance >= DRIFT_DISTANCE_THRESHOLD:
                # Repos impliqués dans ce cluster
                repos = list(dict.fromkeys(
                    p.repo for p in cluster_map.intent_cloud
                    if p.point_id in c.points and not p.is_gravity
                ))
                risks.append(DriftRisk(
                    cluster_id=c.cluster_id,
                    label=c.label_emergent,
                    distance_from_gravity=round(distance, 3),
                    repos=repos,
                    warning=(
                        f"Cluster '{c.label_emergent}' diverge du centre gravitationnel "
                        f"({distance:.0%}). Vérifier alignement ADR/roadmap."
                    ),
                ))
        return sorted(risks, key=lambda r: r.distance_from_gravity, reverse=True)

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    @staticmethod
    def _build_timeline(priorities: list[RoadmapPriority]) -> dict[str, list[str]]:
        timeline: dict[str, list[str]] = {"now": [], "next": [], "later": []}
        for p in priorities:
            timeline[p.cohort].append(p.label)
        return timeline

    # ------------------------------------------------------------------
    # Mermaid
    # ------------------------------------------------------------------

    @staticmethod
    def _build_mermaid(
        priorities: list[RoadmapPriority],
        gaps: list[GapSuggestion],
        drift_risks: list[DriftRisk],
    ) -> str:
        lines = [
            "```mermaid",
            "flowchart TD",
            "",
            "    subgraph NOW[\"\ud83d\udd34 NOW — Priorités immédiates\"]",
        ]
        now_items = [p for p in priorities if p.cohort == "now"]
        next_items = [p for p in priorities if p.cohort == "next"]
        later_items = [p for p in priorities if p.cohort == "later"]

        if now_items:
            for p in now_items:
                safe = p.label.replace("-", "_").replace(" ", "_")
                lines.append(f'        {safe}["{p.label}\\nρ={p.density:.2f}"]')
        else:
            lines.append('        NOW_EMPTY["aucune priorité immédiate"]')
        lines.append("    end")

        lines += ["", '    subgraph NEXT["\ud83d\udfe1 NEXT — Horizon prochain"]']
        if next_items:
            for p in next_items:
                safe = p.label.replace("-", "_").replace(" ", "_")
                lines.append(f'        {safe}_n["{p.label}\\nρ={p.density:.2f}"]')
        else:
            lines.append('        NEXT_EMPTY["aucun cluster next"]')
        lines.append("    end")

        lines += ["", '    subgraph LATER["\u26aa LATER — Horizon long terme"]']
        if later_items:
            for p in later_items:
                safe = p.label.replace("-", "_").replace(" ", "_")
                lines.append(f'        {safe}_l["{p.label}\\nρ={p.density:.2f}"]')
        else:
            lines.append('        LATER_EMPTY["aucun cluster later"]')
        lines.append("    end")

        if gaps:
            lines += ["", '    subgraph GAPS["\u26a0️ GAPS — Zones non couvertes"]']
            for g in gaps[:4]:
                safe = g.dominant_spoke.replace("-", "_")
                lines.append(f'        GAP_{safe}["gap: {g.dominant_spoke}"]')
            lines.append("    end")

        if drift_risks:
            lines += ["", '    subgraph DRIFT["\ud83d\udea8 DRIFT — Risques de dérive"]']
            for r in drift_risks[:3]:
                safe = r.label.replace("-", "_").replace(" ", "_")
                lines.append(f'        DRIFT_{r.cluster_id}["{r.label}\\nΔ={r.distance_from_gravity:.2f}"]')
            lines.append("    end")

        # Styles
        lines += [
            "",
            "    classDef now  fill:#ef4444,color:#fff,stroke:#b91c1c",
            "    classDef next fill:#f59e0b,color:#fff,stroke:#b45309",
            "    classDef later fill:#6b7280,color:#fff,stroke:#374151",
            "    classDef gap  fill:#fef3c7,color:#78350f,stroke:#d97706",
            "    classDef drift fill:#fce7f3,color:#9d174d,stroke:#db2777",
        ]
        for p in now_items:
            safe = p.label.replace("-", "_").replace(" ", "_")
            lines.append(f"    class {safe} now")
        for p in next_items:
            safe = p.label.replace("-", "_").replace(" ", "_")
            lines.append(f"    class {safe}_n next")
        for p in later_items:
            safe = p.label.replace("-", "_").replace(" ", "_")
            lines.append(f"    class {safe}_l later")
        for g in gaps[:4]:
            lines.append(f"    class GAP_{g.dominant_spoke} gap")
        for r in drift_risks[:3]:
            lines.append(f"    class DRIFT_{r.cluster_id} drift")

        lines.append("```")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Lecture du champ (texte libre)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_reading(
        priorities: list[RoadmapPriority],
        gaps: list[GapSuggestion],
        drift_risks: list[DriftRisk],
        cluster_map: MetaClusterMap,
    ) -> str:
        n_repos = len(cluster_map.repos)
        n_intents = len([p for p in cluster_map.intent_cloud if not p.is_gravity])
        now_labels = [p.label for p in priorities if p.cohort == "now"]
        drift_labels = [r.label for r in drift_risks]
        gap_spokes = [g.dominant_spoke for g in gaps]

        parts = [
            f"Le champ metacluster couvre {n_repos} repo(s) avec {n_intents} intent(s) projetés.",
        ]
        if now_labels:
            parts.append(
                f"Les zones à haute densité ({', '.join(now_labels)}) "
                f"indiquent que le champ veut progresser maintenant sur ces dimensions."
            )
        if gap_spokes:
            parts.append(
                f"Gaps structurels détectés sur : {', '.join(gap_spokes)}. "
                f"Ces zones sont non couvertes par aucun intent actuel."
            )
        if drift_labels:
            parts.append(
                f"Risques de dérive sur : {', '.join(drift_labels)}. "
                f"Ces clusters s'éloignent des masses gravitationnelles (ADRs/roadmaps)."
            )
        if not now_labels and not gap_spokes and not drift_labels:
            parts.append(
                "Le champ est homogène et équilibré — aucune tension ou gap majeur détecté."
            )
        return " ".join(parts)
