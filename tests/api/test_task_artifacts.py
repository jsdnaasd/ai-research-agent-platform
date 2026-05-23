from app.db import SessionLocal
from app.main import app
from app.models.brief import ResearchBrief
from app.models.finding import ResearchFinding
from app.models.finding_source_fragment import ResearchFindingSourceFragment
from app.models.report import ResearchReport
from app.models.round import ResearchRound
from app.models.source import ResearchSource
from app.models.source_fragment import ResearchSourceFragment
from app.models.task import ResearchTask
from fastapi.testclient import TestClient


def _seed_artifact_graph() -> str:
    with SessionLocal() as session:
        task = ResearchTask(topic="Artifact task", template_type="market_scan")
        session.add(task)
        session.flush()

        round_row = ResearchRound(task_id=task.id, round_number=1, stage="round_closed")
        session.add(round_row)
        session.flush()

        brief = ResearchBrief(round_id=round_row.id, question="pricing", priority=1, status="accepted")
        session.add(brief)
        session.flush()

        source = ResearchSource(
            task_id=task.id,
            source_url="https://example.com",
            source_title="Example",
            provider="fake",
            raw_content="Pricing starts at $29",
        )
        session.add(source)
        session.flush()

        fragment = ResearchSourceFragment(
            source_id=source.id,
            content="Pricing starts at $29",
            citation_label="fragment-1",
            offset_start=0,
            offset_end=21,
        )
        session.add(fragment)
        session.flush()

        finding = ResearchFinding(brief_id=brief.id, claim="Pricing starts at $29", confidence=0.9)
        session.add(finding)
        session.flush()

        session.add(ResearchFindingSourceFragment(finding_id=finding.id, source_fragment_id=fragment.id))
        session.add(
            ResearchReport(
                task_id=task.id,
                markdown_content="# Market Scan\n- Pricing starts at $29",
                html_content="<h1>Market Scan</h1>",
            )
        )
        session.commit()
        return task.id


def test_get_task_briefs_returns_persisted_briefs() -> None:
    task_id = _seed_artifact_graph()
    client = TestClient(app)

    response = client.get(f"/api/tasks/{task_id}/briefs")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["question"] == "pricing"


def test_get_task_evidence_returns_citations_per_finding() -> None:
    task_id = _seed_artifact_graph()
    client = TestClient(app)

    response = client.get(f"/api/tasks/{task_id}/evidence")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["claim"] == "Pricing starts at $29"
    assert payload[0]["citations"] == ["fragment-1"]


def test_get_task_report_returns_persisted_report() -> None:
    task_id = _seed_artifact_graph()
    client = TestClient(app)

    response = client.get(f"/api/tasks/{task_id}/report")

    assert response.status_code == 200
    payload = response.json()
    assert "Market Scan" in payload["markdown_content"]
