#!/usr/bin/env python3
"""Find delta between repomix-fork 190 repos and GOVERNANCE-HUB known_repositories.yaml."""
import yaml
from pathlib import Path

fork_path = Path("data/known_repositories_190.yaml")
hub_path = Path("D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB/known_repositories.yaml")

with open(fork_path, "r", encoding="utf-8") as f:
    repos_190 = {r["name"]: r for r in yaml.safe_load(f)["repositories"]}

with open(hub_path, "r", encoding="utf-8") as f:
    hub_data = yaml.safe_load(f)

hub_names = set()
hub_entries = {}
for section, repos in hub_data.items():
    if isinstance(repos, list):
        for r in repos:
            if isinstance(r, dict) and r.get("name"):
                hub_names.add(r["name"])
                hub_entries[r["name"]] = (section, r)

delta = set(repos_190.keys()) - hub_names
print(f"repomix-fork 190: {len(repos_190)}")
print(f"GOVERNANCE-HUB: {len(hub_names)}")
print(f"Delta (missing from HUB): {len(delta)}")
for r in sorted(delta):
    layer = repos_190[r].get("layer", "UNKNOWN")
    desc = repos_190[r].get("description", "")[:60]
    print(f"  {r:40s} {layer:10s} {desc}")
