"""
search_engine.py
Handles ranking and searching of indexed files.
"""

from typing import List, Tuple
from models import IndexedFile, SearchResult
from parallax_client import ParallaxClient
import config

class SearchEngine:
    def __init__(self):
        self.parallax_client = ParallaxClient()

    def search_parallax(self, query: str, files: List[IndexedFile], max_results: int = 20) -> Tuple[List[SearchResult], str]:
        """
        Uses Parallax to semantically rank files.
        Sends ALL indexed files to Parallax for re-ranking.
        """
        if not files:
            return [], "No files indexed."

        # 1. Prepare payload for Parallax (Use ALL files)
        # Note: In a real production app with thousands of files, we would need a vector DB or chunking.
        # For this hackathon/local tool, we send all candidates to the context window.
        candidates_payload = [{"id": f.path, "name": f.name, "preview": f.preview} for f in files]
        file_map = {f.path: f for f in files}
        
        # 2. Call Parallax
        ranked_dicts, reasoning = self.parallax_client.rank_files(query, candidates_payload)
        
        # 3. Convert back to SearchResult
        final_results = []
        score = 100.0
        
        for item in ranked_dicts:
            path = item.get('id')
            if path in file_map:
                final_results.append(SearchResult(file=file_map[path], score=score))
                score -= 1.0
                
        return final_results[:max_results], reasoning
