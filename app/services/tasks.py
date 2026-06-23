from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.brief import ResearchBrief
from app.models.finding import ResearchFinding
from app.models.finding_source_fragment import ResearchFindingSourceFragment
from app.models.report import ResearchReport
from app.models.round import ResearchRound
from app.models.source import ResearchSource
from app.models.source_fragment import ResearchSourceFragment
from app.models.task import ResearchTask
from app.schemas.task import (
    BriefResponse,
    CreateTaskRequest,
    EvidenceResponse,
    ReportResponse,
    TaskDetailResponse,
    TaskResponse,
)


def create_task(session: Session, payload: CreateTaskRequest) -> ResearchTask:
    task = ResearchTask(
        topic=payload.topic,
        template_type=payload.template_type,
        user_context=payload.user_context,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_task(session: Session, task_id: str) -> ResearchTask | None:
    return session.get(ResearchTask, task_id)


def to_task_response(task: ResearchTask) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        topic=task.topic,
        template_type=task.template_type,
        user_context=task.user_context,
        status=task.status.value,
        current_round=task.current_round,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def get_task_detail(session: Session, task_id: str) -> TaskDetailResponse | None:
    task = get_task(session, task_id)
    if task is None:
        return None

    brief_count = session.scalar(select(func.count()).select_from(ResearchBrief).join(ResearchRound).where(ResearchRound.task_id == task_id)) or 0
    finding_count = session.scalar(
        select(func.count()).select_from(ResearchFinding).join(ResearchBrief).join(ResearchRound).where(ResearchRound.task_id == task_id)
    ) or 0
    source_count = session.scalar(select(func.count()).select_from(ResearchSource).where(ResearchSource.task_id == task_id)) or 0
    report_ready = session.scalar(select(func.count()).select_from(ResearchReport).where(ResearchReport.task_id == task_id)) or 0

    return TaskDetailResponse(
        id=task.id,
        topic=task.topic,
        template_type=task.template_type,
        user_context=task.user_context,
        status=task.status.value,
        current_round=task.current_round,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
        brief_count=int(brief_count),
        finding_count=int(finding_count),
        source_count=int(source_count),
        report_ready=bool(report_ready),
    )


def list_tasks(session: Session, limit: int = 10) -> list[TaskResponse]:
    tasks = session.scalars(select(ResearchTask).order_by(ResearchTask.created_at.desc()).limit(limit)).all()
    return [to_task_response(task) for task in tasks]


def list_briefs(session: Session, task_id: str) -> list[BriefResponse]:
    briefs = session.scalars(
        select(ResearchBrief).join(ResearchRound).where(ResearchRound.task_id == task_id).order_by(ResearchBrief.priority.asc())
    ).all()
    return [
        BriefResponse(
            id=brief.id,
            question=brief.question,
            priority=brief.priority,
            status=brief.status,
        )
        for brief in briefs
    ]


def list_evidence(session: Session, task_id: str) -> list[EvidenceResponse]:
    findings = session.scalars(
        select(ResearchFinding).join(ResearchBrief).join(ResearchRound).where(ResearchRound.task_id == task_id)
    ).all()
    fragment_links = session.execute(
        select(ResearchFinding.claim, ResearchSourceFragment.citation_label)
        .join(ResearchFindingSourceFragment, ResearchFindingSourceFragment.finding_id == ResearchFinding.id)
        .join(ResearchSourceFragment, ResearchSourceFragment.id == ResearchFindingSourceFragment.source_fragment_id)
        .join(ResearchSource, ResearchSource.id == ResearchSourceFragment.source_id)
        .where(ResearchSource.task_id == task_id)
    ).all()
    citations_by_claim: dict[str, list[str]] = {}
    for claim, citation_label in fragment_links:
        citations_by_claim.setdefault(claim, []).append(citation_label)

    return [
        EvidenceResponse(
            claim=finding.claim,
            citations=citations_by_claim.get(finding.claim, []),
        )
        for finding in findings
    ]


def get_report(session: Session, task_id: str) -> ReportResponse | None:
    report = session.scalar(select(ResearchReport).where(ResearchReport.task_id == task_id))
    if report is None:
        return None
    return ReportResponse(markdown_content=report.markdown_content, html_content=report.html_content)
