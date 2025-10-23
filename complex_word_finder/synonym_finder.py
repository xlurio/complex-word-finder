"""Synonym finding utilities for Brazilian Portuguese words."""

import asyncio
import aiohttp
from typing import List
from bs4 import BeautifulSoup
import re


class SynonymFinder:
    """Finds synonyms for Portuguese words using online resources with async support."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.delay = 1.0  # Delay between requests to be respectful
        self._semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
        self._analyzer = None  # Lazy-loaded WordAnalyzer for syllable counting
    
    async def find_synonyms(self, word: str, max_synonyms: int = 5) -> List[str]:
        """
        Find synonyms for a given Portuguese word using async requests.
        
        Args:
            word: The word to find synonyms for
            max_synonyms: Maximum number of synonyms to return
            
        Returns:
            List of synonyms
        """
        # Create async session and run concurrent requests
        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            # Define synonym sources as coroutines
            tasks = [
                self._get_synonyms_from_sinonimos_online(session, word),
                self._get_synonyms_from_dicio(session, word)
            ]
            
            # Run all tasks concurrently and collect results
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Flatten successful results
            all_synonyms = []
            for result in results:
                if isinstance(result, list):
                    all_synonyms.extend(result)
        
        # Filter and deduplicate
        return self._filter_and_deduplicate(all_synonyms, word, max_synonyms)
    
    def find_synonyms_sync(self, word: str, max_synonyms: int = 5) -> List[str]:
        """
        Synchronous wrapper for finding synonyms.
        
        Args:
            word: The word to find synonyms for
            max_synonyms: Maximum number of synonyms to return
            
        Returns:
            List of synonyms
        """
        return asyncio.run(self.find_synonyms(word, max_synonyms))
    
    async def find_synonyms_batch(self, words: List[str], max_synonyms: int = 5) -> dict[str, List[str]]:
        """
        Find synonyms for multiple words concurrently using a single session.
        
        Args:
            words: List of words to find synonyms for
            max_synonyms: Maximum synonyms per word
            
        Returns:
            Dictionary mapping words to their synonyms
        """
        # Use a single session for all requests to be more efficient
        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            # Create semaphore-limited tasks for batch processing
            semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
            
            async def process_word(word: str) -> tuple[str, List[str]]:
                async with semaphore:
                    await asyncio.sleep(self.delay)  # Rate limiting
                    synonyms = await self._find_synonyms_for_word(session, word, max_synonyms)
                    return word, synonyms
            
            # Execute all tasks concurrently
            tasks = [process_word(word) for word in words]
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert to dictionary, handling exceptions
            results = {}
            for result in results_list:
                if isinstance(result, tuple):
                    word, synonyms = result
                    results[word] = synonyms
                else:
                    # Handle exceptions by assigning empty list to failed words
                    # We don't have the word name here, so we'll assign later
                    pass
            
            # Ensure all words have entries, even if failed
            for word in words:
                if word not in results:
                    results[word] = []
        
        return results
    
    async def _find_synonyms_for_word(self, session: aiohttp.ClientSession, word: str, max_synonyms: int) -> List[str]:
        """Find synonyms for a single word using the provided session."""
        # Define synonym sources as coroutines using the shared session
        tasks = [
            self._get_synonyms_from_sinonimos_online(session, word),
            self._get_synonyms_from_dicio(session, word)
        ]
        
        # Run all tasks concurrently and collect results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten successful results
        all_synonyms = []
        for result in results:
            if isinstance(result, list):
                all_synonyms.extend(result)
        
        # Filter and deduplicate
        return self._filter_and_deduplicate(all_synonyms, word, max_synonyms)
    
    def _filter_and_deduplicate(self, synonyms: List[str], original_word: str, max_count: int) -> List[str]:
        """Filter synonyms and remove duplicates, keeping only simpler words."""
        if self._analyzer is None:
            from .word_analyzer import WordAnalyzer  # Import here to avoid circular imports
            self._analyzer = WordAnalyzer()
        
        word_lower = original_word.lower()
        original_syllables = self._analyzer.count_syllables(original_word)
        
        seen = set()
        unique_synonyms = []
        
        for synonym in synonyms:
            clean_synonym = synonym.lower().strip()
            
            # Check basic conditions first
            if (clean_synonym == word_lower or 
                clean_synonym in seen or 
                len(clean_synonym) <= 2):
                continue
            
            # Count syllables and only keep if fewer than original
            synonym_syllables = self._analyzer.count_syllables(clean_synonym)
            if synonym_syllables < original_syllables:
                unique_synonyms.append(synonym)
                seen.add(clean_synonym)
        
        return unique_synonyms[:max_count]
    
    async def _get_synonyms_from_sinonimos_online(self, session: aiohttp.ClientSession, word: str) -> List[str]:
        """
        Get synonyms from sinonimos.com.br using async requests.
        
        Args:
            session: Async HTTP session
            word: The word to search for
            
        Returns:
            List of synonyms found
        """
        url = f"https://www.sinonimos.com.br/{word}/"
        
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.read()
            
            soup = BeautifulSoup(content, 'html.parser')
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
    
    async def _get_synonyms_from_dicio(self, session: aiohttp.ClientSession, word: str) -> List[str]:
        """
        Get synonyms from dicio.com.br using async requests.
        
        Args:
            session: Async HTTP session
            word: The word to search for
            
        Returns:
            List of synonyms found
        """
        url = f"https://www.dicio.com.br/{word}/"
        
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.read()
            
            soup = BeautifulSoup(content, 'html.parser')
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
    
