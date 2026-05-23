from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.main import app
from app.models.brief import ResearchBrief
from app.models.finding import ResearchFinding
from app.models.report import ResearchReport
from app.models.round import ResearchRound
from app.models.source import ResearchSource
from app.models.source_fragment import ResearchSourceFragment
from app.models.task import ResearchTask


def _seed_task_graph() -> str:
    with SessionLocal() as session:
        task = ResearchTask(topic="OpenAI competitors", template_type="market_scan")
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
            source_url="https://example.com/pricing",
            source_title="Pricing",
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

        finding = ResearchFinding(brief_id=brief.id, claim="SMB pricing starts at $29", confidence=0.9)
        session.add(finding)
        session.add(
            ResearchReport(
                task_id=task.id,
                markdown_content="# Market Scan\n- SMB pricing starts at $29 (fragment-1)",
                html_content="<h1>Market Scan</h1>",
            )
        )
        session.commit()
        return task.id


def test_task_overview_page_renders_round_board_link() -> None:
    task_id = _seed_task_graph()
    client = TestClient(app)

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert "Round Board" in response.text
    assert "OpenAI competitors" in response.text


def test_evidence_page_renders_finding_heading() -> None:
    task_id = _seed_task_graph()
    client = TestClient(app)

    response = client.get(f"/tasks/{task_id}/evidence")

    assert response.status_code == 200
    assert "Evidence Explorer" in response.text
    assert "SMB pricing starts at $29" in response.text
