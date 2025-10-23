"""Word analysis utilities for syllable counting in Brazilian Portuguese."""

import re
from typing import List
import pyphen


class WordAnalyzer:
    """Analyzes words for syllable counting, specifically tuned for Brazilian Portuguese."""
    
    def __init__(self):
        # Initialize Pyphen with Portuguese hyphenation
        try:
            self.hyphenator = pyphen.Pyphen(lang='pt_BR')
        except KeyError:
            # Fallback to Portuguese if Brazilian Portuguese is not available
            try:
                self.hyphenator = pyphen.Pyphen(lang='pt')
            except KeyError:
                # Last fallback to English
                self.hyphenator = pyphen.Pyphen(lang='en')
    
    def count_syllables(self, word: str) -> int:
        """
        Count syllables in a Portuguese word.
        
        Uses a combination of hyphenation and Portuguese-specific rules.
        
        Args:
            word: The word to analyze
            
        Returns:
            Number of syllables in the word
        """
        if not word:
            return 0
        
        word = word.lower().strip()
        
        # Try hyphenation first
        hyphenated = self.hyphenator.inserted(word)
        if '-' in hyphenated:
            return len(hyphenated.split('-'))
        
        # Fallback to rule-based counting for Portuguese
        return self._count_syllables_by_rules(word)
    
    def _count_syllables_by_rules(self, word: str) -> int:
        """
        Count syllables using Portuguese phonetic rules.
        
        Args:
            word: The word to analyze
            
        Returns:
            Number of syllables
        """
        # Preprocess word - remove confusing prefixes and suffixes
        cleaned_word = self._clean_word_for_counting(word)
        
        # Count base vowel groups
        vowel_groups = self._extract_vowel_groups(cleaned_word)
        base_count = len(vowel_groups)
        
        # Apply Portuguese-specific adjustments
        diphthong_adjustment = self._count_diphthong_reductions(vowel_groups)
        hiatus_adjustment = self._count_hiatus_additions(cleaned_word)
        
        final_count = base_count - diphthong_adjustment + hiatus_adjustment
        
        return max(1, final_count)
    
    def _clean_word_for_counting(self, word: str) -> str:
        """Remove prefixes and suffixes that complicate syllable counting."""
        prefixes = r'^(des|dis|re|pre|pro|anti|super)'
        suffixes = r'(mente|ção|são|dade|idade)$'
        
        word = re.sub(prefixes, '', word)
        word = re.sub(suffixes, '', word)
        
        return word
    
    def _extract_vowel_groups(self, word: str) -> List[str]:
        """Extract vowel groups from the word."""
        vowels = 'aeiouáéíóúàèìòùâêîôûãõy'
        return re.findall(r'[' + vowels + ']+', word)
    
    def _count_diphthong_reductions(self, vowel_groups: List[str]) -> int:
        """Count how many syllables to reduce due to diphthongs."""
        diphthongs = {'ai', 'au', 'ei', 'eu', 'oi', 'ou', 'ui', 'ão', 'õe'}
        
        reduction_count = 0
        for group in vowel_groups:
            for diphthong in diphthongs:
                reduction_count += group.count(diphthong)
        
        return reduction_count
    
    def _count_hiatus_additions(self, word: str) -> int:
        """Count additional syllables due to hiatus patterns."""
        hiatus_patterns = {'ia', 'ie', 'io', 'ua', 'ue', 'uo'}
        
        addition_count = 0
        for pattern in hiatus_patterns:
            addition_count += word.count(pattern)
        
        return addition_count
    
    def get_syllable_breakdown(self, word: str) -> List[str]:
        """
        Get the syllable breakdown of a word.
        
        Args:
            word: The word to analyze
            
        Returns:
            List of syllables
        """
        if not word:
            return []
        
        word = word.lower().strip()
        hyphenated = self.hyphenator.inserted(word)
        
        if '-' in hyphenated:
            return hyphenated.split('-')
        else:
            # If no hyphenation found, return the whole word as one syllable
            return [word]
    
    def is_polysyllabic(self, word: str, min_syllables: int = 3) -> bool:
        """
        Check if a word is polysyllabic (has multiple syllables).
        
        Args:
            word: The word to check
            min_syllables: Minimum number of syllables to consider polysyllabic
            
        Returns:
            True if the word has at least min_syllables syllables
        """
        return self.count_syllables(word) >= min_syllables
    
    def analyze_word_complexity(self, word: str) -> dict:
        """
        Provide a complete analysis of a word's complexity.
        
        Args:
            word: The word to analyze
            
        Returns:
            Dictionary with syllable count, breakdown, and complexity metrics
        """
        syllables = self.get_syllable_breakdown(word)
        syllable_count = len(syllables)
        
        return {
            'word': word,
            'syllable_count': syllable_count,
            'syllables': syllables,
            'is_polysyllabic': syllable_count >= 3,
            'complexity_score': self._calculate_complexity_score(word, syllables)
        }
    
    def _calculate_complexity_score(self, word: str, syllables: List[str]) -> float:
        """
        Calculate a complexity score for the word based on various factors.
        
        Args:
            word: The original word
            syllables: List of syllables
            
        Returns:
            Complexity score (higher = more complex)
        """
        word_lower = word.lower()
        
        # Base score components
        syllable_score = len(syllables) * 1.0
        length_score = len(word) * 0.1
        
        # Consonant cluster score
        consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxz]{2,}', word_lower)
        cluster_score = len(consonant_clusters) * 0.5
        
        # Rare letter score (vectorized count)
        rare_letters = 'xzwky'
        rare_score = sum(word_lower.count(letter) for letter in rare_letters) * 0.3
        
        total_score = syllable_score + length_score + cluster_score + rare_score
        
        return round(total_score, 2)