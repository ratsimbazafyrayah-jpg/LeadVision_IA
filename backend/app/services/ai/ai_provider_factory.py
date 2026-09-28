import httpx

from app.config import get_settings
from app.services.ai.openrouter_provider import OpenRouterProvider
from app.services.ai.unavailable_ai_provider import UnavailableAIProvider


def create_ai_provider():
    settings = get_settings()

    if (
        not settings.openrouter_api_key
        or not settings.openrouter_model
    ):
        return UnavailableAIProvider()

    http_client = httpx.Client(timeout=30)

    return OpenRouterProvider(
        http_client=http_client,
        timeout=30,
    )
