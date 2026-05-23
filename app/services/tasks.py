from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.brief import ResearchBrief
from app.models.finding import ResearchFinding
from app.models.report import ResearchReport
from app.models.round import ResearchRound
from app.models.source import ResearchSource
from app.models.task import ResearchTask
from app.schemas.task import CreateTaskRequest, TaskDetailResponse, TaskResponse


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
        brief_count=int(brief_count),
        finding_count=int(finding_count),
        source_count=int(source_count),
        report_ready=bool(report_ready),
    )
