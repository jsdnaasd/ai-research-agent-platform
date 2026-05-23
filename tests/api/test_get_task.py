from app.db import SessionLocal
from app.models.task import ResearchTask
from fastapi.testclient import TestClient

from app.main import app


def test_get_task_returns_persisted_task_details() -> None:
    with SessionLocal() as session:
        task = ResearchTask(topic="Anthropic competitors", template_type="market_scan")
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id

    client = TestClient(app)
    response = client.get(f"/api/tasks/{task_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == task_id
    assert body["topic"] == "Anthropic competitors"
    assert body["report_ready"] is False
