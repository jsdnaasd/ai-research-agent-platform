from app.schemas.finding import AcceptedFinding
from app.services.reporting import ReportBuilder


def test_report_builder_uses_only_accepted_findings() -> None:
    builder = ReportBuilder()

    report = builder.build(
        template_type="market_scan",
        findings=[
            AcceptedFinding(brief_id="brief-1", claim="Claim A", citations=["fragment-1"]),
            AcceptedFinding(brief_id="brief-2", claim="Claim B", citations=["fragment-3"]),
        ],
    )

    assert "Claim A" in report.markdown_content
    assert "Claim B" in report.markdown_content
