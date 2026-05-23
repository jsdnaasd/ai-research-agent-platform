from pydantic import BaseModel


class PlannedBrief(BaseModel):
    brief_id: str
    question: str
    search_queries: list[str]
    evidence_targets: list[str]
    priority: int
    dependencies: list[str] = []


class PlannerAgent:
    def plan(self, topic: str, template_type: str, round_goal: str) -> list[PlannedBrief]:
        return [
            PlannedBrief(
                brief_id="brief-1",
                question=f"{topic} pricing",
                search_queries=[f"{topic} pricing", f"{topic} SMB pricing"],
                evidence_targets=["pricing page", "product docs"],
                priority=1,
            ),
            PlannedBrief(
                brief_id="brief-2",
                question=f"{topic} positioning",
                search_queries=[f"{topic} target market", f"{topic} SMB customers"],
                evidence_targets=["homepage", "case studies"],
                priority=2,
            ),
            PlannedBrief(
                brief_id="brief-3",
                question=f"{topic} traction signals",
                search_queries=[f"{topic} funding", f"{topic} launch news"],
                evidence_targets=["news", "blog"],
                priority=3,
            ),
        ]
