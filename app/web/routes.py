from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import get_db
from app.models.brief import ResearchBrief
from app.models.finding import ResearchFinding
from app.models.report import ResearchReport
from app.models.round import ResearchRound
from app.models.source import ResearchSource
from app.models.source_fragment import ResearchSourceFragment
from app.services.tasks import get_task_detail

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


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

    briefs = session.scalars(
        select(ResearchBrief).join(ResearchRound).where(ResearchRound.task_id == task_id).order_by(ResearchBrief.priority.asc())
    ).all()
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

    findings = session.scalars(
        select(ResearchFinding).join(ResearchBrief).join(ResearchRound).where(ResearchRound.task_id == task_id)
    ).all()
    fragments = session.scalars(
        select(ResearchSourceFragment).join(ResearchSource).where(ResearchSource.task_id == task_id)
    ).all()
    evidence_rows = [
        {
            "claim": finding.claim,
            "citations": [fragment.citation_label for fragment in fragments],
        }
        for finding in findings
    ]
    return templates.TemplateResponse(
        request,
        "evidence_explorer.html",
        {"task_id": task_id, "task": task, "findings": evidence_rows},
    )


@router.get("/tasks/{task_id}/report", response_class=HTMLResponse)
def report_page(request: Request, task_id: str, session: Session = Depends(get_db)) -> HTMLResponse:
    task = get_task_detail(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    report = session.scalar(select(ResearchReport).where(ResearchReport.task_id == task_id))
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
