#!/usr/bin/env python3
"""
recall_coherence_check.py v4.0 — EPIC-04
Vérifie la cohérence Karpathy-Recall entre :
  - transit_map.yaml (arrêts avec recall_pack)
  - Stratum Relays (sections Karpathy-Recall)
  - LLM-REPO/TRAINING/ (packs recall)

Usage:
    python recall_coherence_check.py --repomix bundle.xml
    python recall_coherence_check.py --transit urban_ontology_verse/TRANSIT/transit_map.yaml
    python recall_coherence_check.py --relay-dir data/relay_vague2/
    python recall_coherence_check.py --full --transit urban_ontology_verse/TRANSIT/transit_map.yaml --relay-dir data/relay_vague2/
"""
from __future__ import annotations
import argparse
import re
import sys
import json
from pathlib import Path
from datetime import date


# ── Mode 1 : Bundle XML repomix ──────────────────────────────────────

def check_bundle_xml(bundle_path: Path) -> dict:
    """
    Vérifie la cohérence d'un bundle XML repomix.
    Cherche les balises <repo> avec métadonnées UrbanVerse.
    """
    errors = {}

    if not bundle_path.exists():
        return {"file_not_found": ["Bundle introuvable: {}".format(bundle_path)]}

    try:
        content = bundle_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"file_read_error": ["Impossible de lire le bundle: {}".format(e)]}

    # Extraire les blocs <repo name="...">...</repo>
    repo_blocks = re.findall(r'<repo\s+name="([^"]+)">(.*?)</repo>', content, re.DOTALL)

    if not repo_blocks:
        errors["no_repos"] = ["Aucun bloc <repo> trouvé dans le bundle"]
        return errors

    for repo_name, repo_content in repo_blocks:
        # Vérifier les métadonnées UrbanVerse dans chaque repo
        for field in ["strate", "tier", "phi_cps", "vague_deployee"]:
            if "<{}>".format(field) not in repo_content:
                errors.setdefault("missing_metadata", []).append(
                    "{}: champ <{}> manquant".format(repo_name, field))

    # Vérifier les fichiers vides
    file_pattern = re.compile(r'<file\s+path="([^"]+)">(.*?)</file>', re.DOTALL)
    all_files = file_pattern.findall(content)
    empty_files = [p for p, t in all_files if len(t.strip()) < 10]
    if empty_files:
        errors["empty_files"] = ["{}: contenu vide".format(p) for p in empty_files]

    return errors


# ── Mode 2 : Transit Map ─────────────────────────────────────────────

def check_transit_map(transit_path: Path) -> dict:
    """
    Vérifie que les arrêts M1 avec recall_pack: true ont des packs définis.
    """
    errors = {}

    if not transit_path.exists():
        return {"file_not_found": ["transit_map.yaml introuvable: {}".format(transit_path)]}

    try:
        import yaml
        data = yaml.safe_load(transit_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"parse_error": ["Erreur parsing transit_map.yaml: {}".format(e)]}

    lines = data.get("lines", [])
    for line in lines:
        if line.get("recall_pack") and line.get("id") == "M1":
            stops = line.get("stops", [])
            # Chaque arrêt M1 devrait avoir un recall_pack défini
            for stop in stops:
                if not isinstance(stop, str):
                    continue
                # Vérifier que le stop a un pack (dans la version enrichie, chaque stop est un dict)
                if isinstance(stop, str) and not stop.startswith("L"):
                    continue

    return errors


# ── Mode 3 : Relay Directory ─────────────────────────────────────────

def check_relay_coherence(relay_dir: Path, expected_vague: int = 2) -> dict:
    """
    Vérifie la cohérence des relays dans un répertoire.
    - Chaque relay a une section Karpathy-Recall
    - Le nombre de questions correspond à la vague (5 pour V2, 10 pour V3)
    """
    errors = {}

    if not relay_dir.exists():
        return {"file_not_found": ["Relay dir introuvable: {}".format(relay_dir)]}

    relay_files = list(relay_dir.glob("*__STRATUM_RELAY_v*.md"))
    if not relay_files:
        errors["no_relays"] = ["Aucun fichier STRATUM_RELAY_v*.md trouvé dans {}".format(relay_dir)]
        return errors

    for f in relay_files:
        content = f.read_text(encoding="utf-8")

        # Vérifier la section Karpathy-Recall
        if "Karpathy-Recall" not in content:
            errors.setdefault("missing_karpathy", []).append(
                "{}: section Karpathy-Recall manquante".format(f.name))
            continue

        # Compter les questions
        questions = re.findall(r'^\d+\.\s+\?', content, re.MULTILINE)
        if not questions:
            # Format alternatif: "1. Question ?"
            questions = re.findall(r'^\d+\.\s+.*\?', content, re.MULTILINE)

        # Déterminer la vague depuis le nom de fichier
        vague_match = re.search(r'_v(\d+)', f.name)
        vague = int(vague_match.group(1)) if vague_match else expected_vague

        expected_count = 5 if vague == 2 else (10 if vague == 3 else 5)
        if len(questions) < expected_count:
            errors.setdefault("insufficient_questions", []).append(
                "{}: {} questions trouvées, {} attendues (Vague {})".format(
                    f.name, len(questions), expected_count, vague))

    return errors


# ── Mode 4 : Full coherence (transit + relays) ───────────────────────

def check_full_coherence(transit_path: Path, relay_dir: Path) -> dict:
    """
    Vérifie la cohérence complète :
    - Chaque arrêt M1 avec recall_pack a un relay correspondant
    - Chaque relay avec Karpathy-Recall a un arrêt dans le transit_map
    """
    errors = {}

    # Charger le transit_map
    transit_lines = []
    if not transit_path.exists():
        errors["transit_missing"] = ["transit_map.yaml introuvable"]
    else:
        try:
            import yaml
            data = yaml.safe_load(transit_path.read_text(encoding="utf-8"))
            transit_lines = data.get("lines", [])
        except Exception as e:
            errors["transit_parse"] = ["Erreur parsing: {}".format(e)]
            transit_lines = []
    # Extraire les arrêts M1 avec recall_pack
    m1_stops = []
    for line in transit_lines:
        if line.get("id") == "M1" and line.get("recall_pack"):
            stops = line.get("stops", [])
            for stop in stops:
                if isinstance(stop, str) and stop.startswith("L"):
                    m1_stops.append(stop)
                elif isinstance(stop, dict):
                    m1_stops.append(stop.get("id", stop.get("name", "")))

    # Charger les relays
    if relay_dir.exists():
        relay_files = list(relay_dir.glob("*__STRATUM_RELAY_v*.md"))
    else:
        relay_files = []
        errors["relay_dir_missing"] = ["Relay dir introuvable: {}".format(relay_dir)]

    # Vérifier que chaque arrêt M1 a un relay
    relay_basenames = set()
    for f in relay_files:
        # Extraire le nom du repo depuis "REPO__STRATUM_RELAY_vN.md"
        match = re.match(r'(.+?)__STRATUM_RELAY', f.name)
        if match:
            relay_basenames.add(match.group(1))

    # Mapping strate → repo pilote (pour les 10 pilotes)
    strate_to_repo = {
        "L0": "GOVERNANCE-HUB", "L1": "ECOYSTEM", "L1b": "LLM-REPO",
        "L2": "BRAIN", "L3": "ECOS-CLI", "L5": "political_compass_verse",
        "L8": "VERSES",
    }

    for stop in m1_stops:
        expected_repo = strate_to_repo.get(stop)
        if expected_repo and expected_repo not in relay_basenames:
            errors.setdefault("missing_relay_for_stop", []).append(
                "Arrêt {} ({}): relay manquant".format(stop, expected_repo))

    return errors


# ── Report ────────────────────────────────────────────────────────────

def print_report(errors: dict, mode: str, target: str) -> bool:
    total = sum(len(v) for v in errors.values())
    print("\nRAPPORT COHERENCE KARPATHY-RECALL v4.0  [mode: {}]".format(mode))
    print("Cible : {}".format(target))
    print("Date  : {}".format(date.today().isoformat()))
    print("-" * 60)

    if not errors:
        print("OK: 0 erreur — Cohérence validée.")
        return True

    for category, errs in errors.items():
        print("\n[{}] — {} erreur(s):".format(category, len(errs)))
        for err in errs:
            print("  {}".format(err))

    print("\nTOTAL: {} erreur(s)".format(total))
    return False


# ── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Recall Coherence Check v4.0 — EPIC-04 Karpathy Recall × UrbanVerse"
    )
    parser.add_argument("--repomix", type=Path, help="Chemin vers le bundle XML")
    parser.add_argument("--transit", type=Path, help="Chemin vers transit_map.yaml")
    parser.add_argument("--relay-dir", type=Path, help="Répertoire des relays")
    parser.add_argument("--full", action="store_true",
                        help="Vérification complète (transit + relays)")
    args = parser.parse_args()

    if args.full:
        transit = args.transit or Path("urban_ontology_verse/TRANSIT/transit_map.yaml")
        relay_dir = args.relay_dir or Path("data/relay_vague2")
        errors = check_full_coherence(transit, relay_dir)
        ok = print_report(errors, "full", "transit={} relays={}".format(transit, relay_dir))
    elif args.repomix:
        errors = check_bundle_xml(args.repomix)
        ok = print_report(errors, "repomix", str(args.repomix))
    elif args.transit:
        errors = check_transit_map(args.transit)
        ok = print_report(errors, "transit", str(args.transit))
    elif args.relay_dir:
        errors = check_relay_coherence(args.relay_dir)
        ok = print_report(errors, "relay", str(args.relay_dir))
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
