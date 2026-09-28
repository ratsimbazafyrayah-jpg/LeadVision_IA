from typing import Any, Dict, Iterable

import httpx

from app.services.discovery.sources.base import DiscoverySource


class OverpassDiscoverySource(DiscoverySource):
    """
    Source de découverte basée sur l'Overpass API / OpenStreetMap.

    La source retourne uniquement les informations réellement présentes
    dans les données OSM. Elle ne complète ni n'invente aucune donnée.
    """

    DEFAULT_URL = "https://overpass-api.de/api/interpreter"

    def __init__(
        self,
        http_client: Any,
        endpoint: str = DEFAULT_URL,
        timeout: float = 30.0,
    ):
        if http_client is None:
            raise TypeError("http_client est requis.")
        if not endpoint or not endpoint.strip():
            raise ValueError("L'endpoint Overpass est requis.")

        self.http_client = http_client
        self.endpoint = endpoint.strip()
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "overpass"

    def discover(
        self,
        query: str,
        context: Dict[str, Any] | None = None,
    ) -> Iterable[Dict[str, Any]]:
        if not query or not query.strip():
            raise ValueError("La requête de découverte est requise.")

        overpass_query = self._build_query(query.strip())

        try:
            response = self.http_client.post(
                self.endpoint,
                data=overpass_query,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "La source Overpass a dépassé le délai d'attente."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "La source Overpass a retourné une erreur HTTP."
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(
                "La source Overpass est indisponible."
            ) from exc

        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError("La réponse Overpass doit être un objet JSON.")

        elements = payload.get("elements", [])

        if not isinstance(elements, list):
            raise ValueError("Le champ elements de la réponse Overpass est invalide.")

        return self._map_elements(elements)

    def close(self) -> None:
        close = getattr(self.http_client, "close", None)

        if callable(close):
            close()

    @staticmethod
    def _build_query(query: str) -> str:
        escaped_query = (
            query.replace("\\", "\\\\")
            .replace('"', '\\"')
        )

        return f"""
[out:json][timeout:25];
(
  nwr["name"~"{escaped_query}", i];
);
out center tags;
""".strip()

    @staticmethod
    def _map_elements(elements: list) -> Iterable[Dict[str, Any]]:
        for element in elements:
            if not isinstance(element, dict):
                continue

            tags = element.get("tags")

            if not isinstance(tags, dict):
                continue

            company_name = tags.get("name")

            if not isinstance(company_name, str) or not company_name.strip():
                continue

            lead: Dict[str, Any] = {
                "company_name": company_name.strip(),
                "source": "overpass",
            }

            field_mapping = {
                "website": "website",
                "email": "email",
                "phone": "phone",
                "city": "addr:city",
                "country": "addr:country",
                "sector": "office",
            }

            for lead_field, osm_field in field_mapping.items():
                value = tags.get(osm_field)

                if isinstance(value, str) and value.strip():
                    lead[lead_field] = value.strip()

            social_media = {}

            social_mapping = {
                "facebook": "contact:facebook",
                "instagram": "contact:instagram",
                "twitter": "contact:twitter",
                "linkedin": "contact:linkedin",
            }

            for platform, osm_field in social_mapping.items():
                value = tags.get(osm_field)

                if isinstance(value, str) and value.strip():
                    social_media[platform] = value.strip()

            if social_media:
                lead["social_media"] = social_media

            yield lead
