# STRATUM RELAY — GOVERNANCE-HUB (L0)

VAGUE: 2 | Synchro: 2026-06-11 | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : L0 – Hotel de Ville — Constitution
- **Role canonique** : Constitution, cadastre, registres
- **Parent** : —
- **Enfants** : L1, L1b
- **Connectivite** : DSL (lien hub + regles locales)

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

## Karpathy-Recall local (5Q specifiques)
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

## Vague de mise a jour
- Vague courante : 2 (DSL + regles locales + 5Q Karpathy)
- Prochaine vague : 3 (recall 10Q + dependances + FIBRE)
- Timestamp : 2026-06-11
