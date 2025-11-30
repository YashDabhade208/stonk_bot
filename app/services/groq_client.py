from groq import Groq
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class GroqClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables")

        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)

        # Default model for analysis
        self.default_model = "openai/gpt-oss-20b"

    def run_llm(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> str:
        """Send a prompt to Groq LLM and return text output."""
        selected_model = model or self.default_model

        try:
            completion = self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=1,
                reasoning_effort="medium",
                stream=False   # no streaming for API responses
            )

            return completion.choices[0].message.content

        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            raise

# Singleton client instance
groq_client = GroqClient()
