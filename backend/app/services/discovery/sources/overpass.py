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
        fallback_endpoints: Iterable[str] | None = None,
    ):
        if http_client is None:
            raise TypeError("http_client est requis.")
        if not endpoint or not endpoint.strip():
            raise ValueError("L'endpoint Overpass est requis.")

        self.http_client = http_client
        self.endpoint = endpoint.strip()
        self.timeout = timeout
        self.fallback_endpoints = [
            fallback.strip()
            for fallback in (fallback_endpoints or [])
            if isinstance(fallback, str) and fallback.strip()
        ]

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

        discovery_context = dict(context or {})
        discovery_context.setdefault("search_query", query.strip())

        overpass_query = self._build_query(
            query.strip(),
            context=discovery_context,
        )

        endpoints = [self.endpoint, *self.fallback_endpoints]
        last_error = None

        for endpoint in endpoints:
            try:
                response = self.http_client.post(
                    endpoint,
                    data=overpass_query,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                break
            except (
                httpx.TimeoutException,
                httpx.HTTPStatusError,
                httpx.RequestError,
            ) as exc:
                last_error = exc
        else:
            if isinstance(last_error, httpx.TimeoutException):
                raise RuntimeError(
                    "La source Overpass a dépassé le délai d'attente."
                ) from last_error

            if isinstance(last_error, httpx.HTTPStatusError):
                raise RuntimeError(
                    "La source Overpass a retourné une erreur HTTP."
                ) from last_error

            raise RuntimeError(
                "La source Overpass est indisponible."
            ) from last_error

        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError("La réponse Overpass doit être un objet JSON.")

        elements = payload.get("elements", [])

        if not isinstance(elements, list):
            raise ValueError("Le champ elements de la réponse Overpass est invalide.")

        return self._map_elements(
            elements,
            context=discovery_context,
        )

    def close(self) -> None:
        close = getattr(self.http_client, "close", None)

        if callable(close):
            close()

    @staticmethod
    def _build_query(
        query: str,
        context: Dict[str, Any] | None = None,
    ) -> str:
        if not query or not query.strip():
            raise ValueError("La requête de découverte est requise.")

        context = context or {}

        def escape(value: str) -> str:
            return (
                value.replace("\\", "\\\\")
                .replace('"', '\\"')
            )

        # Backward-compatible behavior for direct source usage/tests.
        # Structured filters are only applied when discovery context exists.
        if not context:
            escaped_query = escape(query.strip())

            return f"""
[out:json][timeout:25];
(
  nwr["name"~"{escaped_query}",i];
);
out center tags;
""".strip()

        country = context.get("country")
        city = context.get("city")
        region = context.get("region")
        sector = context.get("sector")
        search_query = context.get("search_query") or query
        boundingbox = context.get("boundingbox")

        if isinstance(boundingbox, dict):
            required_keys = ("south", "west", "north", "east")

            if all(key in boundingbox for key in required_keys):
                try:
                    south = float(boundingbox["south"])
                    west = float(boundingbox["west"])
                    north = float(boundingbox["north"])
                    east = float(boundingbox["east"])
                except (TypeError, ValueError):
                    pass
                else:
                    if south <= north and west <= east:
                        sector_key = (
                            sector.strip().lower()
                            if isinstance(sector, str)
                            else ""
                        )

                        sector_filters = {
                            "restaurant": '["amenity"="restaurant"]',
                            "cafe": '["amenity"="cafe"]',
                            "bar": '["amenity"="bar"]',
                            "hotel": '["tourism"="hotel"]',
                            "pharmacy": '["amenity"="pharmacy"]',
                            "hospital": '["amenity"="hospital"]',
                        }

                        sector_filter = sector_filters.get(sector_key)
                        escaped_search_query = escape(str(search_query).strip())

                        normalized_search_query = (
                            str(search_query).strip().lower()
                            if search_query is not None
                            else ""
                        )

                        use_name_filter = bool(normalized_search_query) and (
                            not sector_key
                            or normalized_search_query != sector_key
                        )

                        name_filter = (
                            f'["name"~"{escaped_search_query}",i]'
                            if use_name_filter
                            else ""
                        )

                        return f"""
[out:json][timeout:25];
(
  nwr{sector_filter or ""}{name_filter}({south},{west},{north},{east});
);
out center tags;
""".strip()

        geographic_name = city or region or country

        sector_key = (
            sector.strip().lower()
            if isinstance(sector, str)
            else ""
        )

        sector_filters = {
            "restaurant": '["amenity"="restaurant"]',
            "cafe": '["amenity"="cafe"]',
            "bar": '["amenity"="bar"]',
            "hotel": '["tourism"="hotel"]',
            "pharmacy": '["amenity"="pharmacy"]',
            "hospital": '["amenity"="hospital"]',
        }

        sector_filter = sector_filters.get(sector_key)

        escaped_search_query = escape(str(search_query).strip())

        if geographic_name:
            escaped_geographic_name = escape(
                str(geographic_name).strip()
            )

            object_filter = sector_filter or ""

            # When the search query is exactly the selected sector,
            # the sector filter already represents the requested search.
            # A name filter would incorrectly require the sector name
            # to appear in the OSM object's name.
            normalized_search_query = (
                str(search_query).strip().lower()
                if search_query is not None
                else ""
            )
            use_name_filter = bool(normalized_search_query) and (
                not sector_key
                or normalized_search_query != sector_key
            )

            name_filter = (
                f'["name"~"{escaped_search_query}",i]'
                if use_name_filter
                else ""
            )

            return f"""
[out:json][timeout:25];
area["name"="{escaped_geographic_name}"]->.searchArea;
(
  nwr{object_filter}{name_filter}(area.searchArea);
);
out center tags;
""".strip()

        object_filter = ""
        name_filter = f'["name"~"{escaped_search_query}",i]'

        return f"""
[out:json][timeout:25];
(
  nwr{object_filter}{name_filter};
);
out center tags;
""".strip()

    @staticmethod
    def _map_elements(
        elements: list,
        context: Dict[str, Any] | None = None,
    ) -> Iterable[Dict[str, Any]]:
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
            }

            for lead_field, osm_field in field_mapping.items():
                value = tags.get(osm_field)

                if isinstance(value, str) and value.strip():
                    lead[lead_field] = value.strip()

            requested_sector = (context or {}).get("sector")

            if isinstance(requested_sector, str) and requested_sector.strip():
                lead["sector"] = requested_sector.strip()

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
