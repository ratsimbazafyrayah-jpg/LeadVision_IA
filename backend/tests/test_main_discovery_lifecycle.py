from fastapi.testclient import TestClient

from app.main import app


def test_app_initializes_discovery_registry():
    with TestClient(app):
        registry = app.state.discovery_sources

        assert registry.get("overpass").name == "overpass"


def test_app_closes_discovery_clients_on_shutdown():
    with TestClient(app):
        source = app.state.discovery_sources.get("overpass")
        http_client = source.http_client

        assert http_client.is_closed is False

    assert http_client.is_closed is True
