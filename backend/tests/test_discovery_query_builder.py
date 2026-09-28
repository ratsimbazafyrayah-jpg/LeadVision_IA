from app.schemas.discovery import DiscoverySearchRequest
from app.services.discovery.query_builder import build_discovery_query


def test_build_query_with_all_filters():
    request = DiscoverySearchRequest(
        country="Madagascar",
        city="Antananarivo",
        region="Analamanga",
        sector="restaurant",
        source="overpass",
        query="restaurant",
    )

    query = build_discovery_query(request)

    assert "restaurant" in query
    assert "Madagascar" in query
    assert "Antananarivo" in query
    assert "Analamanga" in query


def test_build_query_without_optional_filters():
    request = DiscoverySearchRequest(
        country="Madagascar",
        source="overpass",
        query="restaurant",
    )

    query = build_discovery_query(request)

    assert "restaurant" in query
    assert "Madagascar" in query


def test_build_query_rejects_none_request():
    try:
        build_discovery_query(None)
    except ValueError as error:
        assert str(error) == "La requête de découverte est requise."
    else:
        raise AssertionError("ValueError attendu.")
