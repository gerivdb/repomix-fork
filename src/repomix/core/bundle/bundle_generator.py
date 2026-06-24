"""
bundle_generator.py — Générateur bundle.kiva (EPIC-239 Phase 3)

Interface contractuelle repomix-fork → KIVA.
Le bundle.kiva est un fichier JSON contenant les métadonnées nécessaires
pour que KIVA puisse orchestrer un run via TRIX.
"""

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# === Schema bundle.kiva ===

BUNDLE_SCHEMA_VERSION = "1.0.0"

BUNDLE_REQUIRED_FIELDS = [
    "schema_version",
    "bundle_id",
    "created_at",
    "source_repo",
    "target_strate",
    "intent_hash",
    "components",
]


class BundleComponent:
    """Représente un composant individuel du bundle."""

    def __init__(
        self,
        name: str,
        path: str,
        kind: str = "service",  # service, library, tool, config
        entry_point: Optional[str] = None,
        dependencies: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ):
        self.name = name
        self.path = path
        self.kind = kind
        self.entry_point = entry_point
        self.dependencies = dependencies or []
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "kind": self.kind,
            "entry_point": self.entry_point,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


class BundleGenerator:
    """Génère un bundle.kiva à partir d'un mono-repo."""

    def __init__(self, repo_path: str, target_strate: str = "auto"):
        self.repo_path = Path(repo_path).resolve()
        self.target_strate = target_strate
        self.components: list[BundleComponent] = []
        self.metadata: dict[str, Any] = {}

    def analyze(self) -> "BundleGenerator":
        """Analyse la structure du mono-repo."""
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repo path not found: {self.repo_path}")

        # Détecter la strate si auto
        if self.target_strate == "auto":
            self.target_strate = self._detect_strate()

        # Scanner les sous-répos
        self._scan_subrepos()

        # Si aucun sous-repo trouvé, traiter le repo lui-même comme composant
        if not self.components:
            self._add_self_as_component()

        return self

    def _detect_strate(self) -> str:
        """Détecte la strate basée sur le chemin et le contenu."""
        path_str = str(self.repo_path).lower()

        # Détection par chemin Windows D:\DO\WEB\TOOLS\L*
        for prefix, strate in [
            (r"\\l0-canon", "L0-CANON"),
            (r"\\l1-infra", "L1-INFRA"),
            (r"\\l2-platform", "L2-PLATFORM"),
            (r"\\l3-citizens", "L3-CITIZENS"),
            (r"\\l4-tools", "L4-TOOLS"),
            (r"\\l5-archive", "L5-ARCHIVE"),
        ]:
            if re.search(prefix, path_str):
                return strate

        # Détection par contenu
        if (self.repo_path / ".git").exists():
            # Vérifier si c'est un workspace multi-repo
            gitmodules = self.repo_path / ".gitmodules"
            if gitmodules.exists():
                return "L4-TOOLS"

        return "L4-TOOLS"  # Défaut

    def _scan_subrepos(self):
        """Scane les sous-répos git dans le mono-repo."""
        for child in self.repo_path.iterdir():
            if not child.is_dir():
                continue

            # Vérifier si c'est un repo git
            git_dir = child / ".git"
            if not git_dir.exists():
                continue

            # Ignorer les DOSS communs
            if child.name.startswith((".", "__", "node_modules", ".venv")):
                continue

            # Détecter le kind
            kind = self._detect_component_kind(child)

            # Trouver l'entry point
            entry_point = self._find_entry_point(child)

            # Extraire les dépendances
            dependencies = self._extract_dependencies(child)

            component = BundleComponent(
                name=child.name,
                path=str(child.relative_to(self.repo_path)),
                kind=kind,
                entry_point=entry_point,
                dependencies=dependencies,
                metadata={
                    "git_remote": self._get_git_remote(child),
                    "has_readme": (child / "README.md").exists(),
                    "has_ci": (child / ".github" / "workflows").exists() or
                              (child / ".gitlab-ci.yml").exists(),
                },
            )
            self.components.append(component)

    def _detect_component_kind(self, path: Path) -> str:
        """Détecte le type de composant."""
        if (path / "pyproject.toml").exists() or (path / "setup.py").exists():
            if (path / "src").exists() or (path / path.name.replace("-", "_")).exists():
                return "library"
            return "service"
        if (path / "package.json").exists():
            return "service"
        if (path / "Cargo.toml").exists():
            return "library"
        if (path / "go.mod").exists():
            return "library"
        if (path / "setup.cfg").exists():
            return "library"
        return "config"

    def _find_entry_point(self, path: Path) -> Optional[str]:
        """Trouve le point d'entrée du composant."""
        candidates = [
            "src/main.py",
            "main.py",
            f"src/{path.name.replace('-', '_')}/__main__.py",
            f"{path.name.replace('-', '_')}/__main__.py",
            "app.py",
            "manage.py",
        ]
        for candidate in candidates:
            if (path / candidate).exists():
                return candidate

        # Chercher dans pyproject.toml
        pyproject = path / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8", errors="ignore")
            if "[project.scripts]" in content or "[tool.poetry.scripts]" in content:
                return "pyproject.toml:scripts"

        return None

    def _extract_dependencies(self, path: Path) -> list[str]:
        """Extrait les dépendances du composant."""
        deps = []

        # Python
        pyproject = path / "pyproject.toml"
        if pyproject.exists():
            try:
                import tomllib
                with open(pyproject, "rb") as f:
                    data = tomllib.load(f)
                project_deps = data.get("project", {}).get("dependencies", [])
                deps.extend(project_deps)
            except Exception:
                pass

        requirements = path / "requirements.txt"
        if requirements.exists():
            content = requirements.read_text(encoding="utf-8", errors="ignore")
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    deps.append(line.split("==")[0].split(">=")[0].split("<=")[0])

        return deps[:20]  # Limiter à 20 dépendances

    def _get_git_remote(self, path: Path) -> Optional[str]:
        """Extrait le remote git d'un sous-repo."""
        try:
            git_config = path / ".git" / "config"
            if git_config.exists():
                content = git_config.read_text(encoding="utf-8", errors="ignore")
                import re
                match = re.search(r'url\s*=\s*(.+)', content)
                if match:
                    return match.group(1).strip()
        except Exception:
            pass
        return None

    def _add_self_as_component(self):
        """Ajoute le repo lui-même comme composant unique."""
        component = BundleComponent(
            name=self.repo_path.name,
            path=".",
            kind="service",
            entry_point=None,
            dependencies=[],
            metadata={
                "is_mono_repo": True,
                "git_remote": self._get_git_remote(self.repo_path),
            },
        )
        self.components.append(component)

    def generate(self, actor: str = "unknown") -> dict:
        """Génère le bundle.kiva complet."""
        now = datetime.now(timezone.utc).isoformat()
        bundle_id = hashlib.sha256(
            f"{self.repo_path}:{now}:{len(self.components)}".encode()
        ).hexdigest()[:16]

        intent_hash = hashlib.sha256(
            f"bundle:{self.repo_path.name}:{self.target_strate}:{now}".encode()
        ).hexdigest()[:12].upper()

        bundle = {
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "bundle_id": bundle_id,
            "created_at": now,
            "actor": actor,
            "source_repo": str(self.repo_path),
            "target_strate": self.target_strate,
            "intent_hash": f"0xBUNDLE_{intent_hash}",
            "component_count": len(self.components),
            "components": [c.to_dict() for c in self.components],
            "metadata": {
                "generator": "repomix-fork/bundle_generator",
                "schema_ref": "https://gerivdb/GOVERNANCE-HUB/schemas/bundle.kiva.schema.json",
                "total_dependencies": sum(len(c.dependencies) for c in self.components),
                "kiva_compatible": True,
                "trix_namespace_required": True,
            },
        }

        return bundle

    def write(self, output_path: Optional[str] = None, actor: str = "unknown") -> Path:
        """Génère et écrit le bundle.kiva sur disque."""
        bundle = self.generate(actor=actor)

        if output_path is None:
            output_path = self.repo_path / f"{self.repo_path.name}.bundle.kiva.json"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)

        return output_path


# === CLI ===

def main():
    """CLI pour bundle_generator."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="repomix-bundle",
        description="Générateur bundle.kiva (EPIC-239 Phase 3)",
    )
    parser.add_argument("repo_path", type=str, help="Chemin du mono-repo")
    parser.add_argument(
        "--strate", type=str, default="auto",
        help="Strate cible (L0-CANON, L1-INFRA, ...)",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Chemin de sortie (défaut: <repo>.bundle.kiva.json)",
    )
    parser.add_argument(
        "--actor", type=str, default="unknown",
        help="Identité de l'acteur",
    )
    parser.add_argument(
        "--pretty", action="store_true",
        help="Afficher le JSON formaté",
    )

    args = parser.parse_args()

    try:
        generator = BundleGenerator(args.repo_path, target_strate=args.strate)
        generator.analyze()
        bundle = generator.generate(actor=args.actor)

        if args.pretty:
            print(json.dumps(bundle, indent=2, ensure_ascii=False))
        else:
            output_path = generator.write(output_path=args.output, actor=args.actor)
            print(f"Bundle generated: {output_path}")
            print(f"  Components: {bundle['component_count']}")
            print(f"  Strate: {bundle['target_strate']}")
            print(f"  IntentHash: {bundle['intent_hash']}")

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=__import__("sys").stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=__import__("sys").stderr)
        return 2

    return 0


if __name__ == "__main__":
    __import__("sys").exit(main())
