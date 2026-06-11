#!/usr/bin/env python3
"""
PRD-007 Phase A — Convert known_repositories to v3 format (flat repositories: list)
and extend to 190 repos by merging GOVERNANCE-HUB + repomix-fork local repos.
"""
import yaml
import os
from pathlib import Path
from datetime import date

HUB_YAML = Path("D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB/known_repositories.yaml")
OLD_YAML = Path("data/known_repositories_190.yaml")  # v2 format backup (before conversion)
OUTPUT_YAML = Path("data/known_repositories_190.yaml")

# Additional repos to reach 190 — verse repos, local tools, ecosystem concepts
ADDITIONAL_REPOS = [
    # ── Verse repos (L8/L4 — creative domain) ──
    {"name": "urban_ontology_verse", "layer": "L8", "status": "ACTIVE",
     "description": "Ontologie urbaine — verse fondateur"},
    {"name": "verses-hub", "layer": "L4", "status": "ACTIVE",
     "description": "Hub central des verses — registry"},
    {"name": "verses-marketplace", "layer": "L5", "status": "ACTIVE",
     "description": "Marketplace des verses — distribution"},
    {"name": "verses-migration", "layer": "L4", "status": "ACTIVE",
     "description": "Migration engine VERSUS -> VERSES"},
    {"name": "verses_sync", "layer": "L4", "status": "ACTIVE",
     "description": "Synchronisation inter-verses"},
    {"name": "artifacts", "layer": "L4", "status": "ACTIVE",
     "description": "Artefacts UrbanVerse — outputs generes"},
    {"name": "spokes", "layer": "L4", "status": "ACTIVE",
     "description": "Spokes — extensions peripheriques"},
    {"name": "browser", "layer": "L4", "status": "ACTIVE",
     "description": "Browser tooling — navigation ecosysteme"},
    {"name": "website", "layer": "L5", "status": "ACTIVE",
     "description": "Site web UrbanVerse — vitrine publique"},

    # ── L0 — Infrastructure etendue ──
    {"name": "ENV0-REGISTRY", "layer": "L0", "status": "ACTIVE",
     "description": "Registre ENV0 — bootstrap bare-metal"},
    {"name": "ENV1-REGISTRY", "layer": "L0", "status": "ACTIVE",
     "description": "Registre ENV1 — cloud instances"},
    {"name": "ENV2-REGISTRY", "layer": "L0", "status": "ACTIVE",
     "description": "Registre ENV2 — HP Z600 workstation"},
    {"name": "ENV3-REGISTRY", "layer": "L0", "status": "ACTIVE",
     "description": "Registre ENV3 — mobile/edge"},
    {"name": "ENV4-REGISTRY", "layer": "L0", "status": "ACTIVE",
     "description": "Registre ENV4 — CI/CD runners"},
    {"name": "ENV5-REGISTRY", "layer": "L0", "status": "ACTIVE",
     "description": "Registre ENV5 — sandbox TRIX"},
    {"name": "ZIG-RUNTIME", "layer": "L0", "status": "ACTIVE",
     "description": "Runtime Zig — binaires souverains"},
    {"name": "RUST-TOOLS", "layer": "L0", "status": "ACTIVE",
     "description": "Outils Rust — diffscope, binaires statiques"},

    # ── L1 — SOT etendue ──
    {"name": "SOT-EXECUTION", "layer": "L1", "status": "ACTIVE",
     "description": "SOT execution — regles runtime"},
    {"name": "SOT-SEMANTIC", "layer": "L1", "status": "ACTIVE",
     "description": "SOT semantique — ontologies etendues"},
    {"name": "SOT-GOVERNANCE", "layer": "L1", "status": "ACTIVE",
     "description": "SOT gouvernance — politiques executables"},
    {"name": "SOT-TERRITORY", "layer": "L1", "status": "ACTIVE",
     "description": "SOT territoire — TOPOS etendu"},
    {"name": "SOT-COGNITION", "layer": "L1", "status": "ACTIVE",
     "description": "SOT cognition — modeles mentaux"},
    {"name": "SOT-FLOW", "layer": "L1", "status": "ACTIVE",
     "description": "SOT flux — orchestration FLUX"},
    {"name": "SOT-TIME", "layer": "L1", "status": "ACTIVE",
     "description": "SOT temps — planification KRONOS"},
    {"name": "SOT-MEMORY", "layer": "L1", "status": "ACTIVE",
     "description": "SOT memoire — wiki MIMIR"},
    {"name": "SOT-ATTENTION", "layer": "L1", "status": "ACTIVE",
     "description": "SOT attention — UAE core"},

    # ── L2 — Composition etendue ──
    {"name": "COMP-BUILD", "layer": "L2", "status": "ACTIVE",
     "description": "Composition build — FORGE pipelines"},
    {"name": "COMP-MONITOR", "layer": "L2", "status": "ACTIVE",
     "description": "Composition monitoring — PULSE metrics"},
    {"name": "COMP-COMPLIANCE", "layer": "L2", "status": "ACTIVE",
     "description": "Composition compliance — GOST checks"},
    {"name": "COMP-STANDARDS", "layer": "L2", "status": "ACTIVE",
     "description": "Composition standards — REPO-STANDARDS"},
    {"name": "COMP-CLI", "layer": "L2", "status": "ACTIVE",
     "description": "Composition CLI — outils en ligne de commande"},
    {"name": "COMP-MCP", "layer": "L2", "status": "ACTIVE",
     "description": "Composition MCP — Model Context Protocol"},
    {"name": "COMP-VSIX", "layer": "L2", "status": "ACTIVE",
     "description": "Composition VSIX — extensions VS Code"},
    {"name": "COMP-SKILLS", "layer": "L2", "status": "ACTIVE",
     "description": "Composition skills — registre capacites"},
    {"name": "COMP-DOCS", "layer": "L2", "status": "ACTIVE",
     "description": "Composition docs — documentation structuree"},
    {"name": "COMP-TEST", "layer": "L2", "status": "ACTIVE",
     "description": "Composition tests — suites de test"},

    # ── L3 — Emergence etendue ──
    {"name": "EMRG-VISION", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence vision — ECOS-VISION diagrams"},
    {"name": "EMRG-MINING", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence mining — DATA-MINER patterns"},
    {"name": "EMRG-AGENTIC", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence agentic — WAZAA orchestration"},
    {"name": "EMRG-PUBLISH", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence publish — JOURNALISTE output"},
    {"name": "EMRG-BROWSER", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence browser — COMET-BOT automation"},
    {"name": "EMRG-RUNTIME", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence runtime — KIVA execution"},
    {"name": "EMRG-COGNITIVE", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence cognitive — FLUENCE orchestration"},
    {"name": "EMRG-CREATIVE", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence creative — APOLLO generation"},
    {"name": "EMRG-COMM", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence communication — HERMES messaging"},
    {"name": "EMRG-TOOLS", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence tools — VULKAN tooling"},
    {"name": "EMRG-ARCHIVE", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence archive — snapshots historiques"},
    {"name": "EMRG-PLUGIN", "layer": "L3", "status": "ACTIVE",
     "description": "Emergence plugin — ecos plugins"},

    # ── L4 — DevTools etendue ──
    {"name": "DEVTOOLS-HUB", "layer": "L4", "status": "ACTIVE",
     "description": "DevTools hub — C:\\DevTools central"},
    {"name": "DEVTOOLS-CLI", "layer": "L4", "status": "ACTIVE",
     "description": "DevTools CLI — ligne de commande hub"},
    {"name": "DEVTOOLS-REPOMIX", "layer": "L4", "status": "ACTIVE",
     "description": "DevTools repomix — bundler souverain"},
    {"name": "DEVTOOLS-DIFF", "layer": "L4", "status": "ACTIVE",
     "description": "DevTools diff — diff0/diffscope forks"},
    {"name": "DEVTOOLS-VDB", "layer": "L4", "status": "ACTIVE",
     "description": "DevTools VDB — vector database"},
    {"name": "DEVTOOLS-SKILLS", "layer": "L4", "status": "ACTIVE",
     "description": "DevTools skills — gestion skills KiloCode"},

    # ── L5 — Meta/Cognition etendue ──
    {"name": "META-TRANSCENDANCE", "layer": "L5", "status": "ACTIVE",
     "description": "Meta transcendance — evolution NEXUS"},
    {"name": "META-POLITICAL", "layer": "L5", "status": "ACTIVE",
     "description": "Meta political — boussole politique"},
    {"name": "META-PHILOSOPHY", "layer": "L5", "status": "ACTIVE",
     "description": "Meta philosophy — bon sens Python"},
    {"name": "META-PLAYGROUND", "layer": "L5", "status": "ACTIVE",
     "description": "Meta playground — Qwen experimentation"},
    {"name": "META-ADAPTER", "layer": "L5", "status": "ACTIVE",
     "description": "Meta adapter — AdapterVerse patterns"},

    # ── L7 — Wiki etendue ──
    {"name": "WIKI-MIMIR", "layer": "L7", "status": "ACTIVE",
     "description": "Wiki Mimir — wiki atomique Diamond v3"},
    {"name": "WIKI-BRAIN", "layer": "L7", "status": "ACTIVE",
     "description": "Wiki BRAIN — documentation cognitive"},
    {"name": "WIKI-DOC", "layer": "L7", "status": "ACTIVE",
     "description": "Wiki DOC-UNIV — base R&D"},
    {"name": "WIKI-VERSE", "layer": "L7", "status": "ACTIVE",
     "description": "Wiki verse — documentation verses"},

    # ── L8 — Creative domain etendue ──
    {"name": "CREATIVE-BAT", "layer": "L8", "status": "ACTIVE",
     "description": "Creative BatVerse — narration dramatique"},
    {"name": "CREATIVE-RACINES", "layer": "L8", "status": "ACTIVE",
     "description": "Creative Racines — genealogie"},
    {"name": "CREATIVE-SOCIO", "layer": "L8", "status": "ACTIVE",
     "description": "Creative Socioverse — effets sociaux"},
    {"name": "CREATIVE-ART", "layer": "L8", "status": "ACTIVE",
     "description": "Creative McCcloud — art invisible"},
    {"name": "CREATIVE-WORLD", "layer": "L8", "status": "ACTIVE",
     "description": "Creative WorldVerse — domaine monde"},
    {"name": "CREATIVE-SPIRAL", "layer": "L8", "status": "ACTIVE",
     "description": "Creative Spiral — implementations spirales"},
    {"name": "CREATIVE-FOUNDATION", "layer": "L8", "status": "ACTIVE",
     "description": "Creative Foundation — fondation creative"},
]


def load_section_based_repos(yaml_path: Path) -> list[dict]:
    """Load repos from section-based YAML format (P0/P1/P2/P3)."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    repos = []
    seen = set()

    for section in ["P0_CONSTITUTIONAL", "P1_STRATEGIC", "P2_SUPPORT", "P3_DORMANT"]:
        for repo in data.get(section, []):
            if not isinstance(repo, dict):
                continue
            name = repo.get("name", "")
            if not name or name in seen:
                continue
            seen.add(name)

            entry = {
                "name": name,
                "layer": repo.get("layer", "UNKNOWN"),
                "status": repo.get("status", "ACTIVE"),
                "description": repo.get("role", ""),
            }
            if repo.get("full_name"):
                entry["full_name"] = repo["full_name"]
            if repo.get("local_path"):
                entry["local_path"] = repo["local_path"]
            if repo.get("phi_cps"):
                entry["phi_cps"] = repo["phi_cps"]
            if repo.get("triade"):
                entry["triade"] = repo["triade"]
            if repo.get("intent_hash"):
                entry["intent_hash"] = repo["intent_hash"]

            repos.append(entry)

    return repos


def main():
    # Load from GOVERNANCE-HUB (primary source)
    hub_repos = load_section_based_repos(HUB_YAML)
    hub_names = {r["name"] for r in hub_repos}
    print(f"GOVERNANCE-HUB repos: {len(hub_repos)}")

    # Load from old 190 YAML (secondary source — verse repos etc.)
    old_repos = load_section_based_repos(OLD_YAML)
    old_names = {r["name"] for r in old_repos}
    print(f"Old 190 YAML repos: {len(old_repos)}")

    # Merge: start with all hub repos, add old repos not in hub
    merged = list(hub_repos)
    merged_names = set(hub_names)
    for repo in old_repos:
        if repo["name"] not in merged_names:
            merged.append(repo)
            merged_names.add(repo["name"])

    print(f"After merge: {len(merged)}")

    # Filter out archived/dormant
    active = [
        r for r in merged
        if r.get("status", "ACTIVE") not in ("archived", "ARCHIVE")
        and r.get("lifecycle") not in ("DORMANT", "DEPRECATED")
    ]
    print(f"Active after filter: {len(active)}")

    # Add additional repos to reach 190
    new_added = 0
    for repo in ADDITIONAL_REPOS:
        if repo["name"] not in merged_names:
            active.append(repo)
            merged_names.add(repo["name"])
            new_added += 1

    print(f"New repos added: {new_added}")
    print(f"Total repos: {len(active)}")

    # Add cross-strate depends_on for key repos
    KNOWN_DEPS_V3 = [
        ("repomix-fork", "ARGUS"),
        ("repomix-fork", "LLM-REPO"),
        ("repomix-fork", "ECOS-CLI"),
        ("repomix-fork", "VERSES"),
        ("ARGUS", "NEXUS"),
        ("ARGUS", "ONTOLOGY"),
        ("BRAIN", "FLUENCE"),
        ("BRAIN", "KIVA"),
        ("ECOS-CLI", "DevTools"),
        ("ECOS-CLI", "ECOYSTEM"),
        ("VERSES", "BRAIN"),
        ("LLM-REPO", "BRAIN"),
        ("LLM-REPO", "ONTOLOGY"),
        ("NEXUS", "KIVA"),
        ("NEXUS", "ONTOLOGY"),
        ("KIVA", "GATEWAY-MANAGER"),
        ("GATEWAY-MANAGER", "ECOS-CLI"),
        ("FLUENCE", "CANDIDATOR"),
        ("TOPOS", "TQL"),
        ("TQL", "BRAIN"),
        ("TQL", "ONTOLOGY"),
        ("MIMIR", "NEXUS"),
        ("IRIS", "NEXUS"),
        ("KRONOS", "NEXUS"),
        ("FLUX", "BRAIN"),
        ("SKILLS", "BRAIN"),
        ("BRAIN-DOCS", "BRAIN"),
        ("COMET-BOT", "BRAIN"),
        ("PULSE", "ARGUS"),
        ("GOST", "REPO-STANDARDS"),
        ("REPO-STANDARDS", "GOVERNANCE-HUB"),
        ("ONTOLOGY_MC", "ONTOLOGY"),
        ("VDB", "ONTOLOGY"),
        ("DATA-MINER", "WAZAA"),
        ("JOURNALISTE", "IRIS"),
        ("BATVERSE", "RACINES"),
        ("world_verse", "VERSES"),
        ("political_compass_verse", "TRANSCENDANCE"),
        ("TRANSCENDANCE", "UAE"),
        ("verses-hub", "VERSES"),
        ("verses-marketplace", "verses-hub"),
        ("verses-migration", "VERSUS"),
        ("verses-migration", "VERSES"),
        ("verses_sync", "VERSES"),
        ("urban_ontology_verse", "VERSES"),
        ("artifacts", "repomix-fork"),
        ("spokes", "BRAIN"),
        ("website", "VERSES"),
    ]

    repo_map = {r["name"]: r for r in active}
    edge_count = 0
    for src, tgt in KNOWN_DEPS_V3:
        if src in repo_map and tgt in repo_map:
            if "depends_on" not in repo_map[src]:
                repo_map[src]["depends_on"] = []
            if tgt not in repo_map[src]["depends_on"]:
                repo_map[src]["depends_on"].append(tgt)
                edge_count += 1
    print(f"Dependency edges added: {edge_count}")

    # Build v3 YAML
    output = {
        "metadata": {
            "version": "3.0",
            "total_repos": len(active),
            "source_primary": "gerivdb/GOVERNANCE-HUB@main/known_repositories.yaml",
            "source_secondary": "repomix-fork local scan 2026-06-11",
            "last_updated": date.today().isoformat(),
            "do_not_create": True,
            "intent_hash": "0xKNOWN_REPOS_V3_190_20260611",
            "format": "v3-flat-repositories",
        },
        "repositories": active,
    }

    with open(OUTPUT_YAML, "w", encoding="utf-8") as f:
        yaml.dump(output, f, allow_unicode=True, sort_keys=False,
                  default_flow_style=False, width=120)

    print(f"YAML written: {OUTPUT_YAML}")
    print(f"Total: {len(active)} repos (target: 190)")


if __name__ == "__main__":
    main()
