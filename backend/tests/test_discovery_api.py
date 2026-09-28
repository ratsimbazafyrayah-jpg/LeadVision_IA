from fastapi.testclient import TestClient

from app.main import app


def test_discovery_search_endpoint_returns_search_result():
    class FakeSource:
        name = "overpass"

        def discover(self, query):
            return [
                {
                    "company_name": "Example Company",
                    "country": "Madagascar",
                }
            ]

    class FakeRegistry:
        def get(self, name):
            assert name == "overpass"
            return FakeSource()

    with TestClient(app) as client:
        original_registry = app.state.discovery_sources
        app.state.discovery_sources = FakeRegistry()

        try:
            response = client.post(
                "/api/discovery/search",
                json={
                    "country": "Madagascar",
                    "city": "Antananarivo",
                    "region": "Analamanga",
                    "sector": "technology",
                    "source": "overpass",
                    "query": "technology",
                },
            )
        finally:
            app.state.discovery_sources = original_registry

    assert response.status_code == 200

    data = response.json()

    assert data["source"] == "overpass"
    assert data["query"] == "technology"
    assert data["processed"] == 1
    assert len(data["prospects"]) == 1
    assert data["prospects"][0]["company_name"] == "Example Company"
