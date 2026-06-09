"""
Verses Library - NEXUS Advanced Ecosystem
Management system for quantum verses and creative content
"""

import json
import os
from typing import Dict, List, Any, Optional, Type
from datetime import datetime

# Import depuis le package src/repomix (import relatif)
from repomix.verses_creative_foundation import (
    BaseQuantumVerse,
    QuantumPoetryVerse,
    AnticipatoryNarrativeVerse,
    ArchitectureVerse,
    DebugVerse,
    TeamHarmonyVerse,
    CodeEleganceVerse,
    AlgorithmicSonnetVerse,
    DatabaseSymphonyVerse,
    APISerenadeVerse,
    QuantumFractalVerse,
    BlockchainBalladVerse,
    MachineLearningOdeVerse,
    CybersecuritySonataVerse,
    DevOpsRhapsodyVerse,
    QuantumEntanglementVerse,
    DataVisualizationWaltzVerse,
    CloudComputingConcertoVerse,
    IoTIntermezzoVerse,
    AugmentedRealityAriaVerse,
    NaturalLanguageOperaVerse,
    RoboticSymphonyVerse,
    QuantumCryptographyCantataVerse,
    SwarmIntelligenceChorusVerse,
    VirtualRealityFantasiaVerse,
    EdgeComputingEtudeVerse,
    GeneticAlgorithmRondoVerse,
    BlockchainConsensusCapriceVerse,
    NeuralNetworkNocturneVerse,
    ContainerOrchestrationOvertureVerse,
    QuantumSupremacySonataVerse,
    HumanComputerInteractionMinuetVerse,
    BioinformaticsBalletVerse,
    AutonomousSystemsSymphonyVerse,
    DigitalTwinConcertoVerse,
    EthicalAICantataVerse,
    MetaverseOperaVerse,
    SustainableTechSerenadeVerse,
    CognitiveComputingChorusVerse,
    VerseResult,
    CreationContext,
)


class VersesLibrary:
    """Comprehensive library for managing quantum verses and creative content."""

    def __init__(self, library_path: str = "verses_library.json"):
        self.library_path = library_path
        self.verses: Dict[str, Dict[str, VerseResult]] = {}
        self.verse_classes: Dict[str, Type[BaseQuantumVerse]] = {
            "quantum_poetry": QuantumPoetryVerse,
            "anticipatory_narrative": AnticipatoryNarrativeVerse,
            "architecture_verse": ArchitectureVerse,
            "debug_verse": DebugVerse,
            "team_harmony": TeamHarmonyVerse,
            "code_elegance": CodeEleganceVerse,
            "algorithmic_sonnet": AlgorithmicSonnetVerse,
            "database_symphony": DatabaseSymphonyVerse,
            "api_serenade": APISerenadeVerse,
            "quantum_fractal": QuantumFractalVerse,
            "blockchain_ballad": BlockchainBalladVerse,
            "ml_ode": MachineLearningOdeVerse,
            "cybersecurity_sonata": CybersecuritySonataVerse,
            "devops_rhapsody": DevOpsRhapsodyVerse,
            "quantum_entanglement": QuantumEntanglementVerse,
            "data_viz_waltz": DataVisualizationWaltzVerse,
            "cloud_concerto": CloudComputingConcertoVerse,
            "iot_intermezzo": IoTIntermezzoVerse,
            "ar_aria": AugmentedRealityAriaVerse,
            "nlp_opera": NaturalLanguageOperaVerse,
            "robotic_symphony": RoboticSymphonyVerse,
            "quantum_crypto_cantata": QuantumCryptographyCantataVerse,
            "swarm_chorus": SwarmIntelligenceChorusVerse,
            "vr_fantasia": VirtualRealityFantasiaVerse,
            "edge_etude": EdgeComputingEtudeVerse,
            "ga_rondo": GeneticAlgorithmRondoVerse,
            "blockchain_caprice": BlockchainConsensusCapriceVerse,
            "neural_nocturne": NeuralNetworkNocturneVerse,
            "container_overture": ContainerOrchestrationOvertureVerse,
            "quantum_supremacy_sonata": QuantumSupremacySonataVerse,
            "hci_minuet": HumanComputerInteractionMinuetVerse,
            "bioinformatics_ballet": BioinformaticsBalletVerse,
            "autonomous_symphony": AutonomousSystemsSymphonyVerse,
            "digital_twin_concerto": DigitalTwinConcertoVerse,
            "ethical_ai_cantata": EthicalAICantataVerse,
            "metaverse_opera": MetaverseOperaVerse,
            "sustainable_tech_serenade": SustainableTechSerenadeVerse,
            "cognitive_chorus": CognitiveComputingChorusVerse,
        }
        self._load_library()

    def _load_library(self):
        if os.path.exists(self.library_path):
            try:
                with open(self.library_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for verse_type, verses in data.items():
                        self.verses[verse_type] = {}
                        for verse_id, verse_dict in verses.items():
                            self.verses[verse_type][verse_id] = VerseResult(**verse_dict)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to load verses library: {e}. Starting with empty library.")
                self.verses = {}

    def _save_library(self):
        data = {}
        for verse_type, verses in self.verses.items():
            data[verse_type] = {}
            for verse_id, verse_result in verses.items():
                data[verse_type][verse_id] = {
                    "verse_content": verse_result.verse_content,
                    "verse_type": verse_result.verse_type,
                    "resonance_score": verse_result.resonance_score,
                    "harmony_metrics": verse_result.harmony_metrics,
                    "metadata": verse_result.metadata,
                    "created_at": verse_result.created_at,
                }
        with open(self.library_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def register_verse_type(self, verse_type: str, verse_class: Type[BaseQuantumVerse]):
        self.verse_classes[verse_type] = verse_class

    async def create_verse(self, verse_type: str, context: CreationContext, verse_id: Optional[str] = None) -> Optional[VerseResult]:
        if verse_type not in self.verse_classes:
            return None
        if verse_id is None:
            verse_id = f"{verse_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            verse_class = self.verse_classes[verse_type]
            verse_instance = verse_class(f"test_{verse_type}")
            result = await verse_instance.compose_quantum_verse(context)
            if verse_type not in self.verses:
                self.verses[verse_type] = {}
            self.verses[verse_type][verse_id] = result
            self._save_library()
            return result
        except Exception as e:
            print(f"Failed to create verse: {e}")
            return None

    def get_verse(self, verse_type: str, verse_id: str) -> Optional[VerseResult]:
        if verse_type in self.verses and verse_id in self.verses[verse_type]:
            return self.verses[verse_type][verse_id]
        return None

    def search_verses(self, verse_type: Optional[str] = None, min_resonance: float = 0.0,
                      tags: Optional[List[str]] = None, content_query: Optional[str] = None) -> List[VerseResult]:
        results = []
        search_space = self.verses.items()
        if verse_type:
            if verse_type in self.verses:
                search_space = [(verse_type, self.verses[verse_type])]
            else:
                return []
        for v_type, verses in search_space:
            for verse_id, verse_result in verses.items():
                if verse_result.resonance_score < min_resonance:
                    continue
                if tags:
                    verse_tags = verse_result.metadata.get("tags", [])
                    if not any(tag in verse_tags for tag in tags):
                        continue
                if content_query:
                    if content_query.lower() not in verse_result.verse_content.lower():
                        continue
                results.append(verse_result)
        return results

    def get_verse_statistics(self) -> Dict[str, Any]:
        total_verses = sum(len(verses) for verses in self.verses.values())
        resonance_scores = []
        type_distribution = {}
        for verse_type, verses in self.verses.items():
            type_distribution[verse_type] = len(verses)
            for verse_result in verses.values():
                resonance_scores.append(verse_result.resonance_score)
        avg_resonance = sum(resonance_scores) / len(resonance_scores) if resonance_scores else 0
        return {
            "total_verses": total_verses,
            "verse_types": list(self.verses.keys()),
            "type_distribution": type_distribution,
            "average_resonance": avg_resonance,
            "library_health": self._assess_library_health(),
        }

    def _assess_library_health(self) -> str:
        if not self.verses:
            return "empty"
        total = sum(len(v) for v in self.verses.values())
        if total < 5:
            return "developing"
        elif total < 20:
            return "growing"
        return "mature"


# Global instance
verses_library = VersesLibrary()
