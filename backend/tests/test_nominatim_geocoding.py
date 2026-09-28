import httpx
import pytest

from app.services.discovery.nominatim_geocoding import (
    NominatimGeocodingService,
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
    return NominatimGeocodingService(
        http_client=client,
        base_url="https://nominatim.openstreetmap.org",
    )


def test_geocode_requires_location():
    service = build_service(FakeHttpClient())

    with pytest.raises(ValueError, match="pays.*ville.*région"):
        service.geocode()


def test_geocode_maps_real_coordinates_and_boundingbox():
    client = FakeHttpClient(
        response=FakeResponse(
            [
                {
                    "lat": "-18.9100122",
                    "lon": "47.5255809",
                    "boundingbox": [
                        "-19.0700122",
                        "-18.7500122",
                        "47.3655809",
                        "47.6855809",
                    ],
                }
            ]
        )
    )

    service = build_service(client)

    result = service.geocode(
        country="Madagascar",
        city="Antananarivo",
    )

    assert result == {
        "lat": -18.9100122,
        "lon": 47.5255809,
        "boundingbox": {
            "south": -19.0700122,
            "west": 47.3655809,
            "north": -18.7500122,
            "east": 47.6855809,
        },
    }

    assert client.last_request["url"] == (
        "https://nominatim.openstreetmap.org/search"
    )

    assert client.last_request["params"] == {
        "q": "Antananarivo, Madagascar",
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
    }


def test_geocode_returns_none_when_no_result():
    client = FakeHttpClient(
        response=FakeResponse([])
    )

    service = build_service(client)

    assert service.geocode(country="Madagascar") is None


def test_geocode_returns_none_without_coordinates():
    client = FakeHttpClient(
        response=FakeResponse(
            [
                {
                    "boundingbox": [
                        "-19.0",
                        "-18.8",
                        "47.4",
                        "47.6",
                    ]
                }
            ]
        )
    )

    service = build_service(client)

    assert service.geocode(country="Madagascar") is None


def test_geocode_returns_none_with_invalid_boundingbox():
    client = FakeHttpClient(
        response=FakeResponse(
            [
                {
                    "lat": "-18.9100122",
                    "lon": "47.5255809",
                    "boundingbox": ["invalid"],
                }
            ]
        )
    )

    service = build_service(client)

    assert service.geocode(country="Madagascar") is None


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
        "https://nominatim.openstreetmap.org/search",
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
