from unittest.mock import MagicMock, patch

import pytest

from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_ai_analysis_returns_404_for_unknown_lead(client):
    with patch(
        "app.routes.lead_intelligence.get_lead",
        return_value=None,
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/ai-analysis"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Lead introuvable"


def test_ai_analysis_returns_insufficient_data_without_provider_call(client):
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
    }

    with patch(
        "app.routes.lead_intelligence.get_lead",
        return_value=lead,
    ), patch(
        "app.routes.lead_intelligence.get_lead_interactions",
        return_value=[],
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/ai-analysis"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "insufficient_data"
    assert data["summary"] is None
    assert data["observations"] == []
    assert data["risks"] == []
    assert data["opportunities"] == []
    assert data["recommendations"] == []
    assert data["next_actions"] == []
    assert data["evidence"] == []
    assert data["model_metadata"] is None


def test_ai_analysis_calls_analysis_service_with_lead_intelligence(client):
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
    }

    intelligence = {
        "lead": lead,
        "qualification": {
            "status": "data_incomplete",
        },
        "data_quality": {
            "data_quality_score": 50,
        },
        "commercial_signals": {
            "status": "signals_available",
            "signal_count": 1,
            "signals": [
                {
                    "interaction_id": "interaction-001",
                    "signal_type": "form_submission",
                    "source": "website",
                    "occurred_at": "2026-09-25T21:33:43.151000",
                    "validation_reason": "Valid form submission evidence.",
                }
            ],
        },
        "commercial_score": {
            "commercial_score": 49.77,
            "status": "score_available",
            "confidence": None,
            "evidence": {},
            "calculation": {},
        },
        "evidence_registry": [
            {
                "evidence_id": "commercial-signal:interaction-001",
                "evidence_type": "commercial_signal",
                "source": "website",
                "reference_id": "interaction-001",
                "description": "Valid form submission evidence.",
            }
        ],
    }

    ai_result = {
        "status": "analysis_available",
        "summary": "Analyse basée sur les données disponibles.",
        "observations": [],
        "risks": [],
        "opportunities": [],
        "recommendations": [],
        "next_actions": [],
        "evidence": [],
        "model_metadata": None,
    }

    with patch(
        "app.routes.lead_intelligence.get_lead",
        return_value=lead,
    ), patch(
        "app.routes.lead_intelligence.get_lead_interactions",
        return_value=[],
    ), patch(
        "app.routes.lead_intelligence.build_lead_intelligence",
        return_value=intelligence,
    ), patch(
        "app.routes.lead_intelligence.AIAnalysisService",
    ) as mock_service_class:

        mock_service = mock_service_class.return_value
        mock_service.analyze.return_value = ai_result

        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/ai-analysis"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "analysis_available"

    mock_service_class.assert_called_once()
    mock_service.analyze.assert_called_once()


def test_ai_analysis_does_not_require_openrouter_for_insufficient_data(client):
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
    }

    intelligence = {
        "lead": lead,
        "qualification": {
            "status": "insufficient_data",
        },
        "data_quality": {},
        "commercial_signals": {
            "status": "insufficient_signals",
            "signal_count": 0,
            "signals": [],
            "ignored_interactions": [],
        },
        "commercial_score": {
            "commercial_score": None,
            "status": "insufficient_signals",
            "confidence": None,
            "evidence": {},
            "calculation": None,
        },
    }

    with patch(
        "app.routes.lead_intelligence.get_lead",
        return_value=lead,
    ), patch(
        "app.routes.lead_intelligence.get_lead_interactions",
        return_value=[],
    ), patch(
        "app.routes.lead_intelligence.build_lead_intelligence",
        return_value=intelligence,
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/ai-analysis"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "insufficient_data"
    assert data["summary"] is None


def test_ai_analysis_returns_provider_error_when_ai_provider_fails(client):
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
    }

    intelligence = {
        "lead": lead,
        "qualification": {
            "status": "partially_qualified",
        },
        "data_quality": {
            "data_quality_score": 87.5,
        },
        "commercial_signals": {
            "status": "signals_available",
            "signal_count": 1,
            "signals": [
                {
                    "interaction_id": "interaction-001",
                    "signal_type": "form_submission",
                    "source": "website",
                    "occurred_at": "2026-09-25T21:33:43.151000",
                    "validation_reason": "Valid form submission evidence.",
                }
            ],
        },
        "commercial_score": {
            "commercial_score": 49.77,
            "status": "score_available",
            "confidence": None,
            "evidence": {},
            "calculation": {},
        },
        "evidence_registry": [
            {
                "evidence_id": "commercial-signal:interaction-001",
                "evidence_type": "commercial_signal",
                "source": "website",
                "reference_id": "interaction-001",
                "description": "Valid form submission evidence.",
            }
        ],
    }

    with patch(
        "app.routes.lead_intelligence.get_lead",
        return_value=lead,
    ), patch(
        "app.routes.lead_intelligence.get_lead_interactions",
        return_value=[],
    ), patch(
        "app.routes.lead_intelligence.build_lead_intelligence",
        return_value=intelligence,
    ), patch(
        "app.routes.lead_intelligence.AIAnalysisService",
    ) as mock_service_class:

        mock_service = mock_service_class.return_value
        mock_service.analyze.side_effect = RuntimeError(
            "AI provider indisponible."
        )

        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/ai-analysis"
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "AI provider indisponible."

def test_ai_analysis_uses_provider_from_app_state(client):
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
    }

    intelligence = {
        "lead": lead,
        "qualification": {"status": "partially_qualified"},
        "data_quality": {"data_quality_score": 87.5},
        "commercial_signals": {
            "status": "signals_available",
            "signal_count": 1,
            "signals": [
                {
                    "interaction_id": "interaction-001",
                    "signal_type": "form_submission",
                    "source": "website",
                    "occurred_at": "2026-09-25T21:33:43.151000",
                    "validation_reason": "Valid form submission evidence.",
                }
            ],
        },
        "commercial_score": {
            "commercial_score": 49.77,
            "status": "score_available",
            "confidence": None,
            "evidence": {},
            "calculation": {},
        },
        "evidence_registry": [
            {
                "evidence_id": "commercial-signal:interaction-001",
                "evidence_type": "commercial_signal",
                "source": "website",
                "reference_id": "interaction-001",
                "description": "Valid form submission evidence.",
            }
        ],
    }

    ai_result = {
        "status": "analysis_available",
        "summary": "Analyse basée sur les données disponibles.",
        "observations": [],
        "risks": [],
        "opportunities": [],
        "recommendations": [],
        "next_actions": [],
        "evidence": [],
        "model_metadata": None,
    }

    fake_provider = MagicMock()

    with patch(
        "app.main.create_ai_provider",
        return_value=fake_provider,
    ), patch(
        "app.routes.lead_intelligence.get_lead",
        return_value=lead,
    ), patch(
        "app.routes.lead_intelligence.get_lead_interactions",
        return_value=[],
    ), patch(
        "app.routes.lead_intelligence.build_lead_intelligence",
        return_value=intelligence,
    ), patch(
        "app.routes.lead_intelligence.AIAnalysisService"
    ) as mock_service_class:

        mock_service = mock_service_class.return_value
        mock_service.analyze.return_value = ai_result

        with TestClient(app) as test_client:
            response = test_client.get(
                "/api/leads/507f1f77bcf86cd799439011/ai-analysis"
            )

    assert response.status_code == 200

    mock_service_class.assert_called_once_with(
        provider=fake_provider
    )