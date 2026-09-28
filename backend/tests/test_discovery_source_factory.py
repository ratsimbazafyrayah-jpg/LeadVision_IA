from app.services.discovery.source_factory import build_discovery_sources


def test_factory_builds_overpass_source():
    sources = build_discovery_sources()

    assert len(sources) == 1
    assert sources[0].name == "overpass"


def test_factory_source_has_http_client():
    sources = build_discovery_sources()

    assert len(sources) == 1
    assert sources[0].name == "overpass"
    assert sources[0].http_client is not None

    sources[0].http_client.close()


def test_factory_sources_can_be_closed():
    sources = build_discovery_sources()

    for source in sources:
        source.http_client.close()

        assert source.http_client.is_closed is True
