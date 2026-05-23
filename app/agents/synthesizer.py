from app.schemas.finding import AcceptedFinding
from app.services.reporting import GeneratedReport, ReportBuilder


class SynthesizerAgent:
    def synthesize(self, template_type: str, findings: list[AcceptedFinding]) -> GeneratedReport:
        return ReportBuilder().build(template_type=template_type, findings=findings)
