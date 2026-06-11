# EPIC-01 — Fondations Urbaines UrbanVerse

---

**EPIC** : EPIC-01
**Titre** : Fondations Urbaines — Structure, Ontologie, Cadastre
**PRD parent** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`
**Version** : 2.0.0
**Date** : 2026-05-28
**Statut** : ✅ DÉPLOYÉ (Vague 9 → consolidé Vague 15)
**Priorité** : P0

---

## Objectif

Créer la **structure physique** d'UrbanVerse :
l'arborescence du verse, le cadastre ontologique, le registre des verses mis à jour.

## User Stories

| ID | Story | Critères d'acceptation | Statut |
|----|-------|----------------------|--------|
| US-01-1 | En tant qu'agent LLM, je peux trouver l'ontologie urbaine dans `urban_ontology_verse/` | Dossier existe avec README.md | ✅ |
| US-01-2 | En tant que dev, je peux identifier la strate de tout repo via le cadastre | `cadastre_v2.yaml` (171 parcelles) + `known_repositories_190.yaml` | ✅ |
| US-01-3 | En tant qu'agent LLM, je sais qu'UrbanVerse est un verse déclaratif distinct de BATVERSE | `ontology_registry.json` mis à jour dans VERSES | ✅ |
| US-01-4 | En tant que dev, je dispose d'un template de Stratum Relay | `TEMPLATES/STRATUM_RELAY_TEMPLATE.md` créé et versionné | ✅ |

## Tâches techniques

- [x] Créer `urban_ontology_verse/README.md`
- [x] Créer `urban_ontology_verse/CADASTRE/cadastre_v2.yaml` (171 parcelles actives)
- [x] Créer `urban_ontology_verse/TEMPLATES/STRATUM_RELAY_TEMPLATE.md`
- [x] Mettre à jour `ontology_registry.json` — entrée `urban_ontology_verse`
- [x] Créer `EPICS/INDEX.md` avec liste des EPICs

## Structure livrée

```
urban_ontology_verse/
├── README.md
├── CADASTRE/
│   ├── cadastre_v2.yaml          (171 parcelles actives)
│   └── cadastre_v2.json          (190 parcelles, source de vérité)
├── TRANSIT/
│   ├── transit_map.yaml          (12 arrêts M1 + RER + Tram + Bus)
│   ├── transit_map.mermaid.md
│   ├── tram_lines.yaml
│   └── bus_routes.yaml
├── RELAYS/
│   └── relay_wave_manifest.yaml  (v6.0, 190 repos)
├── TEMPLATES/
│   └── STRATUM_RELAY_TEMPLATE.md
├── ECONOMY/
│   ├── zonage_idf.yaml
│   ├── peripherique.yaml
│   ├── actors_registry.yaml
│   ├── rungis_components.yaml
│   └── geri_currency_ADR_draft.md
└── TOOLS/
    ├── relay_propagator.py       (v3, Vague 1+2+3)
    └── recall_coherence_check.py (v4, modes bundle/transit/relay/full)
```

## Définition de "Done"

- [x] Arborescence créée et committée
- [x] `cadastre_v2.yaml` avec ≥171 entrées validées
- [x] `ontology_registry.json` mis à jour
- [x] Aucun conflit avec `BATVERSE` ni avec `LLM-REPO`

---

*Mis à jour : 2026-06-11 — v2.0.0 : Toutes les US satisfaites, structure complète*
*IntentHash: 0xEPIC01_URBAN_FOUNDATIONS_20260528*
