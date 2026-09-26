from datetime import datetime, timezone


def build_lead_document(data: dict) -> dict:
    now = datetime.now(timezone.utc)

    return {
        "company_name": data["company_name"],
        "sector": data.get("sector"),
        "country": data.get("country"),
        "city": data.get("city"),
        "website": data.get("website"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "social_media": data.get("social_media") or {},
        "source": data.get("source"),
        "status": "new",
        "score": None,
        "qualification": None,
        "analysis": None,
        "recommendations": [],
        "notes": data.get("notes"),
        "created_at": now,
        "updated_at": now,
    }
