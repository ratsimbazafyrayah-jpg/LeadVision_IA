import json
from typing import Any, Dict

import httpx

from app.config import get_settings
from app.schemas.ai_analysis import AIAnalysisResponse
from app.schemas.ai_analysis_input import AIAnalysisInput
from app.services.ai.ai_provider import AIProvider


class OpenRouterProvider(AIProvider):
    """
    Provider AI mampiasa OpenRouter.

    Ny API key sy model dia avy amin'ny configuration.
    Tsy misy secret na model hardcodé eto.
    """

    def __init__(
        self,
        http_client: Any,
        timeout: float = 30,
    ):
        if http_client is None:
            raise TypeError("http_client est requis.")

        settings = get_settings()

        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY est requis.")

        if not settings.openrouter_model:
            raise ValueError("OPENROUTER_MODEL est requis.")

        self.http_client = http_client
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url.rstrip("/")
        self.model = settings.openrouter_model
        self.timeout = timeout

    def analyze(
        self,
        data: AIAnalysisInput,
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Tu es un analyste commercial. "
                        "Analyse uniquement les données fournies. "
                        "N'invente aucune donnée, aucun score, "
                        "aucune evidence et aucune information."
                    ),
                },
                {
                    "role": "user",
                    "content": data.model_dump_json(),
                },
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self.http_client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            response_data = response.json()

            content = self._extract_content(response_data)

            validated = AIAnalysisResponse.model_validate(content)

            return validated.model_dump()

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Le provider OpenRouter est indisponible."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "Le provider OpenRouter a retourné une erreur HTTP."
            ) from exc

        except (ValueError, TypeError, KeyError) as exc:
            raise RuntimeError(
                "La réponse du provider OpenRouter est invalide."
            ) from exc

    @staticmethod
    def _extract_content(response_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            choices = response_data["choices"]

            if not choices:
                raise ValueError(
                    "La réponse OpenRouter ne contient aucun choix."
                )

            message = choices[0]["message"]
            content = message["content"]

        except (KeyError, TypeError) as exc:
            raise ValueError(
                "Réponse OpenRouter invalide ou incomplète."
            ) from exc

        if isinstance(content, dict):
            return content

        if isinstance(content, str):
            try:
                parsed_content = json.loads(content)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Le contenu retourné par OpenRouter "
                    "n'est pas un JSON valide."
                ) from exc

            if not isinstance(parsed_content, dict):
                raise ValueError(
                    "Le JSON retourné par OpenRouter "
                    "doit être un objet."
                )

            return parsed_content

        raise ValueError(
            "Le contenu retourné par OpenRouter doit être "
            "un objet JSON ou une chaîne JSON valide."
        )
