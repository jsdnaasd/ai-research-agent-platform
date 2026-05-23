from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.main import app
from app.models.task import ResearchTask


def test_homepage_renders_task_form_and_recent_tasks() -> None:
    with SessionLocal() as session:
        session.add(ResearchTask(topic="Recent task", template_type="market_scan"))
        session.commit()

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Start Research Task" in response.text
    assert "Recent task" in response.text


def test_homepage_form_submission_redirects_to_task_page() -> None:
    client = TestClient(app)
    response = client.post(
        "/tasks/new",
        data={
            "topic": "Form submitted task",
            "template_type": "market_scan",
            "user_context": "Track pricing",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].startswith("/tasks/")
