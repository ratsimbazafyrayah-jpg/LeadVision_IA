import httpx

import pytest

from app.schemas.ai_analysis_input import AIAnalysisInput
from app.services.ai.openrouter_provider import OpenRouterProvider


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeHttpClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, headers=None, json=None, timeout=None):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return self.response


def build_input():
    return AIAnalysisInput(
        lead={
            "company_name": "Entreprise Test",
            "sector": "Technology",
            "country": "Madagascar",
            "city": "Antananarivo",
        },
        qualification={
            "status": "partially_qualified",
        },
        data_quality={
            "data_quality_score": 87.5,
        },
        commercial_signals={
            "status": "signals_available",
            "signal_count": 1,
            "signals": [
                {
                    "interaction_id": "interaction-001",
                    "signal_type": "form_submission",
                    "source": "website",
                    "occurred_at": "2026-09-25T21:33:43.151000",
                    "evidence": {
                        "source_system": "website",
                        "metadata": {
                            "form_id": "contact-form",
                        },
                    },
                    "validation_reason": "Valid form submission evidence.",
                    "confidence": None,
                }
            ],
            "ignored_interactions": [],
        },
        commercial_score={
            "commercial_score": 49.77,
            "status": "score_available",
            "confidence": None,
            "evidence": {},
            "calculation": {},
        },
        evidence_registry=[
            {
                "evidence_id": "commercial-signal:interaction-001",
                "evidence_type": "commercial_signal",
                "source": "website",
                "reference_id": "interaction-001",
                "description": "Valid form submission evidence.",
            }
        ],
    )


def valid_ai_payload():
    return {
        "status": "analysis_available",
        "summary": "Analyse basée sur les données disponibles.",
        "observations": [],
        "risks": [],
        "opportunities": [],
        "recommendations": [],
        "next_actions": [],
        "evidence": [],
        "model_metadata": {
            "provider": "openrouter",
        },
    }


def test_openrouter_provider_sends_expected_request(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    )
    monkeypatch.setenv(
        "OPENROUTER_MODEL",
        "test-model",
    )

    from app.config import get_settings

    get_settings.cache_clear()

    client = FakeHttpClient(
        FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": valid_ai_payload(),
                        }
                    }
                ]
            }
        )
    )

    provider = OpenRouterProvider(
        http_client=client,
        timeout=30,
    )

    result = provider.analyze(build_input())

    assert result["status"] == "analysis_available"

    assert len(client.calls) == 1

    request = client.calls[0]

    assert request["url"] == (
        "https://openrouter.ai/api/v1/chat/completions"
    )

    assert request["headers"]["Authorization"] == (
        "Bearer test-api-key"
    )

    assert request["headers"]["Content-Type"] == "application/json"

    assert request["json"]["model"] == "test-model"
    assert request["json"]["stream"] is False
    assert len(request["json"]["messages"]) >= 1


def test_openrouter_provider_accepts_json_string_content(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    from app.config import get_settings

    get_settings.cache_clear()

    import json

    client = FakeHttpClient(
        FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(valid_ai_payload()),
                        }
                    }
                ]
            }
        )
    )

    provider = OpenRouterProvider(
        http_client=client,
        timeout=30,
    )

    result = provider.analyze(build_input())

    assert result["status"] == "analysis_available"


def test_openrouter_provider_rejects_invalid_json_string_content(
    monkeypatch,
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    from app.config import get_settings

    get_settings.cache_clear()

    client = FakeHttpClient(
        FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": "{invalid-json",
                        }
                    }
                ]
            }
        )
    )

    provider = OpenRouterProvider(
        http_client=client,
        timeout=30,
    )

    with pytest.raises(
        RuntimeError,
        match="réponse du provider OpenRouter est invalide",
    ):
        provider.analyze(build_input())


def test_openrouter_provider_rejects_non_object_json_content(
    monkeypatch,
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    from app.config import get_settings

    get_settings.cache_clear()

    import json

    client = FakeHttpClient(
        FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(["invalid"]),
                        }
                    }
                ]
            }
        )
    )

    provider = OpenRouterProvider(
        http_client=client,
        timeout=30,
    )

    with pytest.raises(
        RuntimeError,
        match="réponse du provider OpenRouter est invalide",
    ):
        provider.analyze(build_input())



def test_openrouter_provider_converts_http_error_to_runtime_error(
    monkeypatch,
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    from app.config import get_settings

    get_settings.cache_clear()

    class HttpErrorResponse(FakeResponse):
        def raise_for_status(self):
            request = httpx.Request(
                "POST",
                "https://openrouter.ai/api/v1/chat/completions",
            )
            response = httpx.Response(
                500,
                request=request,
            )
            raise httpx.HTTPStatusError(
                "Server error",
                request=request,
                response=response,
            )

    client = FakeHttpClient(HttpErrorResponse({}))

    provider = OpenRouterProvider(
        http_client=client,
        timeout=30,
    )

    with pytest.raises(
        RuntimeError,
        match="erreur HTTP",
    ):
        provider.analyze(build_input())


def test_openrouter_provider_converts_network_error_to_runtime_error(
    monkeypatch,
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    from app.config import get_settings

    get_settings.cache_clear()

    class NetworkErrorClient:
        def post(
            self,
            url,
            headers=None,
            json=None,
            timeout=None,
        ):
            request = httpx.Request("POST", url)

            raise httpx.ConnectError(
                "Connection failed",
                request=request,
            )

    provider = OpenRouterProvider(
        http_client=NetworkErrorClient(),
        timeout=30,
    )

    with pytest.raises(
        RuntimeError,
        match="indisponible",
    ):
        provider.analyze(build_input())


def test_openrouter_provider_converts_invalid_response_to_runtime_error(
    monkeypatch,
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    from app.config import get_settings

    get_settings.cache_clear()

    client = FakeHttpClient(
        FakeResponse(
            {
                "invalid": "provider-response",
            }
        )
    )

    provider = OpenRouterProvider(
        http_client=client,
        timeout=30,
    )

    with pytest.raises(
        RuntimeError,
        match="réponse du provider OpenRouter est invalide",
    ):
        provider.analyze(build_input())


def test_openrouter_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv(
        "OPENROUTER_MODEL",
        "test-model",
    )

    from app.config import get_settings

    get_settings.cache_clear()

    client = FakeHttpClient(FakeResponse({}))

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        OpenRouterProvider(
            http_client=client,
            timeout=30,
        )


def test_openrouter_provider_requires_model(monkeypatch):
    monkeypatch.setenv(
        "OPENROUTER_API_KEY",
        "test-api-key",
    )
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)

    from app.config import get_settings

    get_settings.cache_clear()

    client = FakeHttpClient(FakeResponse({}))

    with pytest.raises(ValueError, match="OPENROUTER_MODEL"):
        OpenRouterProvider(
            http_client=client,
            timeout=30,
        )


def test_openrouter_provider_does_not_accept_invalid_ai_payload(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    from app.config import get_settings

    get_settings.cache_clear()

    client = FakeHttpClient(
        FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": {
                                "status": "analysis_available",
                                "summary": None,
                                "observations": [],
                                "risks": [],
                                "opportunities": [],
                                "recommendations": [],
                                "next_actions": [],
                                "evidence": [
                                    {
                                        "evidence_id": "unknown",
                                        "evidence_type": "interaction",
                                        "source": "website",
                                        "reference_id": "interaction-001",
                                        "description": "Test evidence",
                                    }
                                ],
                            }
                        }
                    }
                ]
            }
        )
    )

    provider = OpenRouterProvider(
        http_client=client,
        timeout=30,
    )

    with pytest.raises(
        RuntimeError,
        match="réponse du provider OpenRouter est invalide",
    ):
        provider.analyze(build_input())
