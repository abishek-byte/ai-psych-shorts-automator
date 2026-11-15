"""Groq LLM client (free tier: 14,400 req/day)."""
import os
import json
from typing import Optional
from groq import Groq
from src.config import CONFIG

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or CONFIG.groq_api_key
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set. Add to GitHub Secrets.")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-70b-versatile"

    def generate(self, system: str, user: str, temperature: float = 0.7, max_tokens: int = 1500) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content