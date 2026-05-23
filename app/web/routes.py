from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import get_db
from app.models.round import ResearchRound
from app.schemas.task import CreateTaskRequest
from app.services.tasks import create_task as create_task_record
from app.services.tasks import get_report, get_task_detail, list_briefs, list_evidence, list_tasks
from app.worker import run_research_task

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def homepage(request: Request, session: Session = Depends(get_db)) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "home.html",
        {"tasks": list_tasks(session)},
    )


@router.post("/tasks/new")
def create_task_from_form(
    topic: str = Form(...),
    template_type: str = Form(...),
    user_context: str | None = Form(default=None),
    session: Session = Depends(get_db),
) -> RedirectResponse:
    task = create_task_record(
        session,
        CreateTaskRequest(topic=topic, template_type=template_type, user_context=user_context),
    )
    run_research_task.delay(task.id)
    return RedirectResponse(url=f"/tasks/{task.id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/tasks/{task_id}", response_class=HTMLResponse)
def task_overview(request: Request, task_id: str, session: Session = Depends(get_db)) -> HTMLResponse:
    task = get_task_detail(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    rounds = session.scalars(
        select(ResearchRound).where(ResearchRound.task_id == task_id).order_by(ResearchRound.round_number.asc())
    ).all()
    return templates.TemplateResponse(
        request,
        "task_overview.html",
        {
            "task_id": task_id,
            "task": task,
            "rounds": rounds,
            "brief_count": task.brief_count,
        },
    )


@router.get("/tasks/{task_id}/briefs", response_class=HTMLResponse)
def brief_board(request: Request, task_id: str, session: Session = Depends(get_db)) -> HTMLResponse:
    task = get_task_detail(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    briefs = list_briefs(session, task_id)
    return templates.TemplateResponse(
        request,
        "brief_board.html",
        {
            "task_id": task_id,
            "task": task,
            "briefs": briefs,
        },
    )


@router.get("/tasks/{task_id}/evidence", response_class=HTMLResponse)
def evidence_explorer(request: Request, task_id: str, session: Session = Depends(get_db)) -> HTMLResponse:
    task = get_task_detail(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return templates.TemplateResponse(
        request,
        "evidence_explorer.html",
        {"task_id": task_id, "task": task, "findings": list_evidence(session, task_id)},
    )


@router.get("/tasks/{task_id}/report", response_class=HTMLResponse)
def report_page(request: Request, task_id: str, session: Session = Depends(get_db)) -> HTMLResponse:
    task = get_task_detail(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    report = get_report(session, task_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return templates.TemplateResponse(
        request,
        "report.html",
        {
            "task_id": task_id,
            "task": task,
            "report": report,
            "template_type": task.template_type,
        },
    )
