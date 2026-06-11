#!/usr/bin/env python3
"""
A9 — Mine bundle XML repomix pour extraction metadonnees.
Usage: python scripts/mine_bundle.py --bundle PATH [--output-json PATH]
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path


def mine_bundle(bundle_path: Path) -> dict:
    """
    Extrait les metadonnees d'un bundle XML repomix.
    
    Returns:
        {
            "repo": str,
            "files_count": int,
            "languages": dict,
            "total_lines": int,
            "imports": list,
            "has_tests": bool,
            "has_config": bool,
            "metadata": dict  # headers STRATUM_RELAY si presents
        }
    """
    content = bundle_path.read_text(encoding="utf-8", errors="replace")
    
    # Extraire les fichiers
    file_pattern = re.compile(r'<file\s+path="([^"]+)">(.*?)</file>', re.DOTALL)
    files = file_pattern.findall(content)
    
    # Compter par extension
    ext_counts = {}
    total_lines = 0
    imports = []
    has_tests = False
    has_config = False
    
    for path, text in files:
        ext = Path(path).suffix or "(no ext)"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        lines = len(text.splitlines())
        total_lines += lines
        
        # Detecter tests
        if "test" in path.lower() or "spec" in path.lower():
            has_tests = True
        
        # Detecter config
        if path.endswith((".json", ".yaml", ".yml", ".toml", ".cfg", ".ini")):
            has_config = True
        
        # Extraire imports Python
        if path.endswith(".py"):
            for match in re.finditer(r'^\s*(?:from|import)\s+([\w.]+)', text, re.MULTILINE):
                imports.append(match.group(1))
    
    # Extraire metadata STRATUM_RELAY du header
    metadata = {}
    for field in ["strate", "layer", "phi_cps", "intent_hash", "vague_deployee"]:
        match = re.search(r'{}\s*[:=]\s*["\']?([^"\'\s]+)["\']?'.format(field), content, re.IGNORECASE)
        if match:
            metadata[field] = match.group(1)
    
    return {
        "bundle": str(bundle_path),
        "files_count": len(files),
        "languages": ext_counts,
        "total_lines": total_lines,
        "imports": list(set(imports))[:20],
        "has_tests": has_tests,
        "has_config": has_config,
        "metadata": metadata,
    }


def main():
    parser = argparse.ArgumentParser(description="A9 — Mine bundle XML pour metadonnees")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()
    
    if not args.bundle.exists():
        print("ERREUR: Bundle introuvable: {}".format(args.bundle))
        raise SystemExit(1)
    
    result = mine_bundle(args.bundle)
    
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    
    # Resume
    print("Bundle: {}".format(result["bundle"]))
    print("Fichiers: {}".format(result["files_count"]))
    print("Lignes: {}".format(result["total_lines"]))
    print("Langages: {}".format(result["languages"]))
    print("Tests: {}".format(result["has_tests"]))
    print("Config: {}".format(result["has_config"]))
    if result["metadata"]:
        print("Metadonnees: {}".format(result["metadata"]))
    if args.output_json:
        print("JSON: {}".format(args.output_json))


if __name__ == "__main__":
    main()
