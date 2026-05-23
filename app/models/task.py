from __future__ import annotations

from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TaskStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_FOR_RETRY = "waiting_for_retry"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"


class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    topic: Mapped[str] = mapped_column(String(255))
    template_type: Mapped[str] = mapped_column(String(64))
    user_context: Mapped[str | None] = mapped_column(Text(), nullable=True, default=None)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.QUEUED)
    current_round: Mapped[int] = mapped_column(Integer, default=0)

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("status", TaskStatus.QUEUED)
        kwargs.setdefault("current_round", 0)
        super().__init__(**kwargs)
