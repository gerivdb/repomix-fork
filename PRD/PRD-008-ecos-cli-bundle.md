---
id: PRD-008
title: "ECOS-CLI — Implementation commande `ecos bundle` (A5)"
repo: gerivdb/ECOS-CLI
status: draft
created: 2026-06-11
author: gerivdb
intent_hash: 0xECOS_CLI_BUNDLE_20260611
related:
  - repomix-fork/docs/ecos-cli-interface.md
---

# PRD-008 — ECOS-CLI A5 : implementation `ecos bundle`

## Objet

Implementer dans `gerivdb/ECOS-CLI` la commande `ecos bundle <repo>` specifiee dans `docs/ecos-cli-interface.md` (A5 Vague 6).

## Contexte

Le wrapper `scripts/relay_propagator.py` dans repomix-fork est pret. Il expose 10 pilotes avec STRATUM_RELAY Vague 1. L'ECOS-CLI doit pouvoir appeler ce wrapper.

## Livrables

1. Commande `ecos bundle <repo> [--tier P0|P1|P2] [--output xml|md]`
2. Appel subprocess vers `repomix-fork/scripts/bundle_for_argus.py`
3. Tests d'integration cross-repo (ECOS-CLI vers repomix-fork)
4. ADR dans GOVERNANCE-HUB validant le contrat d'interface

## Contrat d'interface

```
ecos bundle <repo>           # Bundle mono-repo -> ARGUS
ecos bundle --tier P0        # Corpus tier P0 complet
ecos bundle --recall <repo>  # Pack recall LLM-REPO
ecos bundle --argus <repo>   # Bundle ARGUS (alias)
```

## KPI

- Commande `ecos bundle` fonctionnelle sur 3 repos tests
- Tests d'integration passent
- ADR valide dans GOVERNANCE-HUB

## Dependance

Necessite que `gerivdb/ECOS-CLI` soit clone et accessible.
