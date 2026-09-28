import pytest

from app.services.lead_service import create_lead


def test_create_lead_requires_company_name():
    with pytest.raises(ValueError, match="Le nom de l'entreprise est requis"):
        create_lead({})
