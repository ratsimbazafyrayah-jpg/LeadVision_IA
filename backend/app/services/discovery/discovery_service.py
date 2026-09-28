from typing import Any, Dict, Iterable

from app.services.lead_service import create_lead


def import_prospects(
    prospects: Iterable[Dict[str, Any]],
    source: str,
) -> Dict[str, Any]:
    """
    Importe des prospects collectés depuis une source identifiée.

    Le service ne crée aucune donnée métier.
    Chaque prospect est transmis au pipeline create_lead(),
    qui reste responsable de la normalisation, validation
    et déduplication.

    Returns:
        Un résumé technique de l'import.
    """
    if not source or not source.strip():
        raise ValueError("La source de découverte est requise.")

    if prospects is None:
        raise ValueError("La liste des prospects est requise.")

    result = {
        "source": source.strip(),
        "processed": 0,
        "created": 0,
        "duplicates": 0,
        "rejected": 0,
        "results": [],
    }

    for prospect in prospects:
        result["processed"] += 1

        if not isinstance(prospect, dict):
            result["rejected"] += 1
            result["results"].append({
                "created": False,
                "duplicate": False,
                "rejected": True,
                "reason": "Le prospect doit être un objet.",
            })
            continue

        data = dict(prospect)

        if not data.get("source"):
            data["source"] = source.strip()

        try:
            import_result = create_lead(data)
        except (ValueError, TypeError) as error:
            result["rejected"] += 1
            result["results"].append({
                "created": False,
                "duplicate": False,
                "rejected": True,
                "reason": str(error),
            })
            continue

        if import_result.get("created") is True:
            result["created"] += 1
        elif import_result.get("duplicate") is True:
            result["duplicates"] += 1

        result["results"].append({
            **import_result,
            "rejected": False,
        })

    return result
