import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    app_host: str
    app_port: int

    mongodb_url: str
    mongodb_database: str

    openrouter_api_key: Optional[str]
    openrouter_base_url: str
    openrouter_model: Optional[str]


@lru_cache
def get_settings() -> Settings:
    app_port = int(os.getenv("APP_PORT", "8002"))

    return Settings(
        app_name=os.getenv("APP_NAME", "LeadVision_IA"),
        app_env=os.getenv("APP_ENV", "development"),
        app_host=os.getenv("APP_HOST", "127.0.0.1"),
        app_port=app_port,
        mongodb_url=os.getenv(
            "MONGODB_URL",
            "mongodb://localhost:27017",
        ),
        mongodb_database=os.getenv(
            "MONGODB_DATABASE",
            "leadvision_ia",
        ),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        openrouter_base_url=os.getenv(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        ),
        openrouter_model=os.getenv("OPENROUTER_MODEL"),
    )
