from datetime import datetime

from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    topic: str
    template_type: str
    user_context: str | None = None


class TaskResponse(BaseModel):
    id: str
    topic: str
    template_type: str
    user_context: str | None
    status: str
    current_round: int
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class TaskDetailResponse(TaskResponse):
    brief_count: int
    finding_count: int
    source_count: int
    report_ready: bool


class BriefResponse(BaseModel):
    id: str
    question: str
    priority: int
    status: str


class EvidenceResponse(BaseModel):
    claim: str
    citations: list[str]


class ReportResponse(BaseModel):
    markdown_content: str
    html_content: str
