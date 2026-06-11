# STRATUM RELAY — repomix-fork (L3)

VAGUE: 2 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : L3 – Voiries — Bundler souverain
- **Role canonique** : Bundler repomix fork, scan + verses + marketplace
- **Parent** : L2
- **Enfants** : L4
- **Connectivite** : DSL (lien hub + regles locales)

## Navigation rapide
- PRD canonique : GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md
- Substrat central : gerivdb/LLM-REPO
- Regles strate : LLM-REPO/RULES/behavior_rules.md#L3

## Regles locales (structurees)
- [R1] : Les bundles XML incluent les metadonnées UrbanVerse (strate, phi_cps, intent_hash)
- [R2] : Le chunking est obligatoire pour les bundles > 80 Mo (50 repos/chunk)
- [R3] : known_repositories_190.yaml est la SOT — pas de scan GitHub API (GATE-2)
- [R4] : Les tests unitaires passent avant chaque commit (55 tests minimum)
- [R5] : Le cli_contract.py est stable — pas de modification sans ADR

## Karpathy-Recall local (5Q specifiques)
1. Quel est le role canonique de repomix-fork ?
   → Bundler souverain — mashup de codebase vers format LLM-optimise (XML/MD/texte).
2. Quelle strate amont alimente repomix-fork ?
   → L2 (BRAIN, ECOYSTEM) pour la logique et les metadonnees UrbanVerse.
3. Quelle strate aval repomix-fork alimente-t-il ?
   → L4 (ARGUS, CodeDB, LYCOS, FLUENCE) — bundles pour ingestion et analyse.
4. Quelle est la regle R1 de repomix-fork ?
   → Les bundles XML incluent les metadonnees UrbanVerse (strate, phi_cps, intent_hash).
5. Comment le chunking fonctionne-t-il ?
   → Bundles > 80 Mo sont decoupes en chunks de 50 repos (streaming XML, pas de chargement RAM complet).

## Vague de mise a jour
- Vague courante : 2 (DSL + regles locales + 5Q Karpathy)
- Prochaine vague : 3 (recall 10Q + dependances + FIBRE)
- Timestamp : 2026-06-11
