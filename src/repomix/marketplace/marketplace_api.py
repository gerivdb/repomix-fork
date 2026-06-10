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


def main():
    if not FASTAPI_AVAILABLE:
        print("ERREUR: FastAPI non installe — pip install gerivdb-repomix[marketplace]")
        raise SystemExit(1)
    import uvicorn
    uvicorn.run("repomix.marketplace.marketplace_api:app",
                host="127.0.0.1", port=8742, reload=False)


if __name__ == "__main__":
    main()
