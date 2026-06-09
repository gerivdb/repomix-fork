"""
Backward compatibility shims.
Les fichiers originaux à la racine peuvent être supprimés après validation.
En attendant, ce module permet aux anciens imports de continuer à fonctionner.
"""

# verse_detector
from repomix.verse_detector import (  # noqa: F401
    UniversalVerseDetector,
    VERSE_DETECTOR,
    VerseStatus,
    VerseObservation,
)

# verses_library
from repomix.verses_library import VersesLibrary, verses_library  # noqa: F401

# engines
from repomix.engines.neuro_symbolic import (  # noqa: F401
    NeuroSymbolicVerseEngine,
    generate_with_neurosymbolic_engine,
    DEFAULT_CONFIG,
)
