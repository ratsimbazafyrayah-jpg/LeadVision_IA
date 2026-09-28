import pytest

from app.services.discovery.discovery_service import import_prospects


def test_import_prospects_creates_leads(monkeypatch):
    calls = []

    def fake_create_lead(data):
        calls.append(data)
        return {
            "created": True,
            "duplicate": False,
            "lead": {
                "company_name": data["company_name"],
            },
        }

    monkeypatch.setattr(
        "app.services.discovery.discovery_service.create_lead",
        fake_create_lead,
    )

    result = import_prospects(
        prospects=[
            {
                "company_name": "Entreprise Réelle",
                "website": "https://example.com",
            }
        ],
        source="manual_import",
    )

    assert result["source"] == "manual_import"
    assert result["processed"] == 1
    assert result["created"] == 1
    assert result["duplicates"] == 0
    assert result["rejected"] == 0

    assert calls[0]["source"] == "manual_import"


def test_import_prospects_counts_duplicates(monkeypatch):
    def fake_create_lead(data):
        return {
            "created": False,
            "duplicate": True,
            "duplicate_id": "existing-lead-id",
            "message": "Ce prospect existe déjà",
        }

    monkeypatch.setattr(
        "app.services.discovery.discovery_service.create_lead",
        fake_create_lead,
    )

    result = import_prospects(
        prospects=[
            {
                "company_name": "Entreprise Existante",
            }
        ],
        source="api",
    )

    assert result["processed"] == 1
    assert result["created"] == 0
    assert result["duplicates"] == 1
    assert result["rejected"] == 0


def test_import_prospects_rejects_invalid_prospect(monkeypatch):
    def fake_create_lead(data):
        raise ValueError("Adresse email invalide")

    monkeypatch.setattr(
        "app.services.discovery.discovery_service.create_lead",
        fake_create_lead,
    )

    result = import_prospects(
        prospects=[
            {
                "company_name": "Entreprise Invalide",
                "email": "invalid",
            }
        ],
        source="api",
    )

    assert result["processed"] == 1
    assert result["created"] == 0
    assert result["duplicates"] == 0
    assert result["rejected"] == 1
    assert result["results"][0]["reason"] == "Adresse email invalide"


def test_import_prospects_rejects_non_dict():
    result = import_prospects(
        prospects=["invalid-prospect"],
        source="api",
    )

    assert result["processed"] == 1
    assert result["created"] == 0
    assert result["duplicates"] == 0
    assert result["rejected"] == 1


def test_import_prospects_requires_source():
    with pytest.raises(
        ValueError,
        match="source de découverte est requise",
    ):
        import_prospects(
            prospects=[],
            source="",
        )


def test_import_prospects_requires_prospects():
    with pytest.raises(
        ValueError,
        match="liste des prospects est requise",
    ):
        import_prospects(
            prospects=None,
            source="api",
        )
