from app.services.discovery.source_registry import DiscoverySourceRegistry
from app.services.discovery.sources.overpass import OverpassDiscoverySource


class FakeHttpClient:
    pass


def test_registry_registers_overpass_source():
    source = OverpassDiscoverySource(
        http_client=FakeHttpClient()
    )

    registry = DiscoverySourceRegistry([source])

    assert registry.get("overpass") is source
    assert registry.get("overpass").name == "overpass"
