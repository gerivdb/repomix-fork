# STRATUM RELAY — NEXUS (L1)

VAGUE: 2 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : L1 – Archives centrales — Aggregation data
- **Role canonique** : Aggregation cross-repo, NEXUS core
- **Parent** : L0
- **Enfants** : L2
- **Connectivite** : DSL (lien hub + regles locales)

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

## Karpathy-Recall local (5Q specifiques)
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

## Vague de mise a jour
- Vague courante : 2 (DSL + regles locales + 5Q Karpathy)
- Prochaine vague : 3 (recall 10Q + dependances + FIBRE)
- Timestamp : 2026-06-11
