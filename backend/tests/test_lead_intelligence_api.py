from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_lead_intelligence_returns_404_for_unknown_lead():
    with patch(
        "app.routes.lead_intelligence.get_lead",
        return_value=None,
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/intelligence"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Lead introuvable"


def test_lead_intelligence_returns_insufficient_data_for_empty_lead():
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
    }

    with patch(
        "app.routes.lead_intelligence.get_lead",
        return_value=lead,
    ), patch(
        "app.services.lead_intelligence_service.qualify_lead",
        return_value={
            "qualification": None,
            "status": "insufficient_data",
            "data_completeness": 12.5,
            "evidence": ["company_name"],
            "validated_fields": ["company_name"],
            "missing_data": [
                "sector",
                "country",
                "city",
                "website",
                "email",
                "phone",
                "social_media",
            ],
            "invalid_data": [],
            "social_platforms_found": [],
            "social_platforms_invalid": [],
        },
    ), patch(
        "app.routes.lead_intelligence.get_lead_interactions",
        return_value=[],
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/intelligence"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["lead"]["_id"] == "507f1f77bcf86cd799439011"
    assert data["qualification"]["status"] == "insufficient_data"
    assert data["commercial_signals"]["status"] == "insufficient_signals"
    assert data["commercial_score"]["commercial_score"] is None
    assert data["commercial_score"]["status"] == "insufficient_signals"
    assert data["commercial_score"]["confidence"] is None


def test_lead_intelligence_contains_all_sections():
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
        "sector": "Technologie",
        "country": "Madagascar",
        "city": "Antananarivo",
        "website": "https://example.com",
        "email": "contact@example.com",
        "phone": "+261341111111",
        "social_media": {
            "facebook": "https://facebook.com/example",
        },
    }

    interaction = {
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

    with patch(
        "app.routes.lead_intelligence.get_lead",
        return_value=lead,
    ), patch(
        "app.routes.lead_intelligence.get_lead_interactions",
        return_value=[interaction],
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/intelligence"
        )

    assert response.status_code == 200

    data = response.json()

    assert "lead" in data
    assert "qualification" in data
    assert "data_quality" in data
    assert "commercial_signals" in data
    assert "commercial_score" in data


def test_lead_intelligence_keeps_commercial_traceability():
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Test Company",
    }

    interaction = {
        "_id": "interaction-002",
        "lead_id": "507f1f77bcf86cd799439011",
        "type": "email_reply",
        "source": "email",
        "occurred_at": datetime.now(timezone.utc),
        "metadata": {
            "message_id": "message-001",
        },
    }

    with patch(
        "app.routes.lead_intelligence.get_lead",
        return_value=lead,
    ), patch(
        "app.routes.lead_intelligence.get_lead_interactions",
        return_value=[interaction],
    ):
        response = client.get(
            "/api/leads/507f1f77bcf86cd799439011/intelligence"
        )

    assert response.status_code == 200

    data = response.json()

    commercial_score = data["commercial_score"]

    assert commercial_score["status"] == "score_available"
    assert commercial_score["confidence"] is None
    assert commercial_score["signals_used"] == ["interaction-002"]

    assert len(commercial_score["evidence"]) == 1
    assert commercial_score["evidence"][0]["interaction_id"] == "interaction-002"
    assert commercial_score["evidence"][0]["signal_type"] == "email_reply"
    assert commercial_score["evidence"][0]["source"] == "email"

def test_lead_intelligence_keeps_commercial_score_separate():
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
            "/api/leads/507f1f77bcf86cd799439011/intelligence"
        )

    assert response.status_code == 200

    data = response.json()

    assert "commercial_signals" in data
    assert "commercial_score" in data

    assert "commercial_score" not in data["commercial_signals"]

    assert data["commercial_score"]["commercial_score"] is None
    assert data["commercial_score"]["status"] == "insufficient_signals"