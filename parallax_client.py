"""
parallax_client.py
Handles communication with the Parallax API.
"""

import requests
import json
import config
from typing import List, Dict, Tuple

class ParallaxClient:
    def __init__(self):
        self.api_url = config.PARALLAX_API_URL
        self.timeout = config.PARALLAX_TIMEOUT

    def rank_files(self, query: str, candidates: List[Dict]) -> Tuple[List[Dict], str]:
        """
        rank_files(query, candidates) -> (list[dict], str)
        
        Uses Parallax /v1/chat/completions to semantically re-order candidate files for the given query.
        Expects Parallax to return JSON: {"ranked": ["id1", ...], "reasoning": "..."} in the assistant message content.
        """
        if not candidates:
            return [], "No candidates to rank."

        # Prepare the candidate list for the prompt
        candidate_text = ""
        for i, cand in enumerate(candidates):
            # Sanitize preview to avoid breaking JSON or prompt structure too much
            preview = cand.get('preview', '').replace('\n', ' ')[:config.PREVIEW_CHARS]
            candidate_text += f"ID: {cand['id']}\nName: {cand['name']}\nPreview: {preview}\n\n"

        # Construct the user message
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

        # STRICT PARALLAX PAYLOAD: No 'model' field.
        payload = {
            "messages": messages,
            "temperature": 0.1, # Low temperature for deterministic results
            "max_tokens": 1024,
            "stream": False
        }

        try:
            response = requests.post(
                self.api_url, 
                headers={"Content-Type": "application/json"}, 
                json=payload, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()
            
            # Clean up potential markdown code blocks
            if content.startswith("```json"): 
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"): 
                content = content[:-3]
            
            parsed = json.loads(content.strip())
            ranked_ids = parsed.get("ranked", [])
            reasoning = parsed.get("reasoning", "No reasoning provided.")
            
            # Re-order candidates based on ranked_ids
            cand_map = {c['id']: c for c in candidates}
            ranked_results = []
            
            # Add ranked items first
            for rid in ranked_ids:
                if rid in cand_map:
                    ranked_results.append(cand_map[rid])
            
            return ranked_results, reasoning

        except requests.exceptions.RequestException as e:
            print(f"[ParallaxClient] Request Error: {e}")
            raise Exception(f"Connection failed: {e}")
        except json.JSONDecodeError as e:
            print(f"[ParallaxClient] JSON Error: {e}. Content: {content}")
            raise Exception("Invalid JSON response from Parallax.")
        except Exception as e:
            print(f"[ParallaxClient] Unexpected Error: {e}")
            raise e
