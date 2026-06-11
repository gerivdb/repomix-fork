#!/usr/bin/env python3
"""Update EPIC files 08-11 to reflect deployed status."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')

def update_epic(path, old_stat, new_stat):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_stat in content:
        content = content.replace(old_stat, new_stat)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  OK: {new_stat[:50]}')
    else:
        print(f'  WARN: not found in {os.path.basename(path)}')

epics_dir = r'D:\DO\WEB\TOOLS\L4-TOOLS\REPOMIX-FORK\EPICS'

# These files have emoji statuts that need updating
replacements = [
    (os.path.join(epics_dir, 'EPICS/EPIC-08-ECOS-CLI-A5.md').replace('EPICS/', 'EPIC-08-ECOS-CLI-A5.md').replace('EPICS\\', 'EPIC-08-ECOS-CLI-A5.md'),
     '**Statut** : A DEMARRER', '**Statut** : DEPLOYE (Vague 11)'),
]

# Actually let me just do it directly
files = [
    ('EPIC-08-ECOS-CLI-A5.md', '**Statut** : A DEMARRER', '**Statut** : DEPLOYE (Vague 11)'),
    ('EPIC-09-A9-DATA-MINER-A7-GERICODE.md', '**Statut** : A DEMARRER', '**Statut** : DEPLOYE (Vague 12)'),
    ('EPIC-10-URBANVERSE-VAGUE-2-3.md', '**Statut** : A DEMARRER', '**Statut** : DEPLOYE (Vague 12)'),
    ('EPIC-11-MARKETPLACE-PYPI.md', '**Statut** : PLANIFIE', '**Statut** : DEPLOYE (Vague 13)'),
]

for fname, old_s, new_s in files:
    fpath = os.path.join(epics_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_s in content:
        content = content.replace(old_s, new_s)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK: {fname} -> {new_s[:40]}')
    else:
        print(f'WARN: {fname} - old status not found')

print('Done')
