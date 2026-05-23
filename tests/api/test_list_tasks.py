from app.db import SessionLocal
from app.main import app
from app.models.task import ResearchTask
from fastapi.testclient import TestClient


def test_list_tasks_returns_recent_persisted_tasks() -> None:
    with SessionLocal() as session:
        session.add_all(
            [
                ResearchTask(topic="Task A", template_type="market_scan"),
                ResearchTask(topic="Task B", template_type="company_brief"),
            ]
        )
        session.commit()

    client = TestClient(app)
    response = client.get("/api/tasks")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert {item["topic"] for item in payload} == {"Task A", "Task B"}
