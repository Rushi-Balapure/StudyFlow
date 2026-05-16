from __future__ import annotations
 
from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    model_provider: str
    model_name: str
    base_url: str
    api_key: str | None
    app_env: str

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        model_provider=os.getenv("MODEL_PROVIDER", "openai_compatible"),
        model_name=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        base_url=os.getenv("MODEL_BASE_URL", "http://localhost:1234/v1"),
        api_key=os.getenv("MODEL_API_KEY"),
        app_env=os.getenv("APP_ENV", "dev"),
    )
