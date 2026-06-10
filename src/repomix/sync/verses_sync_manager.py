#!/usr/bin/env python3
"""
PRD-002 Phase 3 -- VersesSyncManager
Sync selective lazy depuis registry central VERSES vers local verses/.
R3 compliant : offline-first, pas de dependance reseau obligatoire.
"""
from __future__ import annotations
import json, hashlib, time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class VerseEntry:
    id: str
    name: str
    domain: str
    version: str
    dependencies: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    local_path: Optional[Path] = None
    cached_at: Optional[float] = None


class VersesSyncManager:
    """
    Sync selectif + lazy loading depuis registry vers cache local.
    Respecte la regle R3 : fonctionne offline si cache present.
    """

    SYNC_TIMEOUT_S = 30
    CACHE_TTL_S = 86400

    def __init__(self, repo_path: str | Path, registry_path: Optional[Path] = None):
        self.repo_path = Path(repo_path)
        self.cache_dir = self.repo_path / "verses" / "cache"
        self.registry_path = registry_path or (
            Path("D:/DO/WEB/TOOLS/L3-CITIZENS/VERSES/registry/verses_registry.json")
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._registry: dict[str, VerseEntry] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        if not self.registry_path.exists():
            return
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
            for v in data.get("verses", []):
                fields = {k: v[k] for k in VerseEntry.__dataclass_fields__ if k in v}
                entry = VerseEntry(**fields)
                self._registry[entry.id] = entry
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    def list_available(self, domain: Optional[str] = None) -> list[VerseEntry]:
        entries = list(self._registry.values())
        if domain:
            entries = [e for e in entries if e.domain == domain]
        return sorted(entries, key=lambda e: e.quality_score, reverse=True)

    def _resolve_dependencies(self, verse_ids: list[str]) -> dict[str, str]:
        resolved: dict[str, str] = {}
        queue = list(verse_ids)
        seen: set[str] = set()
        while queue:
            vid = queue.pop(0)
            if vid in seen:
                continue
            seen.add(vid)
            entry = self._registry.get(vid)
            if not entry:
                resolved[vid] = "unknown"
                continue
            resolved[vid] = entry.version
            queue.extend(entry.dependencies)
        return resolved

    def _pin_versions(self, deps: dict[str, str]) -> dict[str, str]:
        pinned = {}
        for vid, version in deps.items():
            if version == "unknown":
                pinned[vid] = "0.0.0"
            elif version == "latest":
                entry = self._registry.get(vid)
                pinned[vid] = entry.version if entry else "0.0.0"
            else:
                pinned[vid] = version
        return pinned

    def _cache_path(self, verse_id: str, version: str) -> Path:
        slug = "{}__{}".format(verse_id, version).replace("/", "__").replace(":", "__")
        return self.cache_dir / "{}.verse.json".format(slug)

    def _is_cached(self, verse_id: str, version: str) -> bool:
        p = self._cache_path(verse_id, version)
        if not p.exists():
            return False
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            cached_at = data.get("cached_at", 0)
            return (time.time() - cached_at) < self.CACHE_TTL_S
        except (json.JSONDecodeError, KeyError):
            return False

    def _write_cache(self, entry: VerseEntry, version: str) -> None:
        p = self._cache_path(entry.id, version)
        payload = {
            "id": entry.id, "name": entry.name, "domain": entry.domain,
            "version": version, "dependencies": entry.dependencies,
            "quality_score": entry.quality_score,
            "cached_at": time.time(),
            "checksum": hashlib.sha256(entry.name.encode()).hexdigest()[:12],
        }
        p.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def sync_selective(self, needed_verses: list[str]) -> dict:
        t0 = time.time()
        deps = self._resolve_dependencies(needed_verses)
        pinned = self._pin_versions(deps)
        cached, skipped, missing = [], [], []
        for vid, version in pinned.items():
            if self._is_cached(vid, version):
                skipped.append(vid)
                continue
            entry = self._registry.get(vid)
            if entry:
                self._write_cache(entry, version)
                cached.append(vid)
            else:
                missing.append(vid)
        elapsed = time.time() - t0
        return {
            "cached": cached, "skipped": skipped, "missing": missing,
            "elapsed_s": round(elapsed, 3),
            "under_kpi": elapsed < self.SYNC_TIMEOUT_S,
        }

    def invalidate_cache(self, verse_id: Optional[str] = None) -> int:
        if verse_id:
            targets = list(self.cache_dir.glob("{}__*.verse.json".format(verse_id)))
        else:
            targets = list(self.cache_dir.glob("*.verse.json"))
        for f in targets:
            f.unlink()
        return len(targets)
