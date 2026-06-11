#!/usr/bin/env python3
"""Add missing repos from repomix-fork to GOVERNANCE-HUB known_repositories.yaml."""
import yaml
from pathlib import Path
from datetime import date

fork_path = Path("data/known_repositories_190.yaml")
hub_path = Path("D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB/known_repositories.yaml")

with open(fork_path, "r", encoding="utf-8") as f:
    repos_190 = {r["name"]: r for r in yaml.safe_load(f)["repositories"]}

with open(hub_path, "r", encoding="utf-8") as f:
    hub_data = yaml.safe_load(f)

hub_names = set()
for section, repos in hub_data.items():
    if isinstance(repos, list):
        for r in repos:
            if isinstance(r, dict) and r.get("name"):
                hub_names.add(r["name"])

delta = set(repos_190.keys()) - hub_names
print(f"Delta: {len(delta)} repos to add")

# Categorize by layer
layer_map = {
    "L0": "P0_CONSTITUTIONAL", "L1": "P0_CONSTITUTIONAL", "L1a": "P0_CONSTITUTIONAL", "L1b": "P0_CONSTITUTIONAL",
    "L2": "P1_STRATEGIC", "L2b": "P1_STRATEGIC",
    "L3": "P1_STRATEGIC", "L4": "P1_STRATEGIC",
    "L5": "P2_SUPPORT", "L6": "P2_SUPPORT", "L7": "P2_SUPPORT",
    "L8": "P3_DORMANT", "L9": "P3_DORMANT", "UNKNOWN": "P3_DORMANT",
}

added = 0
for name in sorted(delta):
    repo = repos_190[name]
    layer = repo.get("layer", "UNKNOWN")
    status = repo.get("status", "ACTIVE")
    desc = repo.get("description", "")
    
    # Determine section
    section = layer_map.get(layer, "P2_SUPPORT")
    
    entry = {
        "name": name,
        "layer": layer,
        "status": status,
        "do_not_create": True,
        "description": desc,
    }
    
    hub_data[section].append(entry)
    added += 1

# Write back
with open(hub_path, "w", encoding="utf-8") as f:
    yaml.dump(hub_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=120)

# Re-count
total_after = 0
names_after = set()
for section, repos in hub_data.items():
    if isinstance(repos, list):
        for r in repos:
            if isinstance(r, dict) and r.get("name"):
                names_after.add(r["name"])
                total_after += 1

print(f"Added: {added}")
print(f"GOVERNANCE-HUB total before: {len(hub_names)}")
print(f"GOVERNANCE-HUB total after: {len(names_after)}")
