#!/usr/bin/env python3
"""Fix STRATUM_RELAY.md residual inconsistencies."""
with open('STRATUM_RELAY.md', 'rb') as f:
    content = f.read()

replacements = [
    (b'| A5 | ECOS-CLI | Commande `ecos bundle <repo>` wrappant repomix | Vague 6 (spec) |',
     b'| A5 | ECOS-CLI | cli_contract.py v1.0.0 | Vague 11 |'),
    (b'| A9 | DATA-MINER | Mining sur bundle complet sans git clone de 76 repos | Vague 6 |',
     b'| A9 | DATA-MINER | mine_bundle v2 | Vague 12 |'),
    (b'| A7 | GeriCode/KiloCode | Metadonnees UrbanVerse dans XML \xe2\x86\x92 contexte ecosysteme natif | Passif |',
     b'| A7 | GeriCode/KiloCode | Metadonnees UrbanVerse dans XML \xe2\x86\x92 contexte ecosysteme natif | Vague 12 |'),
    (b"2. Mode `--ecosystem` : bundle multi-repo (79 repos \xe2\x86\x92 1 XML structure)",
     b"2. Mode `--ecosystem` : bundle multi-repo (190 repos \xe2\x86\x92 chunks 80 Mo/50 repos)"),
    (b'7. Tests unitaires (28 tests, src/repomix/adapters + verse_detector)',
     b'7. Tests unitaires (92 tests, adapters + sync + marketplace + recall + ecosystem + cli_contract)'),
    (b'| 10 | PRD-003 P3+P4 : Karpathy Recall + Fibre/Economie | Deploye |',
     b'| 10 | PRD-003 P3+P4 : Karpathy Recall packs + Fibre/Economie | Deploye |'),
    (b'| 14 | EPIC-04 : Karpathy Recall v4 + transit_map v2 (12 arrets M1) + recall_coherence_check v4 | Deploye |',
     b'| 14 | EPIC-04 : Karpathy Recall v4 + transit_map v2 (12 arrets M1) + recall_coherence_check v4 | Deploye |\n| 15 | PyPI v1.0.0 publie + corrections residuelles STRATUM_RELAY + ADR GOVERNANCE-HUB | Planifie |'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f'OK: {old[:60]}...')
    else:
        print(f'WARN: not found: {old[:60]}...')

with open('STRATUM_RELAY.md', 'wb') as f:
    f.write(content)
print('Done')
