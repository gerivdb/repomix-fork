---
name: conversation-to-prd
version: 1.0.0
description: Transforme une conversation riche et structurée en PRD (Product Requirement Document) complet avec frontmatter RSS-v2, user stories, tâches techniques et critères d'acceptation.
triggers:
  - "transformer conversation en PRD"
  - "conversation to PRD"
  - "extraire PRD de session"
  - "générer PRD"
layer: L0
strate: L0-GOVERNANCE
intent_hash: 0xCONVERSATION_TO_PRD_20260611
---

# conversation-to-prd

## Objectif

Transformer une conversation riche en PRD structuré :
- Frontmatter RSS-v2 (id, title, status, author, date, intent_hash)
- User Stories avec critères d'acceptation
- Tâches techniques (checklist)
- Définition de "Done"
- Dépendances

## Entrée

Conversation structurée (JSON/MD) avec :
- Messages user/assistant
- Métadonnées (session, env, strate)
- Actions réalisées

## Sortie

```markdown
---
id: PRD-XXX
title: "Titre du PRD"
status: draft
date: "YYYY-MM-DD"
author: gerivdb
intent_hash: 0x...
---

# PRD-XXX — Titre

## Contexte
...

## User Stories
| ID | Story | Critères | Statut |
|----|-------|----------|--------|
| US-X-1 | ... | ... | [ ] |

## Tâches techniques
- [ ] Tâche 1
- [ ] Tâche 2

## Définition de "Done"
- [ ] Critère 1
- [ ] Critère 2
```

## Utilisation

```bash
# Depuis une conversation
python scripts/conv_to_prd.py --input session.json --output PRD/

# Mode interactif
python scripts/conv_to_prd.py --interactive
```
