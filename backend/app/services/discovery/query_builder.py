from typing import Optional

from app.schemas.discovery import DiscoverySearchRequest


def build_discovery_query(
    request: Optional[DiscoverySearchRequest],
) -> str:
    if request is None:
        raise ValueError("La requête de découverte est requise.")

    parts = [
        request.query,
        request.country,
        request.city,
        request.region,
        request.sector,
    ]

    return " ".join(
        part.strip()
        for part in parts
        if isinstance(part, str) and part.strip()
    )
