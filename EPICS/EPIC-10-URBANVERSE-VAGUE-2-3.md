# EPIC-10 — UrbanVerse Vague 2+3 : Karpathy Recall & Connectivité Fibre

---

**EPIC** : EPIC-10
**Titre** : UrbanVerse Vague 2+3 — Recall packs enrichis + passage DSL → Fibre (5 repos critiques)
**PRD parent** : `PRD/PRD-010-urbanverse-vague-2-3.md`
**Version** : 1.0.0
**Date** : 2026-06-11
**Statut** : DEPLOYE (Vague 12)
**Priorité** : P1 — Dépend EPIC-07 (cadastre 190 repos)

---

## Objectif

Enrichir les 11 relais pilotes DSL (Vague 1) avec règles locales et micro-rappels
Karpathy (Vague 2), puis faire passer les 5 repos critiques L0+L1b+L3 en connectivité
FIBRE (Vague 3). Câbler les recall packs vers `LLM-REPO/TRAINING/`.

## User Stories

| ID | Story | Critères d'acceptation |
|----|-------|----------------------|
| US-10-1 | En tant qu'agent LLM lisant GOVERNANCE-HUB/STRATUM_RELAY.md, j'ai accès à 3 micro-rappels Karpathy spécifiques à ce repo | Section "Karpathy-Recall local" contient ≥ 3 questions + réponses contextualisées |
| US-10-2 | En tant que dev, le script `relay_propagator_v2.py` génère les Vague 2 pour 11 repos sans écraser Vague 1 | Mode `--vague 2 --dry-run` affiche le delta uniquement |
| US-10-3 | En tant que dev, les 5 repos FIBRE ont une section "Règles locales étendues" (≥ 5 règles) | GOVERNANCE-HUB, ECOYSTEM, NEXUS, LLM-REPO, repomix-fork → connectivité FIBRE |
| US-10-4 | En tant que dev, les recall packs sont synchronisés dans LLM-REPO/TRAINING/ | `LLM-REPO/TRAINING/recall_packs/` contient 11 fichiers `.yaml` versionés |
| US-10-5 | En tant que dev, le cadastre couvre ~71 repos actifs (vs 11 pilotes) | `cadastre_v2.yaml` — 71 entrées minimum validées |

## Tâches techniques

- [ ] `scripts/relay_propagator_v2.py` — mode `--vague 2`, enrichissement règles locales + Karpathy
- [ ] Générer Karpathy packs pour 11 repos pilotes (3 Q+A spécifiques chacun)
- [ ] `scripts/relay_propagator_v3.py` — mode `--vague 3`, connectivité FIBRE pour 5 repos
- [ ] `VERSES/urban_ontology_verse/CADASTRE/cadastre_v2.yaml` — 71 entrées
- [ ] Synchroniser recall packs → `LLM-REPO/TRAINING/recall_packs/` (11 fichiers)
- [ ] `tests/unit/test_relay_propagator_v2.py` — 6 tests (Vague 2 content, FIBRE flag, cadastre count)
- [ ] Mettre à jour `VERSES/urban_ontology_verse/relay_wave_manifest.yaml` → v6.x

## Définition de "Done"

- [ ] 11 relais Vague 2 générés et committés dans VERSES
- [ ] 5 relais Vague 3 (FIBRE) générés et committés dans VERSES
- [ ] 11 recall packs dans LLM-REPO/TRAINING/recall_packs/
- [ ] `cadastre_v2.yaml` ≥ 71 entrées validées
- [ ] 6 nouveaux tests passent
