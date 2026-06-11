# STRATUM RELAY — ECOYSTEM (L1)

VAGUE: 2 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : L1 – Mairie centrale — SOT operationnel
- **Role canonique** : Source of truth operationnel ecosysteme
- **Parent** : L0
- **Enfants** : L2
- **Connectivite** : DSL (lien hub + regles locales)

## Navigation rapide
- PRD canonique : GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md
- Substrat central : gerivdb/LLM-REPO
- Regles strate : LLM-REPO/RULES/behavior_rules.md#L1

## Regles locales (structurees)
- [R1] : BLO/PLAN/ ne sont jamais modifies sans ADR prealable
- [R2] : WAL integrite verifiee avant chaque operation d'ecriture
- [R3] : Mode BDCP inviolable — jamais de sortie FREE sans ordre explicite
- [R4] : Les scripts PowerShell passent par CMD wrapper (harmonisation-v8)
- [R5] : Verification MCP access avant chaque operation cross-repo

## Karpathy-Recall local (5Q specifiques)
1. Quel est le role canonique d'ECOYSTEM ?
   → SOT operationnel — orchestrateur BLO, WAL, et workflows de l'ecosysteme.
2. Quelle strate amont alimente ECOYSTEM ?
   → L0 (GOVERNANCE-HUB) pour les regles de gouvernance.
3. Quelle strate aval ECOYSTEM alimente-t-il ?
   → L2 (composition) — DevTools, CLI, et outils d'execution.
4. Quelle est la regle R1 d'ECOYSTEM ?
   → BLO/PLAN/ ne sont jamais modifies sans ADR prealable.
5. Comment le WAL garantit-il l'integrite ?
   → Chaque operation d'ecriture est journalisee et verifiee avant execution (wal-reconciler).

## Vague de mise a jour
- Vague courante : 2 (DSL + regles locales + 5Q Karpathy)
- Prochaine vague : 3 (recall 10Q + dependances + FIBRE)
- Timestamp : 2026-06-11
