"""initial schema

Revision ID: 20260524_0001
Revises:
Create Date: 2026-05-24 01:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260524_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "research_tasks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("template_type", sa.String(length=64), nullable=False),
        sa.Column("user_context", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("current_round", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "research_rounds",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("task_id", sa.String(length=36), sa.ForeignKey("research_tasks.id"), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("stage", sa.String(length=64), nullable=False, server_default="planning"),
    )
    op.create_table(
        "research_briefs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("round_id", sa.String(length=36), sa.ForeignKey("research_rounds.id"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="pending"),
    )
    op.create_table(
        "research_sources",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("task_id", sa.String(length=36), sa.ForeignKey("research_tasks.id"), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_title", sa.Text(), nullable=False, server_default=""),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="tavily"),
        sa.Column("raw_content", sa.Text(), nullable=False, server_default=""),
    )
    op.create_table(
        "research_source_fragments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_id", sa.String(length=36), sa.ForeignKey("research_sources.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citation_label", sa.String(length=64), nullable=False),
        sa.Column("offset_start", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("offset_end", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "research_findings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("brief_id", sa.String(length=36), sa.ForeignKey("research_briefs.id"), nullable=False),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_table(
        "research_gaps",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("brief_id", sa.String(length=36), sa.ForeignKey("research_briefs.id"), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
    )
    op.create_table(
        "research_reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("task_id", sa.String(length=36), sa.ForeignKey("research_tasks.id"), nullable=False),
        sa.Column("markdown_content", sa.Text(), nullable=False, server_default=""),
        sa.Column("html_content", sa.Text(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_table("research_reports")
    op.drop_table("research_gaps")
    op.drop_table("research_findings")
    op.drop_table("research_source_fragments")
    op.drop_table("research_sources")
    op.drop_table("research_briefs")
    op.drop_table("research_rounds")
    op.drop_table("research_tasks")
