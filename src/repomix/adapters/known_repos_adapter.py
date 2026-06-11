#!/usr/bin/env python3
"""
Adapter v2: known_repositories.yaml -> networkx.Graph
Support 190 repos avec chargement incrémentiel et partitionnement par strate.
"""
import yaml
import networkx as nx
from pathlib import Path
from typing import Optional

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


if __name__ == "__main__":
    import sys, time
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
