---
id: PRD-010
title: "UrbanVerse — Vague 2+3 : Karpathy Recall + Fibre"
repo: gerivdb/VERSES
status: draft
created: 2026-06-11
author: gerivdb
intent_hash: 0xURBANVERSE_VAGUE2_3_20260611
related:
  - repomix-fork/PRD/PRD-003-urban-ontology-verse.md
---

# PRD-010 — UrbanVerse Vague 2+3

## Objet

Enrichir les 11 relais pilotes deployes (Vague 1) avec :
- Vague 2 : regles locales + micro-rappels (5Q)
- Vague 3 : recall packs complets (10Q) + section dependances + passage FIBRE

## Livrables

### Vague 2 (11 pilotes)
- Enrichir `STRATUM_RELAY_TEMPLATE.md` avec regles locales structurees
- Ajouter 5 questions Karpathy-Recall par relais
- Script `relay_propagator_v2.py` — mode Vague 2

### Vague 3 (5 repos critiques: L0+L1b+L3)
- Recall packs complets (10Q) dans les relais
- Section dependances presente
- Passage DSL -> FIBRE pour 5 repos critiques
- Synchronisation avec `LLM-REPO/TRAINING/` (recall packs)

### Cadastre etendu
- 11 pilotes -> ~71 repos actifs
- `cadastre_v2.yaml` avec tous les repos actifs

## KPI

- 11 relais Vague 2 deployes
- 5 relais Vague 3 (FIBRE)
- Cadastre ~71 repos
- Recall packs synchronises avec LLM-REPO/TRAINING/

## Dependance

Necessite acces a `gerivdb/VERSES` (local ou clone).
