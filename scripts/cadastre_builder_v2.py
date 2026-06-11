#!/usr/bin/env python3
"""
PRD-10 — cadastre_builder v2
Genere cadastre_v2.yaml depuis les 190 repos (cadastre etendu).
"""
from __future__ import annotations
import json
import yaml
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

VALID_STRATES = {"L0","L1","L1a","L1b","L2","L2b","L3","L4","L5","L6","L7","L8","L9","UNKNOWN"}
VALID_CONNECT = {"DSL","FIBRE"}


def build_cadastre_v2(yaml_path: Path = None) -> dict:
    """
    Construit le cadastre v2 depuis known_repositories_190.yaml.
    Couvre ~190 repos (vs 10 pilotes en v1).
    """
    yaml_path = yaml_path or REPO_ROOT / "data" / "known_repositories_190.yaml"
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    repos = data.get("repositories", [])
    parcelles = []
    for repo in repos:
        name = repo.get("name", "UNKNOWN")
        layer = repo.get("layer", "UNKNOWN")
        status = repo.get("status", "ACTIVE")
        # Normaliser le layer pour le cadastre
        strate = _normalize_layer(layer)
        # Déterminer la connectivité selon la strate
        connectivite = "FIBRE" if strate in ("L0", "L1", "L1b", "L3") else "DSL"
        # Déterminer la zone selon la strate
        zone = _strate_to_zone(strate)

        parcelles.append({
            "repo_name": name,
            "strate": strate,
            "layer_detail": layer,
            "status": status,
            "connectivite": connectivite,
            "zone": zone,
            "vague_courante": 2 if connectivite == "DSL" else 3,
            "derniere_synchro": date.today().isoformat(),
        })

    return {
        "version": "2.0",
        "vague": 2,
        "date": date.today().isoformat(),
        "count": len(parcelles),
        "source": str(yaml_path),
        "parcelles": parcelles,
    }


def _normalize_layer(layer: str) -> str:
    """Normalise un layer vers une strate cadastre."""
    if not layer:
        return "UNKNOWN"
    layer = layer.upper()
    # Extraire la strate principale (L0, L1, L2, etc.)
    import re
    match = re.match(r'^(L\d+[a-z]?)', layer)
    if match:
        base = match.group(1)
        # Mapper les sous-strates
        if base in ("L0", "L1", "L1A", "L1B", "L2", "L2B", "L3", "L4", "L5", "L6", "L7", "L8", "L9"):
            return base
    return "UNKNOWN"


def _strate_to_zone(strate: str) -> str:
    """Mappe une strate vers une zone."""
    zone_map = {
        "L0": "zone_1", "L1": "zone_1", "L1A": "zone_1", "L1B": "zone_1",
        "L2": "zone_2", "L2B": "zone_2",
        "L3": "zone_2", "L4": "zone_2",
        "L5": "zone_3", "L6": "zone_3", "L7": "zone_3",
        "L8": "zone_4", "L9": "zone_4",
        "UNKNOWN": "zone_4",
    }
    return zone_map.get(strate, "zone_4")


def validate_parcel(parcel: dict) -> list:
    errors = []
    required = ["repo_name", "strate", "connectivite", "zone", "vague_courante"]
    for f in required:
        if f not in parcel:
            errors.append("Champ requis manquant: {}".format(f))
    if parcel.get("strate") not in VALID_STRATES:
        errors.append("Strate invalide: {}".format(parcel.get("strate")))
    if parcel.get("connectivite") not in VALID_CONNECT:
        errors.append("Connectivite invalide: {}".format(parcel.get("connectivite")))
    return errors


def main():
    cadastre = build_cadastre_v2()
    errors_total = []
    for p in cadastre["parcelles"]:
        errs = validate_parcel(p)
        if errs:
            errors_total.extend(["{}: {}".format(p["repo_name"], e) for e in errs])

    if errors_total:
        print("ERREURS:")
        for e in errors_total:
            print("  - {}".format(e))
        raise SystemExit(1)

    json_path = REPO_ROOT / "data" / "cadastre_v2.json"
    json_path.parent.mkdir(exist_ok=True)
    json_path.write_text(json.dumps(cadastre, indent=2), encoding="utf-8")
    print("Cadastre v2 ecrit: {} parcelles -> {}".format(cadastre["count"], json_path))

    # Stats
    from collections import Counter
    by_strate = Counter(p["strate"] for p in cadastre["parcelles"])
    by_connect = Counter(p["connectivite"] for p in cadastre["parcelles"])
    print("By strate:", dict(by_strate))
    print("By connectivite:", dict(by_connect))


if __name__ == "__main__":
    main()
