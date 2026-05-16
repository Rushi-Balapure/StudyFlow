from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

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
        return content or ""
