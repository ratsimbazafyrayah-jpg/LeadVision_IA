from unittest.mock import MagicMock

import pytest

from app.services.enrichment import lead_enrichment_service


def test_enrich_lead_requires_valid_lead_id():
    with pytest.raises(
        ValueError,
        match="Identifiant du lead invalide",
    ):
        lead_enrichment_service.enrich_lead(
            "invalid-id",
            MagicMock(),
        )


def test_enrich_lead_returns_none_when_lead_does_not_exist(monkeypatch):
    collection = MagicMock()
    collection.find_one.return_value = None

    monkeypatch.setattr(
        lead_enrichment_service,
        "leads_collection",
        collection,
    )

    enrichment_service = MagicMock()

    result = lead_enrichment_service.enrich_lead(
        "507f1f77bcf86cd799439011",
        enrichment_service,
    )

    assert result is None
    enrichment_service.enrich.assert_not_called()
    collection.update_one.assert_not_called()


def test_enrich_lead_requires_website(monkeypatch):
    collection = MagicMock()
    collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
        "website": None,
    }

    monkeypatch.setattr(
        lead_enrichment_service,
        "leads_collection",
        collection,
    )

    enrichment_service = MagicMock()

    with pytest.raises(
        ValueError,
        match="Le lead ne possède pas de site web",
    ):
        lead_enrichment_service.enrich_lead(
            "507f1f77bcf86cd799439011",
            enrichment_service,
        )

    enrichment_service.enrich.assert_not_called()
    collection.update_one.assert_not_called()


def test_enrich_lead_returns_real_enrichment_data(monkeypatch):
    collection = MagicMock()
    collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
        "website": "https://example.com",
    }

    monkeypatch.setattr(
        lead_enrichment_service,
        "leads_collection",
        collection,
    )

    enrichment_service = MagicMock()
    enrichment_service.enrich.return_value = {
        "website": "https://example.com",
        "final_url": "https://example.com/",
        "status_code": 200,
        "content_type": "text/html",
        "emails": ["contact@example.com"],
        "phones": ["+261341234567"],
        "social_links": {
            "facebook": ["https://facebook.com/example"],
            "instagram": [],
            "linkedin": [],
            "x": [],
            "youtube": [],
        },
    }

    result = lead_enrichment_service.enrich_lead(
        "507f1f77bcf86cd799439011",
        enrichment_service,
    )

    enrichment_service.enrich.assert_called_once_with(
        "https://example.com",
    )

    assert result["lead_id"] == "507f1f77bcf86cd799439011"
    assert result["enrichment"]["emails"] == ["contact@example.com"]
    assert result["enrichment"]["phones"] == ["+261341234567"]
    assert result["enrichment"]["social_links"]["facebook"] == [
        "https://facebook.com/example"
    ]

    update = collection.update_one.call_args.args[1]

    assert update["$set"]["email"] == "contact@example.com"
    assert update["$set"]["phone"] == "+261341234567"


def test_enrich_lead_updates_missing_email_and_phone(monkeypatch):
    existing = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
        "website": "https://example.com",
        "email": None,
        "phone": None,
    }

    collection = MagicMock()
    collection.find_one.return_value = existing

    monkeypatch.setattr(
        lead_enrichment_service,
        "leads_collection",
        collection,
    )

    enrichment_service = MagicMock()
    enrichment_service.enrich.return_value = {
        "website": "https://example.com",
        "final_url": "https://example.com/",
        "status_code": 200,
        "content_type": "text/html",
        "emails": ["contact@example.com"],
        "phones": ["+261341234567"],
        "social_links": {
            "facebook": [],
            "instagram": [],
            "linkedin": [],
            "x": [],
            "youtube": [],
        },
    }

    result = lead_enrichment_service.enrich_lead(
        "507f1f77bcf86cd799439011",
        enrichment_service,
    )

    update = collection.update_one.call_args.args[1]

    assert update["$set"]["email"] == "contact@example.com"
    assert update["$set"]["phone"] == "+261341234567"
    assert "updated_at" in update["$set"]

    assert result["updated"] is True
    assert result["updated_fields"] == ["email", "phone"]


def test_enrich_lead_does_not_overwrite_existing_email_and_phone(
    monkeypatch,
):
    existing = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
        "website": "https://example.com",
        "email": "existing@example.com",
        "phone": "+261331111111",
    }

    collection = MagicMock()
    collection.find_one.return_value = existing

    monkeypatch.setattr(
        lead_enrichment_service,
        "leads_collection",
        collection,
    )

    enrichment_service = MagicMock()
    enrichment_service.enrich.return_value = {
        "website": "https://example.com",
        "final_url": "https://example.com/",
        "status_code": 200,
        "content_type": "text/html",
        "emails": ["new@example.com"],
        "phones": ["+261342222222"],
        "social_links": {
            "facebook": [],
            "instagram": [],
            "linkedin": [],
            "x": [],
            "youtube": [],
        },
    }

    result = lead_enrichment_service.enrich_lead(
        "507f1f77bcf86cd799439011",
        enrichment_service,
    )

    collection.update_one.assert_not_called()

    assert result["updated"] is False
    assert result["updated_fields"] == []


def test_enrich_lead_adds_missing_social_links_without_overwriting_existing(
    monkeypatch,
):
    existing = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
        "website": "https://example.com",
        "email": "existing@example.com",
        "phone": "+261331111111",
        "social_media": {
            "facebook": "https://facebook.com/existing",
        },
    }

    collection = MagicMock()
    collection.find_one.return_value = existing

    monkeypatch.setattr(
        lead_enrichment_service,
        "leads_collection",
        collection,
    )

    enrichment_service = MagicMock()
    enrichment_service.enrich.return_value = {
        "website": "https://example.com",
        "final_url": "https://example.com/",
        "status_code": 200,
        "content_type": "text/html",
        "emails": [],
        "phones": [],
        "social_links": {
            "facebook": ["https://facebook.com/new"],
            "instagram": ["https://instagram.com/example"],
            "linkedin": ["https://linkedin.com/company/example"],
            "x": [],
            "youtube": [],
        },
    }

    result = lead_enrichment_service.enrich_lead(
        "507f1f77bcf86cd799439011",
        enrichment_service,
    )

    update = collection.update_one.call_args.args[1]

    assert update["$set"]["social_media"] == {
        "facebook": "https://facebook.com/existing",
        "instagram": "https://instagram.com/example",
        "linkedin": "https://linkedin.com/company/example",
    }

    assert result["updated"] is True
    assert result["updated_fields"] == ["social_media"]


def test_enrich_lead_does_not_update_when_no_new_data_is_found(
    monkeypatch,
):
    existing = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
        "website": "https://example.com",
        "email": "existing@example.com",
        "phone": "+261331111111",
        "social_media": {
            "facebook": "https://facebook.com/existing",
        },
    }

    collection = MagicMock()
    collection.find_one.return_value = existing

    monkeypatch.setattr(
        lead_enrichment_service,
        "leads_collection",
        collection,
    )

    enrichment_service = MagicMock()
    enrichment_service.enrich.return_value = {
        "website": "https://example.com",
        "final_url": "https://example.com/",
        "status_code": 200,
        "content_type": "text/html",
        "emails": [],
        "phones": [],
        "social_links": {
            "facebook": [],
            "instagram": [],
            "linkedin": [],
            "x": [],
            "youtube": [],
        },
    }

    result = lead_enrichment_service.enrich_lead(
        "507f1f77bcf86cd799439011",
        enrichment_service,
    )

    collection.update_one.assert_not_called()

    assert result["updated"] is False
    assert result["updated_fields"] == []


def test_enrich_lead_ignores_invalid_email_and_phone(
    monkeypatch,
):
    existing = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
        "website": "https://example.com",
        "email": None,
        "phone": None,
        "social_media": {},
    }

    collection = MagicMock()
    collection.find_one.return_value = existing

    monkeypatch.setattr(
        lead_enrichment_service,
        "leads_collection",
        collection,
    )

    enrichment_service = MagicMock()
    enrichment_service.enrich.return_value = {
        "website": "https://example.com",
        "final_url": "https://example.com/",
        "status_code": 200,
        "content_type": "text/html",
        "emails": ["email-invalide"],
        "phones": ["phone-invalide"],
        "social_links": {},
    }

    result = lead_enrichment_service.enrich_lead(
        "507f1f77bcf86cd799439011",
        enrichment_service,
    )

    collection.update_one.assert_not_called()

    assert result["updated"] is False
    assert result["updated_fields"] == []
