import os

from app.config import get_settings


def test_settings_reads_openrouter_configuration(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    )
    monkeypatch.setenv(
        "OPENROUTER_MODEL",
        "test-model",
    )

    get_settings.cache_clear()
    settings = get_settings()

    assert settings.openrouter_api_key == "test-api-key"
    assert settings.openrouter_base_url == "https://openrouter.ai/api/v1"
    assert settings.openrouter_model == "test-model"


def test_settings_does_not_use_fake_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    get_settings.cache_clear()
    settings = get_settings()

    assert settings.openrouter_api_key is None
