import httpx
import pytest

from app.services.discovery.sources.geoapify import (
    GeoapifyDiscoverySource,
)


class FakeResponse:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error

    def json(self):
        return self.payload


class FakeHttpClient:
    def __init__(self, response=None, error=None, responses=None, errors=None):
        self.response = response
        self.error = error
        self.responses = responses or {}
        self.errors = errors or {}
        self.closed = False
        self.last_request = None
        self.calls = []

    def get(self, url, params=None, timeout=None):
        request = {
            "url": url,
            "params": params,
            "timeout": timeout,
        }

        self.last_request = request
        self.calls.append(request)

        if self.error:
            raise self.error

        if url in self.errors:
            raise self.errors[url]

        if url in self.responses:
            return self.responses[url]

        return self.response

    def close(self):
        self.closed = True


def build_source(client):
    return GeoapifyDiscoverySource(
        http_client=client,
        api_key="test-key",
        base_url="https://api.geoapify.com",
    )


def test_source_name():
    client = FakeHttpClient()
    source = build_source(client)

    assert source.name == "geoapify"


def test_api_key_is_required():
    client = FakeHttpClient()

    with pytest.raises(ValueError, match="clé API Geoapify"):
        GeoapifyDiscoverySource(
            http_client=client,
            api_key=None,
            base_url="https://api.geoapify.com",
        )


def test_query_is_required():
    client = FakeHttpClient()
    source = build_source(client)

    with pytest.raises(ValueError, match="requête de découverte"):
        source.discover("")


def test_maps_real_returned_fields():
    geocoding_response = FakeResponse(
        {
            "features": [
                {
                    "properties": {
                        "lat": -18.8792,
                        "lon": 47.5079,
                        "place_id": "real-place-id",
                    }
                }
            ]
        }
    )

    places_response = FakeResponse(
        {
            "features": [
                {
                    "properties": {
                        "name": "Entreprise Réelle",
                        "website": "https://example.com",
                        "contact": "+261340000000",
                        "city": "Antananarivo",
                        "country": "Madagascar",
                    }
                }
            ]
        }
    )

    client = FakeHttpClient(
        responses={
            "https://api.geoapify.com/v1/geocode/search": geocoding_response,
            "https://api.geoapify.com/v2/places": places_response,
        }
    )

    source = build_source(client)

    results = list(
        source.discover(
            "informatique",
            context={
                "country": "Madagascar",
                "city": "Antananarivo",
                "sector": "commercial",
            },
        )
    )

    assert results == [
        {
            "company_name": "Entreprise Réelle",
            "source": "geoapify",
            "website": "https://example.com",
            "phone": "+261340000000",
            "city": "Antananarivo",
            "country": "Madagascar",
        }
    ]

    assert client.calls[0]["url"] == (
        "https://api.geoapify.com/v1/geocode/search"
    )
    assert client.calls[0]["params"] == {
        "text": "Antananarivo, Madagascar",
        "apiKey": "test-key",
        "limit": 1,
    }

    assert client.calls[1]["url"] == (
        "https://api.geoapify.com/v2/places"
    )
    assert client.calls[1]["params"] == {
        "categories": "commercial",
        "filter": "place:real-place-id",
        "limit": 20,
        "offset": 0,
        "apiKey": "test-key",
        "name": "informatique",
    }


def test_ignores_feature_without_company_name():
    geocoding_response = FakeResponse(
        {
            "features": [
                {
                    "properties": {
                        "lat": -18.8792,
                        "lon": 47.5079,
                        "place_id": "real-place-id",
                    }
                }
            ]
        }
    )

    places_response = FakeResponse(
        {
            "features": [
                {
                    "properties": {
                        "city": "Antananarivo",
                    }
                }
            ]
        }
    )

    client = FakeHttpClient(
        responses={
            "https://api.geoapify.com/v1/geocode/search": geocoding_response,
            "https://api.geoapify.com/v2/places": places_response,
        }
    )

    source = build_source(client)

    results = list(
        source.discover(
            "informatique",
            context={
                "country": "Madagascar",
                "city": "Antananarivo",
            },
        )
    )

    assert results == []


def test_invalid_response_features_is_rejected():
    geocoding_response = FakeResponse(
        {
            "features": [
                {
                    "properties": {
                        "lat": -18.8792,
                        "lon": 47.5079,
                        "place_id": "real-place-id",
                    }
                }
            ]
        }
    )

    places_response = FakeResponse(
        {
            "features": "invalid",
        }
    )

    client = FakeHttpClient(
        responses={
            "https://api.geoapify.com/v1/geocode/search": geocoding_response,
            "https://api.geoapify.com/v2/places": places_response,
        }
    )

    source = build_source(client)

    with pytest.raises(ValueError, match="features"):
        list(
            source.discover(
                "informatique",
                context={
                    "country": "Madagascar",
                    "city": "Antananarivo",
                },
            )
        )

def test_timeout_is_converted_to_runtime_error():
    geocoding_response = FakeResponse(
        {
            "features": [
                {
                    "properties": {
                        "lat": -18.8792,
                        "lon": 47.5079,
                        "place_id": "real-place-id",
                    }
                }
            ]
        }
    )

    client = FakeHttpClient(
        responses={
            "https://api.geoapify.com/v1/geocode/search": geocoding_response,
        },
        errors={
            "https://api.geoapify.com/v2/places": httpx.ReadTimeout(
                "timeout"
            ),
        },
    )

    source = build_source(client)

    with pytest.raises(
        RuntimeError,
        match="source Geoapify a dépassé le délai",
    ):
        list(
            source.discover(
                "informatique",
                context={
                    "country": "Madagascar",
                    "city": "Antananarivo",
                },
            )
        )

def test_http_error_is_converted_to_runtime_error():
    geocoding_response = FakeResponse(
        {
            "features": [
                {
                    "properties": {
                        "lat": -18.8792,
                        "lon": 47.5079,
                        "place_id": "real-place-id",
                    }
                }
            ]
        }
    )

    places_error = httpx.HTTPStatusError(
        "HTTP 500",
        request=httpx.Request(
            "GET",
            "https://api.geoapify.com/v2/places",
        ),
        response=httpx.Response(
            500,
            request=httpx.Request(
                "GET",
                "https://api.geoapify.com/v2/places",
            ),
        ),
    )

    client = FakeHttpClient(
        responses={
            "https://api.geoapify.com/v1/geocode/search": geocoding_response,
        },
        errors={
            "https://api.geoapify.com/v2/places": places_error,
        },
    )

    source = build_source(client)

    with pytest.raises(
        RuntimeError,
        match="source Geoapify a retourné une erreur HTTP",
    ):
        list(
            source.discover(
                "informatique",
                context={
                    "country": "Madagascar",
                    "city": "Antananarivo",
                },
            )
        )

def test_request_error_is_converted_to_runtime_error():
    geocoding_response = FakeResponse(
        {
            "features": [
                {
                    "properties": {
                        "lat": -18.8792,
                        "lon": 47.5079,
                        "place_id": "real-place-id",
                    }
                }
            ]
        }
    )

    client = FakeHttpClient(
        responses={
            "https://api.geoapify.com/v1/geocode/search": geocoding_response,
        },
        errors={
            "https://api.geoapify.com/v2/places": httpx.ConnectError(
                "connection failed"
            ),
        },
    )

    source = build_source(client)

    with pytest.raises(
        RuntimeError,
        match="source Geoapify est indisponible",
    ):
        list(
            source.discover(
                "informatique",
                context={
                    "country": "Madagascar",
                    "city": "Antananarivo",
                },
            )
        )

def test_close_closes_http_client():
    client = FakeHttpClient()
    source = build_source(client)

    source.close()

    assert client.closed is True
