"""PipelineDAGBuilder — EPIC-12 P2

Construit le DAG de traçabilité INTENT → PRD → EPIC → ADR → Issue → Commit
à partir des résultats de RepoScanner + IntentVectorizer.

Sortie : pipeline_dag.json
    {
      "nodes": [ {id, layer, file, gap} ... ],
      "edges": [ {from, to, type, gap} ... ],
      "gaps": [ {layer, missing_id, reason} ... ],
      "summary": { nodes_total, edges_total, gap_count }
    }
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# networkx optionnel — fallback dict si absent
try:
    import networkx as nx  # type: ignore
    _NX_AVAILABLE = True
except ImportError:
    _NX_AVAILABLE = False

from .repo_scanner import ScanResult
from .intent_vectorizer import RepoIntentVector, IntentVector


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Ordre canonique des couches dans le DAG
LAYER_ORDER = ["intent", "prd", "epic", "adr", "issue", "commit"]

# Types d'arêtes
EDGE_DERIVES   = "derives"    # intent → epic
EDGE_REQUIRES  = "requires"   # epic → adr
EDGE_TRACKS    = "tracks"     # epic → issue
EDGE_IMPLEMENTS = "implements" # issue → commit

# Patterns d'extraction ID dans les noms de fichiers
_ID_PATTERNS = {
    "intent": re.compile(r"INT[-_](\d+)", re.IGNORECASE),
    "prd":    re.compile(r"(?:PRD|EPIC)[-_](\d+)", re.IGNORECASE),
    "epic":   re.compile(r"EPIC[-_](\d+|\d\d)", re.IGNORECASE),
    "adr":    re.compile(r"ADR[-_](\d+)", re.IGNORECASE),
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DAGNode:
    id: str                        # ex. "INT-1211", "EPIC-1211", "ADR-1211"
    layer: str                     # intent / prd / epic / adr / issue / commit
    file: Optional[str] = None     # chemin relatif (None si gap)
    gap: bool = False              # True si noeud manquant inféré
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "layer": self.layer,
            "file": self.file,
            "gap": self.gap,
            "meta": self.meta,
        }


@dataclass
class DAGEdge:
    from_id: str
    to_id: str
    edge_type: str
    gap: bool = False              # True si l'une des extrémités est un gap

    def to_dict(self) -> dict:
        return {
            "from": self.from_id,
            "to": self.to_id,
            "type": self.edge_type,
            "gap": self.gap,
        }


@dataclass
class GapRecord:
    layer: str
    missing_id: str
    reason: str
    inferred_from: Optional[str] = None  # ID du noeud source qui référence ce gap

    def to_dict(self) -> dict:
        return {
            "layer": self.layer,
            "missing_id": self.missing_id,
            "reason": self.reason,
            "inferred_from": self.inferred_from,
        }


@dataclass
class PipelineDAG:
    repo: str
    nodes: list[DAGNode] = field(default_factory=list)
    edges: list[DAGEdge] = field(default_factory=list)
    gaps: list[GapRecord] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "repo": self.repo,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "gaps": [g.to_dict() for g in self.gaps],
            "summary": {
                "nodes_total": len(self.nodes),
                "nodes_real": sum(1 for n in self.nodes if not n.gap),
                "nodes_gap": sum(1 for n in self.nodes if n.gap),
                "edges_total": len(self.edges),
                "gap_count": len(self.gaps),
                "layers_covered": sorted(
                    {n.layer for n in self.nodes if not n.gap}
                ),
            },
        }

    def to_networkx(self):
        """Retourne un nx.DiGraph si networkx disponible."""
        if not _NX_AVAILABLE:
            raise ImportError("networkx requis : pip install networkx")
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(
                node.id,
                layer=node.layer,
                file=node.file,
                gap=node.gap,
            )
        for edge in self.edges:
            G.add_edge(edge.from_id, edge.to_id, type=edge.edge_type, gap=edge.gap)
        return G

    def mermaid(self) -> str:
        """Exporte le DAG en diagramme Mermaid flowchart."""
        lines = ["flowchart TD"]
        # Noeuds
        for node in self.nodes:
            label = node.id
            if node.gap:
                lines.append(f'    {node.id}["{label} ❌"]:::gap')
            else:
                lines.append(f'    {node.id}["{label}"]:::real')
        # Arêtes
        for edge in self.edges:
            arrow = "-.->" if edge.gap else "-->"
            lines.append(f"    {edge.from_id} {arrow}|{edge.edge_type}| {edge.to_id}")
        # Styles
        lines += [
            "    classDef real fill:#22c55e,color:#fff,stroke:#16a34a",
            "    classDef gap  fill:#f87171,color:#fff,stroke:#dc2626",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class PipelineDAGBuilder:
    """Construit le PipelineDAG à partir de ScanResult + RepoIntentVector."""

    def __init__(
        self,
        repo: str,
        scan_result: ScanResult,
        intent_vector: Optional[RepoIntentVector] = None,
    ):
        self.repo = repo
        self.scan = scan_result
        self.iv = intent_vector
        self._dag = PipelineDAG(repo=repo)
        # Index id → node pour références croisées
        self._node_index: dict[str, DAGNode] = {}

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def build(self) -> PipelineDAG:
        self._add_intent_nodes()
        self._add_prd_nodes()
        self._add_epic_nodes()
        self._add_adr_nodes()
        self._add_issue_nodes()
        self._wire_edges()
        self._detect_gaps()
        return self._dag

    def build_to_file(self, output_path: Path) -> PipelineDAG:
        dag = self.build()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(dag.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return dag

    def build_mermaid(self, output_path: Path) -> str:
        dag = self.build()
        mmd = dag.mermaid()
        output_path.write_text(mmd, encoding="utf-8")
        return mmd

    # ------------------------------------------------------------------
    # Ajout de noeuds par couche
    # ------------------------------------------------------------------

    def _add_intent_nodes(self) -> None:
        if self.iv:
            for iv in self.iv.intents:
                node = DAGNode(
                    id=iv.intent_id,
                    layer="intent",
                    file=iv.file,
                    meta={
                        "dimension": iv.dimension_principale,
                        "dominant_spoke": iv.dominant_spoke,
                        "intent_hash": iv.intent_hash,
                    },
                )
                self._add_node(node)
        else:
            # Fallback : lire les fichiers depuis scan_result
            layer = self.scan.layers.get("intents")
            if layer and layer.present:
                for f in layer.files:
                    nid = self._id_from_file(f, "intent") or f
                    self._add_node(DAGNode(id=nid, layer="intent", file=f))

    def _add_prd_nodes(self) -> None:
        layer = self.scan.layers.get("prd")
        if layer and layer.present:
            for f in layer.files:
                nid = self._id_from_file(f, "prd")
                if nid:
                    self._add_node(DAGNode(id=f"EPIC-{nid}", layer="prd", file=f))

    def _add_epic_nodes(self) -> None:
        layer = self.scan.layers.get("epics")
        if layer and layer.present:
            for f in layer.files:
                nid = self._id_from_file(f, "epic")
                if nid:
                    eid = f"EPIC-{nid}"
                    # Eviter doublons avec PRD si déjà ajouté
                    if eid not in self._node_index:
                        self._add_node(DAGNode(id=eid, layer="epic", file=f))

    def _add_adr_nodes(self) -> None:
        layer = self.scan.layers.get("adr")
        if layer and layer.present:
            for f in layer.files:
                if "README" in f:
                    continue
                nid = self._id_from_file(f, "adr")
                if nid:
                    self._add_node(DAGNode(id=f"ADR-{nid}", layer="adr", file=f))

    def _add_issue_nodes(self) -> None:
        layer = self.scan.layers.get("issues")
        if layer and layer.present:
            for f in layer.files:
                self._add_node(DAGNode(id=f"ISSUE:{Path(f).stem}", layer="issue", file=f))

    # ------------------------------------------------------------------
    # Cablage des arêtes
    # ------------------------------------------------------------------

    def _wire_edges(self) -> None:
        """Connecte les noeuds selon la hiérarchie pipeline."""
        intents = self._nodes_by_layer("intent")
        epics_and_prd = self._nodes_by_layer("prd") + self._nodes_by_layer("epic")
        adrs = self._nodes_by_layer("adr")
        issues = self._nodes_by_layer("issue")

        # INTENT → EPIC : matching par numéro
        for intent_node in intents:
            num = self._num_from_id(intent_node.id)
            for epic_node in epics_and_prd:
                epic_num = self._num_from_id(epic_node.id)
                if num and epic_num and num == epic_num:
                    self._add_edge(DAGEdge(
                        from_id=intent_node.id,
                        to_id=epic_node.id,
                        edge_type=EDGE_DERIVES,
                        gap=False,
                    ))

        # EPIC → ADR : matching par numéro
        for epic_node in epics_and_prd:
            epic_num = self._num_from_id(epic_node.id)
            matched = False
            for adr_node in adrs:
                adr_num = self._num_from_id(adr_node.id)
                if epic_num and adr_num and epic_num == adr_num:
                    self._add_edge(DAGEdge(
                        from_id=epic_node.id,
                        to_id=adr_node.id,
                        edge_type=EDGE_REQUIRES,
                        gap=False,
                    ))
                    matched = True
            if not matched and epic_num:
                # Gap : ADR manquant pour cet EPIC
                ghost_id = f"ADR-{epic_num}"
                ghost = DAGNode(id=ghost_id, layer="adr", gap=True)
                self._add_node(ghost)
                self._add_edge(DAGEdge(
                    from_id=epic_node.id,
                    to_id=ghost_id,
                    edge_type=EDGE_REQUIRES,
                    gap=True,
                ))

        # EPIC → ISSUE : si issues présentes
        for epic_node in epics_and_prd:
            for issue_node in issues:
                self._add_edge(DAGEdge(
                    from_id=epic_node.id,
                    to_id=issue_node.id,
                    edge_type=EDGE_TRACKS,
                    gap=False,
                ))

    # ------------------------------------------------------------------
    # Détection des gaps
    # ------------------------------------------------------------------

    def _detect_gaps(self) -> None:
        """Recense tous les noeuds gap + les couches entièrement absentes."""
        # Noeuds ghost déjà ajoutés par _wire_edges
        for node in self._dag.nodes:
            if node.gap:
                self._dag.gaps.append(GapRecord(
                    layer=node.layer,
                    missing_id=node.id,
                    reason=f"Noeud {node.layer.upper()} manquant — inféré depuis les références",
                    inferred_from=self._find_inferred_from(node.id),
                ))

        # Couches entièrement absentes
        present_layers = {n.layer for n in self._dag.nodes if not n.gap}
        for layer in ["intent", "prd", "epic", "adr", "issue"]:
            if layer not in present_layers:
                self._dag.gaps.append(GapRecord(
                    layer=layer,
                    missing_id=f"{layer.upper()}/*",
                    reason=f"Couche {layer.upper()} entièrement absente du repo",
                ))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _add_node(self, node: DAGNode) -> None:
        if node.id not in self._node_index:
            self._dag.nodes.append(node)
            self._node_index[node.id] = node

    def _add_edge(self, edge: DAGEdge) -> None:
        self._dag.edges.append(edge)

    def _nodes_by_layer(self, layer: str) -> list[DAGNode]:
        return [n for n in self._dag.nodes if n.layer == layer and not n.gap]

    def _find_inferred_from(self, ghost_id: str) -> Optional[str]:
        for edge in self._dag.edges:
            if edge.to_id == ghost_id and edge.gap:
                return edge.from_id
        return None

    @staticmethod
    def _id_from_file(filepath: str, layer: str) -> Optional[str]:
        name = Path(filepath).name
        pattern = _ID_PATTERNS.get(layer)
        if pattern:
            m = pattern.search(name)
            return m.group(1) if m else None
        return None

    @staticmethod
    def _num_from_id(node_id: str) -> Optional[str]:
        """Extrait le numéro d'un ID : 'INT-1211' → '1211', 'EPIC-12' → '12'"""
        m = re.search(r"(\d+)$", node_id)
        return m.group(1) if m else None
