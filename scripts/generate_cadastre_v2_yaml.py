#!/usr/bin/env python3
"""Generate cadastre_v2.yaml for VERSES from cadastre_v2.json."""
import json
import yaml
from pathlib import Path

json_path = Path("data/cadastre_v2.json")
output_path = Path("D:/DO/WEB/TOOLS/L4-TOOLS/VERSES/urban_ontology_verse/CADASTRE/cadastre_v2.yaml")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Filter to active repos only (≥ 71 target)
active = [p for p in data["parcelles"] if p.get("status", "ACTIVE") == "ACTIVE"]

output = {
    "metadata": {
        "version": "2.0",
        "source": "gerivdb/repomix-fork/data/cadastre_v2.json",
        "generated": data["date"],
        "total_repos": len(active),
        "intent_hash": "0xCADASTRE_V2_20260611",
    },
    "parcelles": active,
}

output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    yaml.dump(output, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=120)

print(f"Written: {output_path} ({len(active)} parcelles)")
