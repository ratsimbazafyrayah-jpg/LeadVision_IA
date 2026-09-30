from datetime import datetime, timezone
from bson import ObjectId

from app.database.mongodb import db
from app.models.lead import build_lead_document
from app.services.lead_validation_service import (
    normalize_email,
    normalize_text,
    normalize_url,
    validate_email,
    validate_url,
    validate_phone,
    validate_social_media,
    find_duplicate_lead,
)


leads_collection = db["leads"]


def create_lead(data: dict):

    # Normalisation
    data["company_name"] = normalize_text(data.get("company_name"))

    if not data.get("company_name"):
        raise ValueError("Le nom de l'entreprise est requis.")

    data["sector"] = normalize_text(data.get("sector"))
    data["country"] = normalize_text(data.get("country"))
    data["city"] = normalize_text(data.get("city"))
    data["email"] = normalize_email(data.get("email"))
    data["website"] = normalize_url(data.get("website"))

    # Validation email
    if not validate_email(data.get("email")):
        raise ValueError("Adresse email invalide")

    # Validation website
    if not validate_url(data.get("website")):
        raise ValueError("URL du site web invalide")

    # Détection duplicate
    duplicate = find_duplicate_lead(
        email=data.get("email"),
        website=data.get("website"),
        company_name=data.get("company_name"),
        city=data.get("city"),
    )

    if duplicate:
        return {
            "created": False,
            "duplicate": True,
            "duplicate_id": str(duplicate["_id"]),
            "message": "Ce prospect existe déjà",
        }

    # Création du document
    document = build_lead_document(data)

    result = leads_collection.insert_one(document)

    document["_id"] = str(result.inserted_id)

    return {
        "created": True,
        "duplicate": False,
        "lead": document,
    }


def update_lead(lead_id: str, data: dict):
    if not ObjectId.is_valid(lead_id):
        raise ValueError("Identifiant du lead invalide")

    if not isinstance(data, dict):
        raise ValueError("Les données du lead sont invalides.")

    existing = leads_collection.find_one({
        "_id": ObjectId(lead_id)
    })

    if not existing:
        return None

    update_data = {}

    allowed_fields = {
        "company_name",
        "sector",
        "country",
        "city",
        "website",
        "email",
        "phone",
        "social_media",
        "source",
        "status",
        "notes",
    }

    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]

    if "company_name" in update_data:
        update_data["company_name"] = normalize_text(
            update_data["company_name"]
        )
        if not update_data["company_name"]:
            raise ValueError("Le nom de l'entreprise est requis.")

    if "sector" in update_data:
        update_data["sector"] = normalize_text(update_data["sector"])

    if "country" in update_data:
        update_data["country"] = normalize_text(update_data["country"])

    if "city" in update_data:
        update_data["city"] = normalize_text(update_data["city"])

    final_company_name = update_data.get(
        "company_name",
        existing.get("company_name"),
    )
    final_city = update_data.get(
        "city",
        existing.get("city"),
    )

    if final_company_name and final_city:
        duplicate = leads_collection.find_one({
            "company_name": final_company_name,
            "city": final_city,
            "_id": {"$ne": ObjectId(lead_id)},
        })

        if duplicate:
            raise ValueError("Ce prospect existe déjà")

    if "email" in update_data:
        update_data["email"] = normalize_email(update_data["email"])
        if not validate_email(update_data["email"]):
            raise ValueError("Adresse email invalide")

        duplicate = leads_collection.find_one({
            "email": update_data["email"],
            "_id": {"$ne": ObjectId(lead_id)},
        })

        if duplicate:
            raise ValueError("Ce prospect existe déjà")

    if "website" in update_data:
        update_data["website"] = normalize_url(update_data["website"])
        if not validate_url(update_data["website"]):
            raise ValueError("URL du site web invalide")

        duplicate = leads_collection.find_one({
            "website": update_data["website"],
            "_id": {"$ne": ObjectId(lead_id)},
        })

        if duplicate:
            raise ValueError("Ce prospect existe déjà")

    if "phone" in update_data:
        update_data["phone"] = normalize_text(update_data["phone"])
        if not validate_phone(update_data["phone"]):
            raise ValueError("Numéro de téléphone invalide")

    if "social_media" in update_data:
        social_validation = validate_social_media(
            update_data["social_media"]
        )
        if social_validation["invalid"]:
            raise ValueError("Réseaux sociaux invalides")

    update_data["updated_at"] = datetime.now(timezone.utc)

    leads_collection.update_one(
        {"_id": ObjectId(lead_id)},
        {"$set": update_data},
    )

    updated = dict(existing)
    updated.update(update_data)
    updated["_id"] = str(updated["_id"])

    return updated


def get_leads():
    leads = []

    for lead in leads_collection.find().sort("created_at", -1):
        lead["_id"] = str(lead["_id"])
        leads.append(lead)

    return leads


def get_lead(lead_id: str):

    if not ObjectId.is_valid(lead_id):
        return None

    lead = leads_collection.find_one({
        "_id": ObjectId(lead_id)
    })

    if lead:
        lead["_id"] = str(lead["_id"])

    return lead
