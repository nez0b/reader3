import json
import os
from typing import Optional, Dict, Any

from openai import OpenAI, OpenAIError

from config import settings
from prompts import PROMPTS

class LLMClient:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
        self.dry_run = settings.LLM_DRY_RUN
        
        if not self.dry_run and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def get_explanation(self, text: str, level: str, context: str = "") -> str:
        """
        Get an explanation for the given text at the specified JLPT level.
        """
        if self.dry_run:
            return self._get_dry_run_response(level)

        if not self.client:
            return "<p>Error: OpenAI API key not configured and Dry Run is disabled.</p>"

        system_prompt = PROMPTS.get(level, PROMPTS["N5"])
        user_prompt = f"Context: {context}\n\nText to analyze:\n{text}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            print(f"OpenAI API Error: {e}")
            return f"<p>Error communicating with LLM service: {str(e)}</p>"
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return f"<p>An unexpected error occurred: {str(e)}</p>"

    def _get_dry_run_response(self, level: str) -> str:
        return f"""
        <h3>[Dry Run] {level} Explanation</h3>
        <p>This is a simulated response for <strong>{level}</strong> level.</p>
        <ul>
            <li><strong>Summary:</strong> Lorem ipsum dolor sit amet, consectetur adipiscing elit.</li>
            <li><strong>Vocabulary:</strong>
                <ul>
                    <li>単語 (tango) - word</li>
                    <li>学習 (gakushuu) - learning</li>
                </ul>
            </li>
            <li><strong>Grammar:</strong> Explanation of a grammar point would go here.</li>
        </ul>
        <p>Real API calls are disabled.</p>
        """

    def get_cached_explanation(self, cache_path: str, key: str, text: str, level: str, context: str = "") -> str:
        """
        Wrapper to check cache before calling LLM.
        """
        cache = self._load_cache(cache_path)
        
        if key in cache:
            print(f"Cache hit for {key}")
            return cache[key]
        
        print(f"Cache miss for {key}, calling LLM...")
        content = self.get_explanation(text, level, context)
        
        # Only cache if it looks like a valid response (and not an error message we generated)
        # Simple check: if it starts with "Error", maybe don't cache? 
        # But our error messages are HTML <p>Error..., so checking if it contains "Error" might be too aggressive.
        # For now, we cache everything to avoid spamming API on repeated failures, 
        # OR we decide not to cache errors. Let's NOT cache errors.
        if "Error" not in content[:50]: # Simple heuristic
            cache[key] = content
            self._save_cache(cache_path, cache)
            
        return content

    def _load_cache(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache {path}: {e}")
            return {}

    def _save_cache(self, path: str, data: Dict[str, Any]):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache {path}: {e}")

llm_client = LLMClient()
