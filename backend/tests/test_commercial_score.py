from datetime import datetime, timedelta, timezone

from app.services.commercial_score_service import (
    calculate_commercial_score,
)


def test_no_signals_returns_none():
    result = calculate_commercial_score([])

    assert result["commercial_score"] is None
    assert result["status"] == "insufficient_signals"


def test_signal_without_required_identity_is_not_used():
    result = calculate_commercial_score([
        {
            "signal_type": "form_submission",
            "validation_reason": "validated_form_event",
        }
    ])

    assert result["commercial_score"] is None
    assert result["status"] == "insufficient_signals"


def test_valid_signal_is_tracked():
    result = calculate_commercial_score([
        {
            "interaction_id": "signal-001",
            "signal_type": "form_submission",
            "source": "website",
            "occurred_at": datetime.now(timezone.utc),
            "validation_reason": "validated_form_event",
        }
    ])

    assert result["signals_used"] == ["signal-001"]
    assert len(result["evidence"]) == 1


def test_multiple_valid_signals_are_tracked():
    result = calculate_commercial_score([
        {
            "interaction_id": "signal-001",
            "signal_type": "form_submission",
            "source": "website",
            "occurred_at": datetime.now(timezone.utc),
            "validation_reason": "validated_form_event",
        },
        {
            "interaction_id": "signal-002",
            "signal_type": "email_reply",
            "source": "email",
            "occurred_at": datetime.now(timezone.utc),
            "validation_reason": "validated_email_event",
        },
    ])

    assert result["signals_used"] == [
        "signal-001",
        "signal-002",
    ]
    assert len(result["evidence"]) == 2




def test_old_signal_is_preserved_as_evidence():
    old_date = datetime.now(timezone.utc) - timedelta(days=90)

    result = calculate_commercial_score([
        {
            "interaction_id": "signal-old",
            "signal_type": "email_reply",
            "source": "email",
            "occurred_at": old_date,
            "validation_reason": "validated_email_event",
        }
    ])

    assert result["signals_used"] == ["signal-old"]
    assert result["evidence"][0]["occurred_at"] == old_date


# ---------------------------------------------------------
# Commercial Score 0–100 : méthodologie
# ---------------------------------------------------------

def test_commercial_score_has_four_dimensions():
    result = calculate_commercial_score([
        {
            "interaction_id": "signal-001",
            "signal_type": "form_submission",
            "source": "website",
            "occurred_at": datetime.now(timezone.utc),
            "validation_reason": "validated_form_event",
        },
        {
            "interaction_id": "signal-002",
            "signal_type": "email_reply",
            "source": "email",
            "occurred_at": datetime.now(timezone.utc),
            "validation_reason": "validated_email_event",
        },
    ])

    assert result["calculation"] is not None
    assert "intent" in result["calculation"]["dimensions"]
    assert "recency" in result["calculation"]["dimensions"]
    assert "diversity" in result["calculation"]["dimensions"]
    assert "evidence" in result["calculation"]["dimensions"]


def test_commercial_score_is_between_0_and_100():
    result = calculate_commercial_score([
        {
            "interaction_id": "signal-001",
            "signal_type": "form_submission",
            "source": "website",
            "occurred_at": datetime.now(timezone.utc),
            "validation_reason": "validated_form_event",
        },
        {
            "interaction_id": "signal-002",
            "signal_type": "email_reply",
            "source": "email",
            "occurred_at": datetime.now(timezone.utc),
            "validation_reason": "validated_email_event",
        },
    ])

    score = result["commercial_score"]

    assert score is not None
    assert 0 <= score <= 100


def test_commercial_score_keeps_traceability():
    result = calculate_commercial_score([
        {
            "interaction_id": "signal-001",
            "signal_type": "form_submission",
            "source": "website",
            "occurred_at": datetime.now(timezone.utc),
            "validation_reason": "validated_form_event",
        }
    ])

    assert result["signals_used"] == ["signal-001"]
    assert len(result["evidence"]) == 1


def test_old_signal_affects_recency():
    recent_date = datetime.now(timezone.utc)
    old_date = datetime.now(timezone.utc) - timedelta(days=90)

    recent_result = calculate_commercial_score([
        {
            "interaction_id": "recent-001",
            "signal_type": "form_submission",
            "source": "website",
            "occurred_at": recent_date,
            "validation_reason": "validated_form_event",
        }
    ])

    old_result = calculate_commercial_score([
        {
            "interaction_id": "old-001",
            "signal_type": "form_submission",
            "source": "website",
            "occurred_at": old_date,
            "validation_reason": "validated_form_event",
        }
    ])

    assert recent_result["calculation"]["dimensions"]["recency"] > old_result["calculation"]["dimensions"]["recency"]
