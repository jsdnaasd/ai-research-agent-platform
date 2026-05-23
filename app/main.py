from uuid import uuid4

from fastapi import FastAPI, status

from app.config import settings
from app.schemas.task import CreateTaskRequest, TaskResponse
from app.web.routes import router as web_router

app = FastAPI(title=settings.app_name)
_TASKS: list[TaskResponse] = []
app.include_router(web_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: CreateTaskRequest) -> TaskResponse:
    task = TaskResponse(
        id=str(uuid4()),
        topic=payload.topic,
        template_type=payload.template_type,
        user_context=payload.user_context,
        status="queued",
        current_round=0,
    )
    _TASKS.append(task)
    return task
