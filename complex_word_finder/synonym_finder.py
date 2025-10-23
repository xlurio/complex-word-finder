"""Synonym finding utilities for Brazilian Portuguese words."""

import requests
import time
from typing import List
from bs4 import BeautifulSoup
import re


class SynonymFinder:
    """Finds synonyms for Portuguese words using online resources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.delay = 1.0  # Delay between requests to be respectful
        self._last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        self._last_request_time = time.time()
    
    def find_synonyms(self, word: str, max_synonyms: int = 5) -> List[str]:
        """
        Find synonyms for a given Portuguese word.
        
        Args:
            word: The word to find synonyms for
            max_synonyms: Maximum number of synonyms to return
            
        Returns:
            List of synonyms
        """
        # Define synonym sources
        sources = [
            self._get_synonyms_from_sinonimos_online,
            self._get_synonyms_from_dicio
        ]
        
        # Collect synonyms from all sources
        all_synonyms = []
        for source in sources:
            try:
                all_synonyms.extend(source(word))
            except Exception:
                continue  # Skip failed sources silently
        
        # Filter and deduplicate
        return self._filter_and_deduplicate(all_synonyms, word, max_synonyms)
    
    def _filter_and_deduplicate(self, synonyms: List[str], original_word: str, max_count: int) -> List[str]:
        """Filter synonyms and remove duplicates."""
        word_lower = original_word.lower()
        seen = set()
        unique_synonyms = []
        
        for synonym in synonyms:
            clean_synonym = synonym.lower().strip()
            
            if (clean_synonym != word_lower and 
                clean_synonym not in seen and 
                len(clean_synonym) > 2):
                unique_synonyms.append(synonym)
                seen.add(clean_synonym)
        
        return unique_synonyms[:max_count]
    
    def _get_synonyms_from_sinonimos_online(self, word: str) -> List[str]:
        """
        Get synonyms from sinonimos.com.br
        
        Args:
            word: The word to search for
            
        Returns:
            List of synonyms found
        """
        self._rate_limit()
        
        url = f"https://www.sinonimos.com.br/{word}/"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            synonyms = []
            
            # Look for synonym lists in various elements
            synonym_elements = soup.find_all(['a', 'span'], class_=re.compile(r'sinonimo|synonym'))
            
            for element in synonym_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 2 and text.isalpha():
                    synonyms.append(text)
            
            # If no specific synonym elements found, look for links that might be synonyms
            if not synonyms:
                links = soup.find_all('a', href=re.compile(r'/\w+/$'))
                for link in links:
                    text = link.get_text(strip=True)
                    if text and len(text) > 2 and text.isalpha():
                        synonyms.append(text)
            
            return synonyms[:10]  # Limit to avoid too many results
            
        except Exception:
            return []
    
    def _get_synonyms_from_dicio(self, word: str) -> List[str]:
        """
        Get synonyms from dicio.com.br
        
        Args:
            word: The word to search for
            
        Returns:
            List of synonyms found
        """
        self._rate_limit()
        
        url = f"https://www.dicio.com.br/{word}/"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            synonyms = []
            
            # Look for synonym sections
            synonym_sections = soup.find_all(['div', 'p'], class_=re.compile(r'sinonimo|synonym'))
            
            for section in synonym_sections:
                # Extract text and split by common separators
                text = section.get_text()
                words = re.split(r'[,;]', text)
                
                for word_candidate in words:
                    clean_word = re.sub(r'[^a-záéíóúàèìòùâêîôûãõç]', '', word_candidate.strip().lower())
                    if len(clean_word) > 2:
                        synonyms.append(clean_word)
            
            return synonyms[:10]
            
        except Exception:
            return []
    
    def _get_synonyms_from_local_dict(self, word: str) -> List[str]:
        """
        Get synonyms from a local dictionary/mapping.
        This is a fallback method with some common Portuguese synonyms.
        
        Args:
            word: The word to search for
            
        Returns:
            List of synonyms from local dictionary
        """
        # A small local dictionary of common synonyms
        local_synonyms = {
            'grande': ['enorme', 'gigante', 'imenso', 'colossal'],
            'pequeno': ['diminuto', 'minúsculo', 'reduzido', 'mínimo'],
            'bonito': ['belo', 'formoso', 'atraente', 'gracioso'],
            'importante': ['relevante', 'significativo', 'fundamental', 'essencial'],
            'difícil': ['complexo', 'complicado', 'árduo', 'trabalhoso'],
            'rápido': ['veloz', 'acelerado', 'ligeiro', 'célere'],
            'inteligente': ['esperto', 'sagaz', 'perspicaz', 'astuto'],
            'feliz': ['alegre', 'contente', 'satisfeito', 'jubiloso'],
            'triste': ['melancólico', 'deprimido', 'abatido', 'desanimado'],
            'trabalhar': ['laborar', 'executar', 'desempenhar', 'realizar']
        }
        
        return local_synonyms.get(word.lower(), [])
    
    def batch_find_synonyms(self, words: List[str], max_synonyms: int = 5) -> dict:
        """
        Find synonyms for multiple words in batch.
        
        Args:
            words: List of words to find synonyms for
            max_synonyms: Maximum synonyms per word
            
        Returns:
            Dictionary mapping words to their synonyms
        """
        results = {}
        
        for i, word in enumerate(words):
            try:
                synonyms = self.find_synonyms(word, max_synonyms)
                results[word] = synonyms
                
                # Add a longer delay every 10 requests to be extra respectful
                if (i + 1) % 10 == 0:
                    time.sleep(2.0)
                    
            except Exception:
                results[word] = []
        
        return results