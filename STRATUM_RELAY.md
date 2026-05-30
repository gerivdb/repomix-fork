# STRATUM RELAY — REPOMIX (L4-TOOLS)

**VAGUE**: 4 | **Synchro**: 2026-05-30 | **Hub**: gerivdb/LLM-REPO

---

## Identite stratique

- **Strate** : `L4` — Outils transverses
- **Role canonique** : Bundler souverain de codebase → format LLM-optimisé (XML/MD/texte). Fork de yamadashy/repomix v1.14.1 avec customisations UrbanVerse.
- **Parent** : L3 (ECOS-CLI)
- **Fork source** : yamadashy/repomix (upstream)

## Navigation rapide

- Substrat cognitif : `gerivdb/LLM-REPO` (L1b)
- UrbanVerse : `gerivdb/VERSUS` (L8 — cadastre + manifest)
- Outil compagnon : `gerivdb/VERSUS/urban_ontology_verse/TOOLS/recall_coherence_check.py` v3.0
- Config UrbanVerse : `repomix-verse.yaml`

## Regles locales

- R1 — REPOMIX est un outil de mashup — il ne contient pas de logique metier.
- R2 — Tout package Stratum Relay doit etre valide YAML avant push.
- R3 — REPOMIX ne depend pas de donnees externes — fonctionnement offline.
- R4 — Les customisations UrbanVerse (metadonnees strate/phi-CPS/intent_hash dans XML) sont preservees.
- R5 — Le mode `--ecosystem` produit des bundles multi-repo (76 repos → 1 XML).

## Dependances directes

**Parents (amont)** : L3 ECOS-CLI, L8 VERSUS
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

## Auto-conformite (Vague 4)

- Guard 1 : Aucune logique metier dans REPOMIX
- Guard 2 : Tout package Stratum Relay doit passer la validation YAML
- Guard 3 : REPOMIX doit fonctionner offline
- Guard 4 : Les metadonnees UrbanVerse sont injectees dans l'en-tete XML
- Guard 5 : Le mode `--ecosystem` reference `relay_wave_manifest.yaml`

## Apports ecosysteme (Intent)

| ID | Beneficiaire | Apport |
|----|-------------|--------|
| A1 | ARGUS | Bundle unique par repo → scan 7 pathologies sans dependance reseau |
| A2 | recall_coherence_check.py | Mode `--repomix` (exhaustivite) complement de `--opensrc` (vitesse) |
| A3 | CodeDB-E5620 / LYCOS | Corpus d'indexation en 1 commande → ingestion directe FLUENCE |
| A4 | LLM-REPO/TRAINING/ | Packs de recall auto-generes, reproductibles, versionnes |
| A5 | ECOS-CLI | Commande `ecos bundle <repo>` wrappant repomix |
| A6 | IRIS | Canal repomix en complement d'opensrc pour repos tiers upstream |
| A7 | GeriCode/KiloCode | Metadonnees UrbanVerse dans XML → contexte ecosysteme natif |
| A8 | ECOS-VISION | Bundle XML → parse structure → graphes dependances inter-repo |
| A9 | DATA-MINER | Mining sur bundle complet sans git clone de 76 repos |
| A10 | TOPOS/Riddler | Scan secrets/credentials sur fichier unique |

## Customisations fork (vs upstream yamadashy/repomix v1.14.1)

1. Metadonnees UrbanVerse en XML (strate, layer, phi_cps, intent_hash, vague_deployee)
2. Mode `--ecosystem` : bundle multi-repo (79 repos → 1 XML structure)
3. Integration register-repo.py : enregistrement automatique à la création
4. Output path par défaut : `D:\DO\WEB\TOOLS\L4-TOOLS\repomix\`
5. 10 apports ecosysteme (A1→A10) documentes ci-dessus

## Vague de mise a jour

| Vague | Contenu | Statut |
|-------|---------|--------|
| **4 (courante)** | Fork + metadonnees XML + mode ecosystem + agents + auto-conformite | Deploye |
| 5 (suivante) | Packaging npm/pypi, CI/CD pipeline, tests UrbanVerse | Planifie |

---

*Genere par OWL (Kilo) — UrbanVerse v5.0.0*
*IntentHash: 0xREPOMIX_INTENT_20260530*
*Fork: yamadashy/repomix v1.14.1*
*remotes: origin=gerivdb/repomix-fork, upstream=yamadashy/repomix*