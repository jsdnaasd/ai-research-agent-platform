from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ResearchFinding(Base):
    __tablename__ = "research_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    brief_id: Mapped[str] = mapped_column(ForeignKey("research_briefs.id"))
    claim: Mapped[str] = mapped_column(Text())
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
