---
name: vibe-amplifier
version: 1.0.0
description: Densifie sémantiquement un prompt ou texte — supprime les parasites, renforce l'intent, aligne sur le registre de l'écosystème. Transforme un prompt brut en prompt optimisé.
triggers:
  - "améliore cette vibe"
  - "densifie ce prompt"
  - "reformule pour l'écosystème"
  - "vibe-amplifier"
  - "clarifie ce message"
layer: L4
strate: L4-TOOLS
intent_hash: 0xVIBE_AMPLIFIER_20260611
---

# vibe-amplifier

## Objectif

Prendre un prompt/texte brut et retourner une version "densifiée" :
- Suppression des mots parasites (euh, bon, donc, etc.)
- Renforcement de l'intention principale
- Alignement sur le registre de l'écosystème (UrbanVerse, strates L0→L9)
- Clarification des objectifs multiples

## Entrée

```
Texte brut (prompt, message, description)
```

## Sortie

```
Texte densifié avec :
- Intent principal clarifié
- Registre écosystème aligné
- Objectifs hiérarchisés
- Métriques de qualité (score de densité)
```

## Règles de transformation

1. **Suppression parasites** : "euh", "bon", "donc", "en fait", "du coup"
2. **Renforcement intent** : verbes d'action forts (créer, implémenter, vérifier)
3. **Alignement registre** : termes UrbanVerse (strate, tier, strate, IntentHash)
4. **Hiérarchisation** : objectifs primaires → secondaires → optionnels

## Utilisation

```bash
# Mode texte
python scripts/vibe_amplifier.py --text "améliore cette vibe"

# Mode fichier
python scripts/vibe_amplifier.py --input prompt.txt --output prompt_v2.txt

# Mode interactif
python scripts/vibe_amplifier.py --interactive
```

## Métriques

| Métrique | Cible |
|----------|-------|
| Réduction parasites | > 90% |
| Score de densité | > 0.7 |
| Temps d'exécution | < 5s |
