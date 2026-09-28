import pytest

from datetime import datetime, timezone

from app.schemas.ai_analysis import (
    AIAnalysisResponse,
    AIAnalysisStatus,
    AIAnalysisEvidence,
    AIAnalysisObservation,
    AIAnalysisRecommendation,
    AIAnalysisNextAction,
)


def test_ai_analysis_available_response():
    response = AIAnalysisResponse(
        status=AIAnalysisStatus.ANALYSIS_AVAILABLE,
        summary="Analyse basée sur les données disponibles.",
        observations=[
            AIAnalysisObservation(
                statement="Un signal commercial validé a été observé.",
                evidence_ids=["interaction-001"],
            )
        ],
        risks=[],
        opportunities=[],
        recommendations=[
            AIAnalysisRecommendation(
                action="Analyser le contexte du signal.",
                rationale="Le signal commercial est traçable.",
                priority="medium",
                evidence_ids=["interaction-001"],
            )
        ],
        next_actions=[
            AIAnalysisNextAction(
                action="Effectuer un suivi commercial.",
                priority="medium",
                evidence_ids=["interaction-001"],
            )
        ],
        evidence=[
            AIAnalysisEvidence(
                evidence_id="interaction-001",
                evidence_type="commercial_signal",
                source="website",
                reference_id="interaction-001",
                description="Signal commercial validé.",
            )
        ],
        model_metadata=None,
    )

    assert response.status == AIAnalysisStatus.ANALYSIS_AVAILABLE
    assert len(response.observations) == 1
    assert len(response.recommendations) == 1
    assert len(response.next_actions) == 1
    assert len(response.evidence) == 1


def test_ai_analysis_insufficient_data():
    response = AIAnalysisResponse(
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

    assert response.status == AIAnalysisStatus.INSUFFICIENT_DATA
    assert response.summary is None
    assert response.observations == []
    assert response.recommendations == []


def test_ai_analysis_requires_traceable_evidence_for_observation():
    try:
        AIAnalysisObservation(
            statement="Observation sans preuve.",
            evidence_ids=[],
        )
    except ValueError:
        return

    raise AssertionError(
        "Une observation AI ne devrait pas être acceptée sans evidence."
    )


def test_ai_analysis_recommendation_requires_evidence():
    try:
        AIAnalysisRecommendation(
            action="Action commerciale.",
            rationale="Raison.",
            priority="high",
            evidence_ids=[],
        )
    except ValueError:
        return

    raise AssertionError(
        "Une recommandation AI ne devrait pas être acceptée sans evidence."
    )


def test_ai_analysis_rejects_unknown_observation_evidence():
    try:
        AIAnalysisResponse(
            status=AIAnalysisStatus.ANALYSIS_AVAILABLE,
            summary="Analyse.",
            observations=[
                AIAnalysisObservation(
                    statement="Observation.",
                    evidence_ids=["unknown-evidence"],
                )
            ],
            risks=[],
            opportunities=[],
            recommendations=[],
            next_actions=[],
            evidence=[
                AIAnalysisEvidence(
                    evidence_id="real-evidence",
                    evidence_type="commercial_signal",
                    source="website",
                    reference_id="interaction-001",
                    description="Preuve réelle.",
                )
            ],
            model_metadata=None,
        )
    except ValueError:
        return

    raise AssertionError(
        "Une observation ne doit pas référencer une evidence inexistante."
    )


def test_ai_analysis_rejects_unknown_recommendation_evidence():
    try:
        AIAnalysisResponse(
            status=AIAnalysisStatus.ANALYSIS_AVAILABLE,
            summary="Analyse.",
            observations=[],
            risks=[],
            opportunities=[],
            recommendations=[
                AIAnalysisRecommendation(
                    action="Effectuer un suivi.",
                    rationale="Action basée sur une observation.",
                    priority="medium",
                    evidence_ids=["unknown-evidence"],
                )
            ],
            next_actions=[],
            evidence=[
                AIAnalysisEvidence(
                    evidence_id="real-evidence",
                    evidence_type="commercial_signal",
                    source="website",
                    reference_id="interaction-001",
                    description="Preuve réelle.",
                )
            ],
            model_metadata=None,
        )
    except ValueError:
        return

    raise AssertionError(
        "Une recommandation ne doit pas référencer une evidence inexistante."
    )


def test_ai_analysis_rejects_orphan_evidence():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AIAnalysisResponse(
            status=AIAnalysisStatus.ANALYSIS_AVAILABLE,
            summary="Test",
            observations=[],
            risks=[],
            opportunities=[],
            recommendations=[],
            next_actions=[],
            evidence=[
                AIAnalysisEvidence(
                    evidence_id="evidence-001",
                    evidence_type="interaction",
                    source="website",
                    reference_id="interaction-001",
                    description="Evidence non référencée",
                )
            ],
            model_metadata=None,
        )
