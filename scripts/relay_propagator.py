#!/usr/bin/env python3
"""
PRD-003 Phase 2 — relay_propagator.py (wrapper repomix-fork)
Appelle le relay_propagator v4.0 de VERSES via import.
Fallback: generation locale si VERSES inaccessible.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import date
from pathlib import Path

VERSES_ROOT = Path("D:/DO/WEB/TOOLS/L4-TOOLS/VERSES")
REPO_ROOT = Path(__file__).parent.parent

# 10 repos pilotes — 2 par grande strate
PILOT_REPOS = [
    {"repo": "GOVERNANCE-HUB", "strate": "L0", "arrondissement": "Hotel de Ville — Constitution",
     "role": "Constitution, cadastre, registres", "parent": "—", "children": "L1, L1b"},
    {"repo": "ECOYSTEM", "strate": "L1", "arrondissement": "Mairie centrale — SOT operationnel",
     "role": "Source of truth operationnel ecosysteme", "parent": "L0", "children": "L2"},
    {"repo": "BRAIN", "strate": "L2", "arrondissement": "Grandes Ecoles — Cognition",
     "role": "Logique ternaire, cognition distribuee", "parent": "L1", "children": "L3"},
    {"repo": "ECOS-CLI", "strate": "L3", "arrondissement": "Voiries — CLI executable",
     "role": "Interface CLI ecosysteme, commandes automation", "parent": "L2", "children": "L4"},
    {"repo": "repomix-fork", "strate": "L3", "arrondissement": "Voiries — Bundler souverain",
     "role": "Bundler repomix fork, scan + verses + marketplace", "parent": "L2", "children": "L4"},
    {"repo": "LLM-REPO", "strate": "L1b", "arrondissement": "Substrat cognitif LLM",
     "role": "LLM_BOOT_PROTOCOL, GATE-0->4, regles comportement", "parent": "L0", "children": "L1"},
    {"repo": "NEXUS", "strate": "L1", "arrondissement": "Archives centrales — Aggregation data",
     "role": "Aggregation cross-repo, NEXUS core", "parent": "L0", "children": "L2"},
    {"repo": "FLUENCE", "strate": "L2", "arrondissement": "Grandes Ecoles — Logique",
     "role": "Logique FLUENCE, phi-CPS, calcul emergence", "parent": "L1", "children": "L3"},
    {"repo": "VERSES", "strate": "L8", "arrondissement": "Culture — Verses ontologiques",
     "role": "Registry des verses, UrbanVerse, BATVERSE", "parent": "L7", "children": "—"},
    {"repo": "political_compass_verse", "strate": "L5", "arrondissement": "Meta — Gouvernance",
     "role": "Boussole politique, scenarios, trits", "parent": "L4", "children": "L6"},
]


def _render_relay(repo: dict, vague: int = 1) -> str:
    today = date.today().isoformat()
    return """# STRATUM RELAY — {repo} ({strate})

VAGUE: {vague} | Synchro: {today} | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : {strate} – {arrondissement}
- **Role canonique** : {role}
- **Parent** : {parent}
- **Enfants** : {children}
- **Connectivite** : DSL (Vague 1 — lien hub uniquement)

## Navigation rapide
- PRD canonique : GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md
- Substrat central : gerivdb/LLM-REPO
- Regles strate : LLM-REPO/RULES/behavior_rules.md#{strate}

## Regles locales (extrait hub)
- [R1] : Fichiers proteges — jamais ecrases par merge upstream
- [R2] : Push direct sur main interdit — PR obligatoire
- [R3] : Offline-first — fonctionnement sans reseau garanti

## Karpathy-Recall local
1. Quel est le role canonique de ce repo dans l'ecosysteme ?
2. Quelle strate amont alimente ce repo, et quelle strate aval il alimente ?
3. Quelle est la regle R1 de ce repo ?

## Vague de mise a jour
- Vague courante : {vague} (DSL — identite stratique + lien hub)
- Prochaine vague : Vague 2 (regles locales + micro-rappels)
- Timestamp : {today}
""".format(repo=repo["repo"], strate=repo["strate"], arrondissement=repo["arrondissement"],
           role=repo["role"], parent=repo["parent"], children=repo["children"],
           vague=vague, today=today)


def propagate_verses():
    """Importe et appelle le relay_propagator v4.0 de VERSES."""
    sys.path.insert(0, str(VERSES_ROOT / "urban_ontology_verse" / "TOOLS"))
    try:
        import relay_propagator as rp
        if hasattr(rp, 'propagate'):
            print("Utilisation du relay_propagator VERSES v4.0")
            return rp.propagate
        else:
            print("VERSES relay_propagateur: fonction propagate introuvable — fallback local")
            return None
    except (ImportError, AttributeError) as e:
        print("VERSES relay_propagateur inaccessible ({}) — fallback local".format(e))
        return None


def propagate(dry_run: bool = True, output_dir: Path = None) -> dict:
    results = {"generated": [], "skipped": [], "dry_run": dry_run}
    out = output_dir or REPO_ROOT / "data" / "relay_vague1"
    if not dry_run:
        out.mkdir(parents=True, exist_ok=True)

    verses_fn = propagate_verses()

    if verses_fn and not dry_run:
        return verses_fn(dry_run=False, output_dir=out)

    for repo in PILOT_REPOS:
        content = _render_relay(repo)
        fname = "{repo}__STRATUM_RELAY_v1.md".format(repo=repo["repo"])
        if dry_run:
            print("[DRY-RUN] {repo} ({strate}) -> {fname}".format(
                repo=repo["repo"], strate=repo["strate"], fname=fname))
            results["generated"].append(repo["repo"])
        else:
            (out / fname).write_text(content, encoding="utf-8")
            results["generated"].append(repo["repo"])
            print("OK: {}".format(fname))

    manifest = {
        "vague": 1, "date": date.today().isoformat(),
        "repos": [r["repo"] for r in PILOT_REPOS],
        "count": len(PILOT_REPOS),
        "connectivite": "DSL",
    }
    if not dry_run:
        (out / "relay_manifest_v1.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8")
    return results


def main():
    parser = argparse.ArgumentParser(description="relay_propagator — wrapper PRD-003")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    dry = not args.commit
    results = propagate(dry_run=dry, output_dir=args.output_dir)
    print("\n{dry}{count} relais generes".format(
        dry="[DRY-RUN] " if dry else "", count=len(results["generated"])))


if __name__ == "__main__":
    main()
