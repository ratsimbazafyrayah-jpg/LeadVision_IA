from app.schemas.discovery import DiscoverySearchRequest
from app.services.discovery.search_service import search_prospects


class FakeSource:
    @property
    def name(self):
        return "fake"

    def discover(self, query, context=None):
        return [
            {
                "company_name": "Entreprise trouvée",
                "source": "fake",
            }
        ]


def test_search_service_calls_selected_source():
    request = DiscoverySearchRequest(
        country="Madagascar",
        city="Antananarivo",
        sector="informatique",
        source="fake",
        query="entreprise informatique",
    )

    source = FakeSource()

    result = search_prospects(request, source)

    assert result["source"] == "fake"
    assert result["query"] == "entreprise informatique"
    assert result["filters"]["country"] == "Madagascar"
    assert result["filters"]["city"] == "Antananarivo"
    assert result["filters"]["sector"] == "informatique"
    assert result["processed"] == 1
    assert result["prospects"][0]["company_name"] == "Entreprise trouvée"


def test_search_service_rejects_source_mismatch():
    request = DiscoverySearchRequest(
        country="France",
        source="overpass",
        query="entreprise",
    )

    source = FakeSource()

    try:
        search_prospects(request, source)
        assert False
    except ValueError as error:
        assert str(error) == "La source sélectionnée ne correspond pas à la source fournie."
