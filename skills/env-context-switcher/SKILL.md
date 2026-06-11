---
name: env-context-switcher
version: 1.0.0
description: Gère la transition entre environnements (ENV1/ENV2/COMET), résout les alias, et retourne les configurations actives. Centralise la logique de contexte d'exécution.
triggers:
  - "switch env"
  - "quel env actif"
  - "résoudre alias env"
  - "env-context"
  - "transition environnement"
layer: L4
strate: L4-TOOLS
intent_hash: 0xENV_CONTEXT_SWITCHER_20260611
---

# env-context-switcher

## Objectif

Résoudre les alias d'environnement et retourner la configuration active :
- `ENV1` = DEV_COMET = Space "4" = HP Z600 Windows 10
- `ENV2` = DEV_COMET = Space "4" = HP Z600 (même machine, contexte différent)
- `COMET` = alias pour ENV1/ENV2 selon le contexte

## Mapping

| Alias | Environnement | Machine | Strate |
|-------|--------------|---------|--------|
| ENV1 | DEV_COMET | HP Z600 Win10 | L4 |
| ENV2 | DEV_COMET | HP Z600 | L4 |
| COMET | ENV1 ou ENV2 | HP Z600 | L4 |

## Utilisation

```bash
# Résoudre un alias
python scripts/env_resolver.py --alias COMET
# → {"env": "ENV1", "machine": "HP Z600", "strate": "L4"}

# Vérifier la config active
python scripts/env_resolver.py --check

# Lister tous les alias
python scripts/env_resolver.py --list
```

## Intégration

- **ECOS-CLI** : `ecos env check` → appelle env_resolver
- **LLM_BOOT_PROTOCOL** : GATE-0 vérifie l'env actif
- **Scripts PowerShell** : `$env:COMET_ENV` résolu automatiquement
