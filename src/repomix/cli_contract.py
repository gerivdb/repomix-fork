"""
src/repomix/cli_contract.py — PRD-008
Contrat d'interface public pour ECOS-CLI (Apport A5).
API stable : ne pas modifier sans ADR dans GOVERNANCE-HUB.
Version: 1.0.0
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class OutputFormat(str, Enum):
    XML = "xml"
    MD = "md"
    TEXT = "text"


class Tier(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    ALL = "ALL"


@dataclass(frozen=True)
class BundleRequest:
    """Parametres d'une requete de bundling — type stable garanti v1.0.0."""
    repo: str
    tier: Tier = Tier.ALL
    output_format: OutputFormat = OutputFormat.XML
    output_dir: Optional[Path] = None
    include_metadata: bool = True

    def validate(self) -> list[str]:
        errors = []
        if not self.repo or not self.repo.strip():
            errors.append("repo: champ requis non vide")
        if self.output_dir and not isinstance(self.output_dir, Path):
            errors.append("output_dir: doit etre un Path")
        return errors


@dataclass
class BundleResult:
    """Resultat d'une operation de bundling."""
    success: bool
    repo: str
    output_path: Optional[Path]
    size_bytes: int = 0
    elapsed_s: float = 0.0
    error: Optional[str] = None
    chunks: int = 1


# ── Entree principale (appelee par ECOS-CLI via import ou subprocess) ──

def bundle_repo(request: BundleRequest) -> BundleResult:
    """
    Point d'entree stable A5.
    ECOS-CLI appelle cette fonction directement ou via :
      gerivdb-repomix bundle --repo <name> --tier <tier> --output <format>

    Contrat garanti v1.0.0 :
    - Signature stable (BundleRequest -> BundleResult)
    - Levee de ValueError si request.validate() retourne des erreurs
    - Jamais de sys.exit() — toujours retourner BundleResult(success=False, error=...)
    """
    import time
    from repomix.adapters.known_repos_adapter import KnownReposAdapterV3

    errors = request.validate()
    if errors:
        raise ValueError("BundleRequest invalide : {}".format(errors))

    t0 = time.perf_counter()

    try:
        adapter = KnownReposAdapterV3()
        stats = adapter.get_stats()

        # Filtre par repo si nom specifique (pas "ALL")
        if request.repo.upper() != "ALL":
            node = adapter.nodes.get(request.repo)
            if node is None:
                return BundleResult(
                    success=False, repo=request.repo, output_path=None,
                    error="Repo inconnu : {} (non dans known_repositories_190.yaml)".format(
                        request.repo)
                )

        # Delegation a bundle_corpus
        sys_path = str(Path(__file__).parent.parent.parent)
        import sys
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)

        from scripts.bundle_corpus import generate_bundles
        out_dir = request.output_dir or Path("data/bundles") / request.repo

        if request.repo.upper() == "ALL":
            repos = [
                {"name": n.name, "layer": n.layer, "tier": n.tier}
                for n in adapter.active_nodes()
            ]
        else:
            node = adapter.nodes[request.repo]
            repos = [
                {"name": request.repo, "layer": node.layer, "tier": node.tier}
            ]

        manifest = generate_bundles(repos, out_dir, tier_filter=request.tier.value)
        elapsed = time.perf_counter() - t0

        out_path = None
        if manifest["chunks"]:
            out_path = out_dir / "bundle_{:03d}.xml".format(manifest["chunks"][0]["index"])

        return BundleResult(
            success=True,
            repo=request.repo,
            output_path=out_path,
            size_bytes=int(
                out_path.stat().st_size if out_path and out_path.exists() else 0
            ),
            elapsed_s=round(elapsed, 3),
            chunks=len(manifest["chunks"]),
        )

    except Exception as exc:
        return BundleResult(
            success=False, repo=request.repo, output_path=None,
            elapsed_s=round(time.perf_counter() - t0, 3),
            error=str(exc),
        )


# ── Interface subprocess (ECOS-CLI sans import direct) ──────────────

CLI_ENTRYPOINT = "gerivdb-repomix bundle"
CLI_SCHEMA = {
    "command": CLI_ENTRYPOINT,
    "version": "1.0.0",
    "intent_hash": "0xECOS_CLI_CONTRACT_A5_20260611",
    "args": {
        "--repo": {
            "type": "str", "required": True,
            "help": "Nom du repo ou ALL"
        },
        "--tier": {
            "type": "str", "required": False, "default": "ALL",
            "choices": ["P0", "P1", "P2", "P3", "ALL"],
            "help": "Tier de priorite"
        },
        "--output": {
            "type": "str", "required": False, "default": "xml",
            "choices": ["xml", "md", "text"],
            "help": "Format de sortie"
        },
        "--out-dir": {
            "type": "Path", "required": False, "default": None,
            "help": "Repertoire de sortie"
        },
    },
    "exit_codes": {
        0: "success",
        1: "validation_error",
        2: "repo_not_found",
        3: "bundle_failed"
    },
}
