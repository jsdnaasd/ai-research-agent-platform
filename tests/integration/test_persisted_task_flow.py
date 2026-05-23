from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.main import app
from app.models.brief import ResearchBrief
from app.models.finding import ResearchFinding
from app.models.report import ResearchReport
from app.models.source import ResearchSource
from app.models.source_fragment import ResearchSourceFragment
from app.tools.search import SearchResult


class FakeSearchProvider:
    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        return [
            SearchResult(
                url=f"https://example.com/{query.replace(' ', '-')}",
                title=f"Result for {query}",
                content=f"{query} starts at $29 for SMB teams",
                provider="fake",
            ),
            SearchResult(
                url=f"https://backup.example.com/{query.replace(' ', '-')}",
                title=f"Backup for {query}",
                content=f"{query} supports developer workflows",
                provider="fake",
            ),
        ]


def test_post_task_persists_report_and_findings(monkeypatch) -> None:
    from app.services import orchestrator as orchestrator_module

    monkeypatch.setattr(
        orchestrator_module,
        "build_search_provider",
        lambda: FakeSearchProvider(),
    )

    client = TestClient(app)
    response = client.post(
        "/api/tasks",
        json={"topic": "OpenAI competitors", "template_type": "market_scan"},
    )

    assert response.status_code == 201
    task_id = response.json()["id"]

    with SessionLocal() as session:
        briefs = session.query(ResearchBrief).all()
        findings = session.query(ResearchFinding).all()
        sources = session.query(ResearchSource).all()
        fragments = session.query(ResearchSourceFragment).all()
        report = session.query(ResearchReport).filter_by(task_id=task_id).one()

    assert len(briefs) == 3
    assert len(findings) == 3
    assert len(sources) >= 3
    assert len(fragments) >= 3
    assert "Market Scan" in report.markdown_content
