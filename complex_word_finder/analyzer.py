"""Main analyzer that orchestrates the word analysis process."""

from typing import List
from rich.progress import track
from rich.console import Console

from .models import WordData, AnalysisConfig, AnalysisResults
from .text_processor import TextProcessor
from .word_analyzer import WordAnalyzer
from .synonym_finder import SynonymFinder


class ComplexWordAnalyzer:
    """Main analyzer that coordinates all components."""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.text_processor = TextProcessor()
        self.word_analyzer = WordAnalyzer()
        self.synonym_finder = SynonymFinder()
    
    def analyze_text(self, text: str, config: AnalysisConfig) -> AnalysisResults:
        """
        Perform complete analysis of text for polysyllabic words.
        
        Args:
            text: Text content to analyze
            config: Analysis configuration
            
        Returns:
            Complete analysis results
        """
        # Extract words from text
        words = self._extract_words(text)
        
        # Analyze syllables and filter polysyllabic words
        word_data = self._analyze_syllables(words, config.min_syllables)
        
        if not word_data:
            return AnalysisResults(
                word_data={},
                total_words=len(words),
                polysyllabic_words=0,
                total_occurrences=0,
                config=config
            )
        
        # Find synonyms if requested
        if config.find_synonyms:
            self._add_synonyms(word_data, config)
        
        # Calculate totals
        total_occurrences = sum(data.count for data in word_data.values())
        
        return AnalysisResults(
            word_data=word_data,
            total_words=len(words),
            polysyllabic_words=len(word_data),
            total_occurrences=total_occurrences,
            config=config
        )
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract and clean words from text."""
        self.console.print("🔍 Extracting words from text...")
        words = self.text_processor.extract_words(text)
        self.console.print(f"Found [green]{len(words)}[/green] total words")
        return words
    
    def _analyze_syllables(self, words: List[str], min_syllables: int) -> dict[str, WordData]:
        """Analyze syllables and create word data for polysyllabic words."""
        self.console.print("📊 Analyzing syllable counts...")
        word_data = {}
        
        for word in track(words, description="Processing words..."):
            syllable_count = self.word_analyzer.count_syllables(word)
            
            if syllable_count >= min_syllables:
                if word not in word_data:
                    word_data[word] = WordData(
                        syllables=syllable_count,
                        count=0,
                        synonyms=[]
                    )
                word_data[word].count += 1
        
        return word_data
    
    def _add_synonyms(self, word_data: dict[str, WordData], config: AnalysisConfig):
        """Add synonyms to word data."""
        self.console.print("🔍 Finding synonyms...")
        
        # Get words to process (respecting limit for efficiency)
        words_to_process = list(word_data.keys())
        if config.limit:
            # Sort to get the most relevant words first
            sorted_items = sorted(
                word_data.items(), 
                key=lambda x: (-x[1].syllables, -x[1].count)
            )
            words_to_process = [word for word, _ in sorted_items[:config.limit]]
        
        for word in track(words_to_process, description="Finding synonyms..."):
            try:
                synonyms = self.synonym_finder.find_synonyms(word, config.max_synonyms)
                word_data[word].synonyms = synonyms
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not find synonyms for '{word}': {e}[/yellow]")
                word_data[word].synonyms = []