#!/usr/bin/env python3
"""
A8 — Parse bundle XML repomix -> graphe dependances inter-repo.

Extrait les imports Python depuis un bundle XML et produit un graphe
consommable par ECOS-VISION (JSON nodes/edges).

Usage:
    python scripts/xml_to_graph.py --bundle PATH [--output-json PATH]
"""
import argparse
import json
import re
from pathlib import Path


def parse_bundle_xml(bundle_path: Path) -> dict:
    """Parse un bundle XML repomix et retourne {nodes, edges}."""
    content = bundle_path.read_text(encoding="utf-8", errors="replace")

    # Extraire les blocs <file path="...">...</file>
    file_block_pattern = re.compile(r'<file\s+path="([^"]+)">(.*?)</file>', re.DOTALL)
    file_blocks = file_block_pattern.findall(content)

    if not file_blocks:
        return {"nodes": [], "edges": [], "stats": {"nodes": 0, "edges": 0}}

    # Construire les noeuds
    nodes = set()
    file_contents = {}
    for path, text in file_blocks:
        nodes.add(path)
        file_contents[path] = text

    # Extraire les imports Python
    import_pattern = re.compile(
        r'^\s*(?:from|import)\s+([\w][\w.]*)',
        re.MULTILINE
    )

    edges = []
    for src_path, src_text in file_blocks:
        if not src_path.endswith(".py"):
            continue
        for match in import_pattern.finditer(src_text):
            imp = match.group(1)
            # Convertir import path en chemin fichier candidat
            candidate = imp.replace(".", "/") + ".py"
            # Chercher si un fichier du bundle correspond
            for n in nodes:
                if n.endswith(candidate) or n.endswith(imp.replace(".", "/") + ".py"):
                    if n != src_path:
                        edges.append({
                            "source": src_path,
                            "target": n,
                            "type": "import",
                            "import": imp,
                        })
                    break

    return {
        "nodes": [{"id": n} for n in sorted(nodes)],
        "edges": edges,
        "stats": {"nodes": len(nodes), "edges": len(edges)},
    }


def main():
    parser = argparse.ArgumentParser(
        description="A8 — Bundle XML -> graphe dependances JSON"
    )
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    if not args.bundle.exists():
        print(f"ERREUR: Bundle introuvable: {args.bundle}")
        raise SystemExit(1)

    result = parse_bundle_xml(args.bundle)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        print(f"Graphe: {result['stats']['nodes']} nœuds, {result['stats']['edges']} aretes -> {args.output_json}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
