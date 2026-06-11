#!/usr/bin/env python3
"""
A7 — Test E2E: bundle XML -> extraction metadonnees UrbanVerse.
Verifie que les headers STRATUM_RELAY sont presents et lisibles.
"""
from __future__ import annotations
import re
from pathlib import Path


def test_bundle_has_stratum_metadata(bundle_path: Path) -> dict:
    """
    Verifie qu'un bundle XML contient les metadonnees UrbanVerse.
    
    Checks:
    - strate present
    - layer present
    - phi_cps present
    - intent_hash present
    - vague_deployee present
    
    Returns: {field: value|None}
    """
    content = bundle_path.read_text(encoding="utf-8", errors="replace")
    
    fields = {}
    for field in ["strate", "layer", "phi_cps", "intent_hash", "vague_deployee"]:
        # Chercher dans le header XML (commentaire ou balise)
        match = re.search(
            r'(?:<!--\s*|["\']){}\s*[:=]\s*["\']?([^"\'\s,]+)["\']?'.format(field),
            content, re.IGNORECASE
        )
        fields[field] = match.group(1) if match else None
    
    return fields


def validate_bundle_metadata(bundle_path: Path) -> bool:
    """Valide qu'un bundle a toutes les metadonnees requises."""
    fields = test_bundle_has_stratum_metadata(bundle_path)
    
    missing = [k for k, v in fields.items() if v is None]
    if missing:
        print("MANQUANTS: {}".format(missing))
        return False
    
    print("OK: tous les champs presents")
    for k, v in fields.items():
        print("  {}: {}".format(k, v))
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_bundle_a7.py <bundle.xml>")
        sys.exit(1)
    
    bundle_path = Path(sys.argv[1])
    if not bundle_path.exists():
        print("ERREUR: Bundle introuvable")
        sys.exit(1)
    
    ok = validate_bundle_metadata(bundle_path)
    sys.exit(0 if ok else 1)
