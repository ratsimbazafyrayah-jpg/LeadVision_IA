from app.services.commercial_signal_rules import classify_interaction


def test_form_submission_with_evidence():
    result = classify_interaction({
        "type": "form_submission",
        "source": "website",
        "metadata": {
            "form_id": "contact-form",
        },
    })

    assert result["is_signal"] is True
    assert result["classification"] == "form_submission"
    assert result["reason"] == "validated_form_event"


def test_email_reply_with_evidence():
    result = classify_interaction({
        "type": "email_reply",
        "source": "email",
        "metadata": {
            "message_id": "msg-001",
        },
    })

    assert result["is_signal"] is True
    assert result["classification"] == "email_reply"


def test_meeting_booked_with_evidence():
    result = classify_interaction({
        "type": "meeting_booked",
        "source": "calendar",
        "metadata": {
            "meeting_id": "meeting-001",
        },
    })

    assert result["is_signal"] is True
    assert result["classification"] == "meeting_booked"


def test_demo_request_with_evidence():
    result = classify_interaction({
        "type": "demo_request",
        "source": "website",
        "metadata": {
            "request_id": "demo-001",
        },
    })

    assert result["is_signal"] is True
    assert result["classification"] == "demo_request"


def test_quote_request_with_evidence():
    result = classify_interaction({
        "type": "quote_request",
        "source": "website",
        "metadata": {
            "request_id": "quote-001",
        },
    })

    assert result["is_signal"] is True
    assert result["classification"] == "quote_request"


def test_contact_request_with_evidence():
    result = classify_interaction({
        "type": "contact_request",
        "source": "website",
        "metadata": {
            "request_id": "contact-001",
        },
    })

    assert result["is_signal"] is True
    assert result["classification"] == "contact_request"


def test_signal_without_evidence_is_rejected():
    result = classify_interaction({
        "type": "quote_request",
        "source": "website",
        "metadata": {},
    })

    assert result["is_signal"] is False
    assert result["classification"] == "insufficient_evidence"


def test_unknown_interaction_is_not_signal():
    result = classify_interaction({
        "type": "unknown_interaction",
        "source": "unknown",
        "metadata": {},
    })

    assert result["is_signal"] is False
    assert result["classification"] == "unclassified"


def test_manual_test_is_ignored():
    result = classify_interaction({
        "type": "contact_request",
        "source": "website",
        "metadata": {
            "origin": "manual_test",
        },
    })

    assert result["is_signal"] is False
    assert result["classification"] == "test_data"
