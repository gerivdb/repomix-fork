# EPIC-08 — ECOS-CLI A5 : Commande `ecos bundle`

---

**EPIC** : EPIC-08
**Titre** : Implémentation de la commande `ecos bundle` dans ECOS-CLI (Apport A5)
**PRD parent** : `PRD/PRD-008-ecos-cli-a5.md`
**Version** : 1.0.0
**Date** : 2026-06-11
**Statut** : 🟡 À DÉMARRER
**Priorité** : P1 — Dépend EPIC-07

---

## Objectif

Réaliser côté `gerivdb/ECOS-CLI` la commande `ecos bundle <repo>` spécifiée dans
`docs/ecos-cli-interface.md`. Le contrat d'interface est défini ici (repomix-fork)
via `src/repomix/cli_contract.py` — ECOS-CLI le consomme via subprocess ou import direct.

## User Stories

| ID | Story | Critères d'acceptation |
|----|-------|----------------------|
| US-08-1 | En tant que dev, je tape `ecos bundle GOVERNANCE-HUB` et obtiens un bundle XML | Bundle créé dans le répertoire de sortie configuré |
| US-08-2 | En tant que dev, `ecos bundle --tier P0` bundle tous les repos critiques en une commande | Identique à `repomix --ecosystem --tier P0` mais via l'interface ECOS |
| US-08-3 | En tant qu'agent LLM, le contrat d'interface est lisible dans ce repo (repomix-fork) | `src/repomix/cli_contract.py` documenté et versionné |
| US-08-4 | En tant que dev, l'ADR validant le contrat est accessible dans GOVERNANCE-HUB | ADR-XXX accepté dans GOVERNANCE-HUB/ADR/ |

## Tâches techniques

**Dans `gerivdb/repomix-fork` (contrat côté bundler) :**
- [ ] Créer `src/repomix/cli_contract.py` — expose `bundle_repo(repo, tier, output_format)` API publique
- [ ] Documenter `docs/ecos-cli-interface.md` v2 — contrat stabilisé avec types + exemples
- [ ] `tests/unit/test_cli_contract.py` — 4 tests (signature, types de retour, erreurs)

**Dans `gerivdb/ECOS-CLI` (implémentation — hors scope repomix-fork) :**
- [ ] Commande `ecos bundle <repo> [--tier] [--output xml|md]` via subprocess gerivdb-repomix
- [ ] Tests d'intégration cross-repo

**Dans `gerivdb/GOVERNANCE-HUB` (ADR) :**
- [ ] ADR `adr-repomix-ecos-cli-contract` — format MADR + IntentHash

## Définition de "Done"

- [ ] `cli_contract.py` créé et testé (4 tests passent)
- [ ] `docs/ecos-cli-interface.md` v2 publiée
- [ ] ADR dans GOVERNANCE-HUB à l'état `proposed` minimum
- [ ] Note dans PRD-008 : "impl côté ECOS-CLI = Vague suivante"
