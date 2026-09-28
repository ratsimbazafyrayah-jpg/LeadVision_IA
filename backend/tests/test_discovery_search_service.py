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


class FakeGeocoder:
    def geocode(self, country=None, city=None, region=None):
        return {
            "lat": -18.9100122,
            "lon": 47.5255809,
            "boundingbox": {
                "south": -19.0700122,
                "west": 47.3655809,
                "north": -18.7500122,
                "east": 47.6855809,
            },
        }


class ContextCheckingSource:
    name = "fake"

    def __init__(self):
        self.context = None

    def discover(self, query, context=None):
        self.context = context
        return []


def test_search_service_adds_real_geocoding_boundingbox_to_context():
    request = DiscoverySearchRequest(
        country="Madagascar",
        city="Antananarivo",
        source="fake",
        query="restaurant",
    )

    source = ContextCheckingSource()
    geocoder = FakeGeocoder()

    result = search_prospects(
        request=request,
        source=source,
        geocoder=geocoder,
    )

    assert result["processed"] == 0
    assert source.context["boundingbox"] == {
        "south": -19.0700122,
        "west": 47.3655809,
        "north": -18.7500122,
        "east": 47.6855809,
    }
