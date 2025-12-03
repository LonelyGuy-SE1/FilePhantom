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
        """Return the top_k documents most similar to the query using TF-IDF."""
        if not documents:
            return []

        # Prepare corpus: query + document snippets (path + first 1000 chars)
        doc_texts = [f"{d.path}\n{d.content[:1000]}" for d in documents]
        
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([query] + doc_texts)
        except ValueError:
            # Handle case where vocabulary is empty or other vectorizer errors
            return []

        # Compute cosine similarity between the query and documents
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Sort document indices by similarity (highest first)
        related_docs_indices = cosine_similarities.argsort()[::-1]
        
        top_docs = []
        for i in related_docs_indices[:top_k]:
            if cosine_similarities[i] > 0: # Only return documents with some relevance
                top_docs.append(documents[i])
        
        # If none matched strongly, return an empty list
        if not top_docs:
            return []

        return top_docs

    def ai_search_full(self, query: str, files: List[IndexedFile], max_results: int = 20) -> Tuple[List[SearchResult], str]:
        """Run a full model-based search over all files in batches."""
        if not files:
            return [], "No files to search."
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time
        
        batch_size = 300  # Files per batch
        batches = [files[i:i + batch_size] for i in range(0, len(files), batch_size)]
        
        print(f"[SearchEngine] Full search: {len(files)} files split into {len(batches)} batches")
        
        all_results = []
        
        # Process batches in parallel with retry handling
        def process_batch(batch_data):
            batch_idx, batch = batch_data
            max_retries = 2
            retry_delay = 1  # Start with 1 second
            
            for attempt in range(max_retries + 1):
                try:
                    print(f"[SearchEngine] Processing batch {batch_idx + 1}/{len(batches)}" + 
                          (f" (attempt {attempt + 1})" if attempt > 0 else ""))
                    
                    batch_results, _ = self._run_parallax_search(
                        query, batch, max_results, 
                        mode_description=f"full_batch_{batch_idx + 1}"
                    )
                    return batch_results
                    
                except Exception as e:
                    if attempt < max_retries:
                        print(f"[SearchEngine] Batch {batch_idx + 1} failed (attempt {attempt + 1}): {e}. Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        print(f"[SearchEngine] Batch {batch_idx + 1} failed after {max_retries + 1} attempts: {e}")
                        return []
        
        # Use ThreadPoolExecutor for parallel processing (max 3 concurrent requests)
        max_workers = min(3, len(batches))  # Limit concurrent requests to avoid overwhelming API
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all batch jobs
            future_to_batch = {
                executor.submit(process_batch, (idx, batch)): idx 
                for idx, batch in enumerate(batches)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_batch):
                try:
                    batch_results = future.result()
                    if batch_results:
                        all_results.extend(batch_results)
                except Exception as e:
                    batch_idx = future_to_batch[future]
                    print(f"[SearchEngine] Batch {batch_idx + 1} failed: {e}")
        
        # Sort results by score (highest first) and limit to max_results
        all_results.sort(key=lambda x: x.score, reverse=True)
        final_results = all_results[:max_results]
        
        # Simple summary of the search outcome
        if final_results:
            reasoning = f"Searched {len(files)} files and found {len(final_results)} highly relevant matches for your query."
        else:
            reasoning = f"Searched {len(files)} files but found no relevant matches for your query."
        
        return final_results, reasoning

    def ai_search_hybrid(self, query: str, files: List[IndexedFile], top_k: int = 100, max_results: int = 20) -> Tuple[List[SearchResult], str]:
        """Run semantic search first, then refine with the model on top candidates."""
        # 1) Run semantic search
        candidate_docs = self.semantic_search(query, files, top_k=top_k)
        
        # If semantic search returns nothing (e.g. empty index), handle gracefully
        if not candidate_docs:
             return [], "No relevant files found by semantic search."

        # 2) Call parallax with candidates
        return self._run_parallax_search(query, candidate_docs, max_results, mode_description="hybrid")

    def _run_parallax_search(self, query: str, files: List[IndexedFile], max_results: int, mode_description: str) -> Tuple[List[SearchResult], str]:
        """Build the prompt, call Parallax, and parse the JSON response."""
        if not files:
            return [], "No files to search."

        candidate_text = ""
        for f in files:
            preview = f.preview.replace('\n', ' ')[:config.PREVIEW_CHARS]
            candidate_text += f"ID: {f.path}\nName: {f.name}\nPreview: {preview}\n\n"

        # Short note to include in the prompt depending on mode
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
        
        print(f"[SearchEngine] {mode_description} search: {len(files)} files, message size: {len(user_content)} chars")

        messages = [
            {"role": "system", "content": config.PARALLAX_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        try:
            content = self.parallax_client.get_completion(messages)
        except Exception as e:
            print(f"[SearchEngine] API call failed: {e}")
            return [], str(e)

        try:
            # Strip code fences if the response includes them
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

        except json.JSONDecodeError as e:
            print(f"[SearchEngine] JSON parsing error: {e}")
            print(f"[SearchEngine] Raw response (first 500 chars): {content[:500]}")
            return [], f"Failed to parse response. Preview: {content[:200]}..."
        except Exception as e:
            print(f"[SearchEngine] Processing error: {e}")
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
