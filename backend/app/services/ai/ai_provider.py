from abc import ABC, abstractmethod

from app.schemas.ai_analysis import AIAnalysisResponse
from app.schemas.ai_analysis_input import AIAnalysisInput


class AIProvider(ABC):
    """
    Contract abstrait pour tout provider d'analyse AI.

    AIAnalysisService dépend uniquement de ce contrat.
    Le provider concret pourra être OpenRouter, un autre
    fournisseur ou un provider de test.
    """

    @abstractmethod
    def analyze(
        self,
        data: AIAnalysisInput,
    ) -> AIAnalysisResponse:
        """
        Analyse les données Lead Intelligence et retourne
        une réponse AI structurée.

        Les providers concrets doivent implémenter cette méthode.
        """
        raise NotImplementedError
