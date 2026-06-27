"""IntentVectorizer — EPIC-12 P1

Parse les fichiers d'intent (YAML front-matter + corps Markdown)
et les projette sur l'ontologie gerivdb (ontology_registry.json).

Sortie : intent_vector.json
    {
      "repo": "gerivdb/Gitnote",
      "generated_at": "2026-06-27T...",
      "intents": [ {intent_vector}, ... ],
      "repo_vector": { dimensions agrégées },
      "ontology_spokes": { spoke: score }
    }
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# PyYAML optionnel — fallback sur parser regex léger
try:
    import yaml  # type: ignore
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Champs YAML attendus dans le front-matter des intents (cf. INT-1211/1212/1213)
INTENT_YAML_FIELDS = [
    "intent_id",
    "dimension_principale",
    "source_pain",
    "cible",
    "contrainte_hard",
    "resultat_attendu",
]

# Mapping mots-clés → spoke ontologique (ontology_registry.json spokes)
SPOKE_KEYWORDS: dict[str, list[str]] = {
    "AI":      ["llm", "rag", "moe", "router", "enzyme", "embed", "model",
                "inference", "neural", "transformer", "agent", "swarm",
                "vectori", "intent", "semantic", "digest"],
    "TECH":    ["pipeline", "cli", "api", "git", "repo", "cache", "ttl",
                "dispatch", "bus", "wal", "publish", "scaffold", "docker",
                "deploy", "ci", "cd", "webhook", "queue", "stream"],
    "MATH":    ["phi", "cps", "score", "threshold", "confidence", "metric",
                "graph", "dag", "topolog", "vector", "matrix", "weight"],
    "SCIENCE": ["arxiv", "paper", "research", "causal", "hypothes",
                "experiment", "invariant", "signal", "pattern"],
    "PHYSICS": ["flux", "styx", "entropy", "energy", "flow", "wave"],
    "BIO":     ["enzyme", "substrate", "reaction", "protein", "metabol"],
}

# Score de présence minimal pour qu'un spoke soit considéré actif
SPOKE_THRESHOLD = 0.1


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class IntentVector:
    intent_id: str
    file: str
    intent_hash: Optional[str] = None
    dimension_principale: Optional[str] = None
    source_pain: Optional[str] = None
    cible: Optional[str] = None
    contrainte_hard: Any = None          # str ou list
    resultat_attendu: Optional[str] = None
    epic_ref: Optional[str] = None       # EPIC lié (extrait du body)
    adr_ref: Optional[str] = None        # ADR lié (extrait du body)
    raw_yaml: dict = field(default_factory=dict)
    spoke_scores: dict[str, float] = field(default_factory=dict)
    dominant_spoke: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "intent_id": self.intent_id,
            "file": self.file,
            "intent_hash": self.intent_hash,
            "dimension_principale": self.dimension_principale,
            "source_pain": self.source_pain,
            "cible": self.cible,
            "contrainte_hard": self.contrainte_hard,
            "resultat_attendu": self.resultat_attendu,
            "epic_ref": self.epic_ref,
            "adr_ref": self.adr_ref,
            "spoke_scores": {k: round(v, 3) for k, v in self.spoke_scores.items()},
            "dominant_spoke": self.dominant_spoke,
        }


@dataclass
class RepoIntentVector:
    repo: str
    generated_at: str
    intents: list[IntentVector] = field(default_factory=list)
    repo_vector: dict = field(default_factory=dict)   # agrégation cross-intents
    ontology_spokes: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "repo": self.repo,
            "generated_at": self.generated_at,
            "intent_count": len(self.intents),
            "intents": [i.to_dict() for i in self.intents],
            "repo_vector": self.repo_vector,
            "ontology_spokes": {k: round(v, 3) for k, v in self.ontology_spokes.items()},
        }


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class IntentParser:
    """Extrait le YAML front-matter et les références d'un fichier intent .md"""

    # Pattern pour le bloc ```yaml ... ``` dans le corps
    _YAML_BLOCK_RE = re.compile(
        r"```ya?ml\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE
    )
    # Pattern IntentHash dans le body Markdown
    _INTENT_HASH_RE = re.compile(
        r"\*\*IntentHash\*\*[^`]*`([^`]+)`"
    )
    # Pattern EPIC ref : [EPIC-XXXX] ou EPIC-XXXX
    _EPIC_REF_RE = re.compile(r"EPIC[-–](\d+)", re.IGNORECASE)
    # Pattern ADR ref
    _ADR_REF_RE = re.compile(r"ADR[-–](\d+)", re.IGNORECASE)

    def parse_file(self, path: Path) -> IntentVector:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return IntentVector(intent_id="UNKNOWN", file=str(path))

        yaml_data = self._extract_yaml_block(content)
        intent_hash = self._extract_intent_hash(content)
        epic_refs = self._EPIC_REF_RE.findall(content)
        adr_refs = self._ADR_REF_RE.findall(content)

        intent_id = (
            yaml_data.get("intent_id")
            or self._guess_id_from_filename(path.name)
        )

        return IntentVector(
            intent_id=intent_id,
            file=str(path),
            intent_hash=intent_hash,
            dimension_principale=yaml_data.get("dimension_principale"),
            source_pain=yaml_data.get("source_pain"),
            cible=yaml_data.get("cible"),
            contrainte_hard=yaml_data.get("contrainte_hard"),
            resultat_attendu=yaml_data.get("resultat_attendu"),
            epic_ref=epic_refs[0] if epic_refs else None,
            adr_ref=adr_refs[0] if adr_refs else None,
            raw_yaml=yaml_data,
        )

    def _extract_yaml_block(self, content: str) -> dict:
        """Extrait le premier bloc ```yaml``` du body."""
        m = self._YAML_BLOCK_RE.search(content)
        if not m:
            return {}
        block = m.group(1)
        if _YAML_AVAILABLE:
            try:
                data = yaml.safe_load(block)
                return data if isinstance(data, dict) else {}
            except yaml.YAMLError:
                pass
        # Fallback : parser clé: valeur simple
        return self._parse_yaml_fallback(block)

    @staticmethod
    def _parse_yaml_fallback(block: str) -> dict:
        result: dict = {}
        for line in block.splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and v:
                    result[k] = v
        return result

    @staticmethod
    def _extract_intent_hash(content: str) -> Optional[str]:
        m = IntentParser._INTENT_HASH_RE.search(content)
        return m.group(1) if m else None

    @staticmethod
    def _guess_id_from_filename(name: str) -> str:
        """INT-1211-moe-router.md → INT-1211"""
        m = re.match(r"(INT[-_]\d+)", name, re.IGNORECASE)
        return m.group(1).upper() if m else name.replace(".md", "")


# ---------------------------------------------------------------------------
# Vectorizer
# ---------------------------------------------------------------------------

class IntentVectorizer:
    """Vectorise les fichiers d'intent d'un repo et projette sur l'ontologie."""

    def __init__(
        self,
        repo: str,
        intents_dir: Path,
        ontology_path: Optional[Path] = None,
    ):
        self.repo = repo
        self.intents_dir = intents_dir
        self.ontology_path = ontology_path
        self._ontology: dict = self._load_ontology()
        self._parser = IntentParser()

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def vectorize(self) -> RepoIntentVector:
        """Vectorise tous les intents trouvés dans intents_dir."""
        now = datetime.now(timezone.utc).isoformat()
        result = RepoIntentVector(repo=self.repo, generated_at=now)

        intent_files = sorted(
            f for f in self.intents_dir.rglob("*.md")
            if f.name != ".gitkeep" and not f.name.startswith("README")
        )

        for path in intent_files:
            iv = self._parser.parse_file(path)
            iv.spoke_scores = self._compute_spoke_scores(iv)
            iv.dominant_spoke = self._dominant_spoke(iv.spoke_scores)
            result.intents.append(iv)

        result.ontology_spokes = self._aggregate_spokes(result.intents)
        result.repo_vector = self._build_repo_vector(result.intents)
        return result

    def vectorize_to_file(self, output_path: Path) -> RepoIntentVector:
        rv = self.vectorize()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(rv.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return rv

    # ------------------------------------------------------------------
    # Spoke scoring
    # ------------------------------------------------------------------

    def _compute_spoke_scores(self, iv: IntentVector) -> dict[str, float]:
        """Score 0–1 par spoke basé sur la densité de mots-clés."""
        # Concaténer tous les champs texte de l'intent
        text = " ".join(filter(None, [
            iv.dimension_principale or "",
            iv.source_pain or "",
            iv.cible or "",
            str(iv.contrainte_hard or ""),
            iv.resultat_attendu or "",
            iv.intent_hash or "",
        ])).lower()

        scores: dict[str, float] = {}
        for spoke, keywords in SPOKE_KEYWORDS.items():
            hits = sum(1 for kw in keywords if kw.lower() in text)
            # Normaliser par nombre de keywords du spoke
            scores[spoke] = min(hits / max(len(keywords), 1), 1.0)

        return scores

    @staticmethod
    def _dominant_spoke(scores: dict[str, float]) -> Optional[str]:
        if not scores:
            return None
        best = max(scores, key=lambda k: scores[k])
        return best if scores[best] >= SPOKE_THRESHOLD else None

    @staticmethod
    def _aggregate_spokes(intents: list[IntentVector]) -> dict[str, float]:
        """Moyenne des spoke_scores sur tous les intents."""
        if not intents:
            return {spoke: 0.0 for spoke in SPOKE_KEYWORDS}
        agg: dict[str, float] = {spoke: 0.0 for spoke in SPOKE_KEYWORDS}
        for iv in intents:
            for spoke, score in iv.spoke_scores.items():
                agg[spoke] = agg.get(spoke, 0.0) + score
        n = len(intents)
        return {k: round(v / n, 3) for k, v in agg.items()}

    @staticmethod
    def _build_repo_vector(intents: list[IntentVector]) -> dict:
        """Synthèse transversale : dimensions principales + cibles + contraintes."""
        dims = [iv.dimension_principale for iv in intents if iv.dimension_principale]
        pains = [iv.source_pain for iv in intents if iv.source_pain]
        cibles = [iv.cible for iv in intents if iv.cible]
        all_contraintes: list[str] = []
        for iv in intents:
            if isinstance(iv.contrainte_hard, list):
                all_contraintes.extend(iv.contrainte_hard)
            elif iv.contrainte_hard:
                all_contraintes.append(str(iv.contrainte_hard))
        return {
            "dimensions": list(dict.fromkeys(dims)),       # dédupliqué, ordre préservé
            "source_pains": list(dict.fromkeys(pains)),
            "cibles": list(dict.fromkeys(cibles)),
            "contraintes_hard": list(dict.fromkeys(all_contraintes)),
            "epic_refs": list(dict.fromkeys(
                iv.epic_ref for iv in intents if iv.epic_ref
            )),
        }

    # ------------------------------------------------------------------
    # Ontologie
    # ------------------------------------------------------------------

    def _load_ontology(self) -> dict:
        if self.ontology_path and self.ontology_path.exists():
            try:
                return json.loads(self.ontology_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    @property
    def ontology_spokes(self) -> list[str]:
        return list(self._ontology.get("spokes", SPOKE_KEYWORDS).keys())
