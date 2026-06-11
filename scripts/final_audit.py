#!/usr/bin/env python3
"""Final cross-repo consistency audit."""
import yaml, os
from pathlib import Path

fork_dir = Path("D:/DO/WEB/TOOLS/L4-TOOLS/REPOMIX-FORK")
hub_dir = Path("D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB")

# 1. repomix-fork 190.yaml
with open(fork_dir / "data/known_repositories_190.yaml", "r", encoding="utf-8") as f:
    d = yaml.safe_load(f)
repos_190 = {r["name"] for r in d["repositories"]}
print(f"repomix-fork 190.yaml: {len(repos_190)} repos")

# 2. GOVERNANCE-HUB
with open(hub_dir / "known_repositories.yaml", "r", encoding="utf-8") as f:
    hub = yaml.safe_load(f)
hub_repos = set()
for section, repos in hub.items():
    if isinstance(repos, list):
        for r in repos:
            if isinstance(r, dict) and r.get("name"):
                hub_repos.add(r["name"])
print(f"GOVERNANCE-HUB: {len(hub_repos)} repos")

# 3. Delta HUB -> fork (repos in HUB but not in fork)
delta_hub = hub_repos - repos_190
print(f"Delta HUB->fork: {len(delta_hub)} repos")
for r in sorted(delta_hub)[:10]:
    print(f"  + {r}")

# 4. Delta fork -> HUB (repos in fork but not in HUB)
delta_fork = repos_190 - hub_repos
print(f"Delta fork->HUB: {len(delta_fork)} repos")
for r in sorted(delta_fork)[:10]:
    print(f"  - {r}")

# 5. Check ADR statuses
print("\n=== ADR Status ===")
adr_dir = hub_dir / "ADR"
for f in sorted(os.listdir(adr_dir)):
    if f.endswith(".md") and "042" in f or "043" in f:
        content = (adr_dir / f).read_text(encoding="utf-8")
        for line in content.split("\n")[:15]:
            if "status" in line.lower() and ":" in line:
                print(f"  {f}: {line.strip()}")
                break

# 6. Check LLM_BOOT_PROTOCOL
llm_boot = Path("D:/DO/WEB/TOOLS/L1-INFRA/LLM-REPO/LLM_BOOT_PROTOCOL.md")
if llm_boot.exists():
    content = llm_boot.read_text(encoding="utf-8")
    if "GATE-4b" in content:
        print("\nLLM_BOOT_PROTOCOL GATE-4b: PRESENT")
    else:
        print("\nLLM_BOOT_PROTOCOL GATE-4b: MISSING")

# 7. Check VERSES cadastre
verses_cadastre = Path("D:/DO/WEB/TOOLS/L4-TOOLS/VERSES/urban_ontology_verse/CADASTRE/cadastre_v2.yaml")
if verses_cadastre.exists():
    with open(verses_cadastre, "r", encoding="utf-8") as f:
        cadastre = yaml.safe_load(f)
    count = len(cadastre.get("parcelles", []))
    print(f"VERSES cadastre_v2.yaml: {count} parcelles")
else:
    print("VERSES cadastre_v2.yaml: MISSING")

print("\n=== AUDIT COMPLETE ===")
