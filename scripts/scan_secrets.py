#!/usr/bin/env python3
"""
A10 — Scan secrets/credentials sur bundle XML unique (TOPOS/Riddler).

Detection locale uniquement (pas de dependance reseau — R3 offline).
Patterns: GitHub tokens, AWS keys, JWT, private keys, passwords inline.

Usage:
    python scripts/scan_secrets.py --bundle PATH [--output-json PATH]
"""
import argparse
import json
import re
from pathlib import Path

# Patterns de detection locale (R3 — pas de reseau)
SECRET_PATTERNS = {
    "github_token": re.compile(r'ghp_[A-Za-z0-9]{36}'),
    "github_pat_v2": re.compile(r'github_pat_[A-Za-z0-9_]{82}'),
    "api_key_generic": re.compile(
        r'(?i)(api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})["\']?'
    ),
    "aws_access_key": re.compile(r'AKIA[0-9A-Z]{16}'),
    "jwt_token": re.compile(
        r'eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_.+/=]*'
    ),
    "private_key": re.compile(r'-----BEGIN (RSA |EC )?PRIVATE KEY-----'),
    "password_inline": re.compile(
        r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']'
    ),
}

SEVERITY_HIGH = {"github_token", "github_pat_v2", "aws_access_key", "private_key", "jwt_token"}


def scan_bundle(bundle_path: Path) -> dict:
    """Scan un bundle XML pour les secrets potentiels."""
    content = bundle_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    findings = []
    for line_num, line in enumerate(lines, 1):
        for pattern_name, pattern in SECRET_PATTERNS.items():
            match = pattern.search(line)
            if match:
                severity = "HIGH" if pattern_name in SEVERITY_HIGH else "MEDIUM"
                snippet = line.strip()[:120]
                # Masquer la valeur detectee
                if len(snippet) > 60:
                    snippet = snippet[:60] + "..."
                findings.append({
                    "pattern": pattern_name,
                    "line": line_num,
                    "snippet": snippet,
                    "severity": severity,
                })

    return {
        "bundle": str(bundle_path),
        "findings": findings,
        "total": len(findings),
        "clean": len(findings) == 0,
    }


def main():
    parser = argparse.ArgumentParser(
        description="A10 — Scan secrets sur bundle XML (offline)"
    )
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    if not args.bundle.exists():
        print(f"ERREUR: Bundle introuvable: {args.bundle}")
        raise SystemExit(1)

    result = scan_bundle(args.bundle)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )

    if result["findings"]:
        print(f"{result['total']} secrets potentiels trouves dans {args.bundle.name}")
        for f in result["findings"][:10]:
            print(f"  L{f['line']} [{f['severity']}] {f['pattern']}: {f['snippet']}")
    else:
        print(f"Aun detecte dans {args.bundle.name}")


if __name__ == "__main__":
    main()
