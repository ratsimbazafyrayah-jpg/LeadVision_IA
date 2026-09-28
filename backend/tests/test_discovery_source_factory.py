from app.services.discovery.source_factory import build_discovery_sources


def test_factory_builds_overpass_source(monkeypatch):
    from app.config import get_settings

    monkeypatch.delenv("GEOAPIFY_API_KEY", raising=False)
    get_settings.cache_clear()

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


def test_factory_adds_geoapify_when_api_key_is_configured(monkeypatch):
    from app.config import get_settings

    monkeypatch.setenv("GEOAPIFY_API_KEY", "test-key")
    get_settings.cache_clear()

    sources = build_discovery_sources()

    try:
        assert len(sources) == 2
        assert [source.name for source in sources] == [
            "overpass",
            "geoapify",
        ]
        assert sources[1].api_key == "test-key"
    finally:
        for source in sources:
            source.close()

        get_settings.cache_clear()
