from datetime import datetime, timezone

from bson import ObjectId

from app.database.mongodb import db
from app.services.lead_validation_service import (
    normalize_email,
    normalize_text,
    normalize_url,
    validate_email,
    validate_phone,
    validate_url,
)


leads_collection = db["leads"]


def enrich_lead(
    lead_id: str,
    enrichment_service,
):
    if not ObjectId.is_valid(lead_id):
        raise ValueError("Identifiant du lead invalide")

    lead = leads_collection.find_one({
        "_id": ObjectId(lead_id)
    })

    if not lead:
        return None

    website = lead.get("website")

    if not website:
        raise ValueError("Le lead ne possède pas de site web")

    enrichment = enrichment_service.enrich(website)

    update_data = {}
    updated_fields = []

    emails = enrichment.get("emails") or []

    if not lead.get("email") and emails:
        email = normalize_email(emails[0])

        if validate_email(email):
            update_data["email"] = email
            updated_fields.append("email")

    phones = enrichment.get("phones") or []

    if not lead.get("phone") and phones:
        phone = normalize_text(phones[0])

        if validate_phone(phone):
            update_data["phone"] = phone
            updated_fields.append("phone")

    existing_social_media = lead.get("social_media")

    if not isinstance(existing_social_media, dict):
        existing_social_media = {}

    social_links = enrichment.get("social_links") or {}

    if isinstance(social_links, dict):
        merged_social_media = dict(existing_social_media)
        social_media_updated = False

        for platform, links in social_links.items():
            if platform in merged_social_media:
                continue

            if not isinstance(links, list):
                continue

            for link in links:
                if not isinstance(link, str) or not link.strip():
                    continue

                normalized_link = normalize_url(link)

                if validate_url(normalized_link):
                    merged_social_media[platform] = normalized_link
                    social_media_updated = True
                    break

        if social_media_updated:
            update_data["social_media"] = merged_social_media
            updated_fields.append("social_media")

    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)

        leads_collection.update_one(
            {"_id": ObjectId(lead_id)},
            {"$set": update_data},
        )

    return {
        "lead_id": lead_id,
        "updated": bool(update_data),
        "updated_fields": updated_fields,
        "enrichment": enrichment,
    }
