from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db, init_db
from fastapi import HTTPException

from app.schemas.task import BriefResponse, CreateTaskRequest, EvidenceResponse, ReportResponse, TaskDetailResponse, TaskResponse
from app.services.tasks import create_task as create_task_record
from app.services.tasks import get_report, get_task_detail, list_briefs, list_evidence, list_tasks
from app.services.tasks import to_task_response
from app.web.routes import router as web_router
from app.worker import run_research_task


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    if settings.auto_create_tables:
        init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(web_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/detailed")
def detailed_health(session: Session = Depends(get_db)) -> dict[str, str]:
    session.execute(text("select 1"))
    return {"status": "ok", "database": "ok"}


@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: CreateTaskRequest, session: Session = Depends(get_db)) -> TaskResponse:
    task = create_task_record(session, payload)
    response = to_task_response(task)
    run_research_task.delay(task.id)
    return response


@app.get("/api/tasks/{task_id}", response_model=TaskDetailResponse)
def get_task(task_id: str, session: Session = Depends(get_db)) -> TaskDetailResponse:
    task = get_task_detail(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/api/tasks", response_model=list[TaskResponse])
def get_tasks(session: Session = Depends(get_db)) -> list[TaskResponse]:
    return list_tasks(session)


@app.get("/api/tasks/{task_id}/briefs", response_model=list[BriefResponse])
def get_task_briefs(task_id: str, session: Session = Depends(get_db)) -> list[BriefResponse]:
    return list_briefs(session, task_id)


@app.get("/api/tasks/{task_id}/evidence", response_model=list[EvidenceResponse])
def get_task_evidence(task_id: str, session: Session = Depends(get_db)) -> list[EvidenceResponse]:
    return list_evidence(session, task_id)


@app.get("/api/tasks/{task_id}/report", response_model=ReportResponse)
def get_task_report(task_id: str, session: Session = Depends(get_db)) -> ReportResponse:
    report = get_report(session, task_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
