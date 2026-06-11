# STRATUM RELAY — ECOYSTEM (L1)

VAGUE: 3 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : L1 – Mairie centrale — SOT operationnel
- **Role canonique** : Source of truth operationnel ecosysteme
- **Parent** : L0
- **Enfants** : L2
- **Connectivite** : FIBRE (Full Interconnect Bundle for Repository Emergence)

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

## Karpathy-Recall local (10Q specifiques)
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
6. Quels sont les 3 fichiers les plus critiques de ECOYSTEM ?
   → Depend du repo — voir STRATUM_RELAY.md et PRD associe pour les fichiers proteges.
7. Comment ECOYSTEM interagit-il avec LLM-REPO ?
   → Via LLM_BOOT_PROTOCOL.md et les regles comportement (GATE-0->4) — tout agent LLM doit lire ECOYSTEM avant operation.
8. Quel est l'intent_hash de ECOYSTEM ?
   → Voir le STRATUM_RELAY.md du repo — chaque document de gouvernance a un intent_hash unique.
9. Quels tests unitaires couvrent ECOYSTEM ?
   → tests/unit/ — les tests sont dans repomix-fork pour les adapters, scripts, et verse_detector.
10. Quelle est la dependance critique de ECOYSTEM ?
   → LLM-REPO (substrat cognitif) et GOVERNANCE-HUB (constitution) — tout repo depend de ces deux SOT.

## Dependances
- **Amont** : L0
- **Aval** : L2
- **SOT reference** : gerivdb/LLM-REPO (L1b)
- **Gouvernance** : gerivdb/GOVERNANCE-HUB (L0)

## Connectivite FIBRE
- **Niveau** : Vague 3 — Full Interconnect
- **Recall packs** : synchronises dans LLM-REPO/TRAINING/recall_packs/
- **Cadastre** : known_repositories_190.yaml (190 repos)
- **Score emergence** : calcule via FLUENCE/phi-CPS

## Vague de mise a jour
- Vague courante : 3 (FIBRE — recall 10Q + dependances + interconnect)
- Prochaine vague : 4 (extension cadastre 71+ repos)
- Timestamp : 2026-06-11
