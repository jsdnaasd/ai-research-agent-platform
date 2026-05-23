from __future__ import annotations

from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ResearchSourceFragment(Base):
    __tablename__ = "research_source_fragments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[str] = mapped_column(ForeignKey("research_sources.id"))
    content: Mapped[str] = mapped_column(Text())
    citation_label: Mapped[str] = mapped_column(String(64))
    offset_start: Mapped[int] = mapped_column(Integer, default=0)
    offset_end: Mapped[int] = mapped_column(Integer, default=0)
