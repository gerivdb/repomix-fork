# Procedure upstream sync — yamadashy/repomix

## Setup (une seule fois)

```bash
git remote add upstream https://github.com/yamadashy/repomix.git
git remote -v
# origin   https://github.com/gerivdb/repomix-fork.git
# upstream https://github.com/yamadashy/repomix.git
```

## Verifier l'etat actuel

```bash
git fetch upstream
git log --oneline upstream/main..HEAD   # commits locaux non upstream
git log --oneline HEAD..upstream/main   # commits upstream non integres
```

## Regles de merge UrbanVerse

Les fichiers suivants sont **PROTEGES** — jamais ecrases par upstream :
- `STRATUM_RELAY.md`
- `repomix-verse.yaml`
- `repomix.config.json`
- `src/repomix/` (tout le namespace UrbanVerse)
- `scripts/` (tous les scripts A1→A10)
- `PRD/`
- `.githooks/`
- `docs/`
- `data/`

## Procedure de merge

```bash
# Creer branche de merge
git checkout -b feature/upstream-sync-v1.14.1

# Merge upstream en ignorant les fichiers proteges
git merge upstream/main --no-commit --no-ff
git checkout HEAD -- STRATUM_RELAY.md repomix-verse.yaml repomix.config.json
git checkout HEAD -- src/repomix/ scripts/ PRD/ .githooks/ docs/ data/

# Resoudre conflits eventuels dans pyproject.toml / README
# ...

git commit -m "chore(upstream): sync yamadashy/repomix vX.X.X -> gerivdb/repomix-fork"
git push origin feature/upstream-sync-v1.14.1
# Puis PR -> main apres review
```

## Etat actuel (2026-06-11)

- **Fork base** : yamadashy/repomix v1.14.1
- **Upstream actuel** : yamadashy/repomix v1.9.2
- **Delta** : ~20+ commits upstream non integres (fixes ignore-gitignore, multi-root, deps)
- **Action** : Branche `feature/upstream-sync-v1.9.2` a creer pour merge des fixes upstream

## Verification post-merge

```bash
python scripts/validate_all.py   # Tous les guards doivent passer
python -m pytest tests/unit/     # 28+ tests passent
```
