from app.schemas.finding import CriticVerdict, FindingInput
from app.tools.validation import needs_more_sources


class CriticAgent:
    def review(self, findings: list[FindingInput]) -> CriticVerdict:
        if needs_more_sources(findings):
            return CriticVerdict(
                verdict="expand",
                accepted_findings=[],
                rejected_findings=[],
                gaps=["Need at least two source fragments per claim"],
                requested_followups=["Find secondary corroborating sources"],
                quality_score=0.45,
            )

        return CriticVerdict(
            verdict="accept",
            accepted_findings=[item.claim for item in findings],
            rejected_findings=[],
            gaps=[],
            requested_followups=[],
            quality_score=0.91,
        )
