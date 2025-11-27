"""Utility for calling language models to generate the next Zork command."""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional


@dataclass
class LLMGeneration:
    action: str
    tokens_prompt: Optional[int] = None
    tokens_completion: Optional[int] = None


def _clean_action(text: str) -> str:
    """Extract the first non-empty line and strip wrappers."""
    for line in text.splitlines():
        candidate = line.strip().strip("`\"")
        if candidate:
            return candidate
    return "look"


def generate_action(model_name: str, prompt: str) -> LLMGeneration:
    """Call the configured LLM provider and return a cleaned command string.

    The OpenAI API key is read from ``OPENAI_API_KEY``. If the key is missing or
    the request fails, a simple fallback command is returned to keep the episode
    loop running during local development.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Offline fallback.
        return LLMGeneration(action="look", tokens_prompt=None, tokens_completion=None)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=32,
        )
        content = response.choices[0].message.content if response.choices else ""
        action = _clean_action(content or "")
        usage = response.usage
        return LLMGeneration(
            action=action,
            tokens_prompt=getattr(usage, "prompt_tokens", None),
            tokens_completion=getattr(usage, "completion_tokens", None),
        )
    except Exception:
        # Keep the loop alive in environments without network access.
        return LLMGeneration(action="look", tokens_prompt=None, tokens_completion=None)
