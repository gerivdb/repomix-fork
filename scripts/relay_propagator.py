#!/usr/bin/env python3
"""
relay_propagator.py — PRD-003 + PRD-10 (Vague 1+2+3)
Générateur de STRATUM_RELAY pour repos pilotes.

Vague 1 : DSL — identité stratique + lien hub (existant)
Vague 2 : règles locales structurées + Karpathy-Recall 5Q spécifiques
Vague 3 : recall packs 10Q + section dépendances + connectivité FIBRE

Usage:
    python scripts/relay_propagator.py --vague 2 --dry-run
    python scripts/relay_propagator.py --vague 2 --commit --output-dir data/relay_vague2/
    python scripts/relay_propagator.py --vague 3 --commit --output-dir data/relay_vague3/
    python scripts/relay_propagator.py --vague 3 --fibre-only --commit
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import date
from pathlib import Path

VERSES_ROOT = Path("D:/DO/WEB/TOOLS/L4-TOOLS/VERSES")
REPO_ROOT = Path(__file__).parent.parent

# 10 repos pilotes — 2 par grande strate
PILOT_REPOS = [
    {"repo": "GOVERNANCE-HUB", "strate": "L0", "arrondissement": "Hotel de Ville — Constitution",
     "role": "Constitution, cadastre, registres", "parent": "—", "children": "L1, L1b"},
    {"repo": "ECOYSTEM", "strate": "L1", "arrondissement": "Mairie centrale — SOT operationnel",
     "role": "Source of truth operationnel ecosysteme", "parent": "L0", "children": "L2"},
    {"repo": "BRAIN", "strate": "L2", "arrondissement": "Grandes Ecoles — Cognition",
     "role": "Logique ternaire, cognition distribuee", "parent": "L1", "children": "L3"},
    {"repo": "ECOS-CLI", "strate": "L3", "arrondissement": "Voiries — CLI executable",
     "role": "Interface CLI ecosysteme, commandes automation", "parent": "L2", "children": "L4"},
    {"repo": "repomix-fork", "strate": "L3", "arrondissement": "Voiries — Bundler souverain",
     "role": "Bundler repomix fork, scan + verses + marketplace", "parent": "L2", "children": "L4"},
    {"repo": "LLM-REPO", "strate": "L1b", "arrondissement": "Substrat cognitif LLM",
     "role": "LLM_BOOT_PROTOCOL, GATE-0->4, regles comportement", "parent": "L0", "children": "L1"},
    {"repo": "NEXUS", "strate": "L1", "arrondissement": "Archives centrales — Aggregation data",
     "role": "Aggregation cross-repo, NEXUS core", "parent": "L0", "children": "L2"},
    {"repo": "FLUENCE", "strate": "L2", "arrondissement": "Grandes Ecoles — Logique",
     "role": "Logique FLUENCE, phi-CPS, calcul emergence", "parent": "L1", "children": "L3"},
    {"repo": "VERSES", "strate": "L8", "arrondissement": "Culture — Verses ontologiques",
     "role": "Registry des verses, UrbanVerse, BATVERSE", "parent": "L7", "children": "—"},
    {"repo": "political_compass_verse", "strate": "L5", "arrondissement": "Meta — Gouvernance",
     "role": "Boussole politique, scenarios, trits", "parent": "L4", "children": "L6"},
]

# 5 repos critiques pour FIBRE (Vague 3)
FIBRE_REPOS = ["GOVERNANCE-HUB", "ECOYSTEM", "NEXUS", "LLM-REPO", "repomix-fork"]

# Règles locales structurées par repo (Vague 2)
LOCAL_RULES = {
    "GOVERNANCE-HUB": [
        "R1 — Fichiers proteges : ADR/, STRATUM_RELAY.md, known_repositories.yaml — jamais ecrases par merge upstream",
        "R2 — Push direct sur main interdit — PR obligatoire avec review",
        "R3 — Offline-first : toutes les regles doivent fonctionner sans acces reseau",
        "R4 — Intent Hash obligatoire sur chaque document de gouvernance",
        "R5 — Frontmatter YAML valide avant commit (hook pre-commit)",
    ],
    "ECOYSTEM": [
        "R1 — BLO/PLAN/ ne sont jamais modifies sans ADR prealable",
        "R2 — WAL integrite verifiee avant chaque operation d'ecriture",
        "R3 — Mode BDCP inviolable — jamais de sortie FREE sans ordre explicite",
        "R4 — Les scripts PowerShell passent par CMD wrapper (harmonisation-v8)",
        "R5 — Verification MCP access avant chaque operation cross-repo",
    ],
    "BRAIN": [
        "R1 — Les agents cognitifs ne prennent pas de decision D4 sans review humaine",
        "R2 — FLUENCE matrix encoding obligatoire pour les donnees de training",
        "R3 — Les regles comportement (behavior_rules.md) sont SOT — pas de override local",
        "R4 — GATE-0->4 obligatoire avant toute reponse impliquant des repos gerivdb",
        "R5 — Les profils agents sont versionnes — pas de modification inline",
    ],
    "ECOS-CLI": [
        "R1 — Toute commande ecos doit passer par le wrapper CMD (pas de & direct)",
        "R2 — Le stash WIP de DevTools ne doit jamais etre pop sans verification",
        "R3 — Verification d'acces filesystem avant chaque operation (allowedDirectories)",
        "R4 — Les scripts cross-repo sont atomiques — 1 repo par operation",
        "R5 — Le registre repos.json est SOT — pas de creation de repo sans verification GATE-1",
    ],
    "repomix-fork": [
        "R1 — Les bundles XML incluent les metadonnées UrbanVerse (strate, phi_cps, intent_hash)",
        "R2 — Le chunking est obligatoire pour les bundles > 80 Mo (50 repos/chunk)",
        "R3 — known_repositories_190.yaml est la SOT — pas de scan GitHub API (GATE-2)",
        "R4 — Les tests unitaires passent avant chaque commit (55 tests minimum)",
        "R5 — Le cli_contract.py est stable — pas de modification sans ADR",
    ],
    "LLM-REPO": [
        "R1 — LLM_BOOT_PROTOCOL.md est le contrat d'entree force pour tout LLM",
        "R2 — Les GATE-0->4 sont obligatoires — pas de contournement",
        "R3 — Les fichiers de regles (RULES/) sont proteges — PR obligatoire",
        "R4 — Les packs recall sont versionnes et synchronises avec VERSES",
        "R5 — Le comportement par defaut est consultatif — jamais de decision autonome D4",
    ],
    "NEXUS": [
        "R1 — Aggregation cross-repo uniquement — pas de logique metier locale",
        "R2 — Les registres sont immuables — historique preserve en lecture seule",
        "R3 — Verification d'integrite avant chaque aggregation (hash check)",
        "R4 — Les acces sont controles — pas de lecture sans authentification",
        "R5 — Le schema de donnees est versionne — migration ADR obligatoire",
    ],
    "FLUENCE": [
        "R1 — Le calcul phi-CPS est standardise — pas de formule alternative",
        "R2 — La matrice FLUENCE est SOT pour les donnees de training",
        "R3 — Les seuils d'emergence sont configurables mais documentes",
        "R4 — Les resultats de calcul sont reproductibles — seed fixe",
        "R5 — Integration BRAIN obligatoire — pas de calcul isole",
    ],
    "VERSES": [
        "R1 — Chaque verse a un intent_hash unique et immutable",
        "R2 — Le registry verses_library.json est SOT — pas de creation sans ADR",
        "R3 — Les clusters semantiques sont versionnes",
        "R4 — La migration VERSUS -> VERSES est irreversible — backup obligatoire",
        "R5 — Les verses L8/L9 sont consultatifs — pas d'execution autonome",
    ],
    "political_compass_verse": [
        "R1 — Les coordonnees ternaires (S,M,E,I) sont normalisees",
        "R2 — Les projections sur UrbanVerse sont documentees et versionnees",
        "R3 — Pas de decision politique autonome — HITL obligatoire (D4)",
        "R4 — Les scenarios sont reproductibles — seed fixe",
        "R5 — Integration TRANSCENDANCE obligatoire pour les patterns meta",
    ],
}

# Karpathy-Recall 5Q spécifiques par repo (Vague 2)
KARPATHY_5Q = {
    "GOVERNANCE-HUB": [
        ("Quel est le role canonique de GOVERNANCE-HUB ?",
         "Constitution de l'ecosysteme — SOT des regles de gouvernance executables, ADR, registres, et documents de reference."),
        ("Quelle strate amont alimente GOVERNANCE-HUB ?",
         "Aucune — L0 est la strate racine. GOVERNANCE-HUB est la constitution."),
        ("Quelle strate aval GOVERNANCE-HUB alimente-t-il ?",
         "L1 (SOT operationnel) et L1b (substrat cognitif LLM) via les regles et registres."),
        ("Quelle est la regle R1 de GOVERNANCE-HUB ?",
         "Fichiers proteges : ADR/, STRATUM_RELAY.md, known_repositories.yaml ne sont jamais ecrases par merge upstream."),
        ("Comment verifier l'integrite du cadastre ?",
         "Lire known_repositories.yaml (GATE-0), verifier les intent_hash, et valider le frontmatter YAML (hook pre-commit)."),
    ],
    "ECOYSTEM": [
        ("Quel est le role canonique d'ECOYSTEM ?",
         "SOT operationnel — orchestrateur BLO, WAL, et workflows de l'ecosysteme."),
        ("Quelle strate amont alimente ECOYSTEM ?",
         "L0 (GOVERNANCE-HUB) pour les regles de gouvernance."),
        ("Quelle strate aval ECOYSTEM alimente-t-il ?",
         "L2 (composition) — DevTools, CLI, et outils d'execution."),
        ("Quelle est la regle R1 d'ECOYSTEM ?",
         "BLO/PLAN/ ne sont jamais modifies sans ADR prealable."),
        ("Comment le WAL garantit-il l'integrite ?",
         "Chaque operation d'ecriture est journalisee et verifiee avant execution (wal-reconciler)."),
    ],
    "BRAIN": [
        ("Quel est le role canonique de BRAIN ?",
         "Couche IA — agents cognitifs, logique ternaire, et orchestration cognitive."),
        ("Quelle strate amont alimente BRAIN ?",
         "L1 (ECOYSTEM, NEXUS) pour les donnees et regles operationnelles."),
        ("Quelle strate aval BRAIN alimente-t-il ?",
         "L3 (emergence) — FLUENCE, CANDIDATOR, et agents downstream."),
        ("Quelle est la regle R1 de BRAIN ?",
         "Les agents cognitifs ne prennent pas de decision D4 sans review humaine (HITL)."),
        ("Comment BRAIN interagit-il avec FLUENCE ?",
         "BRAIN emet des signaux cognitifs, FLUENCE les qualifie et produit la matrice d'emergence."),
    ],
    "ECOS-CLI": [
        ("Quel est le role canonique d'ECOS-CLI ?",
         "Interface CLI de l'ecosysteme — commandes automation et workflows EECS."),
        ("Quelle strate amont alimente ECOS-CLI ?",
         "L2 (BRAIN, ECOYSTEM) pour la logique et les regles."),
        ("Quelle strate aval ECOS-CLI alimente-t-il ?",
         "L4 (DevTools) — execution sur le hub central C:\\DevTools."),
        ("Quelle est la regle R1 d'ECOS-CLI ?",
         "Toute commande passe par le wrapper CMD — pas de & direct (harmonisation-v8)."),
        ("Comment ECOS-CLI accede-t-il aux repos cross-repo ?",
         "Via le serveur MCP filesystem avec allowedDirectories verifie (C:\\DevTools, D:\\DO\\WEB)."),
    ],
    "repomix-fork": [
        ("Quel est le role canonique de repomix-fork ?",
         "Bundler souverain — mashup de codebase vers format LLM-optimise (XML/MD/texte)."),
        ("Quelle strate amont alimente repomix-fork ?",
         "L2 (BRAIN, ECOYSTEM) pour la logique et les metadonnees UrbanVerse."),
        ("Quelle strate aval repomix-fork alimente-t-il ?",
         "L4 (ARGUS, CodeDB, LYCOS, FLUENCE) — bundles pour ingestion et analyse."),
        ("Quelle est la regle R1 de repomix-fork ?",
         "Les bundles XML incluent les metadonnees UrbanVerse (strate, phi_cps, intent_hash)."),
        ("Comment le chunking fonctionne-t-il ?",
         "Bundles > 80 Mo sont decoupes en chunks de 50 repos (streaming XML, pas de chargement RAM complet)."),
    ],
    "LLM-REPO": [
        ("Quel est le role canonique de LLM-REPO ?",
         "Hub cognitif LLM — LLM_BOOT_PROTOCOL, GATE-0->4, regles comportement agents."),
        ("Quelle strate amont alimente LLM-REPO ?",
         "L0 (GOVERNANCE-HUB) pour les regles de gouvernance."),
        ("Quelle strate aval LLM-REPO alimente-t-il ?",
         "L1 (SOT operationnel) — les regles comportement alimentent tous les agents."),
        ("Quelle est la regle R1 de LLM-REPO ?",
         "LLM_BOOT_PROTOCOL.md est le contrat d'entree force pour tout LLM operant sur gerivdb."),
        ("Que sont les GATE-0->4 ?",
         "Sequence de boot obligatoire : lire known_repositories.yaml, AGENT_RAM.yaml, BRIDGES.yaml, OrgansRegistry.yaml."),
    ],
    "NEXUS": [
        ("Quel est le role canonique de NEXUS ?",
         "Aggregation cross-repo — registre des registres, mega-SOT."),
        ("Quelle strate amont alimente NEXUS ?",
         "L0 (GOVERNANCE-HUB) pour les regles, L1 pour les donnees operationnelles."),
        ("Quelle strate aval NEXUS alimente-t-il ?",
         "L2 (composition) — donnees agregees pour BRAIN, FLUENCE, ECOYSTEM."),
        ("Quelle est la regle R1 de NEXUS ?",
         "Aggregation uniquement — pas de logique metier locale."),
        ("Comment NEXUS garantit-il l'integrite des registres ?",
         "Hash check avant chaque aggregation, historique immuable, acces controles."),
    ],
    "FLUENCE": [
        ("Quel est le role canonique de FLUENCE ?",
         "Logique FLUENCE — calcul phi-CPS, matrice d'emergence, encoding training."),
        ("Quelle strate amont alimente FLUENCE ?",
         "L1 (BRAIN, NEXUS) pour les signaux cognitifs et donnees."),
        ("Quelle strate aval FLUENCE alimente-t-il ?",
         "L3 (emergence) — resultats de calcul pour DATA-MINER, GeriCode."),
        ("Quelle est la regle R1 de FLUENCE ?",
         "Le calcul phi-CPS est standardise — pas de formule alternative."),
        ("Comment phi_CPS est-il calcule ?",
         "Ratio edges/nodes pondere par tier, facteur de connectivite, et score d'emergence UrbanVerse."),
    ],
    "VERSES": [
        ("Quel est le role canonique de VERSES ?",
         "Registry des verses — moteur holographique, clusters semantiques, Base-243."),
        ("Quelle strate amont alimente VERSES ?",
         "L7 (wiki) pour la documentation, L3 pour les patterns."),
        ("Quelle strate aval VERSES alimente-t-il ?",
         "Aucune — L8 est une strate terminale (creativite, ontologie)."),
        ("Quelle est la regle R1 de VERSES ?",
         "Chaque verse a un intent_hash unique et immutable."),
        ("Que sont les clusters semantiques ?",
         "Groupements de verses par proximite ontologique — Base-243, projection holographique."),
    ],
    "political_compass_verse": [
        ("Quel est le role canonique de political_compass_verse ?",
         "Boussole politique — coordonnees ternaires (S,M,E,I), scenarios, trits."),
        ("Quelle strate amont alimente political_compass_verse ?",
         "L4 (gouvernance) pour les regles, L5 pour les patterns meta."),
        ("Quelle strate aval political_compass_verse alimente-t-il ?",
         "L6 (meta) — projections sur TRANSCENDANCE et scenarios emergents."),
        ("Quelle est la regle R1 de political_compass_verse ?",
         "Les coordonnees ternaires (S,M,E,I) sont normalisees — pas de valeurs arbitraires."),
        ("Comment les trits sont-ils utilises ?",
         "Base 3 (-1, 0, +1) encode les orientations politiques, projetes sur UrbanVerse (causalite)."),
    ],
}

# Karpathy-Recall 10Q (Vague 3) — extension des 5Q avec 5 questions supplémentaires
KARPATHY_10Q = {}
for repo_name, qa_5 in KARPATHY_5Q.items():
    extra_qa = [
        ("Quels sont les 3 fichiers les plus critiques de {} ?".format(repo_name),
         "Depend du repo — voir STRATUM_RELAY.md et PRD associe pour les fichiers proteges."),
        ("Comment {} interagit-il avec LLM-REPO ?".format(repo_name),
         "Via LLM_BOOT_PROTOCOL.md et les regles comportement (GATE-0->4) — tout agent LLM doit lire {} avant operation.".format(repo_name)),
        ("Quel est l'intent_hash de {} ?".format(repo_name),
         "Voir le STRATUM_RELAY.md du repo — chaque document de gouvernance a un intent_hash unique."),
        ("Quels tests unitaires couvrent {} ?".format(repo_name),
         "tests/unit/ — les tests sont dans repomix-fork pour les adapters, scripts, et verse_detector."),
        ("Quelle est la dependance critique de {} ?".format(repo_name),
         "LLM-REPO (substrat cognitif) et GOVERNANCE-HUB (constitution) — tout repo depend de ces deux SOT."),
    ]
    KARPATHY_10Q[repo_name] = list(qa_5) + extra_qa


def _render_relay_v1(repo: dict) -> str:
    """Vague 1 : DSL — identité stratique + lien hub."""
    today = date.today().isoformat()
    return """# STRATUM RELAY — {repo} ({strate})

VAGUE: 1 | Synchro: {today} | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : {strate} – {arrondissement}
- **Role canonique** : {role}
- **Parent** : {parent}
- **Enfants** : {children}
- **Connectivite** : DSL (lien hub uniquement)

## Navigation rapide
- PRD canonique : GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md
- Substrat central : gerivdb/LLM-REPO
- Regles strate : LLM-REPO/RULES/behavior_rules.md#{strate}

## Regles locales (extrait hub)
- [R1] : Fichiers proteges — jamais ecrases par merge upstream
- [R2] : Push direct sur main interdit — PR obligatoire
- [R3] : Offline-first — fonctionnement sans reseau garanti

## Karpathy-Recall local
1. Quel est le role canonique de ce repo dans l'ecosysteme ?
2. Quelle strate amont alimente ce repo, et quelle strate aval il alimente ?
3. Quelle est la regle R1 de ce repo ?

## Vague de mise a jour
- Vague courante : 1 (DSL)
- Prochaine vague : 2 (regles locales + micro-rappels)
- Timestamp : {today}
""".format(repo=repo["repo"], strate=repo["strate"], arrondissement=repo["arrondissement"],
           role=repo["role"], parent=repo["parent"], children=repo["children"], today=today)


def _render_relay_v2(repo: dict) -> str:
    """Vague 2 : règles locales structurées + Karpathy-Recall 5Q spécifiques."""
    today = date.today().isoformat()
    rules = LOCAL_RULES.get(repo["repo"], ["R1 — Non defini", "R2 — Non defini", "R3 — Non defini"])
    qa = KARPATHY_5Q.get(repo["repo"], [])

    rules_section = "\n".join("- [{}] : {}".format(r.split(" — ")[0], r.split(" — ", 1)[1]) for r in rules)
    qa_section = "\n".join("{}. {}\n   → {}".format(i+1, q, a) for i, (q, a) in enumerate(qa))

    return """# STRATUM RELAY — {repo} ({strate})

VAGUE: 2 | Synchro: {today} | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : {strate} – {arrondissement}
- **Role canonique** : {role}
- **Parent** : {parent}
- **Enfants** : {children}
- **Connectivite** : DSL (lien hub + regles locales)

## Navigation rapide
- PRD canonique : GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md
- Substrat central : gerivdb/LLM-REPO
- Regles strate : LLM-REPO/RULES/behavior_rules.md#{strate}

## Regles locales (structurees)
{rules}

## Karpathy-Recall local (5Q specifiques)
{qa}

## Vague de mise a jour
- Vague courante : 2 (DSL + regles locales + 5Q Karpathy)
- Prochaine vague : 3 (recall 10Q + dependances + FIBRE)
- Timestamp : {today}
""".format(repo=repo["repo"], strate=repo["strate"], arrondissement=repo["arrondissement"],
           role=repo["role"], parent=repo["parent"], children=repo["children"],
           rules=rules_section, qa=qa_section, today=today)


def _render_relay_v3(repo: dict) -> str:
    """Vague 3 : recall 10Q + section dépendances + connectivité FIBRE."""
    today = date.today().isoformat()
    rules = LOCAL_RULES.get(repo["repo"], ["R1 — Non defini", "R2 — Non defini", "R3 — Non defini"])
    qa = KARPATHY_10Q.get(repo["repo"], [])

    rules_section = "\n".join("- [{}] : {}".format(r.split(" — ")[0], r.split(" — ", 1)[1]) for r in rules)
    qa_section = "\n".join("{}. {}\n   → {}".format(i+1, q, a) for i, (q, a) in enumerate(qa))

    return """# STRATUM RELAY — {repo} ({strate})

VAGUE: 3 | Synchro: {today} | Hub: gerivdb/LLM-REPO

## Identite stratique
- **Strate** : {strate} – {arrondissement}
- **Role canonique** : {role}
- **Parent** : {parent}
- **Enfants** : {children}
- **Connectivite** : FIBRE (Full Interconnect Bundle for Repository Emergence)

## Navigation rapide
- PRD canonique : GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md
- Substrat central : gerivdb/LLM-REPO
- Regles strate : LLM-REPO/RULES/behavior_rules.md#{strate}

## Regles locales (structurees)
{rules}

## Karpathy-Recall local (10Q specifiques)
{qa}

## Dependances
- **Amont** : {parent}
- **Aval** : {children}
- **SOT reference** : gerivdb/LLM-REPO (L1b)
- **Gouvernance** : gerivdb/GOVERNANCE-HUB (L0)

## Connectivite FIBRE
- **Niveau** : Vague 3 — Full Interconnect
- **Recall packs** : synchronises dans LLM-REPO/TRAINING/recall_packs/
- **Cadastre** : known_repositories_190.yaml (190 repos)
- **Score emergence** : calcule via FLUENCE/phi-CPS

## Vague de mise a jour
- Vague courante : 3 (FIBRE — recall 10Q + dependances + interconnect)
- Prochaine vague : 4 (extension cadastre 71+ repos)
- Timestamp : {today}
""".format(repo=repo["repo"], strate=repo["strate"], arrondissement=repo["arrondissement"],
           role=repo["role"], parent=repo["parent"], children=repo["children"],
           rules=rules_section, qa=qa_section, today=today)


def _render_relay(repo: dict, vague: int = 1) -> str:
    if vague == 1:
        return _render_relay_v1(repo)
    elif vague == 2:
        return _render_relay_v2(repo)
    elif vague == 3:
        return _render_relay_v3(repo)
    else:
        return _render_relay_v1(repo)


def propagate_verses():
    """Importe et appelle le relay_propagator v4.0 de VERSES."""
    sys.path.insert(0, str(VERSES_ROOT / "urban_ontology_verse" / "TOOLS"))
    try:
        import relay_propagator as rp
        if hasattr(rp, 'propagate'):
            print("Utilisation du relay_propagator VERSES v4.0")
            return rp.propagate
        else:
            print("VERSES relay_propagateur: fonction propagate introuvable — fallback local")
            return None
    except (ImportError, AttributeError) as e:
        print("VERSES relay_propagateur inaccessible ({}) — fallback local".format(e))
        return None


def propagate(dry_run: bool = True, output_dir: Path = None, vague: int = 1,
              fibre_only: bool = False) -> dict:
    results = {"generated": [], "skipped": [], "dry_run": dry_run, "vague": vague}
    out = output_dir or REPO_ROOT / "data" / "relay_vague{}".format(vague)
    if not dry_run:
        out.mkdir(parents=True, exist_ok=True)

    verses_fn = propagate_verses()

    if verses_fn and not dry_run and vague == 1:
        return verses_fn(dry_run=False, output_dir=out)

    repos = PILOT_REPOS
    if vague == 3 and fibre_only:
        repos = [r for r in repos if r["repo"] in FIBRE_REPOS]

    for repo in repos:
        content = _render_relay(repo, vague=vague)
        fname = "{repo}__STRATUM_RELAY_v{vague}.md".format(repo=repo["repo"], vague=vague)
        if dry_run:
            print("[DRY-RUN] {repo} ({strate}) -> {fname}".format(
                repo=repo["repo"], strate=repo["strate"], fname=fname))
            results["generated"].append(repo["repo"])
        else:
            (out / fname).write_text(content, encoding="utf-8")
            results["generated"].append(repo["repo"])
            print("OK: {}".format(fname))

    manifest = {
        "vague": vague,
        "date": date.today().isoformat(),
        "repos": [r["repo"] for r in repos],
        "count": len(repos),
        "connectivite": "DSL" if vague == 1 else ("DSL+" if vague == 2 else "FIBRE"),
        "fibre_only": fibre_only,
    }
    if not dry_run:
        (out / "relay_manifest_v{}.json".format(vague)).write_text(
            json.dumps(manifest, indent=2), encoding="utf-8")
    return results


def main():
    parser = argparse.ArgumentParser(description="relay_propagator — Vague 1+2+3")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--vague", type=int, choices=[1, 2, 3], default=1,
                        help="Vague a generer (1=DSL, 2=regles+5Q, 3=FIBRE+10Q)")
    parser.add_argument("--fibre-only", action="store_true", default=False,
                        help="Vague 3 uniquement pour les 5 repos FIBRE")
    args = parser.parse_args()
    dry = not args.commit
    results = propagate(dry_run=dry, output_dir=args.output_dir, vague=args.vague,
                        fibre_only=args.fibre_only)
    print("\n{dry}{count} relais generes (Vague {vague})".format(
        dry="[DRY-RUN] " if dry else "", count=len(results["generated"]), vague=args.vague))


if __name__ == "__main__":
    main()
