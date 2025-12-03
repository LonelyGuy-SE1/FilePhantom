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
        if not documents:
            return []

        doc_texts = [f"{d.path}\n{d.content[:1000]}" for d in documents]
        
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([query] + doc_texts)
        except ValueError:
            return []

        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        related_docs_indices = cosine_similarities.argsort()[::-1]
        
        top_docs = []
        for i in related_docs_indices[:top_k]:
            if cosine_similarities[i] > 0:
                top_docs.append(documents[i])
        
        if not top_docs:
            return []

        return top_docs

    def ai_search_full(self, query: str, files: List[IndexedFile], max_results: int = 20) -> Tuple[List[SearchResult], str]:
        if not files:
            return [], "No files to search."
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        batch_size = 300
        batches = [files[i:i + batch_size] for i in range(0, len(files), batch_size)]
        
        all_results = []
        
        def process_batch(batch_data):
            batch_idx, batch = batch_data
            max_retries = 2
            retry_delay = 1
            
            for attempt in range(max_retries + 1):
                try:
                    batch_results, _ = self._run_parallax_search(
                        query, batch, max_results, 
                        mode_description=f"full_batch_{batch_idx + 1}"
                    )
                    return batch_results
                    
                except Exception as e:
                    if attempt < max_retries:
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        return []
        
        max_workers = min(3, len(batches))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_batch = {
                executor.submit(process_batch, (idx, batch)): idx 
                for idx, batch in enumerate(batches)
            }
            
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
        candidate_docs = self.semantic_search(query, files, top_k=top_k)
        
        if not candidate_docs:
             return [], "No relevant files found by semantic search."

        return self._run_parallax_search(query, candidate_docs, max_results, mode_description="hybrid")

    def _run_parallax_search(self, query: str, files: List[IndexedFile], max_results: int, mode_description: str) -> Tuple[List[SearchResult], str]:
        if not files:
            return [], "No files to search."

        candidate_text = ""
        for f in files:
            preview = f.preview.replace('\n', ' ')[:config.PREVIEW_CHARS]
            candidate_text += f"ID: {f.path}\nName: {f.name}\nPreview: {preview}\n\n"

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

        except json.JSONDecodeError as e:
            return [], f"Failed to parse response."
        except Exception as e:
            return [], f"Error processing results: {e}"

    def search(self, query: str, index, mode="hybrid") -> Tuple[List[SearchResult], str]:
        files = index 
        
        if mode == "full":
            return self.ai_search_full(query, files)
        elif mode == "hybrid":
            return self.ai_search_hybrid(query, files)
        else:
            raise ValueError(f"Unknown mode: {mode}")
