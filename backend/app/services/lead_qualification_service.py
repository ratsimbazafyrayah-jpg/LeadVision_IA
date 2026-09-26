from typing import Dict, Any

from app.services.lead_validation_service import (
    validate_email,
    validate_url,
    validate_phone,
    validate_social_media,
)


def qualify_lead(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Qualification basée uniquement sur les données réellement
    disponibles et leur validité.

    Aucun score commercial n'est généré ici.
    """

    evidence = []
    missing_data = []
    invalid_data = []
    validated_fields = []

    # -------------------------
    # Company name
    # -------------------------

    if lead.get("company_name"):
        evidence.append("company_name")
        validated_fields.append("company_name")
    else:
        missing_data.append("company_name")

    # -------------------------
    # Sector
    # -------------------------

    if lead.get("sector"):
        evidence.append("sector")
        validated_fields.append("sector")
    else:
        missing_data.append("sector")

    # -------------------------
    # Country
    # -------------------------

    if lead.get("country"):
        evidence.append("country")
        validated_fields.append("country")
    else:
        missing_data.append("country")

    # -------------------------
    # City
    # -------------------------

    if lead.get("city"):
        evidence.append("city")
        validated_fields.append("city")
    else:
        missing_data.append("city")

    # -------------------------
    # Website
    # -------------------------

    website = lead.get("website")

    if website:
        if validate_url(website):
            evidence.append("website")
            validated_fields.append("website")
        else:
            invalid_data.append("website")
    else:
        missing_data.append("website")

    # -------------------------
    # Email
    # -------------------------

    email = lead.get("email")

    if email:
        if validate_email(email):
            evidence.append("email")
            validated_fields.append("email")
        else:
            invalid_data.append("email")
    else:
        missing_data.append("email")

    # -------------------------
    # Phone
    # -------------------------

    phone = lead.get("phone")

    if phone:
        if validate_phone(phone):
            evidence.append("phone")
            validated_fields.append("phone")
        else:
            invalid_data.append("phone")
    else:
        missing_data.append("phone")

    # -------------------------
    # Social media
    # -------------------------

    social_media = lead.get("social_media") or {}

    social_validation = validate_social_media(social_media)

    valid_socials = social_validation["valid"]
    invalid_socials = social_validation["invalid"]

    if valid_socials:
        evidence.append("social_media")
        validated_fields.append("social_media")

    if invalid_socials:
        invalid_data.append("social_media")

    if not valid_socials and not invalid_socials:
        missing_data.append("social_media")

    # -------------------------
    # Complétude des données
    # -------------------------

    total_fields = (
        len(evidence)
        + len(missing_data)
        + len(invalid_data)
    )

    if total_fields > 0:
        data_completeness = round(
            (len(evidence) / total_fields) * 100,
            2
        )
    else:
        data_completeness = None

    # -------------------------
    # Qualification
    # -------------------------

    if not evidence:
        qualification = None
        status = "insufficient_data"

    elif invalid_data:
        qualification = "partially_qualified"
        status = "data_requires_validation"

    elif missing_data:
        qualification = "partially_qualified"
        status = "data_incomplete"

    else:
        qualification = "complete"
        status = "data_complete"

    return {
        "qualification": qualification,
        "status": status,
        "data_completeness": data_completeness,
        "evidence": evidence,
        "validated_fields": validated_fields,
        "missing_data": missing_data,
        "invalid_data": invalid_data,
        "social_platforms_found": valid_socials,
        "social_platforms_invalid": invalid_socials,
    }
