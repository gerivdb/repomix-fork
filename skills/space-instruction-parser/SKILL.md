---
name: space-instruction-parser
version: 1.0.0
description: Parse les blocs `<space-instructions>` provenant de Perplexity ou d'autres sources et les convertit en règles actives pour le LLM. Extrait les contraintes, permissions et interdictions.
triggers:
  - "parse space instructions"
  - "extraire règles space"
  - "space-instructions"
  - "parsing instructions"
layer: L1b
strate: L1b
intent_hash: 0xSPACE_INSTRUCTION_PARSER_20260611
---

# space-instruction-parser

## Objectif

Parser les blocs `<space-instructions>` et convertir en règles actives :
- **Contraintes** : ce que le LLM doit/ne doit pas faire
- **Permissions** : ce qui est autorisé
- **Interdictions** : ce qui est bloqué
- **Registre** : ton et style attendu

## Entrée

```xml
<space-instructions>
  <constraint>Ne jamais modifier les fichiers L0 sans ADR</constraint>
  <permission>Créer des fichiers dans PRD/, EPICS/, skills/</permission>
  <prohibition>Pas de push sur main sans PR</prohibition>
  <register>Technique, direct, sans émoji</register>
</space-instructions>
```

## Sortie

```yaml
rules:
  constraints:
    - "Ne jamais modifier les fichiers L0 sans ADR"
  permissions:
    - "Créer des fichiers dans PRD/, EPICS/, skills/"
  prohibitions:
    - "Pas de push sur main sans PR"
  register: "Technique, direct, sans émoji"
```

## Utilisation

```bash
# Parser un fichier
python scripts/space_parser.py --input space_instructions.xml

# Parser depuis le clipboard
python scripts/space_parser.py --clipboard

# Mode validateur (vérifie la conformité d'un texte)
python scripts/space_parser.py --validate texte.txt
```
