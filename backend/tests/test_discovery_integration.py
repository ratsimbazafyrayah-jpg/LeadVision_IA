from app.services.discovery.discovery_service import import_prospects
from app.services.discovery.sources.overpass import OverpassDiscoverySource


class FakeHttpClient:
    def __init__(self, payload):
        self.payload = payload

    def post(self, url, data=None, timeout=None):
        return FakeResponse(self.payload)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_overpass_source_integrates_with_discovery_service(monkeypatch):
    payload = {
        "elements": [
            {
                "type": "node",
                "id": 1001,
                "tags": {
                    "name": "Entreprise Integration Test",
                    "website": "https://integration-test.example",
                    "email": "integration@example.com",
                    "addr:city": "Antananarivo",
                },
            }
        ]
    }

    source = OverpassDiscoverySource(
        http_client=FakeHttpClient(payload)
    )

    prospects = list(source.discover("company"))

    captured = []

    def fake_create_lead(data):
        captured.append(data)
        return {
            "created": True,
            "duplicate": False,
            "lead": data,
        }

    monkeypatch.setattr(
        "app.services.discovery.discovery_service.create_lead",
        fake_create_lead,
    )

    result = import_prospects(
        prospects,
        source=source.name,
    )

    assert result["processed"] == 1
    assert result["created"] == 1
    assert result["duplicates"] == 0
    assert result["rejected"] == 0

    assert len(captured) == 1
    assert captured[0]["company_name"] == "Entreprise Integration Test"
    assert captured[0]["website"] == "https://integration-test.example"
    assert captured[0]["email"] == "integration@example.com"
    assert captured[0]["city"] == "Antananarivo"
    assert captured[0]["source"] == "overpass"
