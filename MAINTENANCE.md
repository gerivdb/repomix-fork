# MAINTENANCE.md — gerivdb-repomix

## Procédures de maintenance

### 1. Upstream Sync

```bash
# Recuperer les derniers changements upstream
git fetch upstream

# Voir les changements
git log --oneline HEAD..upstream/main

# Merge (si applicable)
git merge upstream/main --no-ff -m "chore(upstream): sync yamadashy/repomix v1.x"

# Resoudre les conflits (si necessaire)
git mergetool
```

### 2. Tests

```bash
# Suite complete
pytest tests/unit/ -v

# Verification rapide
pytest tests/unit/ -q
# Attendu: 92 passed
```

### 3. Build PyPI

```bash
# Nettoyer l'ancien build
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue

# Build
python -m build

# Verification
twine check dist/*

# Upload (token requis)
$env:TWINE_PASSWORD = "pypi-xxxxxxxxxxxx"
twine upload dist/*
```

### 4. Release

```bash
# Tag
git tag v1.0.X
git push origin main --tags
```

## Fichiers de reference

| Fichier | Usage |
|---------|-------|
| `pyproject.toml` | Configuration build + dependencies |
| `STRATUM_RELAY.md` | Identite stratique L4 |
| `EPICS/INDEX.md` | 11 EPICs deployes |
| `PRD/PRD-000-index.md` | 9 PRDs accepted |
| `docs/CYCLE_BILAN.md` | Bilan complet Vagues 1->21 |
| `docs/PYPI_PUBLISH.md` | Instructions publication PyPI |

## Contacts

- **Upstream** : yamadashy/repomix (GitHub)
- **Hub** : gerivdb/LLM-REPO (GATE-0->4b)
- **Gouvernance** : gerivdb/GOVERNANCE-HUB (ADR-042 accepted)

---

*IntentHash: 0xREPOMIX_INTENT_20260530*
*V1.0.2 — Maintenance mode actif*
