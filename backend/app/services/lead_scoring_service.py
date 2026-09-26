from typing import Dict, Any

from app.services.lead_validation_service import (
    validate_email,
    validate_url,
    validate_phone,
    validate_social_media,
)


def calculate_lead_score(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Évalue la qualité des données réellement disponibles.

    Important :
    - data_quality_score mesure la qualité des données.
    - commercial_score reste None tant qu'aucun signal
      commercial réel n'est disponible.
    - final_score reste None dans ce cas.
    """

    factors = []
    missing_data = []
    invalid_data = []

    # =========================================================
    # 1. CRITÈRES ÉVALUÉS
    # =========================================================

    fields = [
        "company_name",
        "sector",
        "country",
        "city",
        "website",
        "email",
        "phone",
        "social_media",
    ]

    total_fields = len(fields)
    valid_fields = 0

    # =========================================================
    # 2. INFORMATIONS ENTREPRISE
    # =========================================================

    company_fields = {
        "company_name": lead.get("company_name"),
        "sector": lead.get("sector"),
        "country": lead.get("country"),
        "city": lead.get("city"),
    }

    for field, value in company_fields.items():

        if value:
            valid_fields += 1

            factors.append({
                "factor": field,
                "category": "business_information",
                "status": "valid",
                "evidence": True,
            })

        else:
            missing_data.append(field)

            factors.append({
                "factor": field,
                "category": "business_information",
                "status": "missing",
                "evidence": False,
            })

    # =========================================================
    # 3. WEBSITE
    # =========================================================

    website = lead.get("website")

    if website:

        if validate_url(website):
            valid_fields += 1

            factors.append({
                "factor": "website",
                "category": "digital_presence",
                "status": "valid",
                "evidence": True,
            })

        else:
            invalid_data.append("website")

            factors.append({
                "factor": "website",
                "category": "digital_presence",
                "status": "invalid",
                "evidence": False,
            })

    else:
        missing_data.append("website")

        factors.append({
            "factor": "website",
            "category": "digital_presence",
            "status": "missing",
            "evidence": False,
        })

    # =========================================================
    # 4. EMAIL
    # =========================================================

    email = lead.get("email")

    if email:

        if validate_email(email):
            valid_fields += 1

            factors.append({
                "factor": "email",
                "category": "contact_information",
                "status": "valid",
                "evidence": True,
            })

        else:
            invalid_data.append("email")

            factors.append({
                "factor": "email",
                "category": "contact_information",
                "status": "invalid",
                "evidence": False,
            })

    else:
        missing_data.append("email")

        factors.append({
            "factor": "email",
            "category": "contact_information",
            "status": "missing",
            "evidence": False,
        })

    # =========================================================
    # 5. TÉLÉPHONE
    # =========================================================

    phone = lead.get("phone")

    if phone:

        if validate_phone(phone):
            valid_fields += 1

            factors.append({
                "factor": "phone",
                "category": "contact_information",
                "status": "valid",
                "evidence": True,
            })

        else:
            invalid_data.append("phone")

            factors.append({
                "factor": "phone",
                "category": "contact_information",
                "status": "invalid",
                "evidence": False,
            })

    else:
        missing_data.append("phone")

        factors.append({
            "factor": "phone",
            "category": "contact_information",
            "status": "missing",
            "evidence": False,
        })

    # =========================================================
    # 6. RÉSEAUX SOCIAUX
    # =========================================================

    social_media = lead.get("social_media") or {}

    social_validation = validate_social_media(social_media)

    valid_socials = social_validation["valid"]
    invalid_socials = social_validation["invalid"]

    if valid_socials:

        valid_fields += 1

        factors.append({
            "factor": "social_media",
            "category": "digital_presence",
            "status": "valid",
            "platforms": valid_socials,
            "evidence": True,
        })

    elif invalid_socials:

        invalid_data.append("social_media")

        factors.append({
            "factor": "social_media",
            "category": "digital_presence",
            "status": "invalid",
            "platforms": invalid_socials,
            "evidence": False,
        })

    else:
        missing_data.append("social_media")

        factors.append({
            "factor": "social_media",
            "category": "digital_presence",
            "status": "missing",
            "evidence": False,
        })

    # =========================================================
    # 7. DATA QUALITY SCORE
    # =========================================================

    data_quality_score = round(
        (valid_fields / total_fields) * 100,
        2
    )

    # =========================================================
    # 8. COMMERCIAL SCORE
    # =========================================================

    # Aucun signal commercial réel n'est actuellement
    # disponible dans le modèle LeadVision_IA.

    commercial_signals = []

    commercial_score = None
    commercial_status = "insufficient_signals"

    # =========================================================
    # 9. CONFIDENCE
    # =========================================================

    confidence = data_quality_score

    # =========================================================
    # 10. DATA STATUS
    # =========================================================

    if invalid_data:
        data_status = "data_requires_validation"

    elif missing_data:
        data_status = "data_incomplete"

    else:
        data_status = "data_complete"

    # =========================================================
    # 11. FINAL SCORE
    # =========================================================

    final_score = None

    # Aucun final_score ne doit être calculé tant qu'il n'existe
    # pas de signaux commerciaux réels.

    # =========================================================
    # 12. RESULTAT
    # =========================================================

    return {
        "data_quality_score": data_quality_score,
        "data_status": data_status,

        "commercial_score": commercial_score,
        "commercial_status": commercial_status,

        "final_score": final_score,

        "confidence": confidence,

        "commercial_signals": commercial_signals,

        "factors": factors,

        "missing_data": missing_data,
        "invalid_data": invalid_data,

        "social_platforms_found": valid_socials,
        "social_platforms_invalid": invalid_socials,
    }
