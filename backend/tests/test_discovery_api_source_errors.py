from fastapi.testclient import TestClient

from app.main import app


def test_discovery_search_handles_source_failure():
    class FailingSource:
        name = "overpass"

        def discover(self, query):
            raise RuntimeError("Discovery source unavailable.")

    class FakeRegistry:
        def get(self, name):
            return FailingSource()

    with TestClient(app) as client:
        original_registry = app.state.discovery_sources
        app.state.discovery_sources = FakeRegistry()

        try:
            response = client.post(
                "/api/discovery/search",
                json={
                    "country": "Madagascar",
                    "city": "Antananarivo",
                    "sector": "technology",
                    "source": "overpass",
                    "query": "technology",
                },
            )
        finally:
            app.state.discovery_sources = original_registry

    assert response.status_code == 502
    assert response.json()["detail"] == "La source de découverte est indisponible."
