#!/usr/bin/env python3
"""
PRD-003 Phase 2 — cadastre_builder.py
Genere cadastre_v1.yaml depuis les 10 repos pilotes.
Valide contre le schema PRD-003.
"""
from __future__ import annotations
import json
import yaml
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

PILOT_REPOS = [
    {"repo": "GOVERNANCE-HUB", "strate": "L0", "arrondissement": "Hotel de Ville — Constitution",
     "role": "Constitution, cadastre, registres"},
    {"repo": "ECOYSTEM", "strate": "L1", "arrondissement": "Mairie centrale — SOT operationnel",
     "role": "Source of truth operationnel ecosysteme"},
    {"repo": "BRAIN", "strate": "L2", "arrondissement": "Grandes Ecoles — Cognition",
     "role": "Logique ternaire, cognition distribuee"},
    {"repo": "ECOS-CLI", "strate": "L3", "arrondissement": "Voiries — CLI executable",
     "role": "Interface CLI ecosysteme"},
    {"repo": "repomix-fork", "strate": "L3", "arrondissement": "Voiries — Bundler souverain",
     "role": "Bundler repomix fork, scan + verses + marketplace"},
    {"repo": "LLM-REPO", "strate": "L1b", "arrondissement": "Substrat cognitif LLM",
     "role": "LLM_BOOT_PROTOCOL, regles comportement"},
    {"repo": "NEXUS", "strate": "L1", "arrondissement": "Archives centrales — Aggregation data",
     "role": "Aggregation cross-repo"},
    {"repo": "FLUENCE", "strate": "L2", "arrondissement": "Grandes Ecoles — Logique",
     "role": "Logique FLUENCE, calcul emergence"},
    {"repo": "VERSES", "strate": "L8", "arrondissement": "Culture — Verses ontologiques",
     "role": "Registry des verses, UrbanVerse"},
    {"repo": "political_compass_verse", "strate": "L5", "arrondissement": "Meta — Gouvernance",
     "role": "Boussole politique, scenarios"},
]

VALID_STRATES = {"L0","L1","L1a","L1b","L2","L2b","L3","L4","L5","L6","L7","L8","L9"}
VALID_ZONES = {"zone_1","zone_2","zone_3","zone_4"}
VALID_CONNECT = {"DSL","FIBRE"}


def build_cadastre(vague: int = 1) -> list:
    parcelles = []
    for repo in PILOT_REPOS:
        parcelles.append({
            "repo_name": repo["repo"],
            "strate": repo["strate"],
            "arrondissement": repo["arrondissement"],
            "role_canonique": repo["role"],
            "adresse": "{}/STRATUM_RELAY.md".format(repo["repo"]),
            "connectivite": "DSL" if vague <= 2 else "FIBRE",
            "zone": "zone_1",
            "vague_courante": vague,
            "derniere_synchro": date.today().isoformat(),
        })
    return parcelles


def validate_parcel(parcel: dict) -> list:
    errors = []
    required = ["repo_name","strate","arrondissement","adresse","connectivite","zone","vague_courante"]
    for f in required:
        if f not in parcel:
            errors.append("Champ requis manquant: {}".format(f))
    if parcel.get("strate") not in VALID_STRATES:
        errors.append("Strate invalide: {}".format(parcel.get("strate")))
    if parcel.get("zone") not in VALID_ZONES:
        errors.append("Zone invalide: {}".format(parcel.get("zone")))
    if parcel.get("connectivite") not in VALID_CONNECT:
        errors.append("Connectivite invalide: {}".format(parcel.get("connectivite")))
    return errors


def main():
    parcelles = build_cadastre(vague=1)
    errors_total = []
    for p in parcelles:
        errs = validate_parcel(p)
        if errs:
            errors_total.extend(["{}: {}".format(p["repo_name"], e) for e in errs])
    if errors_total:
        print("ERREURS:")
        for e in errors_total:
            print("  - {}".format(e))
        raise SystemExit(1)

    out = {
        "version": "1.0",
        "vague": 1,
        "date": date.today().isoformat(),
        "count": len(parcelles),
        "parcelles": parcelles,
    }
    json_path = REPO_ROOT / "data" / "cadastre_v1.json"
    json_path.parent.mkdir(exist_ok=True)
    json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Cadastre ecrit: {} parcelles -> {}".format(len(parcelles), json_path))


if __name__ == "__main__":
    main()
