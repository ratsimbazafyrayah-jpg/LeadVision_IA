from typing import Any, Dict, Iterable

from app.schemas.discovery import DiscoverySearchRequest
from app.services.discovery.query_builder import build_discovery_query


def search_prospects(
    request: DiscoverySearchRequest,
    source: Any,
    geocoder: Any = None,
) -> Dict[str, Any]:
    if source is None:
        raise ValueError("La source de découverte est requise.")

    if source.name != request.source:
        raise ValueError(
            "La source sélectionnée ne correspond pas à la source fournie."
        )

    filters = {
        "country": request.country,
        "city": request.city,
        "region": request.region,
        "sector": request.sector,
    }

    discovery_query = build_discovery_query(request)

    discovery_context = {
        **filters,
        "search_query": request.query,
    }

    if geocoder is not None:
        geocoding_result = geocoder.geocode(
            country=request.country,
            city=request.city,
            region=request.region,
        )

        if isinstance(geocoding_result, dict):
            boundingbox = geocoding_result.get("boundingbox")

            if isinstance(boundingbox, dict):
                discovery_context["boundingbox"] = boundingbox

    prospects: Iterable[Dict[str, Any]] = source.discover(
        discovery_query,
        context=discovery_context,
    )
    prospects = list(prospects)

    return {
        "source": request.source,
        "query": request.query,
        "filters": filters,
        "processed": len(prospects),
        "prospects": prospects,
    }
