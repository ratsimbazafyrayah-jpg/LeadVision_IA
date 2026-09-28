from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_app_lifespan_creates_and_closes_ai_provider():
    fake_client = MagicMock()
    fake_provider = MagicMock()

    with patch(
        "app.main.create_ai_provider",
        return_value=fake_provider,
    ) as mock_create_provider:

        with TestClient(app):
            mock_create_provider.assert_called_once()

            assert app.state.ai_provider is fake_provider

    fake_provider.http_client.close.assert_called_once()
