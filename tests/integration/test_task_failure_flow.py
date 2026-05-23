from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.main import app
from app.models.task import ResearchTask, TaskStatus


class FailingSearchProvider:
    def search(self, query: str, max_results: int = 5) -> list[object]:
        raise RuntimeError("provider unavailable")


def test_failed_task_persists_error_message(monkeypatch) -> None:
    from app.services import orchestrator as orchestrator_module

    monkeypatch.setattr(orchestrator_module, "build_search_provider", lambda: FailingSearchProvider())

    client = TestClient(app)
    response = client.post("/api/tasks", json={"topic": "Broken run", "template_type": "market_scan"})

    assert response.status_code == 201
    task_id = response.json()["id"]

    with SessionLocal() as session:
        task = session.get(ResearchTask, task_id)

    assert task is not None
    assert task.status is TaskStatus.FAILED
    assert task.error_message == "provider unavailable"
