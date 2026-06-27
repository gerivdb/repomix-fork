"""MetaClusterProjector — EPIC-13 P2

Projecte tous les intents du metacluster gerivdb/* dans un espace
sémantique 6D commun, cluster par gravité et détecte zones vides.

Input  : liste de (repo_name, IntentDraft | FieldDocument)
Output : MetaClusterMap {
    repos, intent_cloud, clusters,
    gravity_centers, void_zones, density_map
}

Dépendances : stdlib uniquement (pas de sklearn).
Fallback cosine manuel — ENV2 compliant.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Optional, Union

from .vibe_crystallizer import IntentDraft
from .coherence_gate import FieldDocument, cosine_similarity

# 6 spokes de l'espace ontologique
SPOKES = ["AI", "TECH", "MATH", "SCIENCE", "PHYSICS", "BIO"]

# Poids × 3 pour les masses gravitationnelles (ADRs accepted)
ADR_MASS_WEIGHT = 3.0
ROADMAP_MASS_WEIGHT = 1.8

# Seuil de similarité pour appartenance à un cluster
CLUSTER_SIM_THRESHOLD = 0.55

# Seuil de densité sous lequel une zone est considérée vide
VOID_DENSITY_THRESHOLD = 0.05

# Max itérations k-means-like
KMEANS_ITERS = 15


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class IntentPoint:
    """Un intent projeté dans l'espace 6D."""
    point_id: str
    repo: str
    coords: dict[str, float]        # spoke → score
    kind: str                        # intent | adr | epic | vibe
    status: str = "unknown"
    cluster_id: Optional[int] = None
    is_gravity: bool = False         # True si masse gravitationnelle
    gravity_weight: float = 1.0


@dataclass
class Cluster:
    cluster_id: int
    centroid: dict[str, float]
    points: list[str] = field(default_factory=list)   # point_ids
    label_emergent: str = ""
    density: float = 0.0


@dataclass
class VoidZone:
    zone_id: int
    dominant_spoke: str
    description: str
    coords_approx: dict[str, float] = field(default_factory=dict)


@dataclass
class MetaClusterMap:
    repos: list[str]
    intent_cloud: list[IntentPoint]
    clusters: list[Cluster]
    gravity_centers: list[IntentPoint]   # ADRs + roadmaps
    void_zones: list[VoidZone]
    density_map: dict[str, float]         # spoke → densité

    def summary(self) -> str:
        lines = [
            f"## MetaClusterMap — {len(self.repos)} repos",
            f"",
            f"| Métrique | Valeur |",
            f"|---|---|",
            f"| Intents dans le cloud | {len(self.intent_cloud)} |",
            f"| Clusters détectés | {len(self.clusters)} |",
            f"| Masses gravitationnelles | {len(self.gravity_centers)} |",
            f"| Zones vides (gaps) | {len(self.void_zones)} |",
            f"",
            f"### Densité par spoke",
        ]
        for spoke, density in sorted(self.density_map.items(), key=lambda x: -x[1]):
            bar = "█" * int(density * 10) + "░" * (10 - int(density * 10))
            lines.append(f"- **{spoke}** {bar} `{density:.2f}`")
        if self.clusters:
            lines += ["", "### Clusters émergents"]
            for c in self.clusters:
                lines.append(f"- **C{c.cluster_id}** `{c.label_emergent}` — {len(c.points)} intents (densité `{c.density:.2f}`)")
        if self.void_zones:
            lines += ["", "### Zones vides (gaps)"]
            for v in self.void_zones:
                lines.append(f"- **Gap-{v.zone_id}** `{v.dominant_spoke}` : {v.description}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "repos": self.repos,
            "intent_count": len(self.intent_cloud),
            "cluster_count": len(self.clusters),
            "gravity_count": len(self.gravity_centers),
            "void_zone_count": len(self.void_zones),
            "density_map": {k: round(v, 3) for k, v in self.density_map.items()},
            "clusters": [
                {
                    "id": c.cluster_id,
                    "label": c.label_emergent,
                    "size": len(c.points),
                    "density": round(c.density, 3),
                    "centroid": {k: round(v, 3) for k, v in c.centroid.items()},
                }
                for c in self.clusters
            ],
            "void_zones": [
                {"id": v.zone_id, "spoke": v.dominant_spoke, "description": v.description}
                for v in self.void_zones
            ],
        }


# ---------------------------------------------------------------------------
# Projector
# ---------------------------------------------------------------------------

class MetaClusterProjector:
    """Projette les intents du metacluster dans l'espace 6D et cluster."""

    def __init__(
        self,
        n_clusters: int = 5,
        cluster_sim_threshold: float = CLUSTER_SIM_THRESHOLD,
        void_threshold: float = VOID_DENSITY_THRESHOLD,
        seed: int = 42,
    ):
        self.n_clusters = n_clusters
        self.cluster_sim_threshold = cluster_sim_threshold
        self.void_threshold = void_threshold
        self._seed = seed

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def project(
        self,
        inputs: list[tuple[str, Union[IntentDraft, FieldDocument]]],
        gravity_docs: Optional[list[FieldDocument]] = None,
    ) -> MetaClusterMap:
        """Construit la MetaClusterMap depuis N (repo, intent) pairs."""
        gravity_docs = gravity_docs or []

        # 1. Construire le cloud de points
        cloud = self._build_cloud(inputs)
        gravity_points = self._build_gravity_points(gravity_docs)
        all_points = cloud + gravity_points

        # 2. Repos uniques
        repos = list(dict.fromkeys(p.repo for p in all_points if not p.is_gravity))

        # 3. Clustering
        clusters = self._cluster(all_points)

        # 4. Density map
        density_map = self._compute_density(cloud)

        # 5. Zones vides
        void_zones = self._detect_void_zones(density_map, cloud)

        return MetaClusterMap(
            repos=repos,
            intent_cloud=all_points,
            clusters=clusters,
            gravity_centers=gravity_points,
            void_zones=void_zones,
            density_map=density_map,
        )

    # ------------------------------------------------------------------
    # Construction du cloud
    # ------------------------------------------------------------------

    @staticmethod
    def _build_cloud(
        inputs: list[tuple[str, Union[IntentDraft, FieldDocument]]]
    ) -> list[IntentPoint]:
        points: list[IntentPoint] = []
        seen: set[str] = set()
        for repo, obj in inputs:
            if isinstance(obj, IntentDraft):
                pid = obj.detected_id or obj.source_file
                coords = dict(obj.spoke_scores)
                kind = "vibe" if obj.intent_hash_draft and "DRAFT" in obj.intent_hash_draft else "intent"
                status = obj.status_detected or "unknown"
            else:  # FieldDocument
                pid = obj.doc_id
                coords = dict(obj.spoke_scores)
                kind = obj.kind
                status = obj.status
            # déduplique
            key = f"{repo}:{pid}"
            if key in seen:
                continue
            seen.add(key)
            # normalise les coords
            coords = MetaClusterProjector._normalize(coords)
            points.append(IntentPoint(
                point_id=pid,
                repo=repo,
                coords=coords,
                kind=kind,
                status=status,
            ))
        return points

    @staticmethod
    def _build_gravity_points(docs: list[FieldDocument]) -> list[IntentPoint]:
        points: list[IntentPoint] = []
        for doc in docs:
            w = ADR_MASS_WEIGHT if doc.kind == "adr" else ROADMAP_MASS_WEIGHT
            coords = MetaClusterProjector._normalize(doc.spoke_scores)
            # Amplifier les coordonnées en fonction de la masse
            coords = {k: min(v * w / ADR_MASS_WEIGHT, 1.0) for k, v in coords.items()}
            points.append(IntentPoint(
                point_id=doc.doc_id,
                repo="GOVERNANCE",
                coords=coords,
                kind=doc.kind,
                status=doc.status,
                is_gravity=True,
                gravity_weight=w,
            ))
        return points

    # ------------------------------------------------------------------
    # Clustering (k-means cosine, fallback greedy)
    # ------------------------------------------------------------------

    def _cluster(self, points: list[IntentPoint]) -> list[Cluster]:
        non_gravity = [p for p in points if not p.is_gravity]
        if not non_gravity:
            return []

        k = min(self.n_clusters, len(non_gravity))
        if k <= 1:
            c = Cluster(cluster_id=0, centroid=non_gravity[0].coords, points=[non_gravity[0].point_id])
            c.label_emergent = self._label_cluster(c.centroid)
            c.density = 1.0
            non_gravity[0].cluster_id = 0
            return [c]

        # Initialisation déterministe (k-means++ simplifié)
        rng = random.Random(self._seed)
        centroids = [dict(non_gravity[rng.randint(0, len(non_gravity)-1)].coords)]
        for _ in range(k - 1):
            dists = []
            for p in non_gravity:
                min_sim = max((cosine_similarity(p.coords, c) for c in centroids), default=0.0)
                dists.append(1.0 - min_sim)
            total = sum(dists) or 1.0
            probs = [d / total for d in dists]
            r = rng.random()
            cumul = 0.0
            chosen = non_gravity[-1]
            for p, prob in zip(non_gravity, probs):
                cumul += prob
                if r <= cumul:
                    chosen = p
                    break
            centroids.append(dict(chosen.coords))

        # Itérations k-means
        for _ in range(KMEANS_ITERS):
            assignments: list[list[IntentPoint]] = [[] for _ in range(k)]
            for p in non_gravity:
                sims = [cosine_similarity(p.coords, c) for c in centroids]
                best = sims.index(max(sims))
                p.cluster_id = best
                assignments[best].append(p)
            # Mise à jour centroids
            new_centroids = []
            for idx, group in enumerate(assignments):
                if not group:
                    new_centroids.append(centroids[idx])
                else:
                    new_centroids.append(self._mean_coords(group))
            centroids = new_centroids

        # Construire objets Cluster
        clusters: list[Cluster] = []
        for idx, centroid in enumerate(centroids):
            members = [p.point_id for p in non_gravity if p.cluster_id == idx]
            if not members:
                continue
            density = len(members) / max(len(non_gravity), 1)
            c = Cluster(
                cluster_id=idx,
                centroid=centroid,
                points=members,
                density=round(density, 3),
            )
            c.label_emergent = self._label_cluster(centroid)
            clusters.append(c)
        return clusters

    # ------------------------------------------------------------------
    # Density + zones vides
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_density(points: list[IntentPoint]) -> dict[str, float]:
        if not points:
            return {s: 0.0 for s in SPOKES}
        totals = {s: 0.0 for s in SPOKES}
        for p in points:
            for s in SPOKES:
                totals[s] += p.coords.get(s, 0.0)
        n = len(points)
        return {s: round(totals[s] / n, 3) for s in SPOKES}

    def _detect_void_zones(self, density_map: dict[str, float], points: list[IntentPoint]) -> list[VoidZone]:
        voids: list[VoidZone] = []
        zone_id = 0
        for spoke in SPOKES:
            density = density_map.get(spoke, 0.0)
            if density < self.void_threshold:
                voids.append(VoidZone(
                    zone_id=zone_id,
                    dominant_spoke=spoke,
                    description=f"Aucun intent couvrant la dimension {spoke} — gap structurel.",
                    coords_approx={s: (1.0 if s == spoke else 0.0) for s in SPOKES},
                ))
                zone_id += 1
        return voids

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize(coords: dict[str, float]) -> dict[str, float]:
        out = {s: coords.get(s, 0.0) for s in SPOKES}
        total = sum(out.values())
        if total == 0:
            return {s: 1.0 / len(SPOKES) for s in SPOKES}
        return {s: round(v / total, 4) for s, v in out.items()}

    @staticmethod
    def _mean_coords(points: list[IntentPoint]) -> dict[str, float]:
        if not points:
            return {s: 0.0 for s in SPOKES}
        result = {s: 0.0 for s in SPOKES}
        for p in points:
            for s in SPOKES:
                result[s] += p.coords.get(s, 0.0)
        n = len(points)
        return {s: round(result[s] / n, 4) for s in SPOKES}

    @staticmethod
    def _label_cluster(centroid: dict[str, float]) -> str:
        if not centroid:
            return "unknown"
        dominant = max(centroid, key=lambda k: centroid.get(k, 0.0))
        labels = {
            "AI":      "intelligence_agentique",
            "TECH":    "infrastructure_pipeline",
            "MATH":    "formalisation_graphes",
            "SCIENCE": "recherche_patterns",
            "PHYSICS": "champ_flux",
            "BIO":     "systemes_adaptatifs",
        }
        return labels.get(dominant, dominant)
