# Architecture repomix-fork

## Structure

```
src/repomix/
  __init__.py
  engines/          # neuro-symbolic, spiral, physic, etc.
  marketplace/      # phase 4 marketplace
  migrations/       # data migrations

tests/              # pytest test suite
data/               # static data, ontology, verses
docs/               # documentation
scripts/            # bash/ps1 operational scripts
```

## Conventions

- Python ≥ 3.11
- Tests : `pytest tests/ -m "not slow and not e2e"`
- Coverage minimum : 70%
- Linting : `ruff check src/ tests/`

## CI/CD

- CI déclenché sur chaque PR → `main`
- Release sur tag `v*.*.*` → PyPI
