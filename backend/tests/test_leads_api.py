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
