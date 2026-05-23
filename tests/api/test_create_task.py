from fastapi.testclient import TestClient

from app.main import app


def test_create_task_returns_queued_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/tasks",
        json={
            "topic": "OpenAI competitors",
            "template_type": "market_scan",
            "user_context": "Focus on SMB pricing signals",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "queued"
    assert body["current_round"] == 0
    assert body["topic"] == "OpenAI competitors"
