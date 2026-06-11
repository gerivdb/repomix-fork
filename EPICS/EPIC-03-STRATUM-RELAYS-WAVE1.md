# EPIC-03 — Stratum Relays Vague 1 (10 repos pilotes)

---

**EPIC** : EPIC-03
**Titre** : Stratum Relays — Vague 1 (10 repos pilotes)
**PRD parent** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`
**Version** : 2.0.0
**Date** : 2026-05-28
**Statut** : ✅ DÉPLOYÉ (Vague 9 → consolidé Vague 15)
**Priorité** : P1 — Dépend EPIC-01, LLM-REPO

---

## Objectif

Déployer les **Stratum Relays Vague 1** dans les 10 repos pilotes + VERSUS.
Chaque relay déclare l'identité stratique, la navigation, les règles locales.

## User Stories

| ID | Story | Critères d'acceptation | Statut |
|----|-------|----------------------|--------|
| US-03-1 | En tant qu'agent LLM, en entrant dans BRAIN, je lis son identité stratique | `STRATUM_RELAY.md` présent avec strate, rôle, parent, enfants | ✅ |
| US-03-2 | En tant que dev, je peux propager les relays en batch | `relay_propagator.py` v3.0 avec `--vague 1/2/3` | ✅ |
| US-03-3 | En tant qu'agent LLM, les 10 pilotes ont des relays Vague 2+ | Karpathy-Recall 5Q+ dans les 10 pilotes | ✅ |
| US-03-4 | En tant que mainteneur, je connais l'état de déploiement | `relay_wave_manifest.yaml` v6.0 à jour | ✅ |

## Tâches techniques

- [x] Créer `STRATUM_RELAY.md` pour les 10 repos pilotes + VERSUS
- [x] Créer `relay_propagator.py` v3.0 (Vague 1+2+3, fibre-only)
- [x] Créer `relay_wave_manifest.yaml` v6.0 (190 repos)
- [x] Enrichir les relays Vague 2 (5Q Karpathy + règles locales)

## Définition de "Done"

- [x] 10 pilotes avec STRATUM_RELAY.md Vague 2+
- [x] relay_propagator.py v3.0 opérationnel
- [x] relay_wave_manifest.yaml v6.0 à jour

---

*Mis à jour : 2026-06-11 — v2.0.0 : Toutes les US satisfaites*
*IntentHash: 0xEPIC03_STRATUM_RELAYS_WAVE1_20260528*
