from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.task import ResearchTask
from app.schemas.task import CreateTaskRequest, TaskResponse


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
