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
