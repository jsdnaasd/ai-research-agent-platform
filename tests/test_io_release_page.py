from pathlib import Path


def test_io_release_page_uses_engineering_project_copy() -> None:
    page = Path("io/index.html").read_text()
    styles = Path("io/styles.css").read_text()

    assert "<img" not in page
    assert "background-image" not in styles
    assert Path("io/.nojekyll").exists()
    assert "No images. Just the system." in page
    assert "Terminal usage" in page
    assert "docker compose up --build" in page
    assert "curl -s -X POST http://localhost:8000/api/tasks" in page
    assert "AI Research Agent Platform" in page
