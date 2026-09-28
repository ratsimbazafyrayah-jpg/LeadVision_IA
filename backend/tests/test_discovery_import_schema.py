from app.schemas.discovery import DiscoveryImportRequest


def test_discovery_import_request_accepts_prospects():
    request = DiscoveryImportRequest(
        source="overpass",
        prospects=[
            {
                "company_name": "Example Company",
                "country": "Madagascar",
                "city": "Antananarivo",
            }
        ],
    )

    assert request.source == "overpass"
    assert len(request.prospects) == 1


def test_discovery_import_request_rejects_empty_source():
    try:
        DiscoveryImportRequest(
            source="",
            prospects=[],
        )
    except ValueError:
        return

    raise AssertionError("Une source vide doit être rejetée.")


def test_discovery_import_request_rejects_missing_prospects():
    try:
        DiscoveryImportRequest(source="overpass")
    except ValueError:
        return

    raise AssertionError("La liste des prospects est requise.")
