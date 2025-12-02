import json
from typing import List, Tuple
from models import IndexedFile, SearchResult
from parallax_client import ParallaxClient
import config
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SearchEngine:
    def __init__(self):
        self.parallax_client = ParallaxClient()

    def semantic_search(self, query: str, documents: List[IndexedFile], top_k: int = 100) -> List[IndexedFile]:
        """
        Returns a list of the top_k documents most relevant to the query,
        ordered from most to least relevant using TF-IDF and cosine similarity.
        """
        if not documents:
            return []

        # Prepare corpus: query + document contents
        # We'll use the file path and the first 1000 chars of content for the vectorization
        doc_texts = [f"{d.path}\n{d.content[:1000]}" for d in documents]
        
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([query] + doc_texts)
        except ValueError:
            # Handle case where vocabulary is empty or other vectorizer errors
            return []

        # Calculate cosine similarity between query (index 0) and all docs (indices 1..)
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Sort by similarity score descending
        # argsort returns indices that would sort the array, so we reverse it
        related_docs_indices = cosine_similarities.argsort()[::-1]
        
        top_docs = []
        for i in related_docs_indices[:top_k]:
            if cosine_similarities[i] > 0: # Only return documents with some relevance
                top_docs.append(documents[i])
        
        # If no documents had > 0 similarity, fallback to returning top_k or all
        if not top_docs and documents:
             # Fallback: just return the first top_k if nothing matched (unlikely with tf-idf unless query is gibberish)
             # But for strict semantic search, maybe empty is better. 
             # Let's return empty if really nothing matches, but the user requirement says "select top k".
             # If similarity is 0, they aren't really "top", but let's stick to the list.
             pass

        return top_docs

    def ai_search_full(self, query: str, files: List[IndexedFile], max_results: int = 20) -> Tuple[List[SearchResult], str]:
        """
        Existing behavior: sends all indexed files to the model.
        """
        return self._run_parallax_search(query, files, max_results, mode_description="full")

    def ai_search_hybrid(self, query: str, files: List[IndexedFile], top_k: int = 100, max_results: int = 20) -> Tuple[List[SearchResult], str]:
        """
        Hybrid behavior: runs semantic search first, then sends top_k files to the model.
        """
        # 1) Run semantic search
        candidate_docs = self.semantic_search(query, files, top_k=top_k)
        
        # If semantic search returns nothing (e.g. empty index), handle gracefully
        if not candidate_docs:
             return [], "No relevant files found by semantic search."

        # 2) Call parallax with candidates
        return self._run_parallax_search(query, candidate_docs, max_results, mode_description="hybrid")

    def _run_parallax_search(self, query: str, files: List[IndexedFile], max_results: int, mode_description: str) -> Tuple[List[SearchResult], str]:
        """
        Helper to build prompt and call Parallax.
        """
        if not files:
            return [], "No files to search."

        candidate_text = ""
        for f in files:
            preview = f.preview.replace('\n', ' ')[:config.PREVIEW_CHARS]
            candidate_text += f"ID: {f.path}\nName: {f.name}\nPreview: {preview}\n\n"

        # Optional: Customize prompt based on mode
        mode_note = ""
        if mode_description == "hybrid":
            mode_note = "You are seeing a subset of the most relevant files selected by a semantic search. Choose the best matching files from this subset."
        elif mode_description == "full":
            mode_note = "You are seeing all indexed files."

        user_content = (
            f"QUERY: {query}\n\n"
            f"CONTEXT: {mode_note}\n\n"
            f"CANDIDATES:\n{candidate_text}\n\n"
            "Please select the files that are most relevant to the query. "
            "Return the output as valid JSON."
        )

        messages = [
            {"role": "system", "content": config.PARALLAX_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        try:
            content = self.parallax_client.get_completion(messages)
        except Exception as e:
            return [], str(e)

        try:
            if content.startswith("```json"): 
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"): 
                content = content[:-3]
            
            parsed = json.loads(content.strip())
            ranked_ids = parsed.get("ranked", [])
            reasoning = parsed.get("reasoning", "No reasoning provided.")
            
            file_map = {f.path: f for f in files}
            final_results = []
            score = 100.0
            
            for rid in ranked_ids:
                if rid in file_map:
                    final_results.append(SearchResult(file=file_map[rid], score=score))
                    score -= 1.0
            
            return final_results[:max_results], reasoning

        except json.JSONDecodeError:
            return [], "Failed to parse AI response."
        except Exception as e:
            return [], f"Error processing results: {e}"

    def search(self, query: str, index, mode="hybrid") -> Tuple[List[SearchResult], str]:
        # index is passed from UI, which seems to be a list of files based on ui_main.py:195
        # "results, reasoning = self.search_engine.search_parallax(query, self.indexed_files)"
        # So 'index' here is actually 'files'.
        files = index 
        
        if mode == "full":
            return self.ai_search_full(query, files)
        elif mode == "hybrid":
            return self.ai_search_hybrid(query, files)
        else:
            raise ValueError(f"Unknown mode: {mode}")
