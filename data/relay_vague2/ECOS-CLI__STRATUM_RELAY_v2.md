# STRATUM RELAY — ECOS-CLI (L3)

VAGUE: 2 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : L3 – Voiries — CLI executable
- **Role canonique** : Interface CLI ecosysteme, commandes automation
- **Parent** : L2
- **Enfants** : L4
- **Connectivite** : DSL (lien hub + regles locales)

## Navigation rapide
- PRD canonique : GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md
- Substrat central : gerivdb/LLM-REPO
- Regles strate : LLM-REPO/RULES/behavior_rules.md#L3

## Regles locales (structurees)
- [R1] : Toute commande ecos doit passer par le wrapper CMD (pas de & direct)
- [R2] : Le stash WIP de DevTools ne doit jamais etre pop sans verification
- [R3] : Verification d'acces filesystem avant chaque operation (allowedDirectories)
- [R4] : Les scripts cross-repo sont atomiques — 1 repo par operation
- [R5] : Le registre repos.json est SOT — pas de creation de repo sans verification GATE-1

## Karpathy-Recall local (5Q specifiques)
1. Quel est le role canonique d'ECOS-CLI ?
   → Interface CLI de l'ecosysteme — commandes automation et workflows EECS.
2. Quelle strate amont alimente ECOS-CLI ?
   → L2 (BRAIN, ECOYSTEM) pour la logique et les regles.
3. Quelle strate aval ECOS-CLI alimente-t-il ?
   → L4 (DevTools) — execution sur le hub central C:\DevTools.
4. Quelle est la regle R1 d'ECOS-CLI ?
   → Toute commande passe par le wrapper CMD — pas de & direct (harmonisation-v8).
5. Comment ECOS-CLI accede-t-il aux repos cross-repo ?
   → Via le serveur MCP filesystem avec allowedDirectories verifie (C:\DevTools, D:\DO\WEB).

## Vague de mise a jour
- Vague courante : 2 (DSL + regles locales + 5Q Karpathy)
- Prochaine vague : 3 (recall 10Q + dependances + FIBRE)
- Timestamp : 2026-06-11
