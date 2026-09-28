from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_discovery_import_rejects_missing_source():
    response = client.post(
        "/api/discovery/import",
        json={
            "prospects": [
                {
                    "company_name": "Test Company",
                }
            ],
        },
    )

    assert response.status_code == 422


def test_discovery_import_rejects_empty_prospects():
    response = client.post(
        "/api/discovery/import",
        json={
            "source": "overpass",
            "prospects": [],
        },
    )

    assert response.status_code == 422


def test_discovery_import_rejects_empty_source():
    response = client.post(
        "/api/discovery/import",
        json={
            "source": "",
            "prospects": [
                {
                    "company_name": "Test Company",
                }
            ],
        },
    )

    assert response.status_code == 422


def test_discovery_import_rejects_invalid_prospect():
    response = client.post(
        "/api/discovery/import",
        json={
            "source": "overpass",
            "prospects": [
                {},
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["processed"] == 1
    assert data["rejected"] == 1
    assert data["created"] == 0
    assert data["duplicates"] == 0
