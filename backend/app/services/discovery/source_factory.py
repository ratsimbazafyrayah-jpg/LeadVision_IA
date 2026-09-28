import httpx

from app.config import get_settings
from app.services.discovery.sources.geoapify import GeoapifyDiscoverySource
from app.services.discovery.sources.overpass import OverpassDiscoverySource


def build_discovery_sources():
    settings = get_settings()

    http_client = httpx.Client(
        headers={
            "User-Agent": "LeadVision_IA/1.0 (academic project)",
            "Accept": "application/json",
        }
    )

    sources = [
        OverpassDiscoverySource(
            http_client=http_client,
        )
    ]

    if settings.geoapify_api_key:
        sources.append(
            GeoapifyDiscoverySource(
                http_client=http_client,
            )
        )

    return sources
