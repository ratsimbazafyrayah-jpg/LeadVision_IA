from typing import Any, Dict, Iterable

import httpx

from app.config import get_settings
from app.services.discovery.geoapify_geocoding import GeoapifyGeocodingService
from app.services.discovery.sources.base import DiscoverySource


class GeoapifyDiscoverySource(DiscoverySource):
    """
    Source de découverte basée sur Geoapify Places API.

    Les données retournées sont limitées aux informations réellement
    présentes dans la réponse Geoapify.
    """

    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        http_client: Any,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        if http_client is None:
            raise TypeError("http_client est requis.")

        settings = get_settings()

        resolved_api_key = api_key or settings.geoapify_api_key
        resolved_base_url = base_url or settings.geoapify_base_url

        if not resolved_api_key:
            raise ValueError("La clé API Geoapify est requise.")

        if not resolved_base_url or not resolved_base_url.strip():
            raise ValueError("L'URL de base Geoapify est requise.")

        self.http_client = http_client
        self.api_key = resolved_api_key
        self.base_url = resolved_base_url.rstrip("/")
        self.timeout = timeout

        self.geocoding_service = GeoapifyGeocodingService(
            http_client=http_client,
            api_key=resolved_api_key,
            base_url=self.base_url,
            timeout=timeout,
        )

    @property
    def name(self) -> str:
        return "geoapify"

    def discover(
        self,
        query: str,
        context: Dict[str, Any] | None = None,
    ) -> Iterable[Dict[str, Any]]:
        if not query or not query.strip():
            raise ValueError("La requête de découverte est requise.")

        context = context or {}

        country = context.get("country")
        city = context.get("city")
        region = context.get("region")
        sector = context.get("sector")

        location = self.geocoding_service.geocode(
            country=country,
            city=city,
            region=region,
        )

        if location is None:
            return []

        place_id = location.get("place_id")

        if not isinstance(place_id, str) or not place_id.strip():
            return []

        params = {
            "categories": sector.strip() if isinstance(sector, str) and sector.strip() else "commercial",
            "filter": f"place:{place_id.strip()}",
            "limit": 20,
            "offset": 0,
            "apiKey": self.api_key,
        }

        if query.strip():
            params["name"] = query.strip()

        try:
            response = self.http_client.get(
                f"{self.base_url}/v2/places",
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "La source Geoapify a dépassé le délai d'attente."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "La source Geoapify a retourné une erreur HTTP."
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(
                "La source Geoapify est indisponible."
            ) from exc

        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "La réponse Geoapify doit être un objet JSON."
            )

        features = payload.get("features", [])

        if not isinstance(features, list):
            raise ValueError(
                "Le champ features de la réponse Geoapify est invalide."
            )

        return self._map_features(features)

    def close(self) -> None:
        close = getattr(self.http_client, "close", None)

        if callable(close):
            close()

    @staticmethod
    def _map_features(features: list) -> Iterable[Dict[str, Any]]:
        for feature in features:
            if not isinstance(feature, dict):
                continue

            properties = feature.get("properties")

            if not isinstance(properties, dict):
                continue

            name = properties.get("name")

            if not isinstance(name, str) or not name.strip():
                continue

            lead: Dict[str, Any] = {
                "company_name": name.strip(),
                "source": "geoapify",
            }

            mapping = {
                "website": "website",
                "phone": "contact",
                "city": "city",
                "country": "country",
            }

            for lead_field, source_field in mapping.items():
                value = properties.get(source_field)

                if isinstance(value, str) and value.strip():
                    lead[lead_field] = value.strip()

            yield lead
