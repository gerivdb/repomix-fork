#!/usr/bin/env python3
"""Update EPIC files 08-11 statuses using regex."""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

epics_dir = r'D:\DO\WEB\TOOLS\L4-TOOLS\REPOMIX-FORK\EPICS'

files = [
    ('EPIC-08-ECOS-CLI-A5.md', 'DEPLOYE (Vague 11)'),
    ('EPIC-09-A9-DATA-MINER-A7-GERICODE.md', 'DEPLOYE (Vague 12)'),
    ('EPIC-10-URBANVERSE-VAGUE-2-3.md', 'DEPLOYE (Vague 12)'),
    ('EPIC-11-MARKETPLACE-PYPI.md', 'DEPLOYE (Vague 13)'),
]

for fname, new_stat in files:
    fpath = os.path.join(epics_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace any status line that has emoji + status
    new_content = re.sub(
        r'\*\*Statut\*\* : .*',
        f'**Statut** : {new_stat}',
        content
    )
    
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'OK: {fname} -> {new_stat}')
    else:
        print(f'WARN: {fname} - no change')

print('Done')
