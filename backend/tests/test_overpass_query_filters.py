from app.services.discovery.sources.overpass import OverpassDiscoverySource


def test_overpass_query_contains_all_discovery_filters():
    query = OverpassDiscoverySource._build_query(
        "restaurant Madagascar Antananarivo Analamanga"
    )

    assert 'restaurant' in query
    assert 'Madagascar' in query
    assert 'Antananarivo' in query
    assert 'Analamanga' in query


def test_overpass_query_escapes_regex_characters():
    query = OverpassDiscoverySource._build_query(
        'restaurant "centre"'
    )

    assert '\\"' in query


def test_overpass_query_uses_city_as_geographic_area():
    query = OverpassDiscoverySource._build_query(
        "restaurant Madagascar Antananarivo Analamanga",
        context={
            "country": "Madagascar",
            "city": "Antananarivo",
            "region": "Analamanga",
            "sector": "restaurant",
            "search_query": "restaurant",
        },
    )

    assert 'area["name"="Antananarivo"]' in query
    assert 'area.searchArea' in query
    assert '["amenity"="restaurant"]' in query


def test_overpass_query_uses_country_when_city_is_missing():
    query = OverpassDiscoverySource._build_query(
        "restaurant Madagascar",
        context={
            "country": "Madagascar",
            "city": None,
            "region": None,
            "sector": "restaurant",
            "search_query": "restaurant",
        },
    )

    assert 'area["name"="Madagascar"]' in query
    assert 'area.searchArea' in query


def test_overpass_query_does_not_duplicate_sector_as_name_filter():
    query = OverpassDiscoverySource._build_query(
        "restaurant Madagascar Antananarivo",
        context={
            "country": "Madagascar",
            "city": "Antananarivo",
            "region": None,
            "sector": "restaurant",
            "search_query": "restaurant",
        },
    )

    assert '["amenity"="restaurant"]' in query
    assert '["name"~"restaurant",i]' not in query


def test_overpass_query_uses_name_filter_for_specific_search():
    query = OverpassDiscoverySource._build_query(
        "La Varangue Madagascar Antananarivo",
        context={
            "country": "Madagascar",
            "city": "Antananarivo",
            "region": None,
            "sector": "restaurant",
            "search_query": "La Varangue",
        },
    )

    assert '["amenity"="restaurant"]' in query
    assert '["name"~"La Varangue",i]' in query
