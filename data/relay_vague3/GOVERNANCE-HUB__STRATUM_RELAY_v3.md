# STRATUM RELAY — GOVERNANCE-HUB (L0)

VAGUE: 3 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : L0 – Hotel de Ville — Constitution
- **Role canonique** : Constitution, cadastre, registres
- **Parent** : —
- **Enfants** : L1, L1b
- **Connectivite** : FIBRE (Full Interconnect Bundle for Repository Emergence)

## Navigation rapide
- PRD canonique : GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md
- Substrat central : gerivdb/LLM-REPO
- Regles strate : LLM-REPO/RULES/behavior_rules.md#L0

## Regles locales (structurees)
- [R1] : Fichiers proteges : ADR/, STRATUM_RELAY.md, known_repositories.yaml — jamais ecrases par merge upstream
- [R2] : Push direct sur main interdit — PR obligatoire avec review
- [R3] : Offline-first : toutes les regles doivent fonctionner sans acces reseau
- [R4] : Intent Hash obligatoire sur chaque document de gouvernance
- [R5] : Frontmatter YAML valide avant commit (hook pre-commit)

## Karpathy-Recall local (10Q specifiques)
1. Quel est le role canonique de GOVERNANCE-HUB ?
   → Constitution de l'ecosysteme — SOT des regles de gouvernance executables, ADR, registres, et documents de reference.
2. Quelle strate amont alimente GOVERNANCE-HUB ?
   → Aucune — L0 est la strate racine. GOVERNANCE-HUB est la constitution.
3. Quelle strate aval GOVERNANCE-HUB alimente-t-il ?
   → L1 (SOT operationnel) et L1b (substrat cognitif LLM) via les regles et registres.
4. Quelle est la regle R1 de GOVERNANCE-HUB ?
   → Fichiers proteges : ADR/, STRATUM_RELAY.md, known_repositories.yaml ne sont jamais ecrases par merge upstream.
5. Comment verifier l'integrite du cadastre ?
   → Lire known_repositories.yaml (GATE-0), verifier les intent_hash, et valider le frontmatter YAML (hook pre-commit).
6. Quels sont les 3 fichiers les plus critiques de GOVERNANCE-HUB ?
   → Depend du repo — voir STRATUM_RELAY.md et PRD associe pour les fichiers proteges.
7. Comment GOVERNANCE-HUB interagit-il avec LLM-REPO ?
   → Via LLM_BOOT_PROTOCOL.md et les regles comportement (GATE-0->4) — tout agent LLM doit lire GOVERNANCE-HUB avant operation.
8. Quel est l'intent_hash de GOVERNANCE-HUB ?
   → Voir le STRATUM_RELAY.md du repo — chaque document de gouvernance a un intent_hash unique.
9. Quels tests unitaires couvrent GOVERNANCE-HUB ?
   → tests/unit/ — les tests sont dans repomix-fork pour les adapters, scripts, et verse_detector.
10. Quelle est la dependance critique de GOVERNANCE-HUB ?
   → LLM-REPO (substrat cognitif) et GOVERNANCE-HUB (constitution) — tout repo depend de ces deux SOT.

## Dependances
- **Amont** : —
- **Aval** : L1, L1b
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
