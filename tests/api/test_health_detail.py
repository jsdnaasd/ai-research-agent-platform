from fastapi.testclient import TestClient

from app.main import app


def test_detailed_health_reports_database_status() -> None:
    client = TestClient(app)

    response = client.get("/health/detailed")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"] == "ok"
