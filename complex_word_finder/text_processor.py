"""Text processing utilities for Brazilian Portuguese."""

import re
from typing import List
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


class TextProcessor:
    """Handles text cleaning and word extraction for Brazilian Portuguese."""
    
    def __init__(self):
        self._download_nltk_data()
        self.portuguese_stopwords = set(stopwords.words('portuguese'))
    
    def _download_nltk_data(self):
        """Download required NLTK data."""
        required_data = [
            ('tokenizers/punkt_tab', 'punkt_tab'),
            ('tokenizers/punkt', 'punkt'),
            ('corpora/stopwords', 'stopwords')
        ]
        
        for resource_path, download_name in required_data:
            self._ensure_nltk_resource(resource_path, download_name)
    
    def _ensure_nltk_resource(self, resource_path: str, download_name: str):
        """Ensure a specific NLTK resource is available."""
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(download_name, quiet=True)
    
    def extract_words(self, text: str) -> List[str]:
        """
        Extract words from text, filtering out stopwords and non-alphabetic tokens.
        
        Args:
            text: Input text to process
            
        Returns:
            List of cleaned words
        """
        # Tokenize and clean
        tokens = word_tokenize(text.lower(), language='portuguese')

        # Filter and clean tokens in one pass
        result = []
        for token in tokens:
            if not token:
                continue
            # Handle enclitic pronouns (e.g., "diga-me" -> "diga") before cleaning
            stripped = self._strip_enclitic(token)
            clean = self._clean_token(stripped)
            if self._is_valid_word(clean):
                result.append(clean)

        return result
    
    def _clean_token(self, token: str) -> str:
        """Remove punctuation from token."""
        # Remove punctuation (keep letters only)
        return re.sub(r'[^\w]', '', token)
    
    def _is_valid_word(self, token: str) -> bool:
        """Check if token represents a valid word."""
        if not token:
            return False

        # token here is expected to be already cleaned (no punctuation)
        clean_token = token
        return (
            bool(clean_token) and
            clean_token.isalpha() and
            len(clean_token) >= 3 and
            clean_token not in self.portuguese_stopwords
        )

    def _strip_enclitic(self, token: str) -> str:
        """Remove enclitic pronouns from a token if present.

        Examples:
            'diga-me' -> 'diga'
            'diga.me' -> 'diga' (punctuation variants)
            'dizme' -> 'diz' (best-effort for missing hyphen)
        """
        if not token:
            return token

        # Common Portuguese clitic pronouns (including contracted forms)
        clitics_hyphen = {
            'me', 'te', 'se', 'o', 'a', 'nos', 'vos', 'lhe', 'lhes',
            'lo', 'la', 'los', 'las'
        }

        # If token contains a hyphen (most common for enclisis), check suffix
        if '-' in token:
            prefix, suffix = token.rsplit('-', 1)
            if suffix.lower() in clitics_hyphen and len(prefix) >= 3:
                return prefix
            # if not a clitic, return original token
            return token

        return token
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and normalizing characters.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Normalize common Portuguese characters
        replacements = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
            'é': 'e', 'ê': 'e',
            'í': 'i',
            'ó': 'o', 'ô': 'o', 'õ': 'o',
            'ú': 'u', 'ü': 'u',
            'ç': 'c'
        }
        
        for accented, normal in replacements.items():
            text = text.replace(accented, normal)
        
        return text
    
    def get_word_frequency(self, words: List[str]) -> dict:
        """
        Calculate word frequency from a list of words.
        
        Args:
            words: List of words
            
        Returns:
            Dictionary with word frequencies
        """
        frequency = {}
        for word in words:
            frequency[word] = frequency.get(word, 0) + 1
        
        return frequency