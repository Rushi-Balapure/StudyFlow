from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Protocol

from openai import OpenAI


class LLMProvider(Protocol):
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        ...


@dataclass
class OpenAICompatibleProvider:
    model_name: str
    base_url: str
    api_key: str | None = None

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        client = OpenAI(base_url=self.base_url, api_key=self.api_key or "not-required")
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content
        return (content or "").strip()


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}

    candidate = stripped[start : end + 1]
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}
