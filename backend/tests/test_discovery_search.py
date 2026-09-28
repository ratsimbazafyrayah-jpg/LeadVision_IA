import pytest

from app.schemas.discovery import DiscoverySearchRequest


def test_discovery_search_request_accepts_valid_filters():
    request = DiscoverySearchRequest(
        country="Madagascar",
        city="Antananarivo",
        sector="informatique",
        source="overpass",
        query="entreprise informatique",
    )

    assert request.country == "Madagascar"
    assert request.city == "Antananarivo"
    assert request.sector == "informatique"
    assert request.source == "overpass"
    assert request.query == "entreprise informatique"


def test_discovery_search_request_allows_optional_location_filters():
    request = DiscoverySearchRequest(
        country="France",
        sector="immobilier",
        source="overpass",
        query="agence immobilière",
    )

    assert request.country == "France"
    assert request.city is None
    assert request.region is None


def test_discovery_search_request_requires_country():
    with pytest.raises(ValueError):
        DiscoverySearchRequest(
            sector="informatique",
            source="overpass",
            query="entreprise",
        )


def test_discovery_search_request_requires_query():
    with pytest.raises(ValueError):
        DiscoverySearchRequest(
            country="Madagascar",
            source="overpass",
        )


def test_discovery_search_request_rejects_blank_query():
    with pytest.raises(ValueError):
        DiscoverySearchRequest(
            country="Madagascar",
            source="overpass",
            query="   ",
        )
