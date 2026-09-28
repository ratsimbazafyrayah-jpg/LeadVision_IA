from typing import Any, Dict, Optional

import httpx

from app.config import get_settings


class NominatimGeocodingService:
    """
    Service de géocodage basé sur Nominatim/OpenStreetMap.

    Les coordonnées et la bounding box retournées doivent provenir
    exclusivement de la réponse réelle de Nominatim.
    """

    DEFAULT_TIMEOUT = 15.0

    def __init__(
        self,
        http_client: Any,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        if http_client is None:
            raise TypeError("http_client est requis.")

        settings = get_settings()
        resolved_base_url = base_url or settings.nominatim_base_url

        if not resolved_base_url or not resolved_base_url.strip():
            raise ValueError("L'URL de base Nominatim est requise.")

        self.http_client = http_client
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
            "q": ", ".join(parts),
            "format": "jsonv2",
            "limit": 1,
            "addressdetails": 1,
        }

        try:
            response = self.http_client.get(
                f"{self.base_url}/search",
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "Le géocodage Nominatim a dépassé le délai d'attente."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "Le géocodage Nominatim a retourné une erreur HTTP."
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(
                "Le service de géocodage Nominatim est indisponible."
            ) from exc

        payload = response.json()

        if not isinstance(payload, list):
            raise ValueError(
                "La réponse du géocodage Nominatim doit être une liste JSON."
            )

        if not payload:
            return None

        result = payload[0]

        if not isinstance(result, dict):
            raise ValueError(
                "Le premier résultat de géocodage Nominatim est invalide."
            )

        lat = result.get("lat")
        lon = result.get("lon")
        boundingbox = result.get("boundingbox")

        if not isinstance(lat, str) or not isinstance(lon, str):
            return None

        if not isinstance(boundingbox, list) or len(boundingbox) != 4:
            return None

        try:
            latitude = float(lat)
            longitude = float(lon)
            south = float(boundingbox[0])
            north = float(boundingbox[1])
            west = float(boundingbox[2])
            east = float(boundingbox[3])
        except (TypeError, ValueError):
            return None

        return {
            "lat": latitude,
            "lon": longitude,
            "boundingbox": {
                "south": south,
                "west": west,
                "north": north,
                "east": east,
            },
        }

    def close(self) -> None:
        close = getattr(self.http_client, "close", None)

        if callable(close):
            close()
