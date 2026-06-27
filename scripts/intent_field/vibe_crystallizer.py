"""VibeCrystallizer — EPIC-13 P0

Transforme une vibe (prose Markdown libre) en IntentDraft vectorisé.
LLM-free : regex + heuristiques structurelles sur le Markdown.

Sortie : IntentDraft {
    source_file, detected_id, intent_hash_draft,
    dimension, pain, cible, contraintes,
    repos_cibles, phi_cps_mentions, env_constraints,
    spoke_scores, dominant_spoke,
    tension_preliminary,    # estimé sans CoherenceGate
    crystallization_score,  # confiance 0–1 de la cristallisation
    ratification_ready      # True si score > seuil
}
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Imports EPIC-12
try:
    from scripts.intent_grapher.intent_vectorizer import (
        SPOKE_KEYWORDS,
        IntentParser,
    )
    _EPIC12_AVAILABLE = True
except ImportError:
    _EPIC12_AVAILABLE = False
    # Fallback inline
    SPOKE_KEYWORDS: dict[str, list[str]] = {
        "AI":      ["llm", "rag", "moe", "router", "enzyme", "embed", "model",
                    "inference", "neural", "transformer", "agent", "swarm",
                    "vectori", "intent", "semantic", "digest", "memory", "skill"],
        "TECH":    ["pipeline", "cli", "api", "git", "repo", "cache", "ttl",
                    "dispatch", "bus", "wal", "publish", "scaffold", "docker",
                    "deploy", "ci", "cd", "webhook", "queue", "stream",
                    "worktree", "acp", "emit", "socket"],
        "MATH":    ["phi", "cps", "score", "threshold", "confidence", "metric",
                    "graph", "dag", "topolog", "vector", "matrix", "weight",
                    "cluster", "gradient", "tensor", "cosine"],
        "SCIENCE": ["arxiv", "paper", "research", "causal", "hypothes",
                    "experiment", "invariant", "signal", "pattern", "trajectory"],
        "PHYSICS": ["flux", "styx", "entropy", "energy", "flow", "wave",
                    "field", "gravity", "mass", "force"],
        "BIO":     ["enzyme", "substrate", "reaction", "protein", "metabol",
                    "evolv", "adapt", "mutation", "self-heal"],
    }


# ---------------------------------------------------------------------------
# Seuils
# ---------------------------------------------------------------------------

CRYSTALLIZATION_THRESHOLD = 0.55   # score minimum pour ratification_ready
PHI_CPS_HARD_THRESHOLD    = 4.559  # gate non négociable

# Patterns de détection
_REPO_RE        = re.compile(r"gerivdb/([\w\-]+)")
_PHI_CPS_RE     = re.compile(r"φ[-_]?CPS[^\d]*(\d+\.\d+)", re.IGNORECASE)
_ENV2_RE        = re.compile(
    r"(ENV2|Z600|24GB|6GB|Ollama|qwen2\.5|codestral|INTERDIT|pip install)",
    re.IGNORECASE
)
_PRIORITY_RE    = re.compile(r"\bP([0-3])\b")
_INTENT_ID_RE   = re.compile(r"(INT[-_]\d+|INTENT[-_][\w]+)", re.IGNORECASE)
_EPIC_ID_RE     = re.compile(r"EPIC[-_](\d+)", re.IGNORECASE)
_DATE_RE        = re.compile(r"(\d{4}-\d{2}-\d{2})")
_STATUS_RE      = re.compile(
    r"Statut[^:]*:[^`]*`([^`]+)`", re.IGNORECASE
)

# Sections Markdown qui portent le signal sémantique
SEMANTIC_SECTIONS = [
    "problème", "objectif", "but", "contexte", "signal",
    "pattern", "architecture", "mécanisme", "composant",
    "synerg", "intégration", "module"
]


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class IntentDraft:
    source_file: str
    detected_id: Optional[str] = None
    intent_hash_draft: Optional[str] = None
    # Champs sémantiques
    dimension: Optional[str] = None
    pain: Optional[str] = None
    cible: Optional[str] = None
    contraintes: list[str] = field(default_factory=list)
    # Contexte technique
    repos_cibles: list[str] = field(default_factory=list)
    phi_cps_mentions: list[float] = field(default_factory=list)
    env_constraints: list[str] = field(default_factory=list)
    priority: Optional[str] = None
    epic_refs: list[str] = field(default_factory=list)
    date_detected: Optional[str] = None
    status_detected: Optional[str] = None
    # Vectorisation
    spoke_scores: dict[str, float] = field(default_factory=dict)
    dominant_spoke: Optional[str] = None
    # Scores de cristallisation
    tension_preliminary: float = 0.0   # estimé (sans CoherenceGate)
    crystallization_score: float = 0.0  # confiance 0–1
    ratification_ready: bool = False
    # Méta
    word_count: int = 0
    section_count: int = 0

    def to_dict(self) -> dict:
        return {
            "source_file": self.source_file,
            "detected_id": self.detected_id,
            "intent_hash_draft": self.intent_hash_draft,
            "dimension": self.dimension,
            "pain": self.pain,
            "cible": self.cible,
            "contraintes": self.contraintes,
            "repos_cibles": self.repos_cibles,
            "phi_cps_mentions": self.phi_cps_mentions,
            "env_constraints": self.env_constraints,
            "priority": self.priority,
            "epic_refs": self.epic_refs,
            "date_detected": self.date_detected,
            "status_detected": self.status_detected,
            "spoke_scores": {k: round(v, 3) for k, v in self.spoke_scores.items()},
            "dominant_spoke": self.dominant_spoke,
            "tension_preliminary": round(self.tension_preliminary, 3),
            "crystallization_score": round(self.crystallization_score, 3),
            "ratification_ready": self.ratification_ready,
            "word_count": self.word_count,
            "section_count": self.section_count,
        }

    def to_markdown_summary(self) -> str:
        icon = "✅" if self.ratification_ready else ("⚠️" if self.crystallization_score > 0.3 else "❌")
        lines = [
            f"## IntentDraft — `{self.detected_id or Path(self.source_file).stem}`",
            f"",
            f"| Champ | Valeur |",
            f"|---|---|",
            f"| **Cristallisation** | {icon} `{self.crystallization_score:.2f}` |",
            f"| **Ratification** | `{'READY' if self.ratification_ready else 'NEEDS_REVIEW'}` |",
            f"| **Dimension** | `{self.dimension or '?'}` |",
            f"| **Pain** | `{self.pain or '?'}` |",
            f"| **Cible** | `{self.cible or '?'}` |",
            f"| **Spoke dominant** | `{self.dominant_spoke or '?'}` |",
            f"| **Repos cibles** | {', '.join(f'`{r}`' for r in self.repos_cibles[:4])} |",
            f"| **Tension prélim.** | `{self.tension_preliminary:.2f}` |",
            f"| **φ-CPS mentions** | {self.phi_cps_mentions} |",
            f"| **Priorité détectée** | `P{self.priority or '?'}` |",
        ]
        if self.contraintes:
            lines += [
                f"",
                f"**Contraintes détectées** :",
            ]
            for c in self.contraintes[:5]:
                lines.append(f"- `{c}`")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Crystallizer
# ---------------------------------------------------------------------------

class VibeCrystallizer:
    """Cristallise une vibe Markdown en IntentDraft vectorisé."""

    # Seuil de confiance minimum pour qu'un champ soit considéré détecté
    _FIELD_CONFIDENCE = 0.4

    def __init__(self, ratification_threshold: float = CRYSTALLIZATION_THRESHOLD):
        self.ratification_threshold = ratification_threshold
        self._parser = IntentParser() if _EPIC12_AVAILABLE else None

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def crystallize(self, path: Path) -> IntentDraft:
        """Cristallise un fichier vibe → IntentDraft."""
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return IntentDraft(source_file=str(path))

        draft = IntentDraft(source_file=str(path))
        draft.word_count = len(content.split())
        draft.section_count = content.count("\n## ") + content.count("\n### ")

        # --- Détection ID + hash ---
        draft.detected_id = self._detect_id(content, path)
        draft.intent_hash_draft = self._detect_or_generate_hash(content, draft.detected_id)

        # --- Champs sémantiques ---
        draft.dimension = self._extract_dimension(content)
        draft.pain      = self._extract_pain(content)
        draft.cible     = self._extract_cible(content)
        draft.contraintes = self._extract_contraintes(content)

        # --- Contexte technique ---
        draft.repos_cibles      = self._extract_repos(content)
        draft.phi_cps_mentions  = self._extract_phi_cps(content)
        draft.env_constraints   = self._extract_env_constraints(content)
        draft.priority          = self._extract_priority(content)
        draft.epic_refs         = _EPIC_ID_RE.findall(content)
        draft.date_detected     = self._extract_date(content)
        draft.status_detected   = self._extract_status(content)

        # --- Vectorisation spoke ---
        draft.spoke_scores  = self._compute_spoke_scores(content)
        draft.dominant_spoke = self._dominant_spoke(draft.spoke_scores)

        # --- Scores ---
        draft.crystallization_score = self._compute_crystallization_score(draft)
        draft.tension_preliminary   = self._estimate_tension(draft)
        draft.ratification_ready    = (
            draft.crystallization_score >= self.ratification_threshold
        )

        return draft

    def crystallize_directory(
        self, directory: Path, pattern: str = "*.md"
    ) -> list[IntentDraft]:
        """Cristallise tous les fichiers .md d'un dossier."""
        drafts = []
        for path in sorted(directory.rglob(pattern)):
            if path.name.startswith("README") or path.name == ".gitkeep":
                continue
            drafts.append(self.crystallize(path))
        return drafts

    def crystallize_to_file(
        self, path: Path, output_path: Path
    ) -> IntentDraft:
        draft = self.crystallize(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(draft.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return draft

    # ------------------------------------------------------------------
    # Extraction sémantique
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_id(content: str, path: Path) -> Optional[str]:
        # 1. Champ explicit dans YAML block
        m = re.search(r"intent_id:\s*([\w\-]+)", content)
        if m:
            return m.group(1)
        # 2. Pattern INT-XXXX dans content
        m = _INTENT_ID_RE.search(content)
        if m:
            return m.group(1).upper()
        # 3. ID en métadonnées (ligne **ID** :)
        m = re.search(r"\*\*ID\*\*\s*:\s*`([^`]+)`", content)
        if m:
            return m.group(1)
        # 4. Filename
        stem = path.stem
        m2 = re.match(r"(\d{8})-([\w\-]+)", stem)
        if m2:
            return f"VIBE-{m2.group(1)}-{m2.group(2)[:20]}"
        return stem[:40]

    @staticmethod
    def _detect_or_generate_hash(content: str, detected_id: Optional[str]) -> str:
        # IntentHash existant dans le contenu ?
        m = re.search(r"`(0x[A-Z0-9_φ\.]+)`", content)
        if m:
            return m.group(1)
        # Générer un draft hash depuis l'ID
        safe_id = re.sub(r"[^A-Z0-9_]", "_", (detected_id or "VIBE").upper())
        return f"0x{safe_id}_DRAFT"

    def _extract_dimension(self, content: str) -> Optional[str]:
        # 1. Champ YAML explicite
        m = re.search(r"dimension_principale:\s*(.+)", content)
        if m:
            return m.group(1).strip().strip('"').strip("'")
        # 2. H1 titre → slug
        m = re.search(r"^#\s+(?:INTENT[^\n]*?—\s*)?(.+)", content, re.MULTILINE)
        if m:
            title = m.group(1).strip()
            slug = re.sub(r"[^\w\s]", "", title.lower()).strip()
            slug = re.sub(r"\s+", "_", slug)[:40]
            return slug
        return None

    @staticmethod
    def _extract_pain(content: str) -> Optional[str]:
        # 1. YAML
        m = re.search(r"source_pain:\s*(.+)", content)
        if m:
            return m.group(1).strip().strip('"').strip("'")
        # 2. Section Problème fondamental
        m = re.search(
            r"(?:## Problème|## Probl[ée]matique|## Contexte)[^\n]*\n+([^\n#]{20,120})",
            content, re.IGNORECASE
        )
        if m:
            return m.group(1).strip()[:80]
        return None

    @staticmethod
    def _extract_cible(content: str) -> Optional[str]:
        # 1. YAML
        m = re.search(r"cible:\s*(.+)", content)
        if m:
            return m.group(1).strip().strip('"').strip("'")
        # 2. Section Objectif
        m = re.search(
            r"(?:## Objectif|## But|## Cible)[^\n]*\n+([^\n#]{20,120})",
            content, re.IGNORECASE
        )
        if m:
            return m.group(1).strip()[:80]
        return None

    @staticmethod
    def _extract_contraintes(content: str) -> list[str]:
        contraintes: list[str] = []
        # 1. YAML contrainte_hard
        m = re.search(r"contrainte_hard:\s*(.+)", content)
        if m:
            val = m.group(1).strip()
            if val.startswith("["):
                # liste inline
                items = re.findall(r"['\"]([^'\"]+)['\"]", val)
                contraintes.extend(items)
            else:
                contraintes.append(val.strip('"').strip("'"))
        # 2. ENV2 hard limits block
        env_block = re.search(
            r"ENV2_CONSTRAINTS:[\s\S]{0,800}?(?=\n#|\Z)", content
        )
        if env_block:
            for line in env_block.group().splitlines()[1:]:
                line = line.strip()
                if line and ":" in line and len(line) < 80:
                    contraintes.append(line.lstrip("- "))
        # 3. INTERDITS explicites
        interdits = re.findall(r"([\w_]+)\s*[=:]\s*INTERDIT", content, re.IGNORECASE)
        contraintes.extend(f"{i}=INTERDIT" for i in interdits)
        return list(dict.fromkeys(contraintes))[:8]  # dédup + limite

    @staticmethod
    def _extract_repos(content: str) -> list[str]:
        repos = list(dict.fromkeys(_REPO_RE.findall(content)))
        # Exclure les repos archivés / irrelévants
        exclude = {"geri-cms", "gericms"}
        return [r for r in repos if not any(ex in r for ex in exclude)][:10]

    @staticmethod
    def _extract_phi_cps(content: str) -> list[float]:
        matches = _PHI_CPS_RE.findall(content)
        values = []
        for m in matches:
            try:
                values.append(float(m))
            except ValueError:
                pass
        return sorted(set(values))

    @staticmethod
    def _extract_env_constraints(content: str) -> list[str]:
        matches = _ENV2_RE.findall(content)
        return list(dict.fromkeys(m.lower() for m in matches))[:8]

    @staticmethod
    def _extract_priority(content: str) -> Optional[str]:
        m = _PRIORITY_RE.search(content)
        return m.group(1) if m else None

    @staticmethod
    def _extract_date(content: str) -> Optional[str]:
        m = _DATE_RE.search(content)
        return m.group(1) if m else None

    @staticmethod
    def _extract_status(content: str) -> Optional[str]:
        m = _STATUS_RE.search(content)
        if m:
            return m.group(1).strip()
        m2 = re.search(r"Statut\s*:\s*([^\n]{3,40})", content, re.IGNORECASE)
        return m2.group(1).strip() if m2 else None

    # ------------------------------------------------------------------
    # Spoke scoring
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_spoke_scores(content: str) -> dict[str, float]:
        text = content.lower()
        scores: dict[str, float] = {}
        for spoke, keywords in SPOKE_KEYWORDS.items():
            hits = sum(1 for kw in keywords if kw.lower() in text)
            scores[spoke] = min(hits / max(len(keywords), 1), 1.0)
        return scores

    @staticmethod
    def _dominant_spoke(scores: dict[str, float]) -> Optional[str]:
        if not scores:
            return None
        best = max(scores, key=lambda k: scores[k])
        return best if scores[best] >= 0.1 else None

    # ------------------------------------------------------------------
    # Score de cristallisation (confiance 0–1)
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_crystallization_score(draft: IntentDraft) -> float:
        """Score composite de qualité de la cristallisation."""
        score = 0.0

        # Champs sémantiques (0.40)
        if draft.dimension:  score += 0.12
        if draft.pain:       score += 0.14
        if draft.cible:      score += 0.14

        # Vectorisation (0.20)
        if draft.dominant_spoke:
            score += 0.10
        max_spoke = max(draft.spoke_scores.values()) if draft.spoke_scores else 0
        score += min(max_spoke * 0.10, 0.10)

        # Contexte technique (0.25)
        if draft.repos_cibles:     score += 0.08
        if draft.intent_hash_draft and "DRAFT" not in draft.intent_hash_draft:
            score += 0.07  # hash réel
        else:
            score += 0.02  # hash draft
        if draft.phi_cps_mentions: score += 0.08
        if draft.priority:         score += 0.05
        if draft.contraintes:      score += 0.02

        # Volume signal (0.15)
        if draft.word_count >= 300:  score += 0.08
        elif draft.word_count >= 100: score += 0.04
        if draft.section_count >= 3: score += 0.07
        elif draft.section_count >= 1: score += 0.03

        return min(round(score, 3), 1.0)

    @staticmethod
    def _estimate_tension(draft: IntentDraft) -> float:
        """Tension préliminaire sans CoherenceGate (heuristique).

        0.0 = parfaitement aligné (prévisible)
        1.0 = forte divergence (inconnu / disruptif)
        """
        tension = 0.5  # valeur de base — neutre

        # Signal déjà validé NEXUS → moins de tension
        status = (draft.status_detected or "").lower()
        if "conforme" in status or "accepted" in status:
            tension -= 0.2
        elif "valider" in status or "draft" in status:
            tension += 0.1  # inconnu, légèrement plus de tension

        # φ-CPS explicit → signal de maîtrise
        if draft.phi_cps_mentions:
            max_phi = max(draft.phi_cps_mentions)
            if max_phi >= PHI_CPS_HARD_THRESHOLD:
                tension -= 0.15
            else:
                tension += 0.10  # phi-cps mentionné mais trop bas

        # Beaucoup de repos cibles → impact large → plus de tension
        if len(draft.repos_cibles) >= 5:
            tension += 0.10
        elif len(draft.repos_cibles) >= 2:
            tension += 0.05

        # ENV2 constraints bien définies → moins de surprise
        if len(draft.env_constraints) >= 3:
            tension -= 0.05

        return max(0.0, min(round(tension, 3), 1.0))
