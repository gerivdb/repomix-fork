"""RepoScanner — EPIC-12 P0
Détecte les couches du thought commit pipeline dans un repo.
Supporte le mode local (filesystem) et le mode remote (GitHub API via MCP ou requests).
"""
from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Couches canoniques du pipeline, par ordre de granularité croissante
PIPELINE_LAYERS = [
    "intents",   # intents/ ou INTENTS/
    "prd",       # PRD/
    "epics",     # EPICS/ ou EPICs dans PRD/
    "adr",       # ADR/
    "issues",    # .github/ISSUE_TEMPLATE/ ou issues GitHub (remote only)
]

# Dossiers candidats par couche (case-insensitive match)
LAYER_DIRS: dict[str, list[str]] = {
    "intents": ["intents", "INTENTS", "intent"],
    "prd":     ["PRD", "prd", "specs"],
    "epics":   ["EPICS", "epics"],
    "adr":     ["ADR", "adr", "decisions"],
    "issues":  [".github/ISSUE_TEMPLATE", ".github/issues"],
}

# Extensions considérées comme artefacts de pipeline
PIPELINE_EXTENSIONS = {".md", ".yaml", ".yml", ".json"}


@dataclass
class LayerResult:
    layer: str
    present: bool
    path: Optional[str] = None          # chemin relatif détecté
    file_count: int = 0
    files: list[str] = field(default_factory=list)
    has_intent_hash: bool = False        # au moins 1 fichier avec IntentHash
    score: float = 0.0                  # 0.0 – 1.0


@dataclass
class ScanResult:
    repo: str                            # "owner/repo" ou chemin local
    mode: str                            # "local" | "remote"
    layers: dict[str, LayerResult] = field(default_factory=dict)
    global_score: float = 0.0           # 0.0 – 5.0
    pipeline_index_present: bool = False

    def to_dict(self) -> dict:
        return {
            "repo": self.repo,
            "mode": self.mode,
            "pipeline_index_present": self.pipeline_index_present,
            "global_score": round(self.global_score, 2),
            "layers": {
                k: {
                    "present": v.present,
                    "path": v.path,
                    "file_count": v.file_count,
                    "has_intent_hash": v.has_intent_hash,
                    "score": round(v.score, 2),
                }
                for k, v in self.layers.items()
            },
        }


class RepoScanner:
    """Scanne un repo local ou remote et retourne un ScanResult."""

    def __init__(self, repo: str, mode: str = "local", base_path: Optional[Path] = None):
        """
        Args:
            repo: "owner/repo" (mode remote) ou chemin local (mode local)
            mode: "local" | "remote"
            base_path: racine locale si mode=="local" (défaut: Path(repo))
        """
        self.repo = repo
        self.mode = mode
        self.base_path = base_path or Path(repo)

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def scan(self) -> ScanResult:
        if self.mode == "local":
            return self._scan_local()
        elif self.mode == "remote":
            return self._scan_remote()
        else:
            raise ValueError(f"mode doit être 'local' ou 'remote', reçu: {self.mode!r}")

    # ------------------------------------------------------------------
    # Mode local
    # ------------------------------------------------------------------

    def _scan_local(self) -> ScanResult:
        result = ScanResult(repo=self.repo, mode="local")

        # Vérification PIPELINE_INDEX.md
        result.pipeline_index_present = (self.base_path / "PIPELINE_INDEX.md").exists()

        for layer in PIPELINE_LAYERS:
            layer_result = self._scan_layer_local(layer)
            result.layers[layer] = layer_result
            result.global_score += layer_result.score

        return result

    def _scan_layer_local(self, layer: str) -> LayerResult:
        candidates = LAYER_DIRS.get(layer, [])
        for candidate in candidates:
            candidate_path = self.base_path / candidate
            if candidate_path.is_dir():
                files = [
                    str(f.relative_to(self.base_path))
                    for f in candidate_path.rglob("*")
                    if f.is_file() and f.suffix in PIPELINE_EXTENSIONS
                    and f.name != ".gitkeep"
                ]
                has_intent_hash = any(
                    self._file_has_intent_hash(self.base_path / f)
                    for f in files
                )
                score = self._compute_score(len(files), has_intent_hash)
                return LayerResult(
                    layer=layer,
                    present=True,
                    path=candidate,
                    file_count=len(files),
                    files=files,
                    has_intent_hash=has_intent_hash,
                    score=score,
                )
        return LayerResult(layer=layer, present=False, score=0.0)

    # ------------------------------------------------------------------
    # Mode remote (GitHub API via env GITHUB_TOKEN)
    # ------------------------------------------------------------------

    def _scan_remote(self) -> ScanResult:
        """Scanne via l'API GitHub REST. Nécessite GITHUB_TOKEN dans l'env."""
        try:
            import requests  # type: ignore
        except ImportError:
            raise ImportError("Le mode remote nécessite 'requests'. pip install requests")

        token = os.environ.get("GITHUB_TOKEN", "")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        owner, repo_name = self.repo.split("/", 1)
        base_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"

        result = ScanResult(repo=self.repo, mode="remote")

        # Lister la racine
        root_entries = self._gh_list(base_url, headers)
        root_names = {e["name"] for e in root_entries if e.get("type") in ("file", "dir")}

        result.pipeline_index_present = "PIPELINE_INDEX.md" in root_names

        for layer in PIPELINE_LAYERS:
            layer_result = self._scan_layer_remote(
                layer, base_url, headers, root_entries
            )
            result.layers[layer] = layer_result
            result.global_score += layer_result.score

        return result

    def _scan_layer_remote(
        self, layer: str, base_url: str, headers: dict, root_entries: list
    ) -> LayerResult:
        import requests  # type: ignore

        candidates = LAYER_DIRS.get(layer, [])
        root_names = {e["name"]: e for e in root_entries if e.get("type") == "dir"}

        for candidate in candidates:
            # Gestion des chemins imbriqués (ex: .github/ISSUE_TEMPLATE)
            parts = candidate.split("/")
            if parts[0] in root_names:
                dir_url = f"{base_url}/{candidate}"
                entries = self._gh_list(dir_url, headers)
                files = [
                    e["path"] for e in entries
                    if e.get("type") == "file"
                    and Path(e["name"]).suffix in PIPELINE_EXTENSIONS
                    and e["name"] != ".gitkeep"
                ]
                has_intent_hash = False  # Simplified: pas de lecture fichier en remote P0
                score = self._compute_score(len(files), has_intent_hash)
                return LayerResult(
                    layer=layer,
                    present=True,
                    path=candidate,
                    file_count=len(files),
                    files=files,
                    has_intent_hash=has_intent_hash,
                    score=score,
                )
        return LayerResult(layer=layer, present=False, score=0.0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _gh_list(url: str, headers: dict) -> list:
        import requests  # type: ignore
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json() if isinstance(resp.json(), list) else []
        return []

    @staticmethod
    def _file_has_intent_hash(path: Path) -> bool:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return "IntentHash" in content or "intent_id" in content
        except OSError:
            return False

    @staticmethod
    def _compute_score(file_count: int, has_intent_hash: bool) -> float:
        """Score 0.0–1.0 : présence (0.6) + fichiers non vides (0.2) + IntentHash (0.2)"""
        if file_count == 0:
            return 0.0
        base = 0.6
        base += 0.2  # au moins 1 fichier présent
        if has_intent_hash:
            base += 0.2
        return min(base, 1.0)
