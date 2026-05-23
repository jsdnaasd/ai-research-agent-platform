from pydantic import BaseModel

from app.schemas.finding import AcceptedFinding


class GeneratedReport(BaseModel):
    markdown_content: str
    html_content: str


class ReportBuilder:
    def build(self, template_type: str, findings: list[AcceptedFinding]) -> GeneratedReport:
        lines = [f"# {template_type.replace('_', ' ').title()}"]
        for finding in findings:
            lines.append(f"- {finding.claim} ({', '.join(finding.citations)})")
        markdown = "\n".join(lines)
        html = "<br>".join(lines)
        return GeneratedReport(markdown_content=markdown, html_content=html)
