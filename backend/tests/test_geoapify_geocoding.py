import httpx
import pytest

from app.services.discovery.geoapify_geocoding import (
    GeoapifyGeocodingService,
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
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.closed = False
        self.last_request = None

    def get(self, url, params=None, timeout=None):
        self.last_request = {
            "url": url,
            "params": params,
            "timeout": timeout,
        }

        if self.error:
            raise self.error

        return self.response

    def close(self):
        self.closed = True


def build_service(client):
    return GeoapifyGeocodingService(
        http_client=client,
        api_key="test-key",
        base_url="https://api.geoapify.com",
    )


def test_geocode_requires_location():
    client = FakeHttpClient()
    service = build_service(client)

    with pytest.raises(ValueError, match="pays.*ville.*région"):
        service.geocode()


def test_geocode_maps_real_coordinates():
    client = FakeHttpClient(
        response=FakeResponse(
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
    )

    service = build_service(client)

    result = service.geocode(
        country="Madagascar",
        city="Antananarivo",
    )

    assert result == {
        "lat": -18.8792,
        "lon": 47.5079,
        "place_id": "real-place-id",
    }

    assert client.last_request["url"] == (
        "https://api.geoapify.com/v1/geocode/search"
    )
    assert client.last_request["params"] == {
        "text": "Antananarivo, Madagascar",
        "apiKey": "test-key",
        "limit": 1,
    }


def test_geocode_returns_none_when_no_result():
    client = FakeHttpClient(
        response=FakeResponse(
            {
                "features": [],
            }
        )
    )

    service = build_service(client)

    assert service.geocode(country="Madagascar") is None


def test_geocode_returns_none_without_real_coordinates():
    client = FakeHttpClient(
        response=FakeResponse(
            {
                "features": [
                    {
                        "properties": {
                            "place_id": "place-without-coordinates",
                        }
                    }
                ]
            }
        )
    )

    service = build_service(client)

    assert service.geocode(country="Madagascar") is None


def test_geocode_rejects_invalid_features():
    client = FakeHttpClient(
        response=FakeResponse(
            {
                "features": "invalid",
            }
        )
    )

    service = build_service(client)

    with pytest.raises(ValueError, match="features"):
        service.geocode(country="Madagascar")


def test_geocode_timeout_is_converted():
    client = FakeHttpClient(
        error=httpx.ReadTimeout("timeout")
    )

    service = build_service(client)

    with pytest.raises(
        RuntimeError,
        match="dépassé le délai d'attente",
    ):
        service.geocode(country="Madagascar")


def test_geocode_http_error_is_converted():
    request = httpx.Request(
        "GET",
        "https://api.geoapify.com/v1/geocode/search",
    )
    response = httpx.Response(
        503,
        request=request,
    )

    client = FakeHttpClient(
        response=FakeResponse(
            error=httpx.HTTPStatusError(
                "service unavailable",
                request=request,
                response=response,
            )
        )
    )

    service = build_service(client)

    with pytest.raises(
        RuntimeError,
        match="erreur HTTP",
    ):
        service.geocode(country="Madagascar")


def test_geocode_request_error_is_converted():
    client = FakeHttpClient(
        error=httpx.ConnectError("connection failed")
    )

    service = build_service(client)

    with pytest.raises(
        RuntimeError,
        match="indisponible",
    ):
        service.geocode(country="Madagascar")


def test_close_closes_http_client():
    client = FakeHttpClient()
    service = build_service(client)

    service.close()

    assert client.closed is True
