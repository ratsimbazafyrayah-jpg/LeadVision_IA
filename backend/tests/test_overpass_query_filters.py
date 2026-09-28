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
