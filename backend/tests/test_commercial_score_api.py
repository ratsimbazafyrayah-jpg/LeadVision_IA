from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_commercial_score_returns_404_for_unknown_lead():
    with patch(
        "app.routes.commercial_signals.get_lead",
        return_value=None,
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/commercial-score"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Lead introuvable"


def test_commercial_score_returns_insufficient_signals():
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
    }

    with patch(
        "app.routes.commercial_signals.get_lead",
        return_value=lead,
    ), patch(
        "app.routes.commercial_signals.get_lead_interactions",
        return_value=[],
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/commercial-score"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["commercial_score"] is None
    assert data["status"] == "insufficient_signals"
    assert data["confidence"] is None
    assert data["signals_used"] == []
    assert data["evidence"] == []
    assert data["calculation"] is None


def test_commercial_score_returns_score_for_valid_signal():
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
    }

    interactions = [
        {
            "_id": "interaction-001",
            "lead_id": "507f1f77bcf86cd799439011",
            "type": "form_submission",
            "source": "website",
            "occurred_at": datetime.now(timezone.utc),
            "metadata": {
                "form_id": "contact-form",
                "event_id": "event-001",
            },
        }
    ]

    with patch(
        "app.routes.commercial_signals.get_lead",
        return_value=lead,
    ), patch(
        "app.routes.commercial_signals.get_lead_interactions",
        return_value=interactions,
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/commercial-score"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["commercial_score"] is not None
    assert 0 <= data["commercial_score"] <= 100
    assert data["status"] == "score_available"
    assert data["confidence"] is None

    assert data["signals_used"] == ["interaction-001"]
    assert len(data["evidence"]) == 1

    assert (
        data["evidence"][0]["interaction_id"]
        == "interaction-001"
    )

    assert data["calculation"] is not None
    assert "dimensions" in data["calculation"]


def test_commercial_score_response_keeps_traceability():
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
    }

    interactions = [
        {
            "_id": "interaction-002",
            "lead_id": "507f1f77bcf86cd799439011",
            "type": "email_reply",
            "source": "email",
            "occurred_at": datetime.now(timezone.utc),
            "metadata": {
                "message_id": "message-001",
            },
        }
    ]

    with patch(
        "app.routes.commercial_signals.get_lead",
        return_value=lead,
    ), patch(
        "app.routes.commercial_signals.get_lead_interactions",
        return_value=interactions,
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/commercial-score"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["signals_used"] == ["interaction-002"]

    evidence = data["evidence"][0]

    assert evidence["interaction_id"] == "interaction-002"
    assert evidence["signal_type"] == "email_reply"
    assert evidence["source"] == "email"
    assert evidence["validation_reason"] == "validated_email_event"
