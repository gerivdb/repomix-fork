#!/usr/bin/env python3
"""
PRD-002 Phase 4 -- Marketplace API (local FastAPI, offline-first R3)
Usage: python -m repomix.marketplace.marketplace_api
       ou: uvicorn repomix.marketplace.marketplace_api:app --port 8742
"""
from __future__ import annotations
import time, json
from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException, Query
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from ..sync.verses_sync_manager import VersesSyncManager, VerseEntry
from ..adapters.verses_registry_adapter import load_registry_from_verses_library

RATINGS_FILE = Path("data/marketplace_ratings.json")


def _load_ratings() -> dict:
    if RATINGS_FILE.exists():
        return json.loads(RATINGS_FILE.read_text(encoding="utf-8"))
    return {}


def _save_ratings(ratings: dict) -> None:
    RATINGS_FILE.parent.mkdir(exist_ok=True)
    RATINGS_FILE.write_text(json.dumps(ratings, indent=2), encoding="utf-8")


if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="UrbanVerse Marketplace API",
        description="Local marketplace for verses -- PRD-002 Phase 4",
        version="1.0.0",
    )

    _manager = VersesSyncManager(repo_path=".")
    _fallback = load_registry_from_verses_library()
    _manager._registry.update(_fallback)

    class PublishPayload(BaseModel):
        id: str
        name: str
        domain: str
        version: str
        dependencies: list[str] = []
        quality_score: float = 50.0

    class RatingPayload(BaseModel):
        score: float
        comment: Optional[str] = None

    @app.post("/verses/publish", status_code=201)
    def publish_verse(payload: PublishPayload):
        entry = VerseEntry(**payload.model_dump())
        _manager._registry[entry.id] = entry
        return {"status": "published", "id": entry.id, "version": entry.version}

    @app.get("/verses/search")
    def search_verses(
        query: str = Query(default=""),
        domain: Optional[str] = Query(default=None),
        min_quality: float = Query(default=0.0),
    ):
        results = _manager.list_available(domain=domain)
        if query:
            q = query.lower()
            results = [r for r in results if q in r.name.lower() or q in r.id.lower()]
        results = [r for r in results if r.quality_score >= min_quality]
        return {
            "count": len(results),
            "verses": [{"id": r.id, "name": r.name, "domain": r.domain,
                        "version": r.version, "quality_score": r.quality_score}
                       for r in results],
        }

    @app.get("/verses/{verse_id}/dependencies")
    def get_dependencies(verse_id: str):
        entry = _manager._registry.get(verse_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Verse '{}' not found".format(verse_id))
        resolved = _manager._resolve_dependencies([verse_id])
        return {"verse_id": verse_id, "dependencies": resolved}

    @app.post("/verses/{verse_id}/rate")
    def rate_verse(verse_id: str, payload: RatingPayload):
        if verse_id not in _manager._registry:
            raise HTTPException(status_code=404, detail="Verse '{}' not found".format(verse_id))
        ratings = _load_ratings()
        if verse_id not in ratings:
            ratings[verse_id] = {"scores": [], "comments": []}
        ratings[verse_id]["scores"].append(payload.score)
        if payload.comment:
            ratings[verse_id]["comments"].append(payload.comment)
        avg = sum(ratings[verse_id]["scores"]) / len(ratings[verse_id]["scores"])
        _manager._registry[verse_id].quality_score = round(avg, 1)
        _save_ratings(ratings)
        return {"verse_id": verse_id, "new_quality_score": avg,
                "total_ratings": len(ratings[verse_id]["scores"])}

    @app.get("/verses/{verse_id}/versions")
    def get_versions(verse_id: str):
        cache_dir = Path("verses/cache")
        if not cache_dir.exists():
            return {"verse_id": verse_id, "versions": []}
        cached = list(cache_dir.glob("{}__*.verse.json".format(verse_id)))
        versions = []
        for f in cached:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                versions.append({"version": data.get("version"), "cached_at": data.get("cached_at")})
            except Exception:
                pass
        return {"verse_id": verse_id, "versions": versions}

    @app.get("/health")
    def health():
        return {"status": "ok", "registry_size": len(_manager._registry),
                "timestamp": time.time()}

    # ── V2: push_to_marketplace ──────────────────────────────────────

    @app.post("/verses/push", status_code=201)
    def push_to_marketplace(payload: PublishPayload):
        """
        V2: Push verse entry to VERSES/ontology_registry.json.
        Bidirectional sync: marketplace -> VERSES registry.
        """
        entry = VerseEntry(**payload.model_dump())
        _manager._registry[entry.id] = entry
        # Persist to VERSES registry
        _manager._save_to_verses_registry(entry)
        return {"status": "pushed", "id": entry.id, "version": entry.version,
                "registry": "VERSES/ontology_registry.json"}


def _save_to_verses_registry(self, entry: VerseEntry) -> None:
    """
    Write/update a verse entry in VERSES/ontology_registry.json.
    Creates the file if it doesn't exist.
    """
    verses_marketplace = Path("D:/DO/WEB/TOOLS/L4-TOOLS/REPOMIX-FORK/verses-marketplace")
    registry_path = verses_marketplace / "ontology_registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing
    if registry_path.exists():
        try:
            data = json.loads(registry_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            data = {"verses": [], "version": "1.0", "last_updated": ""}
    else:
        data = {"verses": [], "version": "1.0", "last_updated": ""}

    # Update or append
    verses_list = data.get("verses", [])
    found = False
    for i, v in enumerate(verses_list):
        if v.get("id") == entry.id:
            verses_list[i] = {
                "id": entry.id, "name": entry.name, "domain": entry.domain,
                "version": entry.version, "dependencies": entry.dependencies,
                "quality_score": entry.quality_score,
            }
            found = True
            break
    if not found:
        verses_list.append({
            "id": entry.id, "name": entry.name, "domain": entry.domain,
            "version": entry.version, "dependencies": entry.dependencies,
            "quality_score": entry.quality_score,
        })

    data["verses"] = verses_list
    data["last_updated"] = time.time()
    data["count"] = len(verses_list)

    registry_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# Attach method to VersesSyncManager class
from ..sync.verses_sync_manager import VersesSyncManager
VersesSyncManager._save_to_verses_registry = _save_to_verses_registry


def main():
    if not FASTAPI_AVAILABLE:
        print("ERREUR: FastAPI non installe — pip install gerivdb-repomix[marketplace]")
        raise SystemExit(1)
    import uvicorn
    uvicorn.run("repomix.marketplace.marketplace_api:app",
                host="127.0.0.1", port=8742, reload=False)


if __name__ == "__main__":
    main()
