from app.services.lead_validation_service import (
    normalize_text,
    normalize_email,
    normalize_url,
    validate_email,
    validate_url,
    validate_phone,
    validate_social_media,
)

from app.services.lead_qualification_service import (
    qualify_lead,
)

from app.services.lead_scoring_service import (
    calculate_lead_score,
)


def test_normalize_email():
    assert normalize_email("  TEST@Example.COM  ") == "test@example.com"


def test_normalize_url():
    assert normalize_url("example.com") == "https://example.com"


def test_valid_email():
    assert validate_email("contact@example.com") is True


def test_invalid_email():
    assert validate_email("contact@example") is False


def test_valid_phone():
    assert validate_phone("+261341111111") is True


def test_invalid_phone():
    assert validate_phone("abc123") is False


def test_valid_multiple_phones():
    assert validate_phone(
        "+261 (20) 226 42 33 / +261 (20) 248 03 49"
    ) is True


def test_invalid_multiple_phones():
    assert validate_phone(
        "+261341111111 / abc123"
    ) is False


def test_valid_social_media():
    result = validate_social_media({
        "facebook": "https://facebook.com/example",
        "linkedin": "https://linkedin.com/company/example",
    })

    assert result["invalid"] == []
    assert set(result["valid"]) == {"facebook", "linkedin"}


def test_invalid_social_media():
    result = validate_social_media({
        "facebook": "not-a-url",
    })

    assert result["invalid"] == ["facebook"]


def test_complete_lead_qualification():
    lead = {
        "company_name": "Tech Solutions Madagascar",
        "sector": "Informatique",
        "country": "Madagascar",
        "city": "Antananarivo",
        "website": "https://example.com",
        "email": "contact@example.com",
        "phone": "+261341111111",
        "social_media": {
            "facebook": "https://facebook.com/example"
        },
    }

    result = qualify_lead(lead)

    assert result["qualification"] == "complete"
    assert result["status"] == "data_complete"
    assert result["data_completeness"] == 100.0


def test_sparse_lead_qualification():
    lead = {
        "company_name": "Test Company",
    }

    result = qualify_lead(lead)

    assert result["qualification"] == "partially_qualified"
    assert result["status"] == "data_incomplete"


def test_lead_score_does_not_create_commercial_score():
    lead = {
        "company_name": "Tech Solutions Madagascar",
        "sector": "Informatique",
        "country": "Madagascar",
        "city": "Antananarivo",
        "website": "https://example.com",
        "email": "contact@example.com",
        "phone": "+261341111111",
        "social_media": {
            "facebook": "https://facebook.com/example"
        },
    }

    result = calculate_lead_score(lead)

    assert result["commercial_score"] is None
    assert result["final_score"] is None
