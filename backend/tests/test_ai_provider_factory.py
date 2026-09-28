from unittest.mock import patch

from app.services.ai.openrouter_provider import OpenRouterProvider


def test_create_ai_provider_returns_openrouter_provider(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    from app.config import get_settings

    get_settings.cache_clear()

    with patch(
        "app.services.ai.ai_provider_factory.httpx.Client"
    ) as mock_client:

        from app.services.ai.ai_provider_factory import (
            create_ai_provider,
        )

        provider = create_ai_provider()

    assert isinstance(provider, OpenRouterProvider)
    mock_client.assert_called_once()


def test_create_ai_provider_passes_http_client_to_provider(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    from app.config import get_settings

    get_settings.cache_clear()

    fake_client = object()

    with patch(
        "app.services.ai.ai_provider_factory.httpx.Client",
        return_value=fake_client,
    ):
        with patch(
            "app.services.ai.ai_provider_factory.OpenRouterProvider"
        ) as mock_provider:

            from app.services.ai.ai_provider_factory import (
                create_ai_provider,
            )

            create_ai_provider()

    mock_provider.assert_called_once()
    call_kwargs = mock_provider.call_args.kwargs

    assert call_kwargs["http_client"] is fake_client

def test_create_ai_provider_closes_http_client_on_close(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    from app.config import get_settings

    get_settings.cache_clear()

    fake_client = object()

    with patch(
        "app.services.ai.ai_provider_factory.httpx.Client",
        return_value=fake_client,
    ):
        from app.services.ai.ai_provider_factory import create_ai_provider

        provider = create_ai_provider()

    assert provider.http_client is fake_client
def test_create_ai_provider_does_not_require_openrouter_configuration(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)

    from app.config import get_settings
    get_settings.cache_clear()

    from app.services.ai.ai_provider_factory import create_ai_provider

    provider = create_ai_provider()

    assert provider is not None
    assert hasattr(provider, "analyze")
