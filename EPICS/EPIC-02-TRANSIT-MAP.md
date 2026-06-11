# EPIC-02 — Réseau de Transit Cognitif

---

**EPIC** : EPIC-02
**Titre** : Réseau de Transit Cognitif — Lignes, Arrêts, Cartes
**PRD parent** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`
**Version** : 2.0.0
**Date** : 2026-05-28
**Statut** : ✅ DÉPLOYÉ (Vague 9 → consolidé Vague 15)
**Priorité** : P1 — Dépend EPIC-01

---

## Objectif

Modéliser le **réseau de transport cognitif** d'UrbanVerse : lignes de métro, RER, tram, bus.
Chaque ligne = un chemin de transit cognitif entre strates.
Chaque arrêt = une strate avec son pack Karpathy-Recall.

## User Stories

| ID | Story | Critères d'acceptation | Statut |
|----|-------|----------------------|--------|
| US-02-1 | En tant que dev, je peux visualiser le réseau de transit complet | `transit_map.yaml` avec M1, RER-A, RER-B, T1, T2, BUS-72, BUS-91, N1 | ✅ |
| US-02-2 | En tant qu'agent LLM, je peux naviguer de L0 à L9 via la Ligne M1 | 12 arrêts M1 avec `recall_pack` par strate | ✅ |
| US-02-3 | En tant que dev, je peux générer un diagramme Mermaid du réseau | `transit_map.mermaid.md` généré | ✅ |
| US-02-4 | En tant qu'agent LLM, je sais quel tram/bus utiliser pour un batch de repos | `tram_lines.yaml` + `bus_routes.yaml` documentés | ✅ |

## Tâches techniques

- [x] Créer `TRANSIT/transit_map.yaml` (12 arrêts M1 + RER + Tram + Bus)
- [x] Créer `TRANSIT/transit_map.mermaid.md` (diagramme)
- [x] Créer `TRANSIT/tram_lines.yaml` (T1 infrastructure, T2 IA)
- [x] Créer `TRANSIT/bus_routes.yaml` (BUS-72 APIs, BUS-91 CLI)
- [x] Référencer dans `boot_sequence.md` (LLM-REPO)

## Définition de "Done"

- [x] Fichiers créés et validés
- [x] Diagramme Mermaid généré
- [x] Référence dans boot_sequence.md

---

*Mis à jour : 2026-06-11 — v2.0.0 : Toutes les US satisfaites*
*IntentHash: 0xEPIC02_TRANSIT_MAP_20260528*
