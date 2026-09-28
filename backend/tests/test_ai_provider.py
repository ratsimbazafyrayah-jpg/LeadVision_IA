from app.schemas.ai_analysis_input import AIAnalysisInput
from app.services.ai.ai_provider import AIProvider


def build_input():
    return AIAnalysisInput(
        lead={
            "company_name": "Entreprise Test",
            "sector": "Technology",
            "country": "Madagascar",
            "city": "Antananarivo",
        },
        qualification={},
        data_quality={},
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
    )


def test_ai_provider_requires_analyze_method():
    assert hasattr(AIProvider, "analyze")


def test_ai_provider_analyze_is_defined_as_contract():
    assert getattr(AIProvider.analyze, "__isabstractmethod__", False)
