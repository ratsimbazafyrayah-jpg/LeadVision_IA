from typing import Any

from app.schemas.ai_analysis import (
    AIAnalysisResponse,
    AIAnalysisStatus,
)
from app.schemas.ai_analysis_input import AIAnalysisInput


class AIAnalysisService:
    """
    Orchestrateur de l'analyse AI.

    Tsy manao calcul commercial vaovao.
    Tsy mamorona score na confidence.
    Ny provider no miandraikitra ny génération AI.
    """

    def __init__(self, provider: Any):
        if provider is None:
            raise TypeError(
                "AIAnalysisService nécessite un provider explicite."
            )

        self.provider = provider

    def _validate_output_evidence(
        self,
        data: AIAnalysisInput,
        result: AIAnalysisResponse,
    ) -> None:
        """
        Vérifie que toutes les evidences retournées par le provider
        existent réellement dans le registry fourni en entrée.

        Tsy mamela evidence vaovao noforonin'ny provider.
        """

        input_evidence_ids = {
            evidence.evidence_id
            for evidence in data.evidence_registry
        }

        output_evidence_ids = {
            evidence.evidence_id
            for evidence in result.evidence
        }

        unknown_ids = output_evidence_ids - input_evidence_ids

        if unknown_ids:
            raise ValueError(
                "Le provider AI a retourné des evidences absentes "
                "du evidence_registry d'entrée : "
                + ", ".join(sorted(unknown_ids))
            )

    def analyze(
        self,
        data: AIAnalysisInput,
    ) -> AIAnalysisResponse:
        """
        Analyse un Lead Intelligence validé.

        Raha tsy ampy ny commercial signals dia tsy miantso
        ny provider AI ary mamerina explicitement insufficient_data.
        """

        if (
            data.commercial_signals.get("status")
            == "insufficient_signals"
        ):
            return AIAnalysisResponse(
                status=AIAnalysisStatus.INSUFFICIENT_DATA,
                summary=None,
                observations=[],
                risks=[],
                opportunities=[],
                recommendations=[],
                next_actions=[],
                evidence=[],
                model_metadata=None,
            )

        provider_result = self.provider.analyze(data)
        result = AIAnalysisResponse(**provider_result)

        self._validate_output_evidence(data, result)

        return result
