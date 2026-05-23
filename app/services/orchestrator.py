from dataclasses import dataclass

from app.agents.critic import CriticAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.synthesizer import SynthesizerAgent
from app.schemas.finding import AcceptedFinding


@dataclass(slots=True)
class TaskRuntimeState:
    task_id: str
    status: str
    current_round: int
    round_stage: str


class Orchestrator:
    def advance_round(self, state: TaskRuntimeState) -> TaskRuntimeState:
        transitions = {
            "planning": "researching",
            "researching": "critic_review",
            "critic_review": "supervisor_decision",
            "supervisor_decision": "round_closed",
        }
        return TaskRuntimeState(
            task_id=state.task_id,
            status=state.status,
            current_round=state.current_round,
            round_stage=transitions.get(state.round_stage, state.round_stage),
        )

    def run_demo_task(self, topic: str, template_type: str) -> "DemoRunResult":
        planner = PlannerAgent()
        researcher = ResearcherAgent()
        critic = CriticAgent()
        synthesizer = SynthesizerAgent()

        briefs = planner.plan(
            topic=topic,
            template_type=template_type,
            round_goal="Initial research round",
        )
        findings = [researcher.research(brief) for brief in briefs]
        verdict = critic.review(findings)
        accepted = [
            AcceptedFinding(
                brief_id=item.brief_id,
                claim=item.claim,
                citations=item.source_fragments,
            )
            for item in findings
        ]
        report = synthesizer.synthesize(
            template_type=template_type,
            findings=accepted if verdict.verdict == "accept" else [],
        )
        return DemoRunResult(status="completed", current_round=1, report=report)


@dataclass(slots=True)
class DemoRunResult:
    status: str
    current_round: int
    report: object
