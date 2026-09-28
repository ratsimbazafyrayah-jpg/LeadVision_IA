from typing import Any, Dict, List

from pydantic import BaseModel, Field, model_validator


class AIAnalysisInputEvidence(BaseModel):
    """
    Evidence canonique disponible pour l'analyse AI.

    Ny evidence dia tsy mamorona donnée vaovao.
    Izy dia référence déterministe amin'ny donnée efa voamarina.
    """

    evidence_id: str = Field(..., min_length=1)

    evidence_type: str = Field(..., min_length=1)

    source: str = Field(..., min_length=1)

    reference_id: str = Field(..., min_length=1)

    description: str = Field(..., min_length=1)


class AIAnalysisInput(BaseModel):
    """
    Contract entre Lead Intelligence et AI.

    Tsy manao calcul métier vaovao ity schema ity.
    Izy ihany no manamarina ny structure sy ny cohérence
    des données efa novokarin'ny Lead Intelligence.
    """

    lead: Dict[str, Any] = Field(default_factory=dict)

    qualification: Dict[str, Any] = Field(default_factory=dict)

    data_quality: Dict[str, Any] = Field(default_factory=dict)

    commercial_signals: Dict[str, Any] = Field(default_factory=dict)

    commercial_score: Dict[str, Any] = Field(default_factory=dict)

    evidence_registry: List[AIAnalysisInputEvidence] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_integrity(self):
        signals_data = self.commercial_signals

        signals = signals_data.get("signals", [])
        signal_count = signals_data.get("signal_count")

        if signal_count is not None:
            if signal_count != len(signals):
                raise ValueError(
                    "signal_count doit correspondre au nombre de signals."
                )

        for signal in signals:
            interaction_id = signal.get("interaction_id")
            validation_reason = signal.get("validation_reason")

            if not interaction_id:
                raise ValueError(
                    "Un signal commercial doit avoir un interaction_id."
                )

            if not validation_reason:
                raise ValueError(
                    "Un signal commercial doit avoir une validation_reason."
                )

        score_data = self.commercial_score

        score = score_data.get("commercial_score")
        status = score_data.get("status")

        if score == 0 and status != "score_available":
            raise ValueError(
                "Un score commercial de 0 doit provenir "
                "d'un calcul réellement disponible."
            )

        evidence_ids = [
            evidence.evidence_id
            for evidence in self.evidence_registry
        ]

        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError(
                "Les evidence_id doivent être uniques."
            )

        signal_interaction_ids = {
            signal.get("interaction_id")
            for signal in signals
            if signal.get("interaction_id")
        }

        registry_reference_ids = {
            evidence.reference_id
            for evidence in self.evidence_registry
        }

        missing_evidence_references = (
            signal_interaction_ids - registry_reference_ids
        )

        if missing_evidence_references:
            raise ValueError(
                "Chaque signal commercial doit avoir une "
                "evidence correspondante dans le registry : "
                + ", ".join(sorted(missing_evidence_references))
            )

        orphan_evidence_references = (
            registry_reference_ids - signal_interaction_ids
        )

        if orphan_evidence_references:
            raise ValueError(
                "Chaque evidence du registry doit correspondre "
                "à un signal commercial existant : "
                + ", ".join(sorted(orphan_evidence_references))
            )

        return self