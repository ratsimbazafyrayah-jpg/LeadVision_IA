from bson import ObjectId

from app.database.mongodb import db
from app.models.lead import build_lead_document
from app.services.lead_validation_service import (
    normalize_email,
    normalize_text,
    normalize_url,
    validate_email,
    validate_url,
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
