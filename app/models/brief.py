from __future__ import annotations

from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ResearchBrief(Base):
    __tablename__ = "research_briefs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    round_id: Mapped[str] = mapped_column(ForeignKey("research_rounds.id"))
    question: Mapped[str] = mapped_column(Text())
    priority: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(64), default="pending")
