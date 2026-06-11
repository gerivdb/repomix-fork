#!/usr/bin/env python3
"""
PRD-007 Phase A — generate_190_repos_yaml.py
Genere un known_repositories.yaml etendu a 190 repos
en combinant les donnees existantes avec les repos manquants.
"""
import yaml
from pathlib import Path
from datetime import date

EXISTING_YAML = Path("D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB/known_repositories.yaml")
OUTPUT_YAML = Path("D:/DO/WEB/TOOLS/L4-TOOLS/repomix-fork/data/known_repositories_190.yaml")

# Repos additionnels a ajouter (estimes ~109 repos manquants)
# Ces repos sont les repos gerivdb/* non encore dans le YAML
# Structure: nom, layer, role, full_name
ADDITIONAL_REPOS = [
    # L1 - SOT operationnel (repos outils centraux)
    {"name": "ECO-CLI", "layer": "L1", "role": "CLI ecosysteme legacy", "full_name": "gerivdb/ECO-CLI", "status": "active"},
    {"name": "FLUENCE-CLI", "layer": "L1", "role": "CLI FLUENCE", "full_name": "gerivdb/FLUENCE-CLI", "status": "active"},
    {"name": "OPENCLAW-CLI", "layer": "L1", "role": "CLI OpenClaw", "full_name": "gerivdb/OPENCLAW-CLI", "status": "active"},
    {"name": "ECIT-CLI", "layer": "L1", "role": "CLI ECIT", "full_name": "gerivdb/ECIT-CLI", "status": "active"},
    {"name": "BRAIN-CLI", "layer": "L1", "role": "CLI BRAIN", "full_name": "gerivdb/BRAIN-CLI", "status": "active"},
    {"name": "REPO-STANDARDS", "layer": "L1", "role": "Standards repos", "full_name": "gerivdb/REPO-STANDARDS", "status": "active"},
    {"name": "TRIX", "layer": "L1", "role": "Sandbox TRIX", "full_name": "gerivdb/TRIX", "status": "active"},
    {"name": "UAE", "layer": "L1", "role": "Attention core", "full_name": "gerivdb/UAE", "status": "active"},
    {"name": "TQL", "layer": "L1", "role": "Query language", "full_name": "gerivdb/TQL", "status": "active"},
    {"name": "TOPOS", "layer": "L1", "role": "Secrets scanning", "full_name": "gerivdb/TOPOS", "status": "active"},
    {"name": "IRIS", "layer": "L1", "role": "Poll repos tiers", "full_name": "gerivdb/IRIS", "status": "active"},
    {"name": "KRONOS", "layer": "L1", "role": "Time/schedule", "full_name": "gerivdb/KRONOS", "status": "active"},
    {"name": "FLUX", "layer": "L1", "role": "Flow engine", "full_name": "gerivdb/FLUX", "status": "active"},
    {"name": "MIMIR", "layer": "L1", "role": "Wiki Atomique", "full_name": "gerivdb/MIMIR", "status": "active"},
    {"name": "TINA", "layer": "L1", "role": "Interface", "full_name": "gerivdb/TINA", "status": "active"},
    {"name": "PULSE", "layer": "L1", "role": "Monitoring", "full_name": "gerivdb/PULSE", "status": "active"},
    {"name": "GOST", "layer": "L1", "role": "Compliance", "full_name": "gerivdb/GOST", "status": "active"},
    {"name": "FORGE", "layer": "L1", "role": "Build system", "full_name": "gerivdb/FORGE", "status": "active"},
    {"name": "BATVERSE", "layer": "L1", "role": "Verse narratif", "full_name": "gerivdb/BATVERSE", "status": "active"},
    {"name": "TRANSCENDANCE", "layer": "L1", "role": "Meta layer", "full_name": "gerivdb/TRANSCENDANCE", "status": "active"},
    {"name": "ONTOLOGY_MC", "layer": "L1", "role": "Ontology Minecraft", "full_name": "gerivdb/ONTOLOGY_MC", "status": "active"},
    {"name": "VDB", "layer": "L1", "role": "Vector DB", "full_name": "gerivdb/VDB", "status": "active"},
    {"name": "WAZAA", "layer": "L1", "role": "Data source", "full_name": "gerivdb/WAZAA", "status": "active"},
    {"name": "DATA-MINER", "layer": "L1", "role": "Data mining", "full_name": "gerivdb/DATA-MINER", "status": "active"},
    {"name": "JOURNALISTE", "layer": "L1", "role": "Publishing", "full_name": "gerivdb/JOURNALISTE", "status": "active"},
    {"name": "COMET-BOT", "layer": "L1", "role": "Browser automation", "full_name": "gerivdb/COMET-BOT", "status": "active"},
    {"name": "strix", "layer": "L1", "role": "Security", "full_name": "gerivdb/strix", "status": "active"},
    {"name": "BatMCP", "layer": "L1", "role": "MCP server", "full_name": "gerivdb/BatMCP", "status": "active"},
    {"name": "vscode-lm-proxy", "layer": "L1", "role": "VSCode LM proxy", "full_name": "gerivdb/vscode-lm-proxy", "status": "active"},
    {"name": "vsix-ai-orchestrator", "layer": "L1", "role": "VSIX AI orchestrator", "full_name": "gerivdb/vsix-ai-orchestrator", "status": "active"},
    {"name": "SKILLS", "layer": "L1", "role": "Skills collection", "full_name": "gerivdb/SKILLS", "status": "active"},
    {"name": "BRAIN-DOCS", "layer": "L1", "role": "BRAIN documentation", "full_name": "gerivdb/BRAIN-DOCS", "status": "active"},
    {"name": "TOOL-FACTORY-1", "layer": "L1", "role": "Tool factory", "full_name": "gerivdb/TOOL-FACTORY-1", "status": "active"},
    {"name": "email-sender-1", "layer": "L1", "role": "Email sender", "full_name": "gerivdb/email-sender-1", "status": "active"},
    {"name": "email-sender-2", "layer": "L1", "role": "Email sender 2", "full_name": "gerivdb/email-sender-2", "status": "active"},
    {"name": "2025-0303-BRAIN", "layer": "L1", "role": "BRAIN archive", "full_name": "gerivdb/2025-0303-BRAIN", "status": "active"},
    {"name": "2025-0312-BRAIN2", "layer": "L1", "role": "BRAIN2 archive", "full_name": "gerivdb/2025-0312-BRAIN2", "status": "active"},
    {"name": "2025-0402-DEEPSITE", "layer": "L1", "role": "DeepSite archive", "full_name": "gerivdb/2025-0402-DEEPSITE", "status": "active"},
    {"name": "2025-0909-DMR", "layer": "L1", "role": "DMR archive", "full_name": "gerivdb/2025-0909-DMR", "status": "active"},
    {"name": "2025-0920-BOOKING", "layer": "L1", "role": "Booking archive", "full_name": "gerivdb/2025-0920-BOOKING", "status": "active"},
    {"name": "2025-1003-GERIBOOKING", "layer": "L1", "role": "GeriBooking archive", "full_name": "gerivdb/2025-1003-GERIBOOKING", "status": "active"},
    {"name": "2025-0902-optimiser-Perplexity", "layer": "L1", "role": "Perplexity plugin", "full_name": "gerivdb/2025-0902-optimiser-Perplexity", "status": "active"},
    {"name": "2025-0903-comparateur-IA-code", "layer": "L1", "role": "IA code comparator", "full_name": "gerivdb/2025-0903-comparateur-IA-code", "status": "active"},
    {"name": "2025-0905-FRUSTRATION", "layer": "L1", "role": "Frustration plugin", "full_name": "gerivdb/2025-0905-FRUSTRATION", "status": "active"},
    {"name": "2025-0906-JP-PETIT", "layer": "L1", "role": "JP Petit plugin", "full_name": "gerivdb/2025-0906-JP-PETIT", "status": "active"},
    {"name": "2025-1103-DOC-UNIV-DEV", "layer": "L1", "role": "Doc univ dev", "full_name": "gerivdb/2025-1103-DOC-UNIV-DEV", "status": "active"},
    {"name": "diff0-fork", "layer": "L1", "role": "Diff fork", "full_name": "gerivdb/diff0-fork", "status": "active"},
    {"name": "diffscope-fork", "layer": "L1", "role": "Diffscope fork", "full_name": "gerivdb/diffscope-fork", "status": "active"},
    {"name": "ecos-diff", "layer": "L1", "role": "ECOS diff", "full_name": "gerivdb/ecos-diff", "status": "active"},
    {"name": "LUKAS-PRESTATIONS", "layer": "L1", "role": "Lukas prestations", "full_name": "gerivdb/LUKAS-PRESTATIONS", "status": "active"},
    {"name": "CLINE", "layer": "L1", "role": "Cline CLI", "full_name": "gerivdb/CLINE", "status": "active"},
    {"name": "GERIBOOKING", "layer": "L1", "role": "GeriBooking", "full_name": "gerivdb/GERIBOOKING", "status": "active"},
    {"name": "RACINES", "layer": "L1", "role": "Racines", "full_name": "gerivdb/RACINES", "status": "active"},
    {"name": "PITCH-1", "layer": "L1", "role": "Pitch 1", "full_name": "gerivdb/PITCH-1", "status": "active"},
    {"name": "GATEWAY-MANAGER", "layer": "L1", "role": "Gateway manager", "full_name": "gerivdb/GATEWAY-MANAGER", "status": "active"},
    {"name": "CANDIDATOR", "layer": "L1", "role": "Candidator", "full_name": "gerivdb/CANDIDATOR", "status": "active"},
    {"name": "BANK-BUSTER", "layer": "L1", "role": "Bank buster", "full_name": "gerivdb/BANK-BUSTER", "status": "active"},
    {"name": "FLUENCE", "layer": "L2", "role": "Logique FLUENCE", "full_name": "gerivdb/FLUENCE", "status": "active"},
    {"name": "KIVA", "layer": "L2", "role": "Runtime KIVA", "full_name": "gerivdb/KIVA", "status": "active"},
    {"name": "BRIDGES", "layer": "L0", "role": "Ponts inter-strates", "full_name": "gerivdb/BRIDGES", "status": "active"},
    {"name": "ONTOLOGY", "layer": "L0", "role": "Ontologie", "full_name": "gerivdb/ONTOLOGY", "status": "active"},
    {"name": "political_compass_verse", "layer": "L5", "role": "Boussole politique", "full_name": "gerivdb/political_compass_verse", "status": "active"},
    {"name": "world_verse", "layer": "L8", "role": "World verse", "full_name": "gerivdb/world_verse", "status": "active"},
    {"name": "verse-template-generator", "layer": "L4", "role": "Verse template generator", "full_name": "gerivdb/verse-template-generator", "status": "active"},
    {"name": "verses_creative_foundation", "layer": "L8", "role": "Creative foundation", "full_name": "gerivdb/verses_creative_foundation", "status": "active"},
    {"name": "neuro_symbolic_verse_engine", "layer": "L2", "role": "Neuro symbolic engine", "full_name": "gerivdb/neuro_symbolic_verse_engine", "status": "active"},
    {"name": "physic_verse", "layer": "L3", "role": "Physics verse", "full_name": "gerivdb/physic_verse", "status": "active"},
    {"name": "brain_bypass_verse", "layer": "L2", "role": "Brain bypass", "full_name": "gerivdb/brain_bypass_verse", "status": "active"},
    {"name": "fluence_bypass_verse", "layer": "L2", "role": "Fluence bypass", "full_name": "gerivdb/fluence_bypass_verse", "status": "active"},
    {"name": "wazaa_bypass_verse", "layer": "L3", "role": "Wazaa bypass", "full_name": "gerivdb/wazaa_bypass_verse", "status": "active"},
    {"name": "verse_auto_projection", "layer": "L3", "role": "Verse auto projection", "full_name": "gerivdb/verse_auto_projection", "status": "active"},
    {"name": "verse_spiral_implementations", "layer": "L8", "role": "Verse spiral", "full_name": "gerivdb/verse_spiral_implementations", "status": "active"},
    {"name": "verse_detector", "layer": "L4", "role": "Verse detector", "full_name": "gerivdb/verse_detector", "status": "active"},
    {"name": "verses_library", "layer": "L4", "role": "Verses library", "full_name": "gerivdb/verses_library", "status": "active"},
    {"name": "freebox_gateway_manager_verse", "layer": "L4", "role": "Freebox gateway", "full_name": "gerivdb/freebox_gateway_manager_verse", "status": "active"},
    {"name": "bon_sens_python_verse", "layer": "L5", "role": "Bon sens Python", "full_name": "gerivdb/bon_sens_python_verse", "status": "active"},
    {"name": "mcccloud_invisible_art_verse", "layer": "L8", "role": "McCcloud art", "full_name": "gerivdb/mcccloud_invisible_art_verse", "status": "active"},
    {"name": "qwen_playground_verse", "layer": "L5", "role": "Qwen playground", "full_name": "gerivdb/qwen_playground_verse", "status": "active"},
    {"name": "atlas_gpu_optimization_verse", "layer": "L4", "role": "GPU optimization", "full_name": "gerivdb/atlas_gpu_optimization_verse", "status": "active"},
    {"name": "bellard_invariant_verse", "layer": "L3", "role": "Bellard invariant", "full_name": "gerivdb/bellard_invariant_verse", "status": "active"},
    {"name": "blo_debug_tools_verse", "layer": "L3", "role": "Debug tools", "full_name": "gerivdb/blo_debug_tools_verse", "status": "active"},
    {"name": "lecun_autosupervision_verse", "layer": "L5", "role": "LeCun autosupervision", "full_name": "gerivdb/lecun_autosupervision_verse", "status": "active"},
    {"name": "poincare_topology_verse", "layer": "L5", "role": "Poincare topology", "full_name": "gerivdb/poincare_topology_verse", "status": "active"},
    {"name": "AdapterVerse", "layer": "L3", "role": "Adapter verse", "full_name": "gerivdb/AdapterVerse", "status": "active"},
    {"name": "WikiVerse", "layer": "L7", "role": "Wiki verse", "full_name": "gerivdb/WikiVerse", "status": "active"},
    {"name": "WorkflowVerse", "layer": "L3", "role": "Workflow verse", "full_name": "gerivdb/WorkflowVerse", "status": "active"},
    {"name": "socioverse", "layer": "L8", "role": "Socioverse", "full_name": "gerivdb/socioverse", "status": "active"},
    {"name": "DEEPSITE", "layer": "L3", "role": "DeepSite", "full_name": "gerivdb/DEEPSITE", "status": "active"},
    {"name": "DMR", "layer": "L3", "role": "DMR", "full_name": "gerivdb/DMR", "status": "active"},
    {"name": "2025-0903-comparateur-IA-code", "layer": "L3", "role": "IA comparator", "full_name": "gerivdb/2025-0903-comparateur-IA-code", "status": "active"},
]

def main():
    # Charger le YAML existant
    with open(EXISTING_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    # Compter les repos existants
    existing_names = set()
    for section in ["P0_CONSTITUTIONAL", "P1_STRATEGIC", "P2_SUPPORT", "P3_DORMANT"]:
        for repo in data.get(section, []):
            if isinstance(repo, dict) and repo.get("name"):
                existing_names.add(repo["name"])
    
    print("Repos existants: {}".format(len(existing_names)))
    
    # Ajouter les repos manquants dans P2_SUPPORT
    added = 0
    for repo in ADDITIONAL_REPOS:
        if repo["name"] not in existing_names:
            data.setdefault("P2_SUPPORT", []).append({
                "name": repo["name"],
                "layer": repo["layer"],
                "role": repo["role"],
                "full_name": repo["full_name"],
                "status": repo.get("status", "active"),
            })
            existing_names.add(repo["name"])
            added += 1
    
    print("Repos ajoutes: {}".format(added))
    print("Total: {}".format(sum(len(v) for k, v in data.items() if isinstance(v, list) and k != "metadata")))
    
    # Mettre a jour les metadata
    data["metadata"]["last_updated"] = date.today().isoformat()
    data["metadata"]["version"] = "2.0"
    
    # Ecrire le YAML etendu
    OUTPUT_YAML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_YAML, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    print("YAML ecrit: {}".format(OUTPUT_YAML))


if __name__ == "__main__":
    main()
