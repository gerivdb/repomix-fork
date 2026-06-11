#!/usr/bin/env python3
"""Update EPIC files 07-11 to reflect deployed status."""
import os, sys

sys.stdout.reconfigure(encoding='utf-8')

def update_epic(path, old_stat, new_stat):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_stat in content:
        content = content.replace(old_stat, new_stat)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  OK: {new_stat[:40]}')
    else:
        print(f'  WARN: old status not found in {os.path.basename(path)}')

epics_dir = r'D:\DO\WEB\TOOLS\L4-TOOLS\REPOMIX-FORK\EPICS'

print('EPIC-07:')
update_epic(os.path.join(epics_dir, 'EPIC-07-ECOSYSTEM-190-REPOS.md'),
    '**Statut** : A DEMARRER', '**Statut** : DEPLOYE (Vague 11)')

print('EPIC-08:')
update_epic(os.path.join(epics_dir, 'EPIC-08-ECOS-CLI-A5.md'),
    '**Statut** : A DEMARRER', '**Statut** : DEPLOYE (Vague 11)')

print('EPIC-09:')
update_epic(os.path.join(epics_dir, 'EPIC-09-A9-DATA-MINER-A7-GERICODE.md'),
    '**Statut** : A DEMARRER', '**Statut** : DEPLOYE (Vague 12)')

print('EPIC-10:')
update_epic(os.path.join(epics_dir, 'EPIC-10-URBANVERSE-VAGUE-2-3.md'),
    '**Statut** : A DEMARRER', '**Statut** : DEPLOYE (Vague 12)')

print('EPIC-11:')
update_epic(os.path.join(epics_dir, 'EPIC-11-MARKETPLACE-PYPI.md'),
    '**Statut** : A DEMARRER', '**Statut** : DEPLOYE (Vague 13)')

print('Done')
