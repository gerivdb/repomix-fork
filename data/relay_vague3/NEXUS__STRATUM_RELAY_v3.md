# STRATUM RELAY — NEXUS (L1)

VAGUE: 3 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : L1 – Archives centrales — Aggregation data
- **Role canonique** : Aggregation cross-repo, NEXUS core
- **Parent** : L0
- **Enfants** : L2
- **Connectivite** : FIBRE (Full Interconnect Bundle for Repository Emergence)

## Navigation rapide
- PRD canonique : GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md
- Substrat central : gerivdb/LLM-REPO
- Regles strate : LLM-REPO/RULES/behavior_rules.md#L1

## Regles locales (structurees)
- [R1] : Aggregation cross-repo uniquement — pas de logique metier locale
- [R2] : Les registres sont immuables — historique preserve en lecture seule
- [R3] : Verification d'integrite avant chaque aggregation (hash check)
- [R4] : Les acces sont controles — pas de lecture sans authentification
- [R5] : Le schema de donnees est versionne — migration ADR obligatoire

## Karpathy-Recall local (10Q specifiques)
1. Quel est le role canonique de NEXUS ?
   → Aggregation cross-repo — registre des registres, mega-SOT.
2. Quelle strate amont alimente NEXUS ?
   → L0 (GOVERNANCE-HUB) pour les regles, L1 pour les donnees operationnelles.
3. Quelle strate aval NEXUS alimente-t-il ?
   → L2 (composition) — donnees agregees pour BRAIN, FLUENCE, ECOYSTEM.
4. Quelle est la regle R1 de NEXUS ?
   → Aggregation uniquement — pas de logique metier locale.
5. Comment NEXUS garantit-il l'integrite des registres ?
   → Hash check avant chaque aggregation, historique immuable, acces controles.
6. Quels sont les 3 fichiers les plus critiques de NEXUS ?
   → Depend du repo — voir STRATUM_RELAY.md et PRD associe pour les fichiers proteges.
7. Comment NEXUS interagit-il avec LLM-REPO ?
   → Via LLM_BOOT_PROTOCOL.md et les regles comportement (GATE-0->4) — tout agent LLM doit lire NEXUS avant operation.
8. Quel est l'intent_hash de NEXUS ?
   → Voir le STRATUM_RELAY.md du repo — chaque document de gouvernance a un intent_hash unique.
9. Quels tests unitaires couvrent NEXUS ?
   → tests/unit/ — les tests sont dans repomix-fork pour les adapters, scripts, et verse_detector.
10. Quelle est la dependance critique de NEXUS ?
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
