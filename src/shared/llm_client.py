"""Groq LLM client (free tier: 14,400 req/day) with model fallback."""
import os
import json
from typing import Optional
from groq import Groq
from src.config import CONFIG


class LLMClient:
    # Ordered list of models to try (most preferred first)
    # Updated for current Groq free tier (as of 2025)
    FALLBACK_MODELS = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.3-70b-instruct",
        "qwen-2.5-32b",
        "deepseek-r1-distill-llama-70b",
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or CONFIG.groq_api_key
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set. Add to GitHub Secrets.")
        self.client = Groq(api_key=self.api_key)
        self.model = self.FALLBACK_MODELS[0]

    def generate(self, system: str, user: str, temperature: float = 0.7, max_tokens: int = 1500) -> str:
        last_error = None

        for model in self.FALLBACK_MODELS:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"}
                )
                print(f"✓ Using model: {model}")
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                print(f"✗ Model {model} failed: {e}")
                continue

        # All models failed
        raise RuntimeError(f"All Groq models failed. Last error: {last_error}")