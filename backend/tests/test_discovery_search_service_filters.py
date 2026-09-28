from app.schemas.discovery import DiscoverySearchRequest
from app.services.discovery.search_service import search_prospects


class FakeSource:
    name = "overpass"

    def __init__(self):
        self.received_query = None

    def discover(self, query):
        self.received_query = query
        return []


def test_search_service_passes_all_filters_to_source():
    request = DiscoverySearchRequest(
        country="Madagascar",
        city="Antananarivo",
        region="Analamanga",
        sector="restaurant",
        source="overpass",
        query="restaurant",
    )

    source = FakeSource()

    result = search_prospects(request, source)

    assert result["processed"] == 0
    assert source.received_query is not None
    assert "restaurant" in source.received_query
    assert "Madagascar" in source.received_query
    assert "Antananarivo" in source.received_query
    assert "Analamanga" in source.received_query
