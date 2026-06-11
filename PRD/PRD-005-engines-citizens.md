---
id: PRD-005
title: "repomix-fork — Activation moteurs internes (src.engines, src.citizens)"
repo: gerivdb/repomix-fork
status: draft
created: 2026-06-11
author: gerivdb
intent_hash: 0xREPOMIX_ENGINES_CITIZENS_20260611
---

# PRD-005 — Activation moteurs internes

## Statut

**NON APPLICABLE** — Les 29 tests ignores sont des tests du projet upstream yamadashy/repomix (TypeScript/Node.js), pas du fork Python. Ils ne peuvent pas etre reactives sans porter tout le codebase TypeScript.

## Analyse

Les modules `src.engines.*`, `src.citizens.*`, `src.joker.*`, `src.events.*`, `src.ontological_memory.*`, `src.triad.*` n'existent pas dans repomix-fork. Ce sont des modules du projet upstream.

## Decision

PRD-005 **annule** — pas de stubs crees pour du code TypeScript upstream. Les 29 tests resteront ignores (conftest.py).

## Alternative

La reactivation de ces tests necessiterait :
1. Un port complet du codebase TypeScript de yamadashy/repomix vers Python
2. Ou un environnement hybride Node.js + Python
3. Hors scope repomix-fork — a traiter dans un dedie repo si necessaire.
