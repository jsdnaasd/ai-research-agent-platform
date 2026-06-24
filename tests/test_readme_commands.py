from pathlib import Path


def test_readme_mentions_main_local_commands() -> None:
    readme = Path("README.md").read_text()

    assert "uvicorn app.main:app --reload" in readme
    assert "pytest" in readme
    assert "docker compose up --build" in readme
    assert "docker compose logs -f worker" in readme
    assert "curl -s -X POST http://localhost:8000/api/tasks" in readme
    assert "docker compose exec db psql" in readme
    assert "make docker-up" in readme
