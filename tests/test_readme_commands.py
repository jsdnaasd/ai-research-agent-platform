from pathlib import Path


def test_readme_mentions_main_local_commands() -> None:
    readme = Path("README.md").read_text()

    assert "uvicorn app.main:app --reload" in readme
    assert "pytest" in readme
