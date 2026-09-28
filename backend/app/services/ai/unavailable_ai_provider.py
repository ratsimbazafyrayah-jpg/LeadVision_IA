from app.schemas.ai_analysis import AIAnalysisResponse
from app.schemas.ai_analysis_input import AIAnalysisInput
from app.services.ai.ai_provider import AIProvider


class UnavailableAIProvider(AIProvider):
    """
    Provider utilisé lorsque la configuration du provider AI
    n'est pas disponible.

    Tsy mamorona résultat AI fake.
    """

    def __init__(self):
        self.http_client = None

    def analyze(
        self,
        data: AIAnalysisInput,
    ) -> AIAnalysisResponse:
        raise RuntimeError(
            "Le provider AI n'est pas configuré."
        )
