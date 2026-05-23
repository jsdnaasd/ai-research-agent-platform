from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

_DEMO_FINDINGS = [
    {"claim": "SMB pricing starts at $29", "citations": ["fragment-1", "fragment-2"]},
    {"claim": "Competitor positioning emphasizes developer workflows", "citations": ["fragment-3"]},
]


@router.get("/tasks/{task_id}", response_class=HTMLResponse)
def task_overview(request: Request, task_id: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "task_overview.html",
        {
            "task_id": task_id,
            "rounds": [{"id": 1, "stage": "critic_review"}],
            "brief_count": 3,
        },
    )


@router.get("/tasks/{task_id}/briefs", response_class=HTMLResponse)
def brief_board(request: Request, task_id: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "brief_board.html",
        {
            "task_id": task_id,
            "briefs": [
                {"id": "brief-1", "status": "accepted", "question": "pricing"},
                {"id": "brief-2", "status": "accepted", "question": "positioning"},
                {"id": "brief-3", "status": "critic_review", "question": "traction"},
            ],
        },
    )


@router.get("/tasks/{task_id}/evidence", response_class=HTMLResponse)
def evidence_explorer(request: Request, task_id: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "evidence_explorer.html",
        {"task_id": task_id, "findings": _DEMO_FINDINGS},
    )


@router.get("/tasks/{task_id}/report", response_class=HTMLResponse)
def report_page(request: Request, task_id: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "report.html",
        {"task_id": task_id, "findings": _DEMO_FINDINGS, "template_type": "market_scan"},
    )
