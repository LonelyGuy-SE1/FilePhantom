import json
from typing import List, Tuple
from models import IndexedFile, SearchResult
from parallax_client import ParallaxClient
import config

class SearchEngine:
    def __init__(self):
        self.parallax_client = ParallaxClient()

    def search_parallax(self, query: str, files: List[IndexedFile], max_results: int = 20) -> Tuple[List[SearchResult], str]:
        if not files:
            return [], "No files indexed."

        candidate_text = ""
        for f in files:
            preview = f.preview.replace('\n', ' ')[:config.PREVIEW_CHARS]
            candidate_text += f"ID: {f.path}\nName: {f.name}\nPreview: {preview}\n\n"

        user_content = (
            f"QUERY: {query}\n\n"
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
