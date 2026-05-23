from app.agents.planner import PlannedBrief
from app.schemas.finding import FindingInput


class ResearcherAgent:
    def research(self, brief: PlannedBrief) -> FindingInput:
        return FindingInput(
            brief_id=brief.brief_id,
            claim=f"{brief.question} validated",
            source_fragments=["fragment-1", "fragment-2"],
            confidence=0.82,
        )
