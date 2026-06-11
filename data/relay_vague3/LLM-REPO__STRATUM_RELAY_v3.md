# STRATUM RELAY — LLM-REPO (L1b)

VAGUE: 3 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : L1b – Substrat cognitif LLM
- **Role canonique** : LLM_BOOT_PROTOCOL, GATE-0->4, regles comportement
- **Parent** : L0
- **Enfants** : L1
- **Connectivite** : FIBRE (Full Interconnect Bundle for Repository Emergence)

## Navigation rapide
- PRD canonique : GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md
- Substrat central : gerivdb/LLM-REPO
- Regles strate : LLM-REPO/RULES/behavior_rules.md#L1b

## Regles locales (structurees)
- [R1] : LLM_BOOT_PROTOCOL.md est le contrat d'entree force pour tout LLM
- [R2] : Les GATE-0->4 sont obligatoires — pas de contournement
- [R3] : Les fichiers de regles (RULES/) sont proteges — PR obligatoire
- [R4] : Les packs recall sont versionnes et synchronises avec VERSES
- [R5] : Le comportement par defaut est consultatif — jamais de decision autonome D4

## Karpathy-Recall local (10Q specifiques)
1. Quel est le role canonique de LLM-REPO ?
   → Hub cognitif LLM — LLM_BOOT_PROTOCOL, GATE-0->4, regles comportement agents.
2. Quelle strate amont alimente LLM-REPO ?
   → L0 (GOVERNANCE-HUB) pour les regles de gouvernance.
3. Quelle strate aval LLM-REPO alimente-t-il ?
   → L1 (SOT operationnel) — les regles comportement alimentent tous les agents.
4. Quelle est la regle R1 de LLM-REPO ?
   → LLM_BOOT_PROTOCOL.md est le contrat d'entree force pour tout LLM operant sur gerivdb.
5. Que sont les GATE-0->4 ?
   → Sequence de boot obligatoire : lire known_repositories.yaml, AGENT_RAM.yaml, BRIDGES.yaml, OrgansRegistry.yaml.
6. Quels sont les 3 fichiers les plus critiques de LLM-REPO ?
   → Depend du repo — voir STRATUM_RELAY.md et PRD associe pour les fichiers proteges.
7. Comment LLM-REPO interagit-il avec LLM-REPO ?
   → Via LLM_BOOT_PROTOCOL.md et les regles comportement (GATE-0->4) — tout agent LLM doit lire LLM-REPO avant operation.
8. Quel est l'intent_hash de LLM-REPO ?
   → Voir le STRATUM_RELAY.md du repo — chaque document de gouvernance a un intent_hash unique.
9. Quels tests unitaires couvrent LLM-REPO ?
   → tests/unit/ — les tests sont dans repomix-fork pour les adapters, scripts, et verse_detector.
10. Quelle est la dependance critique de LLM-REPO ?
   → LLM-REPO (substrat cognitif) et GOVERNANCE-HUB (constitution) — tout repo depend de ces deux SOT.

## Dependances
- **Amont** : L0
- **Aval** : L1
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
