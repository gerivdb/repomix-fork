# EPIC-05 — Économie Urbaine & Gouvernance Étendue

---

**EPIC** : EPIC-05
**Titre** : Économie Interne, Acteurs Urbains, Périphérique et Région IDF
**PRD parent** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`
**Version** : 1.0.0
**Date** : 2026-05-28
**Statut** : ✅ DÉPLOYÉ (Vague 15)
**Priorité** : P3
**Prérequis** : ADR validée dans GOVERNANCE-HUB avant tout déploiement monnaie Geri

---

## Objectif

Modéliser les **acteurs urbains** (salariés-scripts, managers-agents, contrôleurs),
le **périphérique** (API Gateway, échangeurs), et la **région IDF** (zones de confiance 1–4).
La monnaie Geri (Ğ) est documentée mais **non déployée** sans ADR.

## User Stories

| ID | Story | Critères d'acceptation | Statut |
|----|-------|----------------------|--------|
| US-05-1 | En tant que dev, je comprends les zones de confiance 1–4 pour intégrer un repo externe | `zonage_idf.yaml` documenté et complet | ✅ |
| US-05-2 | En tant qu'agent LLM, je sais identifier un échangeur de périphérique | `peripherique.yaml` liste les repos passerelles | ✅ |
| US-05-3 | En tant que mainteneur, je dispose d'un modèle d'acteurs urbains typés | `actors_registry.yaml` avec 5+ types d'acteurs | ✅ |
| US-05-4 | En tant qu'architecte, la monnaie Geri est documentée avec ses risques | `ECONOMY/geri_currency_ADR_draft.md` rédigé | ✅ |

## Tâches techniques

- [x] Créer `urban_ontology_verse/ECONOMY/zonage_idf.yaml`
- [x] Créer `urban_ontology_verse/ECONOMY/peripherique.yaml`
- [x] Créer `urban_ontology_verse/ECONOMY/actors_registry.yaml`
- [x] Créer `urban_ontology_verse/ECONOMY/rungis_components.yaml`
- [x] Rédiger `urban_ontology_verse/ECONOMY/geri_currency_ADR_draft.md` (brouillon ADR — NE PAS DÉPLOYER)

## ⚠️ Règle absolue

> **La monnaie Geri (Ğ) et le système de crédit ne peuvent être implémentés**
> **qu'après validation d'une ADR dans `GOVERNANCE-HUB/ADR/`.**
> Toute implémentation sans ADR = anti-pattern constitutionnel (L0 violation).

## Définition de "Done"

- [x] 5 fichiers YAML créés et validés
- [x] `geri_currency_ADR_draft.md` rédigé mais **non mergé dans implémentation**
- [ ] ADR soumise à review humaine dans GOVERNANCE-HUB (brouillon prêt)

## Fichiers livrés

```
urban_ontology_verse/ECONOMY/
├── zonage_idf.yaml              — Zones de confiance 1–4 + périphérique
├── peripherique.yaml            — Portes d'entrée, échangeurs, règles
├── actors_registry.yaml         — 6 types d'acteurs urbains
├── rungis_components.yaml       — Composants réutilisables (marché de Rungis)
└── geri_currency_ADR_draft.md   — Brouillon ADR monnaie Geri (non déployé)
```
