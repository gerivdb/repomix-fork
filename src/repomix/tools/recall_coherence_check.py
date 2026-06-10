#!/usr/bin/env python3
"""
recall_coherence_check.py v3.1 — Mode --repomix (A2).

Etend recall_coherence_check.py v3.0 (VERSES) avec un mode --repomix
qui accepte un bundle XML repomix et verifie la coherence ontologique
directement depuis le bundle, sans dependance reseau.

Usage:
    python src/repomix/tools/recall_coherence_check.py --repomix bundle.xml [--manifest PATH]
    python src/repomix/tools/recall_coherence_check.py --mode opensrc
    python src/repomix/tools/recall_coherence_check.py --mode local --relay-dir /path/to/repos
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import date


def check_bundle_xml(bundle_path: Path) -> dict:
    """
    Verifie la coherence d'un bundle XML repomix.

    Le bundle repomix a un format mixte: texte brut + XML <files>...</files>.
    On extrait la partie XML pour le parsing.
    """
    errors = {}

    if not bundle_path.exists():
        return {"file_not_found": [f"  Bundle introuvable: {bundle_path}"]}

    try:
        content = bundle_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"file_read_error": [f"  Impossible de lire le bundle: {e}"]}

    # Extraire la section <files>...</files>
    files_match = re.search(r'<files>(.*?)</files>', content, re.DOTALL)
    if not files_match:
        return {"structure": ["  Element <files> absent du bundle"]}

    files_section = files_match.group(1)

    # Parser les <file path="...">...</file> via regex (plus robuste que XML)
    file_pattern = re.compile(
        r'<file\s+path="([^"]+)">(.*?)</file>',
        re.DOTALL
    )
    all_files_raw = file_pattern.findall(files_section)

    if not all_files_raw:
        errors["no_files"] = ["  Aucun element <file> trouve dans le bundle"]

    # Construire des objets similaires a Element
    class FileEntry:
        def __init__(self, path, text):
            self._path = path
            self._text = text
        def get(self, attr, default=""):
            return self._path if attr == "path" else default
        @property
        def text(self):
            return self._text

    all_files = [FileEntry(p, t) for p, t in all_files_raw]

    empty_files = []
    duplicate_paths = []
    seen_paths = set()

    for f in all_files:
        path = f.get("path", "")
        if path in seen_paths:
            duplicate_paths.append(path)
        seen_paths.add(path)
        file_text = f.text or ""
        if len(file_text.strip()) < 10:
            empty_files.append(path)

    if empty_files:
        errors["empty_files"] = [f"  {p}: contenu vide" for p in empty_files]
    if duplicate_paths:
        errors["duplicates"] = [f"  {p}: duplique" for p in duplicate_paths]

    # Check 2: Headers STRATUM_RELAY dans le contenu du bundle
    required_headers = ["strate", "layer", "phi_cps"]
    missing_headers = [h for h in required_headers if h not in content.lower()]
    if missing_headers:
        errors["missing_headers"] = [f"  Header STRATUM_RELAY manquant: {h}" for h in missing_headers]

    # Check 3: Imports Python non resolus (heuristique)
    import_errors = []
    for f in all_files:
        path = f.get("path", "")
        if not path.endswith(".py"):
            continue
        file_text = f.text or ""
        for match in re.finditer(r'^\s*from\s+(src\.\w+|NEXUS\.\w+)', file_text, re.MULTILINE):
            import_errors.append(f"  {path}: import non resolu - {match.group(0).strip()}")
        for match in re.finditer(r'^\s*import\s+(src|NEXUS)\b', file_text, re.MULTILINE):
            import_errors.append(f"  {path}: import non resolu - {match.group(0).strip()}")

    if import_errors:
        errors["unresolved_imports"] = import_errors

    # Check 4: Score de couverture
    total = len(all_files)
    non_empty = total - len(empty_files)
    if total > 0:
        coverage = non_empty / total
        if coverage < 0.8:
            errors["low_coverage"] = [
                f"  Couverture: {coverage*100:.0f}% ({non_empty}/{total} fichiers avec contenu)"
            ]

    return errors
    empty_files = []
    duplicate_paths = []
    seen_paths = set()

    for f in all_files:
        path = f.get("path", "")
        if path in seen_paths:
            duplicate_paths.append(path)
        seen_paths.add(path)

        content = f.text or ""
        if len(content.strip()) < 10:
            empty_files.append(path)

    if empty_files:
        errors["empty_files"] = [f"  {p}: contenu vide ou trop court" for p in empty_files]
    if duplicate_paths:
        errors["duplicates"] = [f"  {p}: chemin duplique" for p in duplicate_paths]

    # Check 3: Headers STRATUM_RELAY dans le contenu
    full_text = ET.tostring(root, encoding="unicode", method="text")
    required_headers = ["strate", "layer", "phi_cps"]
    missing_headers = [h for h in required_headers if h not in full_text.lower()]
    if missing_headers:
        errors["missing_headers"] = [f"  Header STRATUM_RELAY manquant: {h}" for h in missing_headers]

    # Check 4: Imports Python non resolus (heuristique)
    import_errors = []
    for f in all_files:
        path = f.get("path", "")
        if not path.endswith(".py"):
            continue
        content = f.text or ""
        # Chercher les imports from src.* ou from NEXUS.*
        for match in re.finditer(r'^\s*from\s+(src\.\w+|NEXUS\.\w+)', content, re.MULTILINE):
            import_errors.append(f"  {path}: import non resolu — {match.group(0).strip()}")
        for match in re.finditer(r'^\s*import\s+(src|NEXUS)\b', content, re.MULTILINE):
            import_errors.append(f"  {path}: import non resolu — {match.group(0).strip()}")

    if import_errors:
        errors["unresolved_imports"] = import_errors

    # Check 5: Score de couverture
    total = len(all_files)
    non_empty = total - len(empty_files)
    if total > 0:
        coverage = non_empty / total
        if coverage < 0.8:
            errors["low_coverage"] = [
                f"  Couverture: {coverage*100:.0f}% ({non_empty}/{total} fichiers avec contenu)"
            ]

    return errors


def print_report(errors: dict, bundle_path: Path, mode: str = "repomix") -> bool:
    total = sum(len(v) for v in errors.values())
    print(f"\n  RAPPORT COHERENCE REPOMIX v3.1  [mode: {mode}]")
    print(f"  Bundle : {bundle_path}")
    print(f"  Date   : {date.today().isoformat()}")
    print("-" * 60)

    if not errors:
        print("  OK: 0 erreur — Bundle coherent.")
        return True

    for category, errs in errors.items():
        print(f"\n  [{category}] — {len(errs)} erreur(s):")
        for err in errs:
            print(f"    {err}")

    print(f"\n  TOTAL: {total} erreur(s)")
    return total == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recall Coherence Check v3.1 — Mode repomix")
    parser.add_argument("--repomix", type=Path, help="Chemin vers le bundle XML a verifier")
    parser.add_argument("--manifest", type=Path, default=None, help="Chemin vers relay_wave_manifest.yaml")
    args = parser.parse_args()

    if not args.repomix:
        print("ERREUR: --repomix <bundle.xml> requis", file=sys.stderr)
        sys.exit(1)

    errors = check_bundle_xml(args.repomix)
    ok = print_report(errors, args.repomix)
    sys.exit(0 if ok else 1)
