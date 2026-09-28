import pytest

from app.services.discovery.sources.overpass import OverpassDiscoverySource


class FakeHttpClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, data=None, timeout=None):
        self.calls.append({
            "url": url,
            "data": data,
            "timeout": timeout,
        })
        return self.response


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_overpass_source_name():
    source = OverpassDiscoverySource(http_client=FakeHttpClient(FakeResponse({"elements": []})))

    assert source.name == "overpass"


def test_overpass_source_maps_real_osm_tags():
    payload = {
        "elements": [
            {
                "type": "node",
                "id": 123,
                "lat": -18.8792,
                "lon": 47.5079,
                "tags": {
                    "name": "Entreprise réelle",
                    "website": "https://example.com",
                    "email": "contact@example.com",
                    "phone": "+261340000000",
                    "addr:city": "Antananarivo",
                    "office": "company",
                },
            }
        ]
    }

    client = FakeHttpClient(FakeResponse(payload))
    source = OverpassDiscoverySource(http_client=client)

    results = list(source.discover("company"))

    assert len(results) == 1
    assert results[0]["company_name"] == "Entreprise réelle"
    assert results[0]["website"] == "https://example.com"
    assert results[0]["email"] == "contact@example.com"
    assert results[0]["phone"] == "+261340000000"
    assert results[0]["city"] == "Antananarivo"
    assert results[0]["source"] == "overpass"


def test_overpass_source_ignores_elements_without_name():
    payload = {
        "elements": [
            {
                "type": "node",
                "id": 456,
                "tags": {
                    "website": "https://example.com",
                },
            }
        ]
    }

    client = FakeHttpClient(FakeResponse(payload))
    source = OverpassDiscoverySource(http_client=client)

    results = list(source.discover("company"))

    assert results == []


def test_overpass_source_requires_http_client():
    with pytest.raises(TypeError):
        OverpassDiscoverySource(http_client=None)
