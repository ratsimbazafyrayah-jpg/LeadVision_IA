from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_update_lead_returns_updated_lead():
    lead = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Mise à Jour",
        "email": "contact@example.com",
        "website": "https://example.com",
    }

    with patch(
        "app.routes.leads.update_lead",
        return_value=lead,
    ) as mocked_update:
        response = client.put(
            "/api/leads/507f1f77bcf86cd799439011",
            json={
                "company_name": "Entreprise Mise à Jour",
                "email": "contact@example.com",
            },
        )

    assert response.status_code == 200
    assert response.json() == lead

    mocked_update.assert_called_once_with(
        "507f1f77bcf86cd799439011",
        {
            "company_name": "Entreprise Mise à Jour",
            "email": "contact@example.com",
        },
    )


def test_update_lead_returns_404_when_lead_does_not_exist():
    with patch(
        "app.routes.leads.update_lead",
        return_value=None,
    ):
        response = client.put(
            "/api/leads/507f1f77bcf86cd799439011",
            json={
                "company_name": "Entreprise Test",
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Lead introuvable"


def test_update_lead_returns_404_when_lead_does_not_exist():
    with patch(
        "app.routes.leads.update_lead",
        return_value=None,
    ):
        response = client.put(
            "/api/leads/507f1f77bcf86cd799439011",
            json={
                "company_name": "Entreprise Test",
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Lead introuvable"


def test_update_lead_returns_400_for_service_validation_error():
    with patch(
        "app.routes.leads.update_lead",
        side_effect=ValueError("Adresse email invalide"),
    ):
        response = client.put(
            "/api/leads/507f1f77bcf86cd799439011",
            json={
                "email": "email-invalide",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Adresse email invalide"


def test_enrich_lead_returns_404_when_lead_does_not_exist(
    monkeypatch,
):
    from fastapi.testclient import TestClient

    from app.main import app

    monkeypatch.setattr(
        "app.routes.leads.get_lead",
        lambda lead_id: None,
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/leads/507f1f77bcf86cd799439011/enrichment"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Lead introuvable"


def test_enrich_lead_returns_enrichment_result(
    monkeypatch,
):
    from fastapi.testclient import TestClient

    from app.main import app

    lead_id = "507f1f77bcf86cd799439011"

    monkeypatch.setattr(
        "app.routes.leads.enrich_lead",
        lambda lead_id, enrichment_service: {
            "lead_id": lead_id,
            "updated": True,
            "updated_fields": ["email"],
            "enrichment": {
                "website": "https://example.com",
                "final_url": "https://example.com/",
                "status_code": 200,
                "content_type": "text/html",
                "emails": ["contact@example.com"],
                "phones": [],
                "social_links": {},
            },
        },
    )

    class FakeWebsiteEnrichment:
        def close(self):
            pass

    fake_service = FakeWebsiteEnrichment()

    with TestClient(app) as client:
        app.state.website_enrichment = fake_service

        response = client.post(
            f"/api/leads/{lead_id}/enrichment"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["lead_id"] == lead_id
    assert data["updated"] is True
    assert data["updated_fields"] == ["email"]
    assert data["enrichment"]["emails"] == [
        "contact@example.com"
    ]


def test_enrich_lead_returns_400_when_website_is_missing(
    monkeypatch,
):
    from fastapi.testclient import TestClient

    from app.main import app

    lead_id = "507f1f77bcf86cd799439011"

    def raise_missing_website(lead_id, enrichment_service):
        raise ValueError("Le lead ne possède pas de site web")

    monkeypatch.setattr(
        "app.routes.leads.enrich_lead",
        raise_missing_website,
    )

    class FakeWebsiteEnrichment:
        def close(self):
            pass

    with TestClient(app) as client:
        app.state.website_enrichment = FakeWebsiteEnrichment()

        response = client.post(
            f"/api/leads/{lead_id}/enrichment"
        )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Le lead ne possède pas de site web"
    )
