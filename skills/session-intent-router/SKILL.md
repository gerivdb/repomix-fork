---
name: session-intent-router
version: 1.0.0
description: Identifie l'intention réelle derrière une requête ambiguë multi-objectifs. Décompose une requête composite en sous-intentions et route vers le skill/outil approprié. Pattern de décomposition multi-couche.
triggers:
  - "quelle est l'intention"
  - "décomposer requête"
  - "session-intent"
  - "router intent"
  - "multi-objectif"
layer: L2
strate: L2-COGNITION
intent_hash: 0xSESSION_INTENT_ROUTER_20260611
---

# session-intent-router

## Objectif

Identifier l'intention réelle derrière une requête ambiguë multi-objectifs et router vers le bon skill/outil.

## Types d'intents détectés

| Type | Description | Router vers |
|------|-------------|-------------|
| skill | Créer/modifier un skill | conv-mining-extractor |
| pipeline | Automatiser un flux | ECOS-CLI |
| citizen | Créer un outil CTULU | CTULU/tools |
| framework | Formaliser un pattern | GOVERNANCE-HUB |
| audit | Vérifier conformité | boot-sequence-validator |
| doc | Générer documentation | conversation-to-prd |
| env | Changer d'environnement | env-context-switcher |

## Décomposition multi-couche

Une requête peut porter simultanément 4 intentions. Exemple :
> "Créer un skill qui vérifie le boot, génère un PRD, et utilise CTULU"

Décomposition :
1. **skill** → créer `boot-sequence-validator`
2. **pipeline** → intégrer dans ECOS-CLI
3. **citizen** → créeroutil CTULU
4. **framework** → formaliser dans GOVERNANCE-HUB

## Utilisation

```bash
# Analyser une requête
python scripts/intent_router.py --query "vérifier le boot et générer un PRD"

# Mode JSON (pour intégration)
python scripts/intent_router.py --query "..." --json
```

## Sortie

```yaml
intents:
  - type: skill
    confidence: 0.92
    target: boot-sequence-validator
  - type: doc
    confidence: 0.85
    target: conversation-to-prd
routing:
  - skill: boot-sequence-validator
    action: create
  - skill: conversation-to-prd
    action: generate
```
