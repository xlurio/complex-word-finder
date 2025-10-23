"""Data models for the Complex Word Finder application."""

from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum


class OutputFormat(Enum):
    """Supported output formats."""
    TABLE = "table"
    JSON = "json"
    CSV = "csv"


@dataclass
class WordData:
    """Data structure for word analysis results."""
    syllables: int
    count: int
    synonyms: List[str]

    def __post_init__(self):
        """Ensure synonyms is always a list."""
        if self.synonyms is None:
            self.synonyms = []


@dataclass
class AnalysisConfig:
    """Configuration for word analysis."""
    min_syllables: int = 3
    max_synonyms: int = 5
    limit: int = None
    offset: int = 0
    find_synonyms: bool = True
    output_format: OutputFormat = OutputFormat.TABLE


@dataclass
class AnalysisResults:
    """Complete analysis results."""
    word_data: Dict[str, WordData]
    total_words: int
    polysyllabic_words: int
    total_occurrences: int
    config: AnalysisConfig

    @property
    def sorted_words(self) -> List[Tuple[str, WordData]]:
        """Get words sorted by syllables and frequency with offset and limit."""
        items = list(self.word_data.items())
        
        # Sort by: 1) syllables (desc), 2) count (desc), 3) word alphabetically (asc) for consistency
        sorted_items = sorted(
            items, 
            key=lambda x: (-x[1].syllables, -x[1].count, x[0])
        )
        
        # Apply offset first, then limit
        start_idx = self.config.offset
        end_idx = None
        
        if self.config.limit:
            end_idx = start_idx + self.config.limit
        
        return sorted_items[start_idx:end_idx]