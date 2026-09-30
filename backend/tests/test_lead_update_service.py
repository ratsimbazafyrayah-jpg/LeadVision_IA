from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.services import lead_service


def test_update_lead_requires_valid_lead_id():
    with pytest.raises(ValueError, match="Identifiant du lead invalide"):
        lead_service.update_lead(
            "invalid-id",
            {"company_name": "Entreprise Test"},
        )


def test_update_lead_returns_none_when_lead_does_not_exist(monkeypatch):
    collection = MagicMock()
    collection.find_one.return_value = None

    monkeypatch.setattr(
        lead_service,
        "leads_collection",
        collection,
    )

    result = lead_service.update_lead(
        "507f1f77bcf86cd799439011",
        {"company_name": "Entreprise Test"},
    )

    assert result is None
    collection.update_one.assert_not_called()


def test_update_lead_normalizes_and_validates_fields(monkeypatch):
    existing = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Ancienne Entreprise",
        "email": "old@example.com",
        "website": "https://old.example.com",
    }

    collection = MagicMock()
    collection.find_one.side_effect = [
        existing,
        None,
        None,
    ]

    monkeypatch.setattr(
        lead_service,
        "leads_collection",
        collection,
    )

    result = lead_service.update_lead(
        "507f1f77bcf86cd799439011",
        {
            "company_name": "  Nouvelle   Entreprise  ",
            "email": "  NEW@Example.COM  ",
            "website": "new.example.com",
        },
    )

    assert result["company_name"] == "Nouvelle Entreprise"
    assert result["email"] == "new@example.com"
    assert result["website"] == "https://new.example.com"

    collection.update_one.assert_called_once()


def test_update_lead_rejects_invalid_email(monkeypatch):
    collection = MagicMock()
    collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
    }

    monkeypatch.setattr(
        lead_service,
        "leads_collection",
        collection,
    )

    with pytest.raises(ValueError, match="Adresse email invalide"):
        lead_service.update_lead(
            "507f1f77bcf86cd799439011",
            {"email": "email-invalide"},
        )

    collection.update_one.assert_not_called()


def test_update_lead_preserves_created_at(monkeypatch):
    created_at = datetime(2026, 1, 1)

    collection = MagicMock()
    collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
        "created_at": created_at,
    }

    monkeypatch.setattr(
        lead_service,
        "leads_collection",
        collection,
    )

    lead_service.update_lead(
        "507f1f77bcf86cd799439011",
        {"company_name": "Entreprise Modifiée"},
    )

    update = collection.update_one.call_args.args[1]

    assert "created_at" not in update["$set"]
    assert "updated_at" in update["$set"]


def test_update_lead_rejects_invalid_phone(monkeypatch):
    collection = MagicMock()
    collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
    }

    monkeypatch.setattr(
        lead_service,
        "leads_collection",
        collection,
    )

    with pytest.raises(ValueError, match="Numéro de téléphone invalide"):
        lead_service.update_lead(
            "507f1f77bcf86cd799439011",
            {"phone": "abc123"},
        )

    collection.update_one.assert_not_called()


def test_update_lead_rejects_invalid_social_media(monkeypatch):
    collection = MagicMock()
    collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
    }

    monkeypatch.setattr(
        lead_service,
        "leads_collection",
        collection,
    )

    with pytest.raises(ValueError, match="Réseaux sociaux invalides"):
        lead_service.update_lead(
            "507f1f77bcf86cd799439011",
            {
                "social_media": {
                    "facebook": "adresse-invalide",
                }
            },
        )

    collection.update_one.assert_not_called()


def test_update_lead_rejects_duplicate_email(monkeypatch):
    existing = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
        "email": "old@example.com",
    }

    duplicate = {
        "_id": "507f1f77bcf86cd799439012",
        "company_name": "Autre Entreprise",
        "email": "new@example.com",
    }

    collection = MagicMock()
    collection.find_one.side_effect = [
        existing,
        duplicate,
    ]

    monkeypatch.setattr(
        lead_service,
        "leads_collection",
        collection,
    )

    with pytest.raises(ValueError, match="Ce prospect existe déjà"):
        lead_service.update_lead(
            "507f1f77bcf86cd799439011",
            {"email": "new@example.com"},
        )

    collection.update_one.assert_not_called()


def test_update_lead_rejects_duplicate_website(monkeypatch):
    existing = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Entreprise Test",
        "website": "https://ancien.example.com",
    }

    duplicate = {
        "_id": "507f1f77bcf86cd799439012",
        "company_name": "Autre Entreprise",
        "website": "https://nouveau.example.com",
    }

    collection = MagicMock()
    collection.find_one.side_effect = [
        existing,
        duplicate,
    ]

    monkeypatch.setattr(
        lead_service,
        "leads_collection",
        collection,
    )

    with pytest.raises(ValueError, match="Ce prospect existe déjà"):
        lead_service.update_lead(
            "507f1f77bcf86cd799439011",
            {"website": "nouveau.example.com"},
        )

    collection.update_one.assert_not_called()


def test_update_lead_rejects_duplicate_company_and_city(monkeypatch):
    existing = {
        "_id": "507f1f77bcf86cd799439011",
        "company_name": "Ancienne Entreprise",
        "city": "Antananarivo",
    }

    duplicate = {
        "_id": "507f1f77bcf86cd799439012",
        "company_name": "Nouvelle Entreprise",
        "city": "Antananarivo",
    }

    collection = MagicMock()
    collection.find_one.side_effect = [
        existing,
        duplicate,
    ]

    monkeypatch.setattr(
        lead_service,
        "leads_collection",
        collection,
    )

    with pytest.raises(ValueError, match="Ce prospect existe déjà"):
        lead_service.update_lead(
            "507f1f77bcf86cd799439011",
            {
                "company_name": "Nouvelle Entreprise",
                "city": "Antananarivo",
            },
        )

    collection.update_one.assert_not_called()
