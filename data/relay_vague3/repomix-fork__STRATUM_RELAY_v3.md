# STRATUM RELAY — repomix-fork (L3)

VAGUE: 3 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : L3 – Voiries — Bundler souverain
- **Role canonique** : Bundler repomix fork, scan + verses + marketplace
- **Parent** : L2
- **Enfants** : L4
- **Connectivite** : FIBRE (Full Interconnect Bundle for Repository Emergence)

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

## Karpathy-Recall local (10Q specifiques)
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
6. Quels sont les 3 fichiers les plus critiques de repomix-fork ?
   → Depend du repo — voir STRATUM_RELAY.md et PRD associe pour les fichiers proteges.
7. Comment repomix-fork interagit-il avec LLM-REPO ?
   → Via LLM_BOOT_PROTOCOL.md et les regles comportement (GATE-0->4) — tout agent LLM doit lire repomix-fork avant operation.
8. Quel est l'intent_hash de repomix-fork ?
   → Voir le STRATUM_RELAY.md du repo — chaque document de gouvernance a un intent_hash unique.
9. Quels tests unitaires couvrent repomix-fork ?
   → tests/unit/ — les tests sont dans repomix-fork pour les adapters, scripts, et verse_detector.
10. Quelle est la dependance critique de repomix-fork ?
   → LLM-REPO (substrat cognitif) et GOVERNANCE-HUB (constitution) — tout repo depend de ces deux SOT.

## Dependances
- **Amont** : L2
- **Aval** : L4
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
