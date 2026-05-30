# REPOMIX — UrbanVerse Fork

Bundler souverain de codebase → format LLM-optimisé (XML/MD/texte).

**Fork de** [yamadashy/repomix](https://github.com/yamadashy/repomix) v1.14.1

## Installation

```bash
# Via npm (upstream)
npx repomix@latest

# Via ce fork (customisations UrbanVerse)
# Clone + install
git clone https://github.com/gerivdb/repomix-fork.git
cd repomix-fork
npm install
npm run build
```

## Customisations UrbanVerse

### 1. Métadonnées UrbanVerse en XML
L'en-tête XML de chaque bundle inclut :
- `strate`, `layer`, `phi_cps`, `intent_hash`, `vague_deployee`

### 2. Mode `--ecosystem`
Bundle multi-repo (79 repos → 1 XML structuré).
Config : `repomix-verse.yaml`

### 3. Intégration register-repo.py
Enregistrement automatique dans les registres UrbanVerse :
```bash
python scripts/register-repo.py \
  --name mon-repo \
  --layer L3 \
  --path "D:\DO\WEB\mon-repo" \
  --role "Description du role"
```

## Apports écosystème

| ID | Bénéficiaire | Apport |
|----|-------------|--------|
| A1 | ARGUS | Bundle unique → scan 7 pathologies sans dépendance réseau |
| A2 | recall_coherence_check.py | Mode `--repomix` (exhaustivité) complement de `--opensrc` (vitesse) |
| A3 | CodeDB-E5620 / LYCOS | Corpus d'indexation → ingestion directe FLUENCE |
| A4 | LLM-REPO/TRAINING/ | Packs de recall auto-générés, reproductibles, versionnés |
| A5 | ECOS-CLI | Commande `ecos bundle <repo>` wrappant repomix |
| A6 | IRIS | Canal repomix pour repos tiers upstream |
| A7 | GeriCode/KiloCode | Métadonnées UrbanVerse dans XML → contexte écosystème natif |
| A8 | ECOS-VISION | Bundle XML → graphes dépendances inter-repo |
| A9 | DATA-MINER | Mining sur bundle complet sans git clone |
| A10 | TOPOS/Riddler | Scan secrets/credentials sur fichier unique |

## Fichiers

- `STRATUM_RELAY.md` — Identitéstrate L4, Vague 4
- `repomix-verse.yaml` — Configuration UrbanVerse
- `scripts/register-repo.py` — Script d'enregistrement

## Licence

MIT (hérité de yamadashy/repomix)

---

*UrbanVerse v5.0.0 — IntentHash: 0xREPOMIX_INTENT_20260530*