import pytest

from app.services.discovery.source_registry import DiscoverySourceRegistry


class FakeSource:
    @property
    def name(self):
        return "fake"


def test_registry_returns_registered_source():
    source = FakeSource()
    registry = DiscoverySourceRegistry([source])

    assert registry.get("fake") is source


def test_registry_rejects_unknown_source():
    registry = DiscoverySourceRegistry([])

    with pytest.raises(ValueError, match="Source de découverte inconnue"):
        registry.get("unknown")


def test_registry_rejects_duplicate_source_names():
    source_a = FakeSource()
    source_b = FakeSource()

    with pytest.raises(ValueError, match="Source de découverte dupliquée"):
        DiscoverySourceRegistry([source_a, source_b])


def test_registry_closes_registered_source_clients():
    class ClosableSource:
        @property
        def name(self):
            return "closable"

        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    source = ClosableSource()
    registry = DiscoverySourceRegistry([source])

    registry.close()

    assert source.closed is True

def test_registry_supports_multiple_discovery_sources():
    class GeoapifySource:
        @property
        def name(self):
            return "geoapify"

    class OverpassSource:
        @property
        def name(self):
            return "overpass"

    overpass = OverpassSource()
    geoapify = GeoapifySource()

    registry = DiscoverySourceRegistry([overpass, geoapify])

    assert registry.get("overpass") is overpass
    assert registry.get("geoapify") is geoapify
