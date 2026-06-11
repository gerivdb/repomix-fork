# STRATUM RELAY — REPOMIX (L4-TOOLS)

**VAGUE**: 19 | **Synchro**: 2026-06-11 | **Hub**: gerivdb/LLM-REPO

---

## Identite stratique

- **Strate** : `L4` — Outils transverses
- **Role canonique** : Bundler souverain de codebase → format LLM-optimise (XML/MD/texte). Fork de yamadashy/repomix v1.14.1 avec customisations UrbanVerse.
- **Parent** : L3 (ECOS-CLI)
- **Fork source** : yamadashy/repomix (upstream)

## Navigation rapide

- Substrat cognitif : `gerivdb/LLM-REPO` (L1b)
- UrbanVerse : `gerivdb/VERSES` (L3 — SOT migre depuis VERSUS 2026-06-09)
- Outil compagnon : `src/repomix/tools/recall_coherence_check.py` v3.1 (mode --repomix)
- Config bundler : `repomix.config.json`
- Config ecosysteme : `repomix-verse.yaml`

## Regles locales

- R1 — REPOMIX est un outil de mashup — il ne contient pas de logique metier.
- R2 — Tout package Stratum Relay doit etre valide YAML avant push.
- R3 — REPOMIX ne depend pas de donnees externes — fonctionnement offline.
- R4 — Les customisations UrbanVerse (metadonnees strate/phi-CPS/intent_hash dans XML) sont preservees.
- R5 — Le mode `--ecosystem` produit des bundles multi-repo (190 repos → chunks par tier P0/P1/P2/P3).

## Dependances directes

**Parents (amont)** : L3 ECOS-CLI, L3 VERSES
**Enfants (aval)** : Aucun (feuille L4)

## Agents locaux (Vague 4)

```yaml
# .roomodes — profil agent L4
agent: repomix-serializer
strate: L4
role: repo_mashup_serializer
rules: src/relay_pack_rules.md
hub_ref: gerivdb/ECOS-CLI
```

## Auto-conformite

- Guard 1 : Aucune logique metier dans REPOMIX
- Guard 2 : Tout package Stratum Relay doit passer la validation YAML
- Guard 3 : REPOMIX doit fonctionner offline
- Guard 4 : Les metadonnees UrbanVerse sont injectees dans l'en-tete XML
- Guard 5 : Le mode `--ecosystem` reference `relay_wave_manifest.yaml`

## Apports ecosysteme

| ID | Beneficiaire | Apport | Statut |
|----|-------------|--------|--------|
| A1 | ARGUS | Bundle unique par repo → scan 7 pathologies sans dependance reseau | Vague 5 |
| A2 | recall_coherence_check.py | Mode `--repomix` (exhaustivite) complement de `--opensrc` (vitesse) | Vague 5 |
| A3 | CodeDB-E5620 / LYCOS | Corpus d'indexation en 1 commande → ingestion directe FLUENCE | Vague 6 |
| A4 | LLM-REPO/TRAINING/ | Packs de recall auto-generes, reproductibles, versionnes | Vague 6 |
| A5 | ECOS-CLI | cli_contract.py v1.0.0 | Vague 11 |
| A6 | IRIS | Canal repomix en complement d'opensrc pour repos tiers upstream | Vague 7 |
| A7 | GeriCode/KiloCode | Metadonnees UrbanVerse dans XML → contexte ecosysteme natif | Vague 12 |
| A8 | ECOS-VISION | Bundle XML → parse structure → graphes dependances inter-repo | Vague 6 |
| A9 | DATA-MINER | mine_bundle v2 | Vague 12 |
| A10 | TOPOS/Riddler | Scan secrets/credentials sur fichier unique | Vague 6 |

## Customisations fork (vs upstream yamadashy/repomix v1.14.1)

1. Metadonnees UrbanVerse en XML (strate, layer, phi_cps, intent_hash, vague_deployee)
2. Mode `--ecosystem` : bundle multi-repo (190 repos → chunks 80 Mo/50 repos)
3. Integration register-repo.py : enregistrement automatique a la creation
4. Output path par defaut : `D:\DO\WEB\TOOLS\L4-TOOLS\repomix\`
5. 10 apports ecosysteme (A1→A10) documentes ci-dessus
6. CI/CD local (pre-push hook Python, validate_all.py)
7. Tests unitaires (92 tests, adapters + sync + marketplace + recall + ecosystem + cli_contract)

## Vague de mise a jour

| Vague | Contenu | Statut |
|-------|---------|--------|
| 4 | Fork + metadonnees XML + mode ecosystem + agents + auto-conformite | Deploye |
| 5 | CI/CD local + tests UrbanVerse + A1 ARGUS + A2 recall | Deploye |
| 6 | A3→A10 cables, docs ECOS-CLI, scan secrets, STRATUM_RELAY v6 | Deploye |
| 7 | Packaging pypi, upstream sync yamadashy/repomix, score emergence > 72% (BORN) | Deploye |
| 8 | PRD-002 P3+P4 : VersesSyncManager + Marketplace API | Deploye |
| 9 | PRD-003 P1+P2 : UrbanVerse structure + 10 pilotes + upstream sync | Deploye |
| 10 | PRD-003 P3+P4 : Karpathy Recall packs + Fibre/Economie | Deploye |
| 11 | PRD-007+008 : Ecosystem 190 repos + cli_contract A5 + bundle_corpus v2 | Deploye |
| 12 | PRD-009+010 : mine_bundle v2 + A7 tests + relay Vague 2+3 + cadastre 190 | Deploye |
| 13 | PRD-011 : Marketplace sync bidirectionnelle + publication PyPI + CHANGELOG v1.0.0 | Deploye |
| 14 | EPIC-04 : Karpathy Recall v4 + transit_map v2 (12 arrets M1) + recall_coherence_check v4 | Deploye |
| 19 | Publication PyPI v1.0.0 (build + twine check PASSED), ADR-042 accepted, LLM-BOOT GATE-4b, cycle complet Vagues 1→19 | Déployé |

---

*Genere par OWL (Kilo) — UrbanVerse v5.0.0*
*IntentHash: 0xREPOMIX_INTENT_20260530*
*Fork: yamadashy/repomix v1.14.1*
*remotes: origin=gerivdb/repomix-fork, upstream=yamadashy/repomix*
