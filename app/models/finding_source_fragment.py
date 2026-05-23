from __future__ import annotations

from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ResearchFindingSourceFragment(Base):
    __tablename__ = "research_finding_source_fragments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    finding_id: Mapped[str] = mapped_column(ForeignKey("research_findings.id"))
    source_fragment_id: Mapped[str] = mapped_column(ForeignKey("research_source_fragments.id"))
