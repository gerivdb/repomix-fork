# PyPI Publication — gerivdb-repomix v1.0.0

## Statut

- Build : OK (wheel 108 Ko + sdist 280 Ko)
- twine check : PASSED
- Upload : EN ATTENTE (token PyPI requis)

## Commande d'upload

```bash
# Option 1 : Token en variable d'environnement
$env:TWINE_PASSWORD = "pypi-xxxxxxxxxxxx"
twine upload dist/*

# Option 2 : Fichier .pypirc
# Creer %USERPROFILE%\.pypirc :
# [pypi]
#   username = __token__
#   password = pypi-xxxxxxxxxxxx

# Option 3 : Saisie interactive
twine upload dist/*
# -> Entrer le token quand demande
```

## Apres upload

```bash
# Verification
pip install gerivdb-repomix==1.0.0
python -c "import repomix; print(repomix.__version__)"
```
