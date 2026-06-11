---
name: conv-mining-extractor
version: 1.0.0
description: Extrait automatiquement des skills, patterns, pipelines, frameworks et artefacts citoyennables depuis l'historique d'une conversation. Génère des candidats avec score de valeur et IntentHash.
triggers:
  - "extraire skills depuis conversation"
  - "mining de session"
  - "session closeout"
  - "extraction de valeur conversation"
  - "conv-mining"
layer: L4
strate: L4-TOOLS
intent_hash: 0xCONV_MINING_EXTRACTOR_20260611
---

# conv-mining-extractor

## Objectif

Analyser l'historique d'une conversation (JSON/MD) et extraire automatiquement :
- **Skills** candidats (patterns d'interaction réutilisables)
- **Pipelines** détectables (séquences d'actions automatisables)
- **Frameworks** émergents (patterns structurels réutilisables)
- **Citoyens CTULU** (outils actionnables)

## Entrée

```json
{
  "conversation": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "metadata": {
    "session_id": "DEV_COMET_20260611",
    "env": "ENV1",
    "strate": "L4"
  }
}
```

## Sortie

```yaml
# candidates/YYYY-MM-DD-skills.yaml
candidates:
  - name: conv-mining-extractor
    type: skill
    score: 0.95
    strate: L4
    intent_hash: 0xCONV_MINING_EXTRACTOR_20260611
    triggers: [...]
    description: "..."
  - name: boot-sequence-validator
    type: skill
    score: 0.88
    strate: L1b
    intent_hash: 0xBOOT_SEQ_VAL_20260611
    triggers: [...]
    description: "..."
```

## Algorithme

1. **Parse** : tokenizer la conversation en tours (user→assistant)
2. **Detect** : identifier les verbes d'action (créer, extraire, vérifier, transformer)
3. **Classer** : chaque pattern détecté → type (skill/pipeline/framework/citizen)
4. **Scorer** : fréquence × spécificité × réutilisabilité = score [0,1]
5. **Générer** : fichier YAML candidat avec IntentHash et strate
6. **Diff** : comparer avec skills existants → seuls les nouveaux sont proposés

## Utilisation

```bash
# Depuis une conversation exportée
python scripts/conv_mining.py --input session.json --output candidates/

# Depuis le clipboard (session courante)
python scripts/conv_mining.py --clipboard --output candidates/

# Mode interactif
python scripts/conv_mining.py --interactive
```

## Déclencheurs automatiques

- `session-closeout` : à chaque fin de session, lancer automatiquement
- `git pre-commit` : si `candidates/` a des nouveaux fichiers → warning
- `weekly-review` : agréger les candidats de la semaine

## Métriques

| Métrique | Cible |
|----------|-------|
| Précision détection | > 80% |
| Faux positifs | < 15% |
| Temps d'exécution | < 30s par session |
