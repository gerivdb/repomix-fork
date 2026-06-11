#!/usr/bin/env python3
"""
mine_bundle.py v2 — PRD-009 A9
Mine bundle XML repomix pour extraction metadonnees.
Support multi-repo, filtre par repo, extraction fonctions/classes/todos/strings.

Usage:
    python scripts/mine_bundle.py --input bundle.xml --output report.json
    python scripts/mine_bundle.py --input bundle.xml --repo-filter NEXUS --repo-filter BRAIN
    python scripts/mine_bundle.py --input bundle_001.xml --output mining_report.json
"""
from __future__ import annotations
import argparse
import json
import re
import time
from pathlib import Path
from typing import Optional


def mine_bundle(bundle_path: Path, repo_filter: Optional[list[str]] = None) -> dict:
    """
    Extrait les metadonnees d'un bundle XML repomix.

    Args:
        bundle_path: Chemin vers le bundle XML
        repo_filter: Liste de noms de repos a filtrer (None = tous)

    Returns:
        {
            "bundle": str,
            "repos": [
                {
                    "name": str,
                    "layer": str,
                    "tier": str,
                    "files_count": int,
                    "languages": dict,
                    "total_lines": int,
                    "imports": list,
                    "functions": list,
                    "classes": list,
                    "todos": list,
                    "strings": list,
                    "has_tests": bool,
                    "has_config": bool,
                    "metadata": dict
                }
            ],
            "summary": {...}
        }
    """
    t0 = time.perf_counter()
    content = bundle_path.read_text(encoding="utf-8", errors="replace")

    # Extraire les repos du bundle
    repo_blocks = re.findall(
        r'<repo\s+name="([^"]+)">(.*?)</repo>', content, re.DOTALL
    )

    if not repo_blocks:
        # Fallback: traiter le bundle comme un seul repo
        repo_blocks = [("unknown", content)]

    repos = []
    for repo_name, repo_content in repo_blocks:
        if repo_filter and repo_name not in repo_filter:
            continue

        repo_data = _mine_repo(repo_name, repo_content)
        repos.append(repo_data)

    elapsed = time.perf_counter() - t0

    # Summary
    total_files = sum(r["files_count"] for r in repos)
    total_lines = sum(r["total_lines"] for r in repos)
    all_languages = {}
    for r in repos:
        for ext, count in r["languages"].items():
            all_languages[ext] = all_languages.get(ext, 0) + count

    return {
        "bundle": str(bundle_path),
        "repos_count": len(repos),
        "repos": repos,
        "summary": {
            "total_files": total_files,
            "total_lines": total_lines,
            "languages": all_languages,
            "has_tests": any(r["has_tests"] for r in repos),
            "has_config": any(r["has_config"] for r in repos),
            "elapsed_s": round(elapsed, 3),
        },
    }


def _mine_repo(repo_name: str, content: str) -> dict:
    """Mine un seul bloc repo."""
    # Extraire les fichiers
    file_pattern = re.compile(r'<file\s+path="([^"]+)">(.*?)</file>', re.DOTALL)
    files = file_pattern.findall(content)

    ext_counts = {}
    total_lines = 0
    imports = []
    functions = []
    classes = []
    todos = []
    strings = []
    has_tests = False
    has_config = False

    for path, text in files:
        ext = Path(path).suffix or "(no ext)"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        lines = len(text.splitlines())
        total_lines += lines

        if "test" in path.lower() or "spec" in path.lower():
            has_tests = True
        if path.endswith((".json", ".yaml", ".yml", ".toml", ".cfg", ".ini")):
            has_config = True

        # Extraire imports Python/JS/TS
        if path.endswith((".py", ".js", ".ts", ".tsx", ".jsx")):
            for match in re.finditer(r'^\s*(?:from|import)\s+([\w.]+)', text, re.MULTILINE):
                imports.append(match.group(1))

        # Extraire fonctions
        if path.endswith(".py"):
            for match in re.finditer(r'^\s*def\s+(\w+)\s*\(', text, re.MULTILINE):
                functions.append(match.group(1))
        elif path.endswith((".js", ".ts", ".tsx")):
            for match in re.finditer(r'(?:function|const|let|var)\s+(\w+)\s*[=(]', text):
                functions.append(match.group(1))

        # Extraire classes
        if path.endswith((".py", ".js", ".ts", ".tsx", ".jsx")):
            for match in re.finditer(r'^\s*class\s+(\w+)', text, re.MULTILINE):
                classes.append(match.group(1))

        # Extraire TODO/FIXME/HACK
        for match in re.finditer(r'(?:#|//|/\*)\s*(TODO|FIXME|HACK|XXX)[:\s]*(.*)', text):
            todos.append({"type": match.group(1), "text": match.group(2).strip()})

        # Extraire strings courts (messages, labels)
        for match in re.finditer(r'["\']([^"\']{5,80})["\']', text):
            s = match.group(1)
            if not s.startswith("http") and not s.startswith("data:"):
                strings.append(s)

    # Extraire metadata UrbanVerse du bloc
    metadata = {}
    for field in ["strate", "tier", "phi_cps", "intent_hash", "vague_deployee", "layer"]:
        match = re.search(
            r'<{field}>([^<]+)</{field}>'.format(field=field), content
        )
        if not match:
            match = re.search(
                r'{}\s*[:=]\s*["\']?([^"\'\s,]+)["\']?'.format(field),
                content, re.IGNORECASE
            )
        if match:
            metadata[field] = match.group(1)

    return {
        "name": repo_name,
        "files_count": len(files),
        "languages": ext_counts,
        "total_lines": total_lines,
        "imports": sorted(set(imports))[:30],
        "functions": sorted(set(functions))[:30],
        "classes": sorted(set(classes))[:20],
        "todos": todos[:20],
        "strings": sorted(set(strings))[:20],
        "has_tests": has_tests,
        "has_config": has_config,
        "metadata": metadata,
    }


def main():
    parser = argparse.ArgumentParser(
        description="mine_bundle v2 — Extraction metadonnees depuis bundle XML"
    )
    parser.add_argument("--input", type=Path, required=True,
                        help="Chemin vers le bundle XML")
    parser.add_argument("--output", type=Path, default=None,
                        help="Chemin vers le rapport JSON de sortie")
    parser.add_argument("--repo-filter", action="append", default=[],
                        help="Filtrer par nom de repo (repetable)")
    args = parser.parse_args()

    if not args.input.exists():
        print("ERREUR: Bundle introuvable: {}".format(args.input))
        raise SystemExit(1)

    result = mine_bundle(args.input, repo_filter=args.repo_filter or None)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Resume
    s = result["summary"]
    print("Bundle: {}".format(result["bundle"]))
    print("Repos: {}".format(result["repos_count"]))
    print("Fichiers: {}".format(s["total_files"]))
    print("Lignes: {}".format(s["total_lines"]))
    print("Langages: {}".format(s["languages"]))
    print("Tests: {}".format(s["has_tests"]))
    print("Config: {}".format(s["has_config"]))
    print("Elapsed: {}s".format(s["elapsed_s"]))
    if args.output:
        print("JSON: {}".format(args.output))


if __name__ == "__main__":
    main()
