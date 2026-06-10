#!/usr/bin/env python3
"""
Validation complete repomix-fork (CI/CD local ENV1).

1. Guards STRATUM_RELAY (R1, R2, R3)
2. Scan ecosysteme (verse_detector)
3. Bundle mono-repo test (dry-run)
4. Rapport JSON -> data/validation_report.json

Usage: python scripts/validate_all.py [--json]
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
REPO_ROOT.mkdir(exist_ok=True) if not REPO_ROOT.exists() else None

report = {
    "timestamp": datetime.now().isoformat(),
    "guards": {},
    "scan": {},
    "bundle": {},
    "overall_ok": False,
}


# ── 1. Guards ───────────────────────────────────────────────────────────────
def run_guards() -> bool:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / ".githooks" / "pre-push")],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    report["guards"]["stdout"] = result.stdout.strip()
    report["guards"]["returncode"] = result.returncode
    return result.returncode == 0


# ── 2. Scan ecosysteme ──────────────────────────────────────────────────────
def run_scan() -> bool:
    scan_script = REPO_ROOT / "scripts" / "scan_ecosystem.py"
    if not scan_script.exists():
        report["scan"]["error"] = "scan_ecosystem.py introuvable"
        return False
    result = subprocess.run(
        [sys.executable, str(scan_script), "--json"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO_ROOT),
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}
    )
    if result.returncode == 0 and result.stdout.strip():
        try:
            data = json.loads(result.stdout)
            report["scan"] = data
            return True
        except json.JSONDecodeError:
            report["scan"]["error"] = "JSON invalide"
            return False
    report["scan"]["error"] = result.stderr.strip() or "Echec scan"
    return False


# ── 3. Bundle dry-run ────────────────────────────────────────────────────────
def run_bundle_dry_run() -> bool:
    bundle_script = REPO_ROOT / "scripts" / "bundle_for_argus.py"
    if not bundle_script.exists():
        report["bundle"]["error"] = "bundle_for_argus.py introuvable"
        return False
    result = subprocess.run(
        [sys.executable, str(bundle_script),
         "--repo", "gerivdb/repomix-fork", "--dry-run"],
        capture_output=True, text=True, timeout=10, cwd=str(REPO_ROOT)
    )
    report["bundle"]["dry_run_ok"] = result.returncode == 0
    report["bundle"]["stdout"] = result.stdout.strip()
    return result.returncode == 0


# ── 4. Scan secrets sur le dernier bundle ARGUS ──────────────────────────────
def run_secrets_scan() -> bool:
    import glob
    bundle_dir = REPO_ROOT / "data" / "argus" / "bundles"
    if not bundle_dir.exists():
        report["secrets"] = {"status": "no_bundle_dir"}
        return True
    bundles = sorted(bundle_dir.glob("*.xml"), reverse=True)
    if not bundles:
        report["secrets"] = {"status": "no_bundles"}
        return True
    latest = bundles[0]
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "scan_secrets.py"),
         "--bundle", str(latest), "--output-json",
         str(REPO_ROOT / "data" / "secrets_report.json")],
        capture_output=True, text=True, timeout=30, cwd=str(REPO_ROOT)
    )
    report["secrets"] = {"status": "scanned", "bundle": str(latest)}
    return result.returncode == 0


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validation complete repomix-fork")
    parser.add_argument("--json", action="store_true", help="Sortie JSON uniquement")
    args = parser.parse_args()

    guards_ok = run_guards()
    scan_ok = run_scan()
    bundle_ok = run_bundle_dry_run()
    secrets_ok = run_secrets_scan()

    report["overall_ok"] = guards_ok and scan_ok and bundle_ok and secrets_ok

    # Ecriture rapport
    out = REPO_ROOT / "data" / "validation_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"  RAPPORT VALIDATION REPOMIX-FORK")
        print(f"  {report['timestamp']}")
        print(f"{'='*60}")
        print(f"  Guards R1/R2/R3 : {'OK' if guards_ok else 'ECHEC'}")
        print(f"  Scan ecosysteme : {'OK' if scan_ok else 'ECHEC'}", end="")
        if scan_ok:
            print(f" (score: {report['scan'].get('score', 0)*100:.1f}% [{report['scan'].get('status', '?')}])")
        else:
            print()
        print(f"  Bundle dry-run  : {'OK' if bundle_ok else 'ECHEC'}")
        print(f"  Scan secrets    : {'OK' if secrets_ok else 'ECHEC'}")
        print(f"{'='*60}")
        print(f"  RESULTAT: {'OK' if report['overall_ok'] else 'ECHEC'}")
        print(f"  Rapport: data/validation_report.json")

    sys.exit(0 if report["overall_ok"] else 1)


if __name__ == "__main__":
    main()
