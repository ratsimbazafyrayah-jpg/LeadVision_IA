from fastapi import FastAPI

from app.services.discovery.source_factory import build_discovery_sources
from app.services.discovery.source_registry import DiscoverySourceRegistry


def test_discovery_registry_can_be_attached_to_app_state():
    app = FastAPI()

    sources = build_discovery_sources()
    registry = DiscoverySourceRegistry(sources)

    app.state.discovery_sources = registry

    assert app.state.discovery_sources.get("overpass") is sources[0]

    for source in sources:
        source.http_client.close()
