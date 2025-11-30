import json
from .groq_client import groq_client

class AIService:
    def analyze_news(self, article: dict) -> dict:
        prompt = f"""
You are a financial analysis AI. Read the news article below and return ONLY a valid JSON object.

JSON schema:
{{
    "summary": "Short 40-word summary of the article.",
    "sentiment": -1.0,  
    "impact": 1,
    "key_points": ["", "", ""]
}}

Rules:
- Output ONLY valid JSON.
- No explanations.
- No extra text.
- sentiment must be between -1 and 1.
- impact must be an integer 1–5.

Article:
TITLE: {article.get("title","")}
CONTENT: {article.get("content","")}
"""

        try:
            raw = groq_client.run_llm(prompt)
            cleaned = self._extract_json(raw)
            return cleaned

        except Exception as e:
            print(f"AI analysis error: {str(e)}")
            return self._default_response()

    def _extract_json(self, text: str) -> dict:
        """
        Attempts to extract a JSON object from model output 
        even if the model includes extra characters.
        """
        try:
            # Find the first "{" and last "}"
            start = text.find("{")
            end = text.rfind("}") + 1

            json_str = text[start:end]
            return json.loads(json_str)

        except Exception as e:
            print("JSON parse failed:", e)
            return self._default_response()

    def _default_response(self):
        return {
            "summary": "Analysis unavailable",
            "sentiment": 0.0,
            "impact": 3,
            "key_points": []
        }
