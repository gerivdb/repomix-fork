"""repomix — neuro-symbolic verse engine."""

__version__ = "0.1.0"

from repomix.verse_detector import UniversalVerseDetector, VERSE_DETECTOR, VerseStatus, VerseObservation
from repomix.verses_library import VersesLibrary, verses_library

__all__ = [
    "UniversalVerseDetector",
    "VERSE_DETECTOR",
    "VerseStatus",
    "VerseObservation",
    "VersesLibrary",
    "verses_library",
]
