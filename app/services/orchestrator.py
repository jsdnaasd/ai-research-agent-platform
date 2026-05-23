from dataclasses import dataclass

from app.agents.critic import CriticAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.synthesizer import SynthesizerAgent
from app.schemas.finding import AcceptedFinding
from app.db import SessionLocal
from app.models.brief import ResearchBrief
from app.models.finding import ResearchFinding
from app.models.finding_source_fragment import ResearchFindingSourceFragment
from app.models.report import ResearchReport
from app.models.round import ResearchRound
from app.models.source import ResearchSource
from app.models.source_fragment import ResearchSourceFragment
from app.models.task import ResearchTask, TaskStatus
from app.tools.search import build_search_provider


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
        researcher = ResearcherAgent(search_provider=_DemoSearchProvider())
        critic = CriticAgent()
        synthesizer = SynthesizerAgent()

        briefs = planner.plan(
            topic=topic,
            template_type=template_type,
            round_goal="Initial research round",
        )
        researcher_outputs = [researcher.research(brief) for brief in briefs]
        verdict = critic.review([item.finding for item in researcher_outputs])
        accepted = [
            AcceptedFinding(
                brief_id=item.finding.brief_id,
                claim=item.finding.claim,
                citations=item.finding.source_fragments,
            )
            for item in researcher_outputs
        ]
        report = synthesizer.synthesize(
            template_type=template_type,
            findings=accepted if verdict.verdict == "accept" else [],
        )
        return DemoRunResult(status="completed", current_round=1, report=report)

    def run_task(self, task_id: str) -> None:
        with SessionLocal() as session:
            task = session.get(ResearchTask, task_id)
            if task is None:
                return

            try:
                task.status = TaskStatus.RUNNING
                task.current_round = 1
                task.error_message = None
                round_row = ResearchRound(task_id=task.id, round_number=1, stage="planning")
                session.add(round_row)
                session.flush()

                planner = PlannerAgent()
                researcher = ResearcherAgent(search_provider=build_search_provider())
                critic = CriticAgent()
                synthesizer = SynthesizerAgent()

                planned_briefs = planner.plan(
                    topic=task.topic,
                    template_type=task.template_type,
                    round_goal="Initial research round",
                )

                researcher_outputs = []
                for planned_brief in planned_briefs:
                    brief_row = ResearchBrief(
                        id=planned_brief.brief_id,
                        round_id=round_row.id,
                        question=planned_brief.question,
                        priority=planned_brief.priority,
                        status="submitted",
                    )
                    session.add(brief_row)
                    session.flush()

                    output = researcher.research(planned_brief)
                    researcher_outputs.append(output)
                    fragment_rows: list[ResearchSourceFragment] = []

                    for index, result in enumerate(output.sources[:2]):
                        source_row = ResearchSource(
                            task_id=task.id,
                            source_url=result.url,
                            source_title=result.title,
                            provider=result.provider,
                            raw_content=result.content,
                        )
                        session.add(source_row)
                        session.flush()

                        fragment_payload = output.fragments[index]
                        fragment_row = ResearchSourceFragment(
                            source_id=source_row.id,
                            content=fragment_payload.content,
                            citation_label=fragment_payload.citation_label,
                            offset_start=fragment_payload.offset_start,
                            offset_end=fragment_payload.offset_end,
                        )
                        session.add(fragment_row)
                        session.flush()
                        fragment_rows.append(fragment_row)

                    finding_row = ResearchFinding(
                        brief_id=brief_row.id,
                        claim=output.finding.claim,
                        confidence=output.finding.confidence,
                    )
                    session.add(finding_row)
                    session.flush()
                    for fragment_row in fragment_rows:
                        session.add(
                            ResearchFindingSourceFragment(
                                finding_id=finding_row.id,
                                source_fragment_id=fragment_row.id,
                            )
                        )

                session.flush()

                verdict = critic.review([item.finding for item in researcher_outputs])
                accepted = [
                    AcceptedFinding(
                        brief_id=item.finding.brief_id,
                        claim=item.finding.claim,
                        citations=item.finding.source_fragments,
                    )
                    for item in researcher_outputs
                ]
                report = synthesizer.synthesize(
                    template_type=task.template_type,
                    findings=accepted if verdict.verdict == "accept" else [],
                )
                session.add(
                    ResearchReport(
                        task_id=task.id,
                        markdown_content=report.markdown_content,
                        html_content=report.html_content,
                    )
                )

                round_row.stage = "round_closed"
                task.status = TaskStatus.COMPLETED
                session.commit()
            except Exception as exc:
                task.status = TaskStatus.FAILED
                task.error_message = str(exc)
                session.commit()
                raise


@dataclass(slots=True)
class DemoRunResult:
    status: str
    current_round: int
    report: object


class _DemoSearchProvider:
    def search(self, query: str, max_results: int = 2) -> list[object]:
        from app.tools.search import SearchResult

        return [
            SearchResult(
                url=f"https://example.com/{query.replace(' ', '-')}",
                title=f"Result for {query}",
                content=f"{query} supports SMB buyers",
                provider="demo",
            ),
            SearchResult(
                url=f"https://backup.example.com/{query.replace(' ', '-')}",
                title=f"Backup for {query}",
                content=f"{query} highlights pricing and positioning",
                provider="demo",
            ),
        ]
