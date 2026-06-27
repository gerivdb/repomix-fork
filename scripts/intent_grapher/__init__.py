"""intent_grapher — EPIC-12 INTENT-GRAPHER

Orchestre la chaîne complète :
  P0 RepoScanner → P1 IntentVectorizer → P2 PipelineDAGBuilder
  → P3 CompletenessScorer → P4 CrossRepoDiff → llm-pack
"""

__version__ = "0.1.0-p5"
__all__ = [
    "RepoScanner",
    "IntentVectorizer",
    "PipelineDAGBuilder",
    "CompletenessScorer",
    "CrossRepoDiff",
    "LLMPack",
]

from .repo_scanner import RepoScanner
from .intent_vectorizer import IntentVectorizer
from .pipeline_dag_builder import PipelineDAGBuilder
from .completeness_scorer import CompletenessScorer
from .cross_repo_diff import CrossRepoDiff, RepoDiffEntry
from .llm_pack import LLMPack
