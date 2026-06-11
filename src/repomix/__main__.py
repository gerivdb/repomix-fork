# CLI entrypoints pour gerivdb-repomix (pyproject.toml [project.scripts])
# Chaque fonction importe le script correspondant depuis scripts/ et appelle main().

import sys
from pathlib import Path

# Ajouter la racine du repo au path pour importer les scripts
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def cli_main():
    """repomix-scan — Scan ecosysteme via verse_detector."""
    from scripts.scan_ecosystem import main
    main()


def bundle_main():
    """repomix-bundle — Bundle mono-repo pour ARGUS."""
    from scripts.bundle_for_argus import main
    main()


def corpus_main():
    """repomix-corpus — Corpus multi-repo par tier."""
    from scripts.bundle_corpus import main
    main()


def ecosystem_main():
    """repomix-ecosystem — Bundle 190 repos avec tier filter et chunking."""
    import argparse
    from pathlib import Path
    from scripts.bundle_corpus import generate_bundles
    from src.repomix.adapters.known_repos_adapter import KnownReposAdapterV3

    parser = argparse.ArgumentParser(
        description="repomix-ecosystem v3 — Bundle 190 repos avec tier filter"
    )
    parser.add_argument(
        "--tier",
        choices=["P0", "P1", "P2", "P3", "ALL"],
        default="ALL",
        help="Filtrer par tier de priorite (P0=critique, ALL=tous)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/bundles/"),
        help="Repertoire de sortie des bundles",
    )
    parser.add_argument(
        "--chunk-size-mb",
        type=float,
        default=80.0,
        help="Taille max par chunk en Mo (defaut: 80)",
    )
    parser.add_argument(
        "--yaml",
        type=Path,
        default=Path("data/known_repositories_190.yaml"),
        help="Chemin vers le YAML 190 repos",
    )
    args = parser.parse_args()

    adapter = KnownReposAdapterV3(yaml_path=args.yaml)
    repos = [
        {"name": n.name, "layer": n.layer, "tier": n.tier, "status": n.status}
        for n in adapter.active_nodes()
    ]
    print(f"[ecosystem] {len(repos)} repos charges depuis {args.yaml}")

    manifest = generate_bundles(
        repos,
        output_dir=args.output_dir,
        chunk_size_mb=args.chunk_size_mb,
        max_per_chunk=50,
        tier_filter=args.tier,
    )
    print(f"[ecosystem] {len(manifest['chunks']} chunks generes — {manifest['elapsed_s']}s")
    if not manifest["kpi_ok"]:
        print("WARN: KPI bundle > 5min")


def recall_main():
    """repomix-recall — Pack recall versionne pour LLM-REPO."""
    from scripts.pack_recall import main
    main()


def validate_main():
    """repomix-validate — Validation complete CI/CD local."""
    from scripts.validate_all import main
    main()


def secrets_main():
    """repomix-secrets — Scan secrets sur bundle XML."""
    from scripts.scan_secrets import main
    main()


def graph_main():
    """repomix-graph — Bundle XML -> graphe dependances JSON."""
    from scripts.xml_to_graph import main
    main()
