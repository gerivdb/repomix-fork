# EPIC-04 — Synchronisation Karpathy Recall × UrbanVerse

---

**EPIC** : EPIC-04
**Titre** : Karpathy Recall — Spirale d'apprentissage × Transit cognitif
**PRD parent** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`
**Version** : 2.0.0
**Date** : 2026-05-28
**Statut** : ✅ DÉPLOYÉ (Vague 14)
**Priorité** : P2 — Dépend EPIC-07, EPIC-10

---

## Objectif

Synchroniser la **logique Karpathy-Recall** (LLM-REPO/TRAINING/) avec la **métaphore urbaine** (UrbanVerse).
Chaque ligne de métro devient une spirale d'apprentissage ; chaque station = un recall pack.

## User Stories

| ID | Story | Critères d'acceptation | Statut |
|----|-------|----------------------|--------|
| US-04-1 | En tant qu'agent LLM, après avoir ingéré L0, je réponds à un recall avant de passer à L1b | `transit_map.yaml` référence le recall pack de chaque strate M1 | ✅ |
| US-04-2 | En tant que dev, la mise à jour d'un recall pack déclenche la mise à jour du relais correspondant | Procédure documentée dans `SYNC/recall_relay_sync.md` | ✅ |
| US-04-3 | En tant qu'agent LLM, je suis la Ligne M1 avec un recall à chaque station | 12 arrêts M1 avec `recall_pack` + 5Q/10Q par strate | ✅ |
| US-04-4 | En tant que mainteneur, je peux vérifier la cohérence recall ↔ relais | `recall_coherence_check.py` v4.0 opérationnel (--repomix/--transit/--relay-dir/--full) | ✅ |

## Tâches techniques

- [x] Enrichir `transit_map.yaml` : ajouter champ `recall_pack` à chaque arrêt Ligne M1
- [x] Créer `SYNC/recall_relay_sync.md` (procédure de synchronisation)
- [x] Créer `TOOLS/recall_coherence_check.py` v4.0
- [x] Enrichir les relais Vague 2+ (5Q/10Q Karpathy spécifiques par repo)
- [x] Lien bidirectionnel : LLM-REPO/TRAINING/ et UrbanVerse en référence croisée

## Définition de "Done"

- [x] `transit_map.yaml` inclut `recall_pack` pour chaque strate de M1
- [x] Script de cohérence passe sans erreur sur les 10 repos pilotes
- [x] LLM-REPO/TRAINING/ et UrbanVerse en référence croisée validée

---

*Mis à jour : 2026-06-11 — v2.0.0 : Toutes les US satisfaites, recall_coherence_check v4 opérationnel*
*IntentHash: 0xEPIC04_KARPATHY_RECALL_SYNC_20260528*
