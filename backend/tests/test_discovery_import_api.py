from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_discovery_import_api():
    response = client.post(
        "/api/discovery/import",
        json={
            "source": "overpass",
            "prospects": [
                {
                    "company_name": "API Import Test Company",
                    "country": "Madagascar",
                    "city": "Antananarivo",
                }
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source"] == "overpass"
    assert data["processed"] == 1
    assert "created" in data
    assert "duplicates" in data
    assert "rejected" in data
    assert "results" in data
