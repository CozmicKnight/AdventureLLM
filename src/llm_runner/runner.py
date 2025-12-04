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
        if not candidate:
            continue

        candidate = candidate.lower().strip(" .!?")

        # Avoid obvious refusals or meta responses.
        blacklist = {"i can't", "cannot", "sorry", "i'm an ai", "as an ai"}
        if any(candidate.startswith(bad) for bad in blacklist):
            continue

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
        print(f"No API Key")
        exit()
        return LLMGeneration(action="look", tokens_prompt=None, tokens_completion=None)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        if (model_name.upper().find("GPT-5") > -1):
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=1,
                max_completion_tokens=10000,
            )
        else:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=10000,
            )

        content = response.choices[0].message.content if response.choices else ""
        action = _clean_action(content or "")
        usage = response.usage
        return LLMGeneration(
            action=action,
            tokens_prompt=getattr(usage, "prompt_tokens", None),
            tokens_completion=getattr(usage, "completion_tokens", None),
        )
    except Exception as e:
        # Keep the loop alive in environments without network access.
        print(type(e))
        print(e)
        exit()
        return LLMGeneration(action="look", tokens_prompt=None, tokens_completion=None)
