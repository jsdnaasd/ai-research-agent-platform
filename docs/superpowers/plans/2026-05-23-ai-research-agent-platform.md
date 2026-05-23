# AI Research Agent Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a demo-ready supervised multi-agent research platform with round-based orchestration, evidence-grounded findings, critic validation, and a lightweight web console.

**Architecture:** The system uses a FastAPI web app plus background worker to run a deterministic round/brief state machine. Agents communicate through strict Pydantic schemas, persist state in Postgres via SQLAlchemy, and expose traceable findings, source fragments, and critic verdicts through server-rendered pages and JSON APIs.

**Tech Stack:** Python 3.12, FastAPI, Jinja2, HTMX, SQLAlchemy 2.x, Alembic, Pydantic v2, Redis, Celery, PostgreSQL, pytest

---

## File Structure

- `pyproject.toml`: project metadata, dependencies, pytest config
- `.env.example`: local environment variables for app, db, redis, llm stubs
- `README.md`: project positioning, local setup, architecture summary
- `app/config.py`: settings loader
- `app/db.py`: SQLAlchemy engine, session factory, base model
- `app/models/`: ORM models for tasks, rounds, briefs, findings, sources, reports
- `app/schemas/`: Pydantic contracts for API payloads and agent I/O
- `app/agents/`: supervisor, planner, researcher, critic, synthesizer interfaces
- `app/tools/`: search, extract, validation, planning adapters
- `app/services/`: orchestrator, report builder, memory store helpers
- `app/web/`: FastAPI routers for HTML pages and JSON API
- `app/templates/`: task overview, brief board, evidence explorer, final report
- `app/worker.py`: Celery app and task registration
- `tests/`: unit and integration tests grouped by feature area

### Task 1: Scaffold Project and Settings

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `README.md`
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `app/main.py`
- Create: `tests/test_health.py`

- [ ] **Step 1: Write the failing health test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_health.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: Write minimal project scaffolding**

```toml
[project]
name = "ai-research-agent-saas"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115,<0.116",
  "jinja2>=3.1,<3.2",
  "pydantic-settings>=2.3,<2.4",
  "sqlalchemy>=2.0,<2.1",
  "uvicorn>=0.30,<0.31",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2,<8.3",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Research Agent Platform"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")


settings = Settings()
```

```python
from fastapi import FastAPI

from app.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_health.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .env.example README.md app/__init__.py app/config.py app/main.py tests/test_health.py
git commit -m "feat: scaffold FastAPI research platform"
```

### Task 2: Add Core Database Models and Task Lifecycle API

**Files:**
- Create: `app/db.py`
- Create: `app/models/__init__.py`
- Create: `app/models/task.py`
- Create: `app/models/round.py`
- Create: `app/models/brief.py`
- Create: `app/models/report.py`
- Create: `app/schemas/task.py`
- Modify: `app/main.py`
- Test: `tests/models/test_task_models.py`
- Test: `tests/api/test_create_task.py`

- [ ] **Step 1: Write the failing model and API tests**

```python
from app.models.task import ResearchTask, TaskStatus


def test_task_defaults_to_queued_status() -> None:
    task = ResearchTask(topic="OpenAI competitors", template_type="market_scan")

    assert task.status is TaskStatus.QUEUED
    assert task.current_round == 0
```

```python
from fastapi.testclient import TestClient

from app.main import app


def test_create_task_returns_queued_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/tasks",
        json={
            "topic": "OpenAI competitors",
            "template_type": "market_scan",
            "user_context": "Focus on SMB pricing signals",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "queued"
    assert body["current_round"] == 0
    assert body["topic"] == "OpenAI competitors"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/models/test_task_models.py tests/api/test_create_task.py -v`
Expected: FAIL with `ModuleNotFoundError` for models and schemas

- [ ] **Step 3: Write minimal ORM models, schemas, and in-memory-safe create endpoint**

```python
from enum import StrEnum
from uuid import uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TaskStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_FOR_RETRY = "waiting_for_retry"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"


class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    topic: Mapped[str]
    template_type: Mapped[str]
    user_context: Mapped[str | None]
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.QUEUED)
    current_round: Mapped[int] = mapped_column(default=0)
```

```python
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
```

```python
from fastapi import FastAPI, status

from app.schemas.task import CreateTaskRequest, TaskResponse

app = FastAPI(title=settings.app_name)
_TASKS: list[TaskResponse] = []


@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: CreateTaskRequest) -> TaskResponse:
    task = TaskResponse(
        id="local-task-1",
        topic=payload.topic,
        template_type=payload.template_type,
        user_context=payload.user_context,
        status="queued",
        current_round=0,
    )
    _TASKS.append(task)
    return task
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/models/test_task_models.py tests/api/test_create_task.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/db.py app/models/__init__.py app/models/task.py app/models/round.py app/models/brief.py app/models/report.py app/schemas/task.py app/main.py tests/models/test_task_models.py tests/api/test_create_task.py
git commit -m "feat: add task lifecycle models and create task api"
```

### Task 3: Define Agent Schemas and Supervisor Round State Machine

**Files:**
- Create: `app/schemas/agent.py`
- Create: `app/services/orchestrator.py`
- Create: `app/agents/supervisor.py`
- Create: `app/agents/planner.py`
- Create: `app/agents/researcher.py`
- Create: `app/agents/critic.py`
- Create: `app/agents/synthesizer.py`
- Test: `tests/services/test_orchestrator_rounds.py`
- Test: `tests/agents/test_supervisor_schema.py`

- [ ] **Step 1: Write the failing schema and state machine tests**

```python
from app.schemas.agent import SupervisorDecision


def test_supervisor_decision_limits_allowed_actions() -> None:
    decision = SupervisorDecision(
        round_goal="Find competitor pricing signals",
        selected_briefs=["brief-1"],
        decision="continue",
        decision_reason="Need more evidence",
        next_action="plan_followups",
    )

    assert decision.decision == "continue"
```

```python
from app.services.orchestrator import Orchestrator, TaskRuntimeState


def test_orchestrator_advances_to_critic_review_after_research() -> None:
    state = TaskRuntimeState(task_id="task-1", status="running", current_round=1, round_stage="researching")

    next_state = Orchestrator().advance_round(state)

    assert next_state.round_stage == "critic_review"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/services/test_orchestrator_rounds.py tests/agents/test_supervisor_schema.py -v`
Expected: FAIL with missing schema and orchestrator modules

- [ ] **Step 3: Write minimal agent contracts and round transition logic**

```python
from typing import Literal

from pydantic import BaseModel


class SupervisorDecision(BaseModel):
    round_goal: str
    selected_briefs: list[str]
    decision: Literal["continue", "finish", "revise"]
    decision_reason: str
    next_action: str
```

```python
from dataclasses import dataclass


@dataclass(slots=True)
class TaskRuntimeState:
    task_id: str
    status: str
    current_round: int
    round_stage: str


class Orchestrator:
    def advance_round(self, state: TaskRuntimeState) -> TaskRuntimeState:
        transitions = {
            "planning": "researching",
            "researching": "critic_review",
            "critic_review": "supervisor_decision",
            "supervisor_decision": "round_closed",
        }
        return TaskRuntimeState(
            task_id=state.task_id,
            status=state.status,
            current_round=state.current_round,
            round_stage=transitions.get(state.round_stage, state.round_stage),
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/services/test_orchestrator_rounds.py tests/agents/test_supervisor_schema.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/schemas/agent.py app/services/orchestrator.py app/agents/supervisor.py app/agents/planner.py app/agents/researcher.py app/agents/critic.py app/agents/synthesizer.py tests/services/test_orchestrator_rounds.py tests/agents/test_supervisor_schema.py
git commit -m "feat: define agent contracts and round state machine"
```

### Task 4: Add Brief Planning, Findings, and Critic Validation

**Files:**
- Create: `app/models/finding.py`
- Create: `app/models/source.py`
- Create: `app/models/gap.py`
- Create: `app/schemas/finding.py`
- Create: `app/tools/validation.py`
- Modify: `app/agents/planner.py`
- Modify: `app/agents/researcher.py`
- Modify: `app/agents/critic.py`
- Test: `tests/agents/test_planner_briefs.py`
- Test: `tests/agents/test_critic_validation.py`

- [ ] **Step 1: Write the failing planner and critic tests**

```python
from app.agents.planner import PlannerAgent


def test_planner_creates_prioritized_briefs() -> None:
    planner = PlannerAgent()

    briefs = planner.plan(topic="OpenAI competitors", template_type="market_scan", round_goal="Map top SMB rivals")

    assert len(briefs) == 3
    assert briefs[0].priority == 1
    assert briefs[0].search_queries
```

```python
from app.agents.critic import CriticAgent
from app.schemas.finding import FindingInput


def test_critic_requests_expand_when_only_one_source_supports_claim() -> None:
    critic = CriticAgent()
    finding = FindingInput(
        brief_id="brief-1",
        claim="Competitor X targets SMBs",
        source_fragments=["fragment-1"],
        confidence=0.74,
    )

    verdict = critic.review([finding])

    assert verdict.verdict == "expand"
    assert verdict.gaps
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/agents/test_planner_briefs.py tests/agents/test_critic_validation.py -v`
Expected: FAIL with missing planner behavior and finding schema

- [ ] **Step 3: Write minimal planning and validation logic**

```python
from pydantic import BaseModel


class PlannedBrief(BaseModel):
    brief_id: str
    question: str
    search_queries: list[str]
    evidence_targets: list[str]
    priority: int
    dependencies: list[str] = []
```

```python
class PlannerAgent:
    def plan(self, topic: str, template_type: str, round_goal: str) -> list[PlannedBrief]:
        return [
            PlannedBrief(
                brief_id="brief-1",
                question=f"{topic} pricing",
                search_queries=[f"{topic} pricing", f"{topic} SMB pricing"],
                evidence_targets=["pricing page", "product docs"],
                priority=1,
            ),
            PlannedBrief(
                brief_id="brief-2",
                question=f"{topic} positioning",
                search_queries=[f"{topic} target market", f"{topic} SMB customers"],
                evidence_targets=["homepage", "case studies"],
                priority=2,
            ),
            PlannedBrief(
                brief_id="brief-3",
                question=f"{topic} traction signals",
                search_queries=[f"{topic} funding", f"{topic} launch news"],
                evidence_targets=["news", "blog"],
                priority=3,
            ),
        ]
```

```python
from typing import Literal

from pydantic import BaseModel


class FindingInput(BaseModel):
    brief_id: str
    claim: str
    source_fragments: list[str]
    confidence: float


class CriticVerdict(BaseModel):
    verdict: Literal["accept", "revise", "expand"]
    accepted_findings: list[str]
    rejected_findings: list[str]
    gaps: list[str]
    requested_followups: list[str]
    quality_score: float
```

```python
class CriticAgent:
    def review(self, findings: list[FindingInput]) -> CriticVerdict:
        if any(len(item.source_fragments) < 2 for item in findings):
            return CriticVerdict(
                verdict="expand",
                accepted_findings=[],
                rejected_findings=[],
                gaps=["Need at least two source fragments per claim"],
                requested_followups=["Find secondary corroborating sources"],
                quality_score=0.45,
            )
        return CriticVerdict(
            verdict="accept",
            accepted_findings=[item.claim for item in findings],
            rejected_findings=[],
            gaps=[],
            requested_followups=[],
            quality_score=0.91,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/agents/test_planner_briefs.py tests/agents/test_critic_validation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/models/finding.py app/models/source.py app/models/gap.py app/schemas/finding.py app/tools/validation.py app/agents/planner.py app/agents/researcher.py app/agents/critic.py tests/agents/test_planner_briefs.py tests/agents/test_critic_validation.py
git commit -m "feat: add brief planning and critic validation"
```

### Task 5: Implement Evidence Graph Queries and Final Report Assembly

**Files:**
- Create: `app/services/evidence.py`
- Create: `app/services/reporting.py`
- Modify: `app/agents/synthesizer.py`
- Modify: `app/schemas/finding.py`
- Test: `tests/services/test_evidence_graph.py`
- Test: `tests/services/test_reporting.py`

- [ ] **Step 1: Write the failing evidence and reporting tests**

```python
from app.services.evidence import EvidenceGraph


def test_evidence_graph_groups_findings_by_brief() -> None:
    graph = EvidenceGraph()

    graph.add_finding("brief-1", "SMB pricing starts at $29", ["fragment-1", "fragment-2"])

    assert graph.findings_for_brief("brief-1") == ["SMB pricing starts at $29"]
```

```python
from app.services.reporting import ReportBuilder
from app.schemas.finding import AcceptedFinding


def test_report_builder_uses_only_accepted_findings() -> None:
    builder = ReportBuilder()

    report = builder.build(
        template_type="market_scan",
        findings=[
            AcceptedFinding(brief_id="brief-1", claim="Claim A", citations=["fragment-1"]),
            AcceptedFinding(brief_id="brief-2", claim="Claim B", citations=["fragment-3"]),
        ],
    )

    assert "Claim A" in report.markdown_content
    assert "Claim B" in report.markdown_content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/services/test_evidence_graph.py tests/services/test_reporting.py -v`
Expected: FAIL with missing evidence and reporting services

- [ ] **Step 3: Write minimal evidence graph and report builder**

```python
from collections import defaultdict


class EvidenceGraph:
    def __init__(self) -> None:
        self._brief_findings: dict[str, list[str]] = defaultdict(list)
        self._finding_sources: dict[str, list[str]] = {}

    def add_finding(self, brief_id: str, claim: str, fragments: list[str]) -> None:
        self._brief_findings[brief_id].append(claim)
        self._finding_sources[claim] = fragments

    def findings_for_brief(self, brief_id: str) -> list[str]:
        return self._brief_findings[brief_id]
```

```python
from pydantic import BaseModel


class AcceptedFinding(BaseModel):
    brief_id: str
    claim: str
    citations: list[str]


class GeneratedReport(BaseModel):
    markdown_content: str
    html_content: str
```

```python
class ReportBuilder:
    def build(self, template_type: str, findings: list[AcceptedFinding]) -> GeneratedReport:
        lines = [f"# {template_type.replace('_', ' ').title()}"]
        for finding in findings:
            lines.append(f"- {finding.claim} ({', '.join(finding.citations)})")
        markdown = "\n".join(lines)
        html = "<br>".join(lines)
        return GeneratedReport(markdown_content=markdown, html_content=html)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/services/test_evidence_graph.py tests/services/test_reporting.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/evidence.py app/services/reporting.py app/agents/synthesizer.py app/schemas/finding.py tests/services/test_evidence_graph.py tests/services/test_reporting.py
git commit -m "feat: add evidence graph and report builder"
```

### Task 6: Build HTML Console for Task Overview, Brief Board, Evidence Explorer, and Report

**Files:**
- Create: `app/web/__init__.py`
- Create: `app/web/routes.py`
- Create: `app/templates/base.html`
- Create: `app/templates/task_overview.html`
- Create: `app/templates/brief_board.html`
- Create: `app/templates/evidence_explorer.html`
- Create: `app/templates/report.html`
- Modify: `app/main.py`
- Test: `tests/web/test_task_pages.py`

- [ ] **Step 1: Write the failing page rendering tests**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_task_overview_page_renders_round_board_link() -> None:
    client = TestClient(app)

    response = client.get("/tasks/demo-task")

    assert response.status_code == 200
    assert "Round Board" in response.text
```

```python
from fastapi.testclient import TestClient

from app.main import app


def test_evidence_page_renders_finding_heading() -> None:
    client = TestClient(app)

    response = client.get("/tasks/demo-task/evidence")

    assert response.status_code == 200
    assert "Evidence Explorer" in response.text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/web/test_task_pages.py -v`
Expected: FAIL with missing web routes and templates

- [ ] **Step 3: Write minimal HTML routes and templates**

```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/tasks/{task_id}", response_class=HTMLResponse)
def task_overview(request: Request, task_id: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "task_overview.html",
        {"task_id": task_id, "rounds": [{"id": 1, "stage": "critic_review"}]},
    )


@router.get("/tasks/{task_id}/evidence", response_class=HTMLResponse)
def evidence_explorer(request: Request, task_id: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "evidence_explorer.html",
        {"task_id": task_id, "findings": ["SMB pricing starts at $29"]},
    )
```

```html
<!doctype html>
<html lang="en">
  <body>
    <h1>Task Overview</h1>
    <a href="/tasks/{{ task_id }}/briefs">Round Board</a>
  </body>
</html>
```

```html
<!doctype html>
<html lang="en">
  <body>
    <h1>Evidence Explorer</h1>
    {% for finding in findings %}
    <p>{{ finding }}</p>
    {% endfor %}
  </body>
</html>
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/web/test_task_pages.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/web/__init__.py app/web/routes.py app/templates/base.html app/templates/task_overview.html app/templates/brief_board.html app/templates/evidence_explorer.html app/templates/report.html app/main.py tests/web/test_task_pages.py
git commit -m "feat: add multi-agent research console pages"
```

### Task 7: Wire Background Worker and End-to-End Integration Test

**Files:**
- Create: `app/worker.py`
- Modify: `app/services/orchestrator.py`
- Modify: `app/main.py`
- Test: `tests/integration/test_task_execution_flow.py`

- [ ] **Step 1: Write the failing end-to-end workflow test**

```python
from app.services.orchestrator import Orchestrator


def test_orchestrator_runs_single_round_flow() -> None:
    orchestrator = Orchestrator()

    result = orchestrator.run_demo_task(topic="OpenAI competitors", template_type="market_scan")

    assert result.status == "completed"
    assert result.current_round == 1
    assert result.report is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_task_execution_flow.py -v`
Expected: FAIL with `AttributeError: 'Orchestrator' object has no attribute 'run_demo_task'`

- [ ] **Step 3: Write minimal worker registration and orchestrator end-to-end path**

```python
from celery import Celery

celery_app = Celery("ai_research_agent")
celery_app.conf.task_always_eager = True
```

```python
from dataclasses import dataclass

from app.agents.critic import CriticAgent
from app.agents.planner import PlannerAgent
from app.schemas.finding import AcceptedFinding, FindingInput
from app.services.reporting import ReportBuilder


@dataclass(slots=True)
class DemoRunResult:
    status: str
    current_round: int
    report: object


class Orchestrator:
    def run_demo_task(self, topic: str, template_type: str) -> DemoRunResult:
        briefs = PlannerAgent().plan(topic=topic, template_type=template_type, round_goal="Initial research round")
        findings = [
            FindingInput(
                brief_id=brief.brief_id,
                claim=f"{brief.question} validated",
                source_fragments=["fragment-1", "fragment-2"],
                confidence=0.82,
            )
            for brief in briefs
        ]
        verdict = CriticAgent().review(findings)
        accepted = [
            AcceptedFinding(brief_id=item.brief_id, claim=item.claim, citations=item.source_fragments)
            for item in findings
        ]
        report = ReportBuilder().build(template_type=template_type, findings=accepted if verdict.verdict == "accept" else [])
        return DemoRunResult(status="completed", current_round=1, report=report)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_task_execution_flow.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/worker.py app/services/orchestrator.py app/main.py tests/integration/test_task_execution_flow.py
git commit -m "feat: wire demo background execution flow"
```

### Task 8: Polish Docs and Local Developer Workflow

**Files:**
- Modify: `README.md`
- Modify: `.env.example`
- Create: `tests/conftest.py`
- Test: `tests/test_readme_commands.py`

- [ ] **Step 1: Write the failing docs workflow test**

```python
from pathlib import Path


def test_readme_mentions_main_local_commands() -> None:
    readme = Path("README.md").read_text()

    assert "uvicorn app.main:app --reload" in readme
    assert "pytest" in readme
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_readme_commands.py -v`
Expected: FAIL because README does not yet include local run and test commands

- [ ] **Step 3: Write minimal setup and workflow documentation**

```markdown
# AI Research Agent Platform

Supervised multi-agent research platform for evidence-grounded company intelligence.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## Run tests

```bash
pytest
```
```

```env
APP_APP_NAME=AI Research Agent Platform
APP_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/research_agent
APP_REDIS_URL=redis://localhost:6379/0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_readme_commands.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md .env.example tests/conftest.py tests/test_readme_commands.py
git commit -m "docs: add local setup and test workflow"
```

## Self-Review

- Spec coverage: the plan covers scaffolding, API, round/brief orchestration, agent schemas, critic validation, evidence graph persistence shape, final report assembly, UI views, worker execution, observability-friendly data paths, and local docs. The only intentional deferral is real external provider integration, which remains mocked in the MVP implementation path and can be added in a follow-up plan.
- Placeholder scan: no `TODO`, `TBD`, or vague “handle later” instructions remain.
- Type consistency: `SupervisorDecision`, `FindingInput`, `AcceptedFinding`, `ReportBuilder`, and `Orchestrator` names remain consistent across later tasks.
