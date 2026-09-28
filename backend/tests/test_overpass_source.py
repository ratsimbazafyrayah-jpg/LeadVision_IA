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


def test_overpass_source_maps_requested_sector_from_context():
    payload = {
        "elements": [
            {
                "type": "node",
                "id": 789,
                "tags": {
                    "name": "Restaurant réel",
                    "office": "company",
                },
            }
        ]
    }

    client = FakeHttpClient(FakeResponse(payload))
    source = OverpassDiscoverySource(http_client=client)

    results = list(
        source.discover(
            "restaurant",
            context={"sector": "restaurant"},
        )
    )

    assert len(results) == 1
    assert results[0]["company_name"] == "Restaurant réel"
    assert results[0]["sector"] == "restaurant"



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

class FailingResponse:
    def __init__(self, error):
        self.error = error

    def raise_for_status(self):
        raise self.error


class SequenceHttpClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, data=None, timeout=None):
        self.calls.append(url)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_overpass_source_uses_fallback_after_primary_timeout():
    client = SequenceHttpClient([
        pytest.importorskip("httpx").TimeoutException("primary timeout"),
        FakeResponse({"elements": []}),
    ])

    source = OverpassDiscoverySource(
        http_client=client,
        endpoint="https://primary.example/api",
        fallback_endpoints=["https://fallback.example/api"],
    )

    assert list(source.discover("restaurant")) == []
    assert client.calls == [
        "https://primary.example/api",
        "https://fallback.example/api",
    ]


def test_overpass_source_does_not_use_fallback_when_primary_succeeds():
    client = SequenceHttpClient([
        FakeResponse({"elements": []}),
    ])

    source = OverpassDiscoverySource(
        http_client=client,
        endpoint="https://primary.example/api",
        fallback_endpoints=["https://fallback.example/api"],
    )

    assert list(source.discover("restaurant")) == []
    assert client.calls == ["https://primary.example/api"]


def test_overpass_source_raises_when_primary_and_fallback_fail():
    httpx = pytest.importorskip("httpx")
    client = SequenceHttpClient([
        httpx.TimeoutException("primary timeout"),
        httpx.TimeoutException("fallback timeout"),
    ])

    source = OverpassDiscoverySource(
        http_client=client,
        endpoint="https://primary.example/api",
        fallback_endpoints=["https://fallback.example/api"],
    )

    with pytest.raises(RuntimeError, match="Overpass"):
        list(source.discover("restaurant"))

    assert client.calls == [
        "https://primary.example/api",
        "https://fallback.example/api",
    ]



def test_overpass_source_uses_real_boundingbox_from_context():
    client = FakeHttpClient(FakeResponse({"elements": []}))
    source = OverpassDiscoverySource(http_client=client)

    context = {
        "country": "Madagascar",
        "city": "Antananarivo",
        "sector": "restaurant",
        "search_query": "restaurant",
        "boundingbox": {
            "south": -19.0700122,
            "west": 47.3655809,
            "north": -18.7500122,
            "east": 47.6855809,
        },
    }

    list(source.discover("restaurant", context=context))

    query = client.calls[0]["data"]

    assert 'nwr["amenity"="restaurant"](-19.0700122,47.3655809,-18.7500122,47.6855809);' in query
    assert 'area["name"="Antananarivo"]' not in query
