from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db, init_db
from app.schemas.task import CreateTaskRequest, TaskResponse
from app.services.tasks import create_task as create_task_record
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


@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: CreateTaskRequest, session: Session = Depends(get_db)) -> TaskResponse:
    task = create_task_record(session, payload)
    response = to_task_response(task)
    run_research_task.delay(task.id)
    return response
