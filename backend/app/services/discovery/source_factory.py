import httpx

from app.services.discovery.sources.overpass import OverpassDiscoverySource


def build_discovery_sources():
    http_client = httpx.Client(
        headers={
            "User-Agent": "LeadVision_IA/1.0 (academic project)",
            "Accept": "application/json",
        }
    )

    return [
        OverpassDiscoverySource(
            http_client=http_client,
        )
    ]
