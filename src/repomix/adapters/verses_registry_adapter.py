#!/usr/bin/env python3
"""
Adaptateur : verses_library.py local -> format registry central VersesSyncManager.
Fallback offline si VERSES inaccessible.
"""
import json
from pathlib import Path
from typing import Optional
from ..sync.verses_sync_manager import VerseEntry


def load_registry_from_verses_library(
    library_path: Optional[Path] = None
) -> dict[str, VerseEntry]:
    """
    Charge verses_library.json comme source de registry local (fallback offline).
    Priorite : registry VERSES central > library locale.
    """
    if library_path is None:
        library_path = Path(__file__).parent.parent / "verses_library.py"

    json_path = library_path.with_suffix(".json")
    if not json_path.exists():
        return {}

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, TypeError):
        return {}

    entries = {}
    verses_list = data.get("verses", data if isinstance(data, list) else [])
    for item in verses_list:
        vid = item.get("id") or item.get("name", "")
        if not vid:
            continue
        entries[vid] = VerseEntry(
            id=vid,
            name=item.get("name", vid),
            domain=item.get("domain", "unknown"),
            version=item.get("version", "1.0.0"),
            dependencies=item.get("dependencies", []),
            quality_score=float(item.get("quality_score", 50.0)),
        )
    return entries


def build_verses_registry_json(entries: dict[str, VerseEntry], output_path: Path) -> None:
    """Serialise les VerseEntry vers le format JSON registry central."""
    registry = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "version": "1.0",
        "verses": [
            {
                "id": e.id, "name": e.name, "domain": e.domain,
                "version": e.version, "dependencies": e.dependencies,
                "quality_score": e.quality_score,
            }
            for e in entries.values()
        ],
    }
    output_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print("Registry ecrit: {} verses -> {}".format(len(entries), output_path))
