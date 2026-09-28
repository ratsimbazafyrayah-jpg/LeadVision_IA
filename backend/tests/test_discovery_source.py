import pytest

from app.services.discovery.sources.base import DiscoverySource


class FakeDiscoverySource(DiscoverySource):
    @property
    def name(self):
        return "fake_source"

    def discover(self, query):
        return [
            {
                "company_name": "Entreprise collectée",
                "website": "https://example.com",
            }
        ]


def test_discovery_source_contract():
    source = FakeDiscoverySource()

    assert source.name == "fake_source"

    results = list(source.discover("technology"))

    assert len(results) == 1
    assert results[0]["company_name"] == "Entreprise collectée"


def test_discovery_source_requires_name():
    class InvalidSource(DiscoverySource):
        def discover(self, query):
            return []

    with pytest.raises(TypeError):
        InvalidSource()


def test_discovery_source_requires_discover():
    class InvalidSource(DiscoverySource):
        @property
        def name(self):
            return "invalid"

    with pytest.raises(TypeError):
        InvalidSource()
