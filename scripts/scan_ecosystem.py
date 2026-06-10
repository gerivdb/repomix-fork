#!/usr/bin/env python3
"""
CLI : scan de l'ecosysteme gerivdb via verse_detector.

Usage:
    python scripts/scan_ecosystem.py [--yaml PATH] [--json] [--verbose]
"""
import argparse
import json
import os
import sys
from pathlib import Path

# Fix encoding Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Ajouter src/repomix au path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "repomix"))

from adapters.known_repos_adapter import load_known_repos_graph
from verse_detector import VERSE_DETECTOR, VerseStatus

DEFAULT_YAML = Path("D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB/known_repositories.yaml")

STATUS_EMOJI = {
    VerseStatus.DORMANT: "💤",
    VerseStatus.EMERGING: "🌱",
    VerseStatus.CATALYZING: "🔮",
    VerseStatus.BORN: "🌟",
    VerseStatus.MATURE: "✨",
}


def main():
    parser = argparse.ArgumentParser(
        description="Scan de l'ecosysteme gerivdb via verse_detector"
    )
    parser.add_argument("--yaml", type=Path, default=DEFAULT_YAML,
                        help="Chemin vers known_repositories.yaml")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Affiche les details par strate")
    args = parser.parse_args()

    if not args.yaml.exists():
        print(f"ERREUR: Fichier YAML introuvable: {args.yaml}", file=sys.stderr)
        sys.exit(1)

    G = load_known_repos_graph(args.yaml)
    obs = VERSE_DETECTOR.observe("gerivdb_ecosystem", G)

    if args.json:
        output = {
            "name": obs.name,
            "score": obs.score,
            "status": obs.status.name,
            "nodes": obs.nodes,
            "edges": obs.edges,
            "eta_days": obs.eta_days,
            "seuil_magique": VERSE_DETECTOR.SEUIL_MAGIQUE,
        }
        print(json.dumps(output, indent=2))
        return

    emoji = STATUS_EMOJI.get(obs.status, "❓")
    born = obs.status in (VerseStatus.BORN, VerseStatus.MATURE)

    print(f"\n{emoji} Ecosysteme gerivdb — {obs.score * 100:.1f}% [{obs.status.name}]")
    print(f"   Repos actifs : {obs.nodes} nœuds / {obs.edges} aretes")
    print(f"   Seuil magique : {VERSE_DETECTOR.SEUIL_MAGIQUE * 100:.0f}%")
    if obs.eta_days:
        print(f"   ETA emergence BORN : {obs.eta_days:.0f} jours")
    else:
        print("   ETA : N/A (1ere observation)")

    if args.verbose:
        # Detail par strate
        from collections import defaultdict
        by_layer = defaultdict(list)
        for n, attr in G.nodes(data=True):
            by_layer[attr.get("layer", "unknown")].append(n)

        print(f"\n   Detail par strate:")
        for layer in sorted(by_layer.keys()):
            repos = by_layer[layer]
            print(f"   {layer}: {len(repos)} repos")
            for r in sorted(repos):
                print(f"     - {r}")

    print()


if __name__ == "__main__":
    main()
