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

    def search_basic(self, query: str, files: List[IndexedFile]) -> List[IndexedFile]:
        """
        Performs a basic keyword search to find initial candidates.
        Returns files sorted by keyword match score.
        """
        if not query or not files:
            return []

        query_tokens = query.lower().split()
        scored_files = []

        for f in files:
            score = 0
            # Check filename
            if query.lower() in f.name.lower():
                score += 10
            
            # Check content tokens
            # This is a very naive implementation, but sufficient for "basic keyword scoring"
            for token in query_tokens:
                if token in f.tokens:
                    score += 1
            
            if score > 0:
                scored_files.append((score, f))

        # Sort by score descending
        scored_files.sort(key=lambda x: x[0], reverse=True)
        
        return [f for _, f in scored_files]

    def search_parallax(self, query: str, files: List[IndexedFile], max_results: int = 20) -> Tuple[List[SearchResult], str]:
        """
        Uses Parallax to semantically rank files.
        First filters using search_basic, then sends top candidates to Parallax.
        """
        if not files:
            return [], "No files indexed."

        # 1. Get initial candidates using basic search
        initial_candidates = self.search_basic(query, files)
        
        # If no keyword matches, we might want to return empty or try all?
        # Let's try top N of all files if no keyword matches? 
        # No, if no keywords match, it's likely not relevant. 
        # But for semantic search, sometimes keywords don't match.
        # However, sending ALL files to LLM is too expensive/slow if there are thousands.
        # Let's stick to initial_candidates. If empty, maybe take top 50 recent files?
        # For now, let's just use initial_candidates.
        
        if not initial_candidates:
             # Fallback: if no keyword matches, maybe the user is asking a conceptual question.
             # We could send a random sample or recent files, but let's just return empty for safety/speed.
             return [], "No keyword matches found to re-rank."

        # Limit to TOP_K_CANDIDATES
        top_candidates = initial_candidates[:config.TOP_K_CANDIDATES]

        # 2. Prepare payload for Parallax
        candidates_payload = [{"id": f.path, "name": f.name, "preview": f.preview} for f in top_candidates]
        file_map = {f.path: f for f in top_candidates}
        
        # 3. Call Parallax
        ranked_dicts, reasoning = self.parallax_client.rank_files(query, candidates_payload)
        
        # 4. Convert back to SearchResult
        final_results = []
        score = 100.0
        
        for item in ranked_dicts:
            path = item.get('id')
            if path in file_map:
                final_results.append(SearchResult(file=file_map[path], score=score))
                score -= 1.0
                
        # If Parallax failed or returned nothing, fall back to basic search results
        if not final_results:
             # If Parallax returned nothing (and didn't error out completely returning original list),
             # it might mean it filtered everything out.
             # But if parallax_client returns the original list on error, we are good.
             # If it returns empty list (meaning it thinks nothing matches), we respect that.
             pass

        return final_results[:max_results], reasoning
