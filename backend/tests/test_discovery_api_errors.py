from fastapi.testclient import TestClient

from app.main import app


def test_discovery_search_rejects_unknown_source():
    with TestClient(app) as client:
        response = client.post(
            "/api/discovery/search",
            json={
                "country": "Madagascar",
                "city": "Antananarivo",
                "sector": "technology",
                "source": "unknown-source",
                "query": "technology",
            },
        )

    assert response.status_code == 400
    assert "Source de découverte inconnue" in response.json()["detail"]


def test_discovery_search_rejects_invalid_payload():
    with TestClient(app) as client:
        response = client.post(
            "/api/discovery/search",
            json={
                "country": "Madagascar",
                "source": "overpass",
            },
        )

    assert response.status_code == 422
