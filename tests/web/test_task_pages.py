from fastapi.testclient import TestClient

from app.main import app


def test_task_overview_page_renders_round_board_link() -> None:
    client = TestClient(app)

    response = client.get("/tasks/demo-task")

    assert response.status_code == 200
    assert "Round Board" in response.text


def test_evidence_page_renders_finding_heading() -> None:
    client = TestClient(app)

    response = client.get("/tasks/demo-task/evidence")

    assert response.status_code == 200
    assert "Evidence Explorer" in response.text
