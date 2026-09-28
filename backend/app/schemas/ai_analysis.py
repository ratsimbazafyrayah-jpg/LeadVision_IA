from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator, field_validator


class AIAnalysisStatus(str, Enum):
    ANALYSIS_AVAILABLE = "analysis_available"
    INSUFFICIENT_DATA = "insufficient_data"
    VALIDATION_FAILED = "validation_failed"
    PROVIDER_ERROR = "provider_error"


class AIAnalysisEvidence(BaseModel):
    evidence_id: str = Field(..., min_length=1)
    evidence_type: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    reference_id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class AIAnalysisObservation(BaseModel):
    statement: str = Field(..., min_length=1)
    evidence_ids: List[str] = Field(..., min_length=1)

    @field_validator("evidence_ids")
    @classmethod
    def validate_evidence_ids(cls, value):
        if not value:
            raise ValueError(
                "Une observation doit avoir au moins une evidence."
            )
        return value


class AIAnalysisRecommendation(BaseModel):
    action: str = Field(..., min_length=1)
    rationale: str = Field(..., min_length=1)
    priority: str = Field(..., min_length=1)
    evidence_ids: List[str] = Field(..., min_length=1)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value):
        allowed = {"low", "medium", "high"}

        if value not in allowed:
            raise ValueError(
                "La priorité doit être low, medium ou high."
            )

        return value

    @field_validator("evidence_ids")
    @classmethod
    def validate_evidence_ids(cls, value):
        if not value:
            raise ValueError(
                "Une recommandation doit avoir au moins une evidence."
            )
        return value


class AIAnalysisNextAction(BaseModel):
    action: str = Field(..., min_length=1)
    priority: str = Field(..., min_length=1)
    evidence_ids: List[str] = Field(..., min_length=1)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value):
        allowed = {"low", "medium", "high"}

        if value not in allowed:
            raise ValueError(
                "La priorité doit être low, medium ou high."
            )

        return value

    @field_validator("evidence_ids")
    @classmethod
    def validate_evidence_ids(cls, value):
        if not value:
            raise ValueError(
                "Une next action doit avoir au moins une evidence."
            )
        return value


class AIAnalysisResponse(BaseModel):
    status: AIAnalysisStatus

    summary: Optional[str] = None

    observations: List[AIAnalysisObservation] = Field(
        default_factory=list
    )

    risks: List[AIAnalysisObservation] = Field(
        default_factory=list
    )

    opportunities: List[AIAnalysisObservation] = Field(
        default_factory=list
    )

    recommendations: List[AIAnalysisRecommendation] = Field(
        default_factory=list
    )

    next_actions: List[AIAnalysisNextAction] = Field(
        default_factory=list
    )

    evidence: List[AIAnalysisEvidence] = Field(
        default_factory=list
    )

    model_metadata: Optional[dict] = None

    @model_validator(mode="after")
    def validate_evidence_integrity(self):
        evidence_ids = {
            item.evidence_id
            for item in self.evidence
        }

        referenced_ids = set()

        for item in self.observations:
            referenced_ids.update(item.evidence_ids)

        for item in self.risks:
            referenced_ids.update(item.evidence_ids)

        for item in self.opportunities:
            referenced_ids.update(item.evidence_ids)

        for item in self.recommendations:
            referenced_ids.update(item.evidence_ids)

        for item in self.next_actions:
            referenced_ids.update(item.evidence_ids)

        unknown_ids = referenced_ids - evidence_ids

        if unknown_ids:
            raise ValueError(
                "Certaines evidence_ids ne correspondent "
                "à aucune evidence déclarée : "
                + ", ".join(sorted(unknown_ids))
            )

        orphan_ids = evidence_ids - referenced_ids

        if orphan_ids:
            raise ValueError(
                "Certaines evidences ne sont référencées "
                "par aucune observation, risk, opportunity, "
                "recommendation ou next action : "
                + ", ".join(sorted(orphan_ids))
            )

        return self
