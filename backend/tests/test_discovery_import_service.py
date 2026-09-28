from app.services.discovery.discovery_service import import_prospects


def test_import_prospects_processes_discovered_leads():
    prospects = [
        {
            "company_name": "Company A",
            "country": "Madagascar",
        },
        {
            "company_name": "Company B",
            "country": "Madagascar",
        },
    ]

    result = import_prospects(
        prospects=prospects,
        source="overpass",
    )

    assert result["source"] == "overpass"
    assert result["processed"] == 2
    assert result["created"] + result["duplicates"] + result["rejected"] == 2
    assert len(result["results"]) == 2
