from app.schemas.ai_analysis import AIAnalysisStatus
from app.schemas.ai_analysis_input import AIAnalysisInput
from app.services.ai.ai_analysis_service import AIAnalysisService
from app.services.ai.ai_provider import AIProvider


def build_valid_input():
    return AIAnalysisInput(
        lead={
            "company_name": "Entreprise Test",
            "sector": "Technology",
            "country": "Madagascar",
            "city": "Antananarivo",
        },
        qualification={
            "qualification": "partially_qualified",
            "status": "data_incomplete",
            "completeness": 87.5,
            "missing_data": ["social_media"],
        },
        data_quality={
            "data_quality_score": 87.5,
            "data_status": "data_incomplete",
            "commercial_score": None,
            "commercial_status": "insufficient_signals",
            "confidence": 87.5,
        },
        commercial_signals={
            "status": "signals_available",
            "signal_count": 1,
            "signals": [
                {
                    "interaction_id": "interaction-001",
                    "signal_type": "form_submission",
                    "source": "website",
                    "occurred_at": "2026-09-25T21:33:43.151000",
                    "evidence": {
                        "source_system": "website",
                        "metadata": {
                            "form_id": "contact-form",
                        },
                    },
                    "validation_reason": "Valid form submission evidence.",
                    "confidence": None,
                }
            ],
            "ignored_interactions": [],
        },
        commercial_score={
            "commercial_score": 49.77,
            "status": "score_available",
            "confidence": None,
            "evidence": {},
            "calculation": {},
        },
        evidence_registry=[
            {
                "evidence_id": "commercial-signal:interaction-001",
                "evidence_type": "commercial_signal",
                "source": "website",
                "reference_id": "interaction-001",
                "description": "Valid form submission evidence.",
            }
        ],
    )


def test_ai_service_requires_provider():
    try:
        AIAnalysisService()
    except TypeError:
        return

    raise AssertionError(
        "AIAnalysisService doit nécessiter un provider explicite."
    )


def test_ai_service_returns_insufficient_data_without_provider_call():
    class FailingProvider:
        def analyze(self, data):
            raise AssertionError(
                "Le provider ne doit pas être appelé si les données "
                "sont insuffisantes."
            )

    data = build_valid_input()

    data.commercial_signals = {
        "status": "insufficient_signals",
        "signal_count": 0,
        "signals": [],
        "ignored_interactions": [],
    }

    data.commercial_score = {
        "commercial_score": None,
        "status": "insufficient_signals",
        "confidence": None,
        "evidence": {},
        "calculation": None,
    }

    service = AIAnalysisService(provider=FailingProvider())

    result = service.analyze(data)

    assert result.status == AIAnalysisStatus.INSUFFICIENT_DATA
    assert result.summary is None
    assert result.observations == []
    assert result.recommendations == []


def test_ai_service_does_not_create_confidence_or_score():
    class Provider:
        def analyze(self, data):
            return {
                "status": "analysis_available",
                "summary": "Analyse basée sur les données disponibles.",
                "observations": [],
                "risks": [],
                "opportunities": [],
                "recommendations": [],
                "next_actions": [],
                "evidence": [],
                "model_metadata": None,
            }

    service = AIAnalysisService(provider=Provider())

    result = service.analyze(build_valid_input())

    assert result.status == AIAnalysisStatus.ANALYSIS_AVAILABLE
    assert result.model_metadata is None


def test_ai_service_rejects_provider_evidence_not_in_input_registry():
    class Provider:
        def analyze(self, data):
            return {
                "status": "analysis_available",
                "summary": "Analyse basée sur les données disponibles.",
                "observations": [
                    {
                        "statement": "Observation basée sur une evidence inconnue.",
                        "evidence_ids": [
                            "commercial-signal:interaction-999"
                        ],
                    }
                ],
                "risks": [],
                "opportunities": [],
                "recommendations": [],
                "next_actions": [],
                "evidence": [
                    {
                        "evidence_id": "commercial-signal:interaction-999",
                        "evidence_type": "commercial_signal",
                        "source": "website",
                        "reference_id": "interaction-999",
                        "description": "Evidence inventée par le provider.",
                    }
                ],
                "model_metadata": None,
            }

    service = AIAnalysisService(provider=Provider())

    try:
        service.analyze(build_valid_input())
    except ValueError as exc:
        assert "evidence_registry" in str(exc)
        return

    raise AssertionError(
        "Le service doit rejeter une evidence absente "
        "du registry d'entrée."
    )


def test_ai_service_accepts_ai_provider_contract():
    class TestProvider(AIProvider):
        def analyze(self, data):
            return {
                "status": "analysis_available",
                "summary": "Analyse basée sur les données disponibles.",
                "observations": [],
                "risks": [],
                "opportunities": [],
                "recommendations": [],
                "next_actions": [],
                "evidence": [],
                "model_metadata": None,
            }

    provider = TestProvider()
    service = AIAnalysisService(provider=provider)

    result = service.analyze(build_valid_input())

    assert result.status == AIAnalysisStatus.ANALYSIS_AVAILABLE
