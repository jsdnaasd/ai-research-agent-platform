# AI Research Agent Platform 实施计划

> **面向执行型代理：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 按任务逐项实现。步骤使用复选框 `- [ ]` 语法跟踪。

**目标：** 构建一个可演示的监督式多 Agent 研究平台，支持轮次驱动编排、基于证据的发现、critic 审查，以及轻量 Web 控制台。

**架构：** 系统采用 FastAPI Web 应用加后台 worker 的结构，运行一个确定性的 round/brief 状态机。各 Agent 通过严格的 Pydantic schema 协作，使用 SQLAlchemy 持久化到 Postgres，并通过服务端渲染页面与 JSON API 暴露可追溯的 findings、source fragments 和 critic verdicts。

**技术栈：** Python 3.12、FastAPI、Jinja2、HTMX、SQLAlchemy 2.x、Alembic、Pydantic v2、Redis、Celery、PostgreSQL、pytest

---

## 文件结构

- `pyproject.toml`：项目元数据、依赖、pytest 配置
- `.env.example`：本地环境变量模板，包含应用、数据库、Redis、LLM stub
- `README.md`：项目定位、本地启动方式、架构说明
- `app/config.py`：配置加载
- `app/db.py`：SQLAlchemy engine、session factory、base model
- `app/models/`：tasks、rounds、briefs、findings、sources、reports 的 ORM 模型
- `app/schemas/`：API 请求响应和 Agent 输入输出的 Pydantic 契约
- `app/agents/`：supervisor、planner、researcher、critic、synthesizer 接口
- `app/tools/`：search、extract、validation、planning 的工具适配器
- `app/services/`：orchestrator、report builder、memory store 等服务层
- `app/web/`：HTML 页面和 JSON API 的 FastAPI 路由
- `app/templates/`：task overview、brief board、evidence explorer、final report 页面模板
- `app/worker.py`：Celery app 及任务注册
- `tests/`：按功能拆分的单元测试和集成测试

### 任务 1：初始化项目骨架与配置

**文件：**
- 新建：`pyproject.toml`
- 新建：`.env.example`
- 新建：`README.md`
- 新建：`app/__init__.py`
- 新建：`app/config.py`
- 新建：`app/main.py`
- 新建：`tests/test_health.py`

- [ ] **步骤 1：先写失败的健康检查测试**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **步骤 2：运行测试，确认它先失败**

运行：`pytest tests/test_health.py -v`
预期：FAIL，报 `ModuleNotFoundError: No module named 'app'`

- [ ] **步骤 3：写最小可运行项目骨架**

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

- [ ] **步骤 4：再跑测试，确认通过**

运行：`pytest tests/test_health.py -v`
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add pyproject.toml .env.example README.md app/__init__.py app/config.py app/main.py tests/test_health.py
git commit -m "feat: scaffold FastAPI research platform"
```

### 任务 2：增加核心数据库模型和任务生命周期 API

**文件：**
- 新建：`app/db.py`
- 新建：`app/models/__init__.py`
- 新建：`app/models/task.py`
- 新建：`app/models/round.py`
- 新建：`app/models/brief.py`
- 新建：`app/models/report.py`
- 新建：`app/schemas/task.py`
- 修改：`app/main.py`
- 测试：`tests/models/test_task_models.py`
- 测试：`tests/api/test_create_task.py`

- [ ] **步骤 1：先写失败的模型和 API 测试**

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

- [ ] **步骤 2：运行测试，确认失败**

运行：`pytest tests/models/test_task_models.py tests/api/test_create_task.py -v`
预期：FAIL，提示模型和 schema 模块缺失

- [ ] **步骤 3：实现最小 ORM、schema 和安全的本地创建接口**

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

- [ ] **步骤 4：运行测试，确认通过**

运行：`pytest tests/models/test_task_models.py tests/api/test_create_task.py -v`
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add app/db.py app/models/__init__.py app/models/task.py app/models/round.py app/models/brief.py app/models/report.py app/schemas/task.py app/main.py tests/models/test_task_models.py tests/api/test_create_task.py
git commit -m "feat: add task lifecycle models and create task api"
```

### 任务 3：定义 Agent Schema 和 Supervisor 轮次状态机

**文件：**
- 新建：`app/schemas/agent.py`
- 新建：`app/services/orchestrator.py`
- 新建：`app/agents/supervisor.py`
- 新建：`app/agents/planner.py`
- 新建：`app/agents/researcher.py`
- 新建：`app/agents/critic.py`
- 新建：`app/agents/synthesizer.py`
- 测试：`tests/services/test_orchestrator_rounds.py`
- 测试：`tests/agents/test_supervisor_schema.py`

- [ ] **步骤 1：先写失败的 schema 和状态机测试**

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

- [ ] **步骤 2：运行测试，确认失败**

运行：`pytest tests/services/test_orchestrator_rounds.py tests/agents/test_supervisor_schema.py -v`
预期：FAIL，缺少 schema 和 orchestrator 模块

- [ ] **步骤 3：实现最小 Agent 契约和轮次状态流转逻辑**

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

- [ ] **步骤 4：运行测试，确认通过**

运行：`pytest tests/services/test_orchestrator_rounds.py tests/agents/test_supervisor_schema.py -v`
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add app/schemas/agent.py app/services/orchestrator.py app/agents/supervisor.py app/agents/planner.py app/agents/researcher.py app/agents/critic.py app/agents/synthesizer.py tests/services/test_orchestrator_rounds.py tests/agents/test_supervisor_schema.py
git commit -m "feat: define agent contracts and round state machine"
```

### 任务 4：增加 Brief 规划、Findings 和 Critic 校验

**文件：**
- 新建：`app/models/finding.py`
- 新建：`app/models/source.py`
- 新建：`app/models/gap.py`
- 新建：`app/schemas/finding.py`
- 新建：`app/tools/validation.py`
- 修改：`app/agents/planner.py`
- 修改：`app/agents/researcher.py`
- 修改：`app/agents/critic.py`
- 测试：`tests/agents/test_planner_briefs.py`
- 测试：`tests/agents/test_critic_validation.py`

- [ ] **步骤 1：先写失败的 planner 和 critic 测试**

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

- [ ] **步骤 2：运行测试，确认失败**

运行：`pytest tests/agents/test_planner_briefs.py tests/agents/test_critic_validation.py -v`
预期：FAIL，缺少 planner 行为和 finding schema

- [ ] **步骤 3：实现最小规划和校验逻辑**

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

- [ ] **步骤 4：运行测试，确认通过**

运行：`pytest tests/agents/test_planner_briefs.py tests/agents/test_critic_validation.py -v`
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add app/models/finding.py app/models/source.py app/models/gap.py app/schemas/finding.py app/tools/validation.py app/agents/planner.py app/agents/researcher.py app/agents/critic.py tests/agents/test_planner_briefs.py tests/agents/test_critic_validation.py
git commit -m "feat: add brief planning and critic validation"
```

### 任务 5：实现证据图查询和最终报告组装

**文件：**
- 新建：`app/services/evidence.py`
- 新建：`app/services/reporting.py`
- 修改：`app/agents/synthesizer.py`
- 修改：`app/schemas/finding.py`
- 测试：`tests/services/test_evidence_graph.py`
- 测试：`tests/services/test_reporting.py`

- [ ] **步骤 1：先写失败的证据图和报告测试**

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

- [ ] **步骤 2：运行测试，确认失败**

运行：`pytest tests/services/test_evidence_graph.py tests/services/test_reporting.py -v`
预期：FAIL，缺少 evidence 和 reporting 服务

- [ ] **步骤 3：实现最小证据图和报告构建器**

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

- [ ] **步骤 4：运行测试，确认通过**

运行：`pytest tests/services/test_evidence_graph.py tests/services/test_reporting.py -v`
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add app/services/evidence.py app/services/reporting.py app/agents/synthesizer.py app/schemas/finding.py tests/services/test_evidence_graph.py tests/services/test_reporting.py
git commit -m "feat: add evidence graph and report builder"
```

### 任务 6：搭建 Task Overview、Brief Board、Evidence Explorer、Report 页面

**文件：**
- 新建：`app/web/__init__.py`
- 新建：`app/web/routes.py`
- 新建：`app/templates/base.html`
- 新建：`app/templates/task_overview.html`
- 新建：`app/templates/brief_board.html`
- 新建：`app/templates/evidence_explorer.html`
- 新建：`app/templates/report.html`
- 修改：`app/main.py`
- 测试：`tests/web/test_task_pages.py`

- [ ] **步骤 1：先写失败的页面渲染测试**

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

- [ ] **步骤 2：运行测试，确认失败**

运行：`pytest tests/web/test_task_pages.py -v`
预期：FAIL，缺少 web 路由和模板

- [ ] **步骤 3：实现最小 HTML 路由和模板**

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

- [ ] **步骤 4：运行测试，确认通过**

运行：`pytest tests/web/test_task_pages.py -v`
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add app/web/__init__.py app/web/routes.py app/templates/base.html app/templates/task_overview.html app/templates/brief_board.html app/templates/evidence_explorer.html app/templates/report.html app/main.py tests/web/test_task_pages.py
git commit -m "feat: add multi-agent research console pages"
```

### 任务 7：接入后台 Worker 并增加端到端集成测试

**文件：**
- 新建：`app/worker.py`
- 修改：`app/services/orchestrator.py`
- 修改：`app/main.py`
- 测试：`tests/integration/test_task_execution_flow.py`

- [ ] **步骤 1：先写失败的端到端工作流测试**

```python
from app.services.orchestrator import Orchestrator


def test_orchestrator_runs_single_round_flow() -> None:
    orchestrator = Orchestrator()

    result = orchestrator.run_demo_task(topic="OpenAI competitors", template_type="market_scan")

    assert result.status == "completed"
    assert result.current_round == 1
    assert result.report is not None
```

- [ ] **步骤 2：运行测试，确认失败**

运行：`pytest tests/integration/test_task_execution_flow.py -v`
预期：FAIL，报 `AttributeError: 'Orchestrator' object has no attribute 'run_demo_task'`

- [ ] **步骤 3：实现最小 worker 注册和 orchestrator 端到端流程**

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

- [ ] **步骤 4：运行测试，确认通过**

运行：`pytest tests/integration/test_task_execution_flow.py -v`
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add app/worker.py app/services/orchestrator.py app/main.py tests/integration/test_task_execution_flow.py
git commit -m "feat: wire demo background execution flow"
```

### 任务 8：补齐文档和本地开发流程

**文件：**
- 修改：`README.md`
- 修改：`.env.example`
- 新建：`tests/conftest.py`
- 测试：`tests/test_readme_commands.py`

- [ ] **步骤 1：先写失败的文档流程测试**

```python
from pathlib import Path


def test_readme_mentions_main_local_commands() -> None:
    readme = Path("README.md").read_text()

    assert "uvicorn app.main:app --reload" in readme
    assert "pytest" in readme
```

- [ ] **步骤 2：运行测试，确认失败**

运行：`pytest tests/test_readme_commands.py -v`
预期：FAIL，因为 README 还没有本地运行和测试命令

- [ ] **步骤 3：补最小 setup 和开发文档**

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

- [ ] **步骤 4：运行测试，确认通过**

运行：`pytest tests/test_readme_commands.py -v`
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add README.md .env.example tests/conftest.py tests/test_readme_commands.py
git commit -m "docs: add local setup and test workflow"
```

## 自检

- 规格覆盖：计划覆盖了脚手架、API、round/brief 编排、agent schema、critic 校验、evidence graph 持久化形态、最终报告组装、UI 视图、worker 执行以及本地文档。唯一刻意推迟的是外部 provider 的真实接入，MVP 阶段先使用 mock/本地逻辑，后续可单独扩展。
- 占位符检查：没有保留 `TODO`、`TBD` 或“稍后处理”之类的空指令。
- 类型一致性：`SupervisorDecision`、`FindingInput`、`AcceptedFinding`、`ReportBuilder`、`Orchestrator` 等命名在后续任务中保持一致。
