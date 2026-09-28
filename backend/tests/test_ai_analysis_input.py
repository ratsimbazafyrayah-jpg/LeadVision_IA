import pytest

from app.schemas.ai_analysis_input import AIAnalysisInput


def test_ai_analysis_input_accepts_complete_lead_intelligence():
    data = {
        "lead": {
            "company_name": "Entreprise Test",
            "sector": "Technology",
            "country": "Madagascar",
            "city": "Antananarivo",
        },
        "qualification": {
            "qualification": "partially_qualified",
            "status": "data_incomplete",
            "completeness": 87.5,
            "evidence": ["company_name", "sector"],
            "validated_fields": ["company_name", "sector"],
            "missing_data": ["social_media"],
            "invalid_data": [],
            "social_platforms": [],
        },
        "data_quality": {
            "data_quality_score": 87.5,
            "data_status": "data_incomplete",
            "factors": {},
            "missing": ["social_media"],
            "invalid": [],
            "commercial_score": None,
            "commercial_status": "insufficient_signals",
            "commercial_signals": [],
            "final_score": None,
            "confidence": 87.5,
        },
        "commercial_signals": {
            "status": "signals_available",
            "signal_count": 1,
            "signals": [
                {
                    "interaction_id": "interaction-001",
                    "signal_type": "form_submission",
                    "source": "website",
                    "occurred_at": "2026-09-25T21:33:43.151000",
                    "evidence": {
                        "form_id": "contact-form",
                        "event_id": "test-event-001",
                    },
                    "validation_reason": "Valid form submission evidence.",
                    "confidence": None,
                }
            ],
            "ignored_interactions": [],
        },
        "commercial_score": {
            "commercial_score": 49.77,
            "status": "score_available",
            "confidence": None,
            "evidence": {},
            "calculation": {},
        },
        "evidence_registry": [
            {
                "evidence_id": "commercial-signal:interaction-001",
                "evidence_type": "commercial_signal",
                "source": "website",
                "reference_id": "interaction-001",
                "description": "Valid form submission evidence.",
            }
        ],
    }

    result = AIAnalysisInput(**data)

    assert result.lead["company_name"] == "Entreprise Test"
    assert result.commercial_score["commercial_score"] == 49.77


def test_ai_analysis_input_accepts_null_commercial_score():
    data = {
        "lead": {},
        "qualification": {},
        "data_quality": {
            "data_quality_score": None,
            "commercial_score": None,
            "commercial_status": "insufficient_signals",
        },
        "commercial_signals": {
            "status": "insufficient_signals",
            "signal_count": 0,
            "signals": [],
            "ignored_interactions": [],
        },
        "commercial_score": {
            "commercial_score": None,
            "status": "insufficient_signals",
            "confidence": None,
            "evidence": {},
            "calculation": None,
        },
    }

    result = AIAnalysisInput(**data)

    assert result.commercial_score["commercial_score"] is None


def test_ai_analysis_input_does_not_require_fake_defaults():
    data = {
        "lead": {},
        "qualification": {},
        "data_quality": {
            "commercial_score": None,
            "commercial_status": "insufficient_signals",
        },
        "commercial_signals": {
            "status": "insufficient_signals",
            "signal_count": 0,
            "signals": [],
            "ignored_interactions": [],
        },
        "commercial_score": {
            "commercial_score": None,
            "status": "insufficient_signals",
            "confidence": None,
            "evidence": {},
            "calculation": None,
        },
    }

    result = AIAnalysisInput(**data)

    assert result.commercial_score["commercial_score"] is None
    assert result.commercial_score["confidence"] is None


def test_ai_analysis_input_rejects_inconsistent_signal_count():
    data = {
        "lead": {},
        "qualification": {},
        "data_quality": {},
        "commercial_signals": {
            "status": "signals_available",
            "signal_count": 0,
            "signals": [
                {
                    "interaction_id": "interaction-001",
                    "signal_type": "form_submission",
                    "source": "website",
                    "occurred_at": "2026-09-25T21:33:43.151000",
                    "evidence": {
                        "form_id": "contact-form",
                    },
                    "validation_reason": "Valid evidence.",
                    "confidence": None,
                }
            ],
            "ignored_interactions": [],
        },
        "commercial_score": {
            "commercial_score": None,
            "status": "insufficient_signals",
            "confidence": None,
            "evidence": {},
            "calculation": None,
        },
    }

    try:
        AIAnalysisInput(**data)
    except ValueError:
        return

    raise AssertionError(
        "signal_count doit correspondre au nombre de signals."
    )


def test_ai_analysis_input_rejects_score_zero_without_available_status():
    data = {
        "lead": {},
        "qualification": {},
        "data_quality": {},
        "commercial_signals": {
            "status": "insufficient_signals",
            "signal_count": 0,
            "signals": [],
            "ignored_interactions": [],
        },
        "commercial_score": {
            "commercial_score": 0,
            "status": "insufficient_signals",
            "confidence": None,
            "evidence": {},
            "calculation": None,
        },
    }

    try:
        AIAnalysisInput(**data)
    except ValueError:
        return

    raise AssertionError(
        "Un score 0 ne doit pas être utilisé pour représenter "
        "une absence de signaux."
    )


def test_ai_analysis_input_rejects_signal_without_interaction_reference():
    data = {
        "lead": {},
        "qualification": {},
        "data_quality": {},
        "commercial_signals": {
            "status": "signals_available",
            "signal_count": 1,
            "signals": [
                {
                    "interaction_id": "",
                    "signal_type": "form_submission",
                    "source": "website",
                    "occurred_at": "2026-09-25T21:33:43.151000",
                    "evidence": {
                        "source_system": "website",
                        "metadata": {
                            "form_id": "contact-form",
                        },
                    },
                    "validation_reason": "Valid evidence.",
                    "confidence": None,
                }
            ],
            "ignored_interactions": [],
        },
        "commercial_score": {
            "commercial_score": None,
            "status": "insufficient_signals",
            "confidence": None,
            "evidence": {},
            "calculation": None,
        },
    }

    try:
        AIAnalysisInput(**data)
    except ValueError:
        return

    raise AssertionError(
        "Un signal commercial doit avoir un interaction_id."
    )


def test_ai_analysis_input_rejects_signal_without_validation_reason():
    data = {
        "lead": {},
        "qualification": {},
        "data_quality": {},
        "commercial_signals": {
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
                    "validation_reason": "",
                    "confidence": None,
                }
            ],
            "ignored_interactions": [],
        },
        "commercial_score": {
            "commercial_score": None,
            "status": "insufficient_signals",
            "confidence": None,
            "evidence": {},
            "calculation": None,
        },
    }

    try:
        AIAnalysisInput(**data)
    except ValueError:
        return

    raise AssertionError(
        "Un signal commercial doit avoir une validation_reason."
    )


def test_ai_analysis_input_accepts_null_signal_confidence():
    data = {
        "lead": {},
        "qualification": {},
        "data_quality": {},
        "commercial_signals": {
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
        "commercial_score": {
            "commercial_score": 49.77,
            "status": "score_available",
            "confidence": None,
            "evidence": {},
            "calculation": {},
        },
        "evidence_registry": [
            {
                "evidence_id": "commercial-signal:interaction-001",
                "evidence_type": "commercial_signal",
                "source": "website",
                "reference_id": "interaction-001",
                "description": "Valid form submission evidence.",
            }
        ],
    }

    result = AIAnalysisInput(**data)

    assert result.commercial_signals["signals"][0]["confidence"] is None


def test_ai_analysis_input_accepts_traceable_evidence_registry():
    data = {
        "lead": {
            "_id": "507f1f77bcf86cd799439011",
            "company_name": "Test Company",
        },
        "qualification": {
            "qualification": "qualified",
            "status": "available",
        },
        "data_quality": {
            "score": 80,
        },
        "commercial_signals": {
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
        "commercial_score": {
            "commercial_score": 49.77,
            "status": "score_available",
            "confidence": None,
            "evidence": {},
            "calculation": {},
        },
        "evidence_registry": [
            {
                "evidence_id": "commercial-signal:interaction-001",
                "evidence_type": "commercial_signal",
                "source": "website",
                "reference_id": "interaction-001",
                "description": "Signal commercial validé provenant de interaction-001.",
            }
        ],
    }

    result = AIAnalysisInput(**data)

    assert len(result.evidence_registry) == 1
    assert (
        result.evidence_registry[0].evidence_id
        == "commercial-signal:interaction-001"
    )
    assert (
        result.evidence_registry[0].reference_id
        == "interaction-001"
    )


def test_ai_analysis_input_rejects_unmatched_evidence_registry():
    data = {
        "lead": {
            "_id": "507f1f77bcf86cd799439011",
            "company_name": "Test Company",
        },
        "qualification": {
            "qualification": "qualified",
            "status": "available",
        },
        "data_quality": {
            "score": 80,
        },
        "commercial_signals": {
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
        "commercial_score": {
            "commercial_score": 49.77,
            "status": "score_available",
            "confidence": None,
            "evidence": {},
            "calculation": {},
        },
        "evidence_registry": [
            {
                "evidence_id": "commercial-signal:interaction-999",
                "evidence_type": "commercial_signal",
                "source": "website",
                "reference_id": "interaction-999",
                "description": "Valid form submission evidence.",
            }
        ],
    }

    with pytest.raises(ValueError, match="evidence"):
        AIAnalysisInput(**data)
