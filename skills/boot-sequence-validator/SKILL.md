---
name: boot-sequence-validator
version: 1.0.0
description: Valide que le LLM a bien chargé et respecte la séquence de boot LLM_BOOT_PROTOCOL.md (GATE-0→4) avant toute action. Fichier de vérification formelle.
triggers:
  - "vérifier boot sequence"
  - "boot check"
  - "GATE validation"
  - "boot-sequence-validator"
  - "vérifier GATE-0"
layer: L1b
strate: L1b
intent_hash: 0xBOOT_SEQUENCE_VALIDATOR_20260611
---

# boot-sequence-validator

## Objectif

Vérifier qu'un LLM opérant sur gerivdb/* a bien chargé les GATE 0→4 avant d'agir.

## GATEs vérifiés

| GATE | Fichier | Vérifié ? |
|------|---------|-----------|
| GATE-0 | known_repositories.yaml | [ ] |
| GATE-1 | GATE-1 (grep repos) | [ ] |
| GATE-2 | GATE-2 (pas scan GitHub) | [ ] |
| GATE-3 | OrgansRegistry.yaml | [ ] |
| GATE-4 | status dans known_repos | [ ] |
| GATE-4b | repos opérationnels confirmés | [ ] |

## Utilisation

```bash
# Vérifier le boot complet
python scripts/boot_validator.py --full

# Vérifier un GATE spécifique
python scripts/boot_validator.py --gate 0

# Mode silencieux (exit code 0 = OK, 1 = FAIL)
python scripts/boot_validator.py --quiet
```

## Intégration

- **Pre-prompt** : exécuter avant toute réponse impliquant des repos gerivdb
- **ECOS-CLI** : `ecos boot check`
- **Session closeout** : vérifier que tous les GATEs ont été respectés
