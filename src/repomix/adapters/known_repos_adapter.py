#!/usr/bin/env python3
"""
Adapter v2+v3: known_repositories.yaml -> networkx.Graph + RepoNode graphe

v2 (legacy): load_known_repos_graph() — networkx, section-based YAML
v3 (PRD-007): KnownReposAdapterV3 — dataclass-based, lazy loading, tier API

Support 190 repos avec chargement incrémentiel et partitionnement par strate.
"""
import yaml
import networkx as nx
from pathlib import Path
from typing import Optional
import time

# ══════════════════════════════════════════════════════════════════════
# v2 — Legacy (networkx-based, section YAML format)
# ══════════════════════════════════════════════════════════════════════

LAYER_ORDER = {
    "L0_INFRASTRUCTURE": 0, "L0": 0,
    "L1_CAUSALITY": 1, "L1": 1, "L1a": 1, "L1b": 1,
    "L2_COMPOSITION": 2, "L2_RUNTIME": 2, "L2": 2, "L2b": 2,
    "L3_EMERGENCE": 3, "L3_TOOLS": 3, "L3": 3, "L4-TOOLS": 3,
    "L4_GOVERNANCE": 4, "L4": 4,
    "L5_META": 5, "L5_COGNITION": 5, "L5": 5,
    "L6": 6, "L7": 7, "L8": 8, "L9": 9,
}

SKIP_LIFECYCLE = {"DEPRECATED", "DORMANT"}
SKIP_NAME_PREFIXES = ("geri-cms-", "gericms")
SKIP_SECTIONS = {"ARCHIVE_GERI_CMS"}


def _is_active(repo: dict) -> bool:
    lifecycle = repo.get("lifecycle", "")
    status = repo.get("status", "")
    name = repo.get("name", "")
    if lifecycle in SKIP_LIFECYCLE:
        return False
    if status in ("archived", "DEPRECATED"):
        return False
    if any(name.lower().startswith(p) for p in SKIP_NAME_PREFIXES):
        return False
    return True


def _get_layer(repo: dict) -> str:
    layer = repo.get("layer", "L3_EMERGENCE")
    if layer is None:
        return "L3_EMERGENCE"
    return layer


def load_known_repos_graph(
    yaml_path: Path,
    max_repos: Optional[int] = None,
    domain_filter: Optional[str] = None,
) -> nx.Graph:
    """
    Charge known_repositories.yaml et retourne un graphe non-oriente.

    Args:
        yaml_path: Chemin vers known_repositories.yaml
        max_repos: Limite max de repos (None = tous)
        domain_filter: Filtre par domaine (ex: "L0", "L1")
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    G = nx.Graph()
    count = 0

    for section, repos in data.items():
        if section in SKIP_SECTIONS or section == "metadata":
            continue
        if not isinstance(repos, list):
            continue

        for repo in repos:
            if max_repos and count >= max_repos:
                break
            if not isinstance(repo, dict):
                continue
            name = repo.get("name", "")
            if not name:
                continue
            if not _is_active(repo):
                continue

            layer = _get_layer(repo)
            if domain_filter and layer != domain_filter:
                continue

            phi_cps = repo.get("phi_cps", 3.697)
            triade = repo.get("triade", None)

            G.add_node(
                name,
                layer=layer,
                phi_cps=phi_cps,
                role=repo.get("role", ""),
                triade=triade,
                layer_order=LAYER_ORDER.get(layer, 3),
                full_name=repo.get("full_name", ""),
                url=repo.get("url", ""),
                local_path=repo.get("local_path", ""),
            )
            count += 1

    # Arêtes par strate
    nodes = list(G.nodes(data=True))
    for i, (n1, a1) in enumerate(nodes):
        for n2, a2 in nodes[i + 1:]:
            if a1.get("layer_order") == a2.get("layer_order"):
                G.add_edge(n1, n2, weight=1.0, reason="same_layer")
            if a1.get("triade") and a1["triade"] == a2.get("triade"):
                G.add_edge(n1, n2, weight=2.0, reason="same_triade")

    # Arêtes cross-strate (KNOWN_DEPS)
    _add_cross_strate_edges(G)

    return G


def _add_cross_strate_edges(G: nx.Graph) -> None:
    """Ajoute les arêtes cross-strate connues."""
    KNOWN_DEPS = [
        ("repomix-fork", "ARGUS", "consumer"),
        ("repomix-fork", "LLM-REPO", "hub_ref"),
        ("repomix-fork", "ECOS-CLI", "parent_L3"),
        ("repomix-fork", "VERSES", "registry"),
        ("ARGUS", "NEXUS", "reads"),
        ("ARGUS", "ONTOLOGY", "reads"),
        ("BRAIN", "FLUENCE", "cognitive"),
        ("BRAIN", "KIVA", "runtime"),
        ("ECOS-CLI", "DevTools", "hub_L3"),
        ("ECOS-CLI", "ECOYSTEM", "orchestrates"),
        ("VERSES", "BRAIN", "cognitive_layer"),
        ("LLM-REPO", "BRAIN", "training"),
        ("LLM-REPO", "ONTOLOGY", "semantic"),
        ("NEXUS", "KIVA", "runtime"),
        ("NEXUS", "ONTOLOGY", "semantic"),
        ("KIVA", "GATEWAY-MANAGER", "proxy"),
        ("GATEWAY-MANAGER", "ECOS-CLI", "network"),
        ("FLUENCE", "CANDIDATOR", "pipeline"),
        ("TOPOS", "TQL", "grammar"),
        ("TQL", "BRAIN", "query_lang"),
        ("TQL", "ONTOLOGY", "query"),
        ("TOPOS", "ONTOLOGY", "semantic"),
        ("MIMIR", "NEXUS", "memory"),
        ("IRIS", "NEXUS", "reads"),
        ("KRONOS", "NEXUS", "time"),
        ("FLUX", "BRAIN", "flow"),
        ("SKILLS", "BRAIN", "skills"),
        ("BRAIN-DOCS", "BRAIN", "docs"),
        ("COMET-BOT", "BRAIN", "interface"),
        ("PULSE", "ARGUS", "monitors"),
        ("GOST", "REPO-STANDARDS", "compliance"),
        ("REPO-STANDARDS", "GOVERNANCE-HUB", "standards"),
        ("ONTOLOGY_MC", "ONTOLOGY", "minecraft"),
        ("VDB", "ONTOLOGY", "db"),
        ("DATA-MINER", "WAZAA", "feeds"),
        ("JOURNALISTE", "IRIS", "publishes"),
        ("political_compass_verse", "TRANSCENDANCE", "governance"),
        ("TRANSCENDANCE", "UAE", "meta"),
        ("BATVERSE", "RACINES", "narrative"),
        ("world_verse", "VERSES", "ontology"),
    ]
    for src, tgt, reason in KNOWN_DEPS:
        if G.has_node(src) and G.has_node(tgt):
            G.add_edge(src, tgt, weight=1.5, reason=reason)


def get_graph_stats(G: nx.Graph) -> dict:
    """Retourne les statistiques du graphe."""
    from collections import Counter
    layers = Counter(a.get("layer", "?") for _, a in G.nodes(data=True))
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "layers": dict(layers),
        "components": nx.number_connected_components(G),
        "density": round(nx.density(G), 4),
    }


# ══════════════════════════════════════════════════════════════════════
# v3 — PRD-007 Phase A: 190 nœuds, lazy loading, tier API
# ══════════════════════════════════════════════════════════════════════

# Ordre canonique strates — étendu L0→L9 + sous-strates
LAYER_ORDER_V3: list[str] = [
    "L0", "L1", "L1a", "L1b",
    "L2", "L2b",
    "L3",
    "L4",  # repomix-fork est ici
    "L5", "L6", "L7", "L8", "L9",
    "UNKNOWN",
]

# Tiers de priorité
TIER_MAP: dict[str, list[str]] = {
    "P0": ["L0", "L1", "L1a", "L1b", "L2", "L2b"],
    "P1": ["L3", "L4"],
    "P2": ["L5", "L6", "L7"],
    "P3": ["L8", "L9", "UNKNOWN"],
}

# Statuts exclus du graphe actif
EXCLUDED_STATUSES: set[str] = {"DORMANT", "DEPRECATED", "ARCHIVE", "archived"}


class RepoNode:
    """Nœud de graphe v3 — dataclass léger avec __slots__."""
    __slots__ = ("name", "layer", "tier", "status", "description", "edges")

    def __init__(self, name: str, layer: str, tier: str,
                 status: str = "ACTIVE", description: str = ""):
        self.name        = name
        self.layer       = layer
        self.tier        = tier
        self.status      = status
        self.description = description
        self.edges: list[str] = []   # noms des dépendances

    def is_active(self) -> bool:
        return self.status not in EXCLUDED_STATUSES

    def __repr__(self) -> str:
        return f"<RepoNode {self.name} {self.layer} {self.tier}>"


class KnownReposAdapterV3:
    """
    Charge known_repositories_190.yaml → graphe 190 nœuds.
    Lazy-loading : le graphe n'est construit qu'au premier accès.
    """

    def __init__(self, yaml_path: Optional[Path] = None):
        self._yaml_path = yaml_path or (
            Path(__file__).parent.parent.parent.parent
            / "data" / "known_repositories_190.yaml"
        )
        self._nodes: Optional[dict[str, RepoNode]] = None
        self._edges: Optional[list[tuple[str, str]]] = None
        self._load_time: float = 0.0

    # ── Lazy loading ────────────────────────────────────────────────

    def _ensure_loaded(self) -> None:
        if self._nodes is not None:
            return
        t0 = time.perf_counter()
        self._nodes, self._edges = self._parse_yaml()
        self._load_time = time.perf_counter() - t0
        assert self._load_time < 5.0, \
            f"KPI FAILED: chargement {self._load_time:.2f}s > 5s"

    def _parse_yaml(self) -> tuple[dict[str, RepoNode], list[tuple[str, str]]]:
        raw = yaml.safe_load(self._yaml_path.read_text(encoding="utf-8"))
        nodes: dict[str, RepoNode] = {}
        edges: list[tuple[str, str]] = []

        # Format v3: repositories: [{name, layer, status, ...}]
        # Format v2 (legacy): P0_CONSTITUTIONAL: [{name, layer, ...}]
        entries: list[dict] = []
        if "repositories" in raw:
            entries = raw["repositories"]
        else:
            # Legacy section-based format
            for section, repos in raw.items():
                if section in SKIP_SECTIONS or section == "metadata":
                    continue
                if isinstance(repos, list):
                    entries.extend(repos)

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            name = entry.get("name", "")
            if not name:
                continue
            layer = entry.get("layer", "UNKNOWN")
            status = entry.get("status", "ACTIVE")
            tier = self._resolve_tier(layer)

            node = RepoNode(
                name=name,
                layer=layer,
                tier=tier,
                status=status,
                description=entry.get("description", ""),
            )
            # Dépendances → arêtes
            for dep in entry.get("depends_on", []):
                node.edges.append(dep)
                edges.append((name, dep))

            nodes[name] = node

        return nodes, edges

    @staticmethod
    def _resolve_tier(layer: str) -> str:
        for tier, layers in TIER_MAP.items():
            if layer in layers:
                return tier
        return "P3"

    # ── API publique ─────────────────────────────────────────────────

    @property
    def nodes(self) -> dict[str, RepoNode]:
        self._ensure_loaded()
        return self._nodes  # type: ignore[return-value]

    @property
    def edges(self) -> list[tuple[str, str]]:
        self._ensure_loaded()
        return self._edges  # type: ignore[return-value]

    def active_nodes(self) -> list[RepoNode]:
        return [n for n in self.nodes.values() if n.is_active()]

    def by_tier(self, tier: str) -> list[RepoNode]:
        return [n for n in self.active_nodes() if n.tier == tier]

    def by_layer(self, layer: str) -> list[RepoNode]:
        return [n for n in self.active_nodes() if n.layer == layer]

    def get_stats(self) -> dict:
        active = self.active_nodes()
        by_tier = {t: len(self.by_tier(t)) for t in TIER_MAP}
        return {
            "nodes":          len(self.nodes),
            "active_nodes":   len(active),
            "edges":          len(self.edges),
            "load_time_s":    round(self._load_time, 4),
            "by_tier":        by_tier,
            "emergence_score": self._compute_emergence(active),
        }

    def _compute_emergence(self, active: list[RepoNode]) -> float:
        """Score d'émergence simplifié : ratio arêtes/nœuds × facteur tier."""
        if not active:
            return 0.0
        n = len(active)
        e = len(self.edges)
        tier_weight = sum(
            {"P0": 1.0, "P1": 0.8, "P2": 0.6, "P3": 0.4}.get(nd.tier, 0.4)
            for nd in active
        ) / n
        raw = min(1.0, (e / max(n, 1)) / 10.0) * tier_weight
        return round(raw * 100, 1)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from verse_detector import VERSE_DETECTOR

    yaml_path = Path("D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB/known_repositories.yaml")

    t0 = time.time()
    G = load_known_repos_graph(yaml_path)
    elapsed = time.time() - t0

    stats = get_graph_stats(G)
    print("Graphe charge: {} nœuds, {} aretes en {:.3f}s".format(
        stats["nodes"], stats["edges"], elapsed))
    print("Layers:", stats["layers"])
    print("Composantes:", stats["components"])
    print("Densite:", stats["density"])

    obs = VERSE_DETECTOR.observe("gerivdb_ecosystem", G)
    print("\nScore d'emergence: {:.1f}%".format(obs.score * 100))
    print("Statut: {}".format(obs.status.name))

    # v3 adapter test
    print("\n--- v3 Adapter ---")
    adapter_v3 = KnownReposAdapterV3()
    stats_v3 = adapter_v3.get_stats()
    print("v3 nodes: {} | active: {} | edges: {} | load: {}s".format(
        stats_v3["nodes"], stats_v3["active_nodes"],
        stats_v3["edges"], stats_v3["load_time_s"]))
    print("By tier:", stats_v3["by_tier"])
    print("Emergence score v3: {}%".format(stats_v3["emergence_score"]))
