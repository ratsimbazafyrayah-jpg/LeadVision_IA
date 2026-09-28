from app.services.discovery.source_factory import build_discovery_sources


def test_discovery_sources_can_be_initialized_and_closed():
    sources = build_discovery_sources()

    assert len(sources) == 1
    assert sources[0].name == "overpass"

    for source in sources:
        assert source.http_client.is_closed is False
        source.http_client.close()
        assert source.http_client.is_closed is True
