#!/usr/bin/env python3
"""
Adapter: known_repositories.yaml -> networkx.Graph
pour alimentation de UniversalVerseDetector.

Structure connue:
- P0_CONSTITUTIONAL: 7 repos (name, layer, phi_cps, coord, full_name, url, local_path, role)
- P1_STRATEGIC: 18 repos (memes champs)
- P2_SUPPORT: 48 repos (+ status)
- P3_DORMANT: 8 repos (+ lifecycle=DORMANT)
- ARCHIVE_GERI_CMS: structure differente (exclue)
"""
import yaml
import networkx as nx
from pathlib import Path
from typing import Optional


# Mapping layer -> ordre numerique pour inferrence d'arêtes
LAYER_ORDER = {
    "L0_INFRASTRUCTURE": 0,
    "L1_CAUSALITY": 1,
    "L1b": 1,
    "L2_COMPOSITION": 2,
    "L2_RUNTIME": 2,
    "L3_EMERGENCE": 3,
    "L3_TOOLS": 3,
    "L4_GOVERNANCE": 4,
    "L4-TOOLS": 4,
    "L5_META": 5,
    "L5_COGNITION": 5,
}

SKIP_LIFECYCLE = {"DEPRECATED", "DORMANT"}
SKIP_NAME_PREFIXES = ("geri-cms-", "gericms")
SKIP_SECTIONS = {"ARCHIVE_GERI_CMS"}


def _is_active(repo: dict) -> bool:
    """Determine si un repo est actif (non archive/dormant/deprecated)."""
    lifecycle = repo.get("lifecycle", "")
    status = repo.get("status", "")
    name = repo.get("name", "")

    if lifecycle in SKIP_LIFECYCLE:
        return False
    if status in ("archived", "DEPRECATED"):
        return False
    if name.lower().startswith(SKIP_NAME_PREFIXES):
        return False
    return True


def _get_layer(repo: dict) -> str:
    """Extrait la layer d'un repo, fallback L3_EMERGENCE."""
    layer = repo.get("layer", "L3_EMERGENCE")
    if layer is None:
        return "L3_EMERGENCE"
    return layer


def load_known_repos_graph(yaml_path: Path) -> nx.Graph:
    """
    Charge known_repositories.yaml et retourne un graphe non-oriente.

    Nœuds = repos actifs (hors ARCHIVE_GERI_CMS, DORMANT, DEPRECATED).
    Attributs par nœud: layer, phi_cps, role, layer_order
    Arêtes = meme strate L (weight=1.0) ou meme triade (weight=2.0)
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    G = nx.Graph()

    for section, repos in data.items():
        if section in SKIP_SECTIONS or section == "metadata":
            continue
        if not isinstance(repos, list):
            continue

        for repo in repos:
            if not isinstance(repo, dict):
                continue
            name = repo.get("name", "")
            if not name:
                continue
            if not _is_active(repo):
                continue

            layer = _get_layer(repo)
            phi_cps = repo.get("phi_cps", 3.697)
            triade = repo.get("triade", None)

            G.add_node(
                name,
                layer=layer,
                phi_cps=phi_cps,
                role=repo.get("role", ""),
                triade=triade,
                layer_order=LAYER_ORDER.get(layer, 3),
            )

    # Construction des arêtes
    nodes = list(G.nodes(data=True))
    for i, (n1, a1) in enumerate(nodes):
        for n2, a2 in nodes[i + 1:]:
            # Arête par strate
            if a1.get("layer_order") == a2.get("layer_order"):
                G.add_edge(n1, n2, weight=1.0, reason="same_layer")
            # Arête forte par triade
            if a1.get("triade") and a1["triade"] == a2.get("triade"):
                G.add_edge(n1, n2, weight=2.0, reason="same_triade")

    # Arêtes cross-strate : dépendances connues (réduisent les composantes)
    KNOWN_DEPS = [
        ("repomix-fork", "ARGUS",       "consumer"),
        ("repomix-fork", "LLM-REPO",    "hub_ref"),
        ("repomix-fork", "ECOS-CLI",    "parent_L3"),
        ("repomix-fork", "VERSES",      "registry"),
        ("repomix-fork", "IRIS",        "canal_A6"),
        ("ARGUS",        "NEXUS",       "reads"),
        ("ARGUS",        "ONTOLOGY",    "reads"),
        ("ARGUS",        "ECOYSTEM",    "writes_WAL"),
        ("BRAIN",        "FLUENCE",     "cognitive"),
        ("BRAIN",        "KIVA",        "runtime"),
        ("ECOS-CLI",     "DevTools",    "hub_L3"),
        ("ECOS-CLI",     "ECOYSTEM",    "orchestrates"),
        ("IRIS",         "KRONOS",      "triade"),
        ("KRONOS",       "FLUX",        "triade"),
        ("diff0-fork",   "ARGUS",       "feeds"),
        ("diffscope-fork","diff0-fork", "complement"),
        ("VERSES",       "BRAIN",       "cognitive_layer"),
        ("TRIX",         "AUTO-DEV",    "sandbox"),
        ("UAE",          "BRAIN",       "attention_core"),
        ("TQL",          "BRAIN",       "query_lang"),
        ("TOPOS",        "TQL",         "grammar"),
        ("LLM-REPO",     "BRAIN",       "training"),
        ("LLM-REPO",     "ONTOLOGY",    "semantic"),
        ("NEXUS",        "KIVA",        "runtime"),
        ("NEXUS",        "ONTOLOGY",    "semantic"),
        ("KIVA",         "GATEWAY-MANAGER", "proxy"),
        ("GATEWAY-MANAGER", "ECOS-CLI", "network"),
        ("FLUENCE",      "CANDIDATOR",  "pipeline"),
        ("CANDIDATOR",   "PITCH-1",     "applies"),
        ("GERIBOOKING",  "BANK-BUSTER", "financial"),
        ("RACINES",      "PITCH-1",     "narrative"),
        ("WAZAA",        "DATA-MINER",  "feeds"),
        ("JOURNALISTE",  "IRIS",        "publishes"),
        ("COMET-BOT",    "BRAIN",       "interface"),
        ("PULSE",        "ARGUS",       "monitors"),
        ("GOST",         "REPO-STANDARDS", "compliance"),
        ("TRANSCENDANCE","UAE",         "meta"),
        ("political_compass_verse", "TRANSCENDANCE", "governance"),
        # Connexions inter-composantes (ponts entre clusters isoles)
        ("TOOL-FACTORY-1",  "DevTools",    "tools"),
        ("email-sender-1",  "FLUENCE",     "email_pipeline"),
        ("email-sender-2",  "FLUENCE",     "email_pipeline"),
        ("2025-0303-BRAIN", "BRAIN",       "archive"),
        ("2025-0312-BRAIN2","BRAIN",       "archive"),
        ("2025-0402-DEEPSITE","BRAIN",     "archive"),
        ("2025-0909-DMR",   "BRAIN",       "archive"),
        ("2025-0920-BOOKING","GERIBOOKING","archive"),
        ("2025-1003-GERIBOOKING","GERIBOOKING","archive"),
        ("2025-0902-optimiser-Perplexity","BRAIN", "plugin"),
        ("2025-0903-comparateur-IA-code","BRAIN", "plugin"),
        ("2025-0905-FRUSTRATION","BRAIN",   "plugin"),
        ("2025-0906-JP-PETIT","BRAIN",      "plugin"),
        ("2025-1103-DOC-UNIV-DEV","BRAIN",  "plugin"),
        ("BATVERSE",        "RACINES",     "narrative"),
        ("BATVERSE",        "world_verse", "creative"),
        ("world_verse",     "VERSEs",      "ontology"),
        ("VERSEs",          "ONTOLOGY",    "semantic"),
        ("TOPOS",           "ONTOLOGY",    "semantic"),
        ("TQL",             "ONTOLOGY",    "query"),
        ("FLUX",            "BRAIN",       "flow"),
        ("MIMIR",           "NEXUS",       "memory"),
        ("IRIS",            "NEXUS",       "reads"),
        ("KRONOS",          "NEXUS",       "time"),
        ("TINA",            "BRAIN",       "interface"),
        ("ECOS-VISION",     "BRAIN",       "vision"),
        ("FORGE",           "DevTools",    "build"),
        ("SKILLS",          "BRAIN",       "skills"),
        ("BRAIN-DOCS",      "BRAIN",       "docs"),
        ("BRAIN-CLI",       "BRAIN",       "cli"),
        ("ECIT-CLI",        "ECOS-CLI",    "cli"),
        ("ECO-CLI",         "ECOS-CLI",    "cli"),
        ("OPENCLAW-CLI",    "ECOS-CLI",    "cli"),
        ("FLUENCE-CLI",     "FLUENCE",     "cli"),
        ("BatMCP",          "ECOS-CLI",    "mcp"),
        ("vscode-lm-proxy", "LLM-REPO",    "proxy"),
        ("vsix-ai-orchestrator","BRAIN",   "orchestrator"),
        ("strix",           "GATEWAY-MANAGER", "security"),
        ("GATEWAY-MANAGER", "BDCP",        "network"),
        ("KEEL",            "GATEWAY-MANAGER", "auth"),
        ("REPO-STANDARDS",  "GOVERNANCE-HUB", "standards"),
        ("diff0-fork",      "REPO-STANDARDS", "diff"),
        ("diffscope-fork",  "REPO-STANDARDS", "review"),
        ("ecos-diff",       "REPO-STANDARDS", "diff"),
        ("ONTOLOGY_MC",     "ONTOLOGY",    "minecraft"),
        ("VDB",             "ONTOLOGY",    "db"),
        ("DATA-MINER",      "WAZAA",       "feeds"),
        ("JOURNALISTE",     "IRIS",        "publishes"),
        ("COMET-BOT",       "BRAIN",       "interface"),
        ("PULSE",           "ARGUS",       "monitors"),
        ("GOST",            "REPO-STANDARDS", "compliance"),
        ("TRANSCENDANCE",   "UAE",         "meta"),
        ("political_compass_verse", "TRANSCENDANCE", "governance"),
    ]

    for src, tgt, reason in KNOWN_DEPS:
        if G.has_node(src) and G.has_node(tgt):
            G.add_edge(src, tgt, weight=1.5, reason=reason)

    return G


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from verse_detector import VERSE_DETECTOR

    yaml_path = Path("D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB/known_repositories.yaml")
    G = load_known_repos_graph(yaml_path)

    print(f"Graphe charge : {G.number_of_nodes()} nœuds, {G.number_of_edges()} aretes")

    obs = VERSE_DETECTOR.observe("gerivdb_ecosystem", G)
    print(f"\nScore d'emergence : {obs.score * 100:.1f}%")
    print(f"Statut            : {obs.status.name}")
    if obs.eta_days:
        print(f"ETA               : {obs.eta_days:.1f} jours")
    else:
        print("ETA               : N/A (1ere observation)")
    print(f"\nSeuil magique (BORN) : 72.0%")
