from typing import Any, Dict, Optional

import httpx

from app.config import get_settings


class GeoapifyGeocodingService:
    """
    Service de géocodage basé sur l'API Geoapify.

    Les coordonnées retournées doivent provenir exclusivement
    de la réponse réelle de Geoapify.
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

    def geocode(
        self,
        country: str | None = None,
        city: str | None = None,
        region: str | None = None,
    ) -> Optional[Dict[str, Any]]:
        parts = [
            value.strip()
            for value in (city, region, country)
            if isinstance(value, str) and value.strip()
        ]

        if not parts:
            raise ValueError(
                "Au moins un pays, une ville ou une région est requis."
            )

        params = {
            "text": ", ".join(parts),
            "apiKey": self.api_key,
            "limit": 1,
        }

        try:
            response = self.http_client.get(
                f"{self.base_url}/v1/geocode/search",
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "Le géocodage Geoapify a dépassé le délai d'attente."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "Le géocodage Geoapify a retourné une erreur HTTP."
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(
                "Le service de géocodage Geoapify est indisponible."
            ) from exc

        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "La réponse du géocodage Geoapify doit être un objet JSON."
            )

        features = payload.get("features", [])

        if not isinstance(features, list):
            raise ValueError(
                "Le champ features du géocodage Geoapify est invalide."
            )

        if not features:
            return None

        feature = features[0]

        if not isinstance(feature, dict):
            raise ValueError(
                "Le premier résultat du géocodage Geoapify est invalide."
            )

        properties = feature.get("properties")

        if not isinstance(properties, dict):
            raise ValueError(
                "Les propriétés du résultat de géocodage sont invalides."
            )

        lat = properties.get("lat")
        lon = properties.get("lon")

        if not isinstance(lat, (int, float)) or not isinstance(
            lon, (int, float)
        ):
            return None

        result = {
            "lat": lat,
            "lon": lon,
        }

        place_id = properties.get("place_id")
        if isinstance(place_id, str) and place_id.strip():
            result["place_id"] = place_id.strip()

        return result

    def close(self) -> None:
        close = getattr(self.http_client, "close", None)

        if callable(close):
            close()
