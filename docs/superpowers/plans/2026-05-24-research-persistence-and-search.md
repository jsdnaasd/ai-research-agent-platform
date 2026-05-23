# Research Persistence and Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the in-memory demo flow with a database-backed research pipeline that persists tasks, rounds, briefs, findings, source fragments, and triggers a real search-backed worker automatically after task creation.

**Architecture:** The app will persist task state in PostgreSQL through SQLAlchemy and manage schema evolution with Alembic. Task creation will enqueue a Celery worker job that loads a real search provider, executes the round/brief pipeline, stores sources and fragments, validates findings, and writes the final report back to the database.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Celery, Redis, PostgreSQL, httpx, pytest

---

## File Structure

- `app/config.py`: add Postgres, Alembic, search provider, and auto-create flags
- `app/db.py`: engine, sessionmaker, session dependency, init helpers
- `app/models/`: extend task graph with source fragments and persistence timestamps
- `app/tools/search.py`: real Tavily-backed search provider and search result schema
- `app/services/tasks.py`: create task, fetch task, queue worker
- `app/services/orchestrator.py`: run persisted workflow against database rows
- `app/worker.py`: register Celery task for persisted execution
- `app/main.py`: switch API to database-backed task creation and retrieval
- `alembic.ini`, `alembic/`, `alembic/versions/`: migration scaffolding and initial schema
- `tests/`: persistence, search mocking, and worker execution coverage

### Task 1: Database Runtime and Alembic Scaffold

**Files:**
- Modify: `pyproject.toml`
- Modify: `app/config.py`
- Modify: `app/db.py`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/script.py.mako`
- Create: `alembic/versions/20260524_0001_initial_schema.py`
- Test: `tests/db/test_session_factory.py`

- [ ] **Step 1: Write the failing database runtime test**

```python
from sqlalchemy import text

from app.db import SessionLocal


def test_session_factory_executes_simple_query() -> None:
    with SessionLocal() as session:
        value = session.execute(text("select 1")).scalar_one()

    assert value == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/db/test_session_factory.py -v`
Expected: FAIL because `SessionLocal` does not exist

- [ ] **Step 3: Implement engine, session factory, and Alembic config**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/db/test_session_factory.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml app/config.py app/db.py alembic.ini alembic tests/db/test_session_factory.py
git commit -m "feat: add database runtime and alembic scaffold"
```

### Task 2: Persist Tasks, Briefs, Findings, Sources, and Source Fragments

**Files:**
- Modify: `app/models/task.py`
- Modify: `app/models/round.py`
- Modify: `app/models/brief.py`
- Modify: `app/models/finding.py`
- Modify: `app/models/source.py`
- Create: `app/models/source_fragment.py`
- Modify: `app/models/report.py`
- Modify: `app/models/__init__.py`
- Test: `tests/models/test_persisted_research_graph.py`

- [ ] **Step 1: Write the failing persistence graph test**

```python
from app.models.source_fragment import ResearchSourceFragment


def test_source_fragment_keeps_text_and_offsets() -> None:
    fragment = ResearchSourceFragment(
        source_id="source-1",
        content="Pricing starts at $29",
        citation_label="fragment-1",
        offset_start=0,
        offset_end=21,
    )

    assert fragment.citation_label == "fragment-1"
    assert fragment.offset_end == 21
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/models/test_persisted_research_graph.py -v`
Expected: FAIL because `ResearchSourceFragment` does not exist

- [ ] **Step 3: Add persisted graph models**

```python
class ResearchSourceFragment(Base):
    __tablename__ = "research_source_fragments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[str] = mapped_column(ForeignKey("research_sources.id"))
    content: Mapped[str] = mapped_column(Text())
    citation_label: Mapped[str] = mapped_column(String(64))
    offset_start: Mapped[int] = mapped_column(Integer, default=0)
    offset_end: Mapped[int] = mapped_column(Integer, default=0)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/models/test_persisted_research_graph.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/models tests/models/test_persisted_research_graph.py
git commit -m "feat: persist research graph models"
```

### Task 3: Real Search Provider and Persisted Orchestrator

**Files:**
- Create: `app/tools/search.py`
- Modify: `app/agents/researcher.py`
- Modify: `app/services/orchestrator.py`
- Create: `app/services/tasks.py`
- Test: `tests/tools/test_tavily_search_provider.py`
- Test: `tests/integration/test_persisted_task_flow.py`

- [ ] **Step 1: Write the failing search provider and persisted flow tests**

```python
from app.tools.search import SearchResult


def test_search_result_keeps_url_title_and_content() -> None:
    result = SearchResult(url="https://example.com", title="Example", content="Body")

    assert result.url == "https://example.com"
```
```

```python
from fastapi.testclient import TestClient

from app.main import app


def test_post_task_persists_report_and_findings(monkeypatch) -> None:
    client = TestClient(app)

    response = client.post("/api/tasks", json={"topic": "OpenAI competitors", "template_type": "market_scan"})

    assert response.status_code == 201
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/tools/test_tavily_search_provider.py tests/integration/test_persisted_task_flow.py -v`
Expected: FAIL because search provider and persisted flow are missing

- [ ] **Step 3: Implement real search provider and persisted orchestrator**

```python
class TavilySearchProvider:
    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        ...
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tools/test_tavily_search_provider.py tests/integration/test_persisted_task_flow.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/tools/search.py app/agents/researcher.py app/services/orchestrator.py app/services/tasks.py tests/tools/test_tavily_search_provider.py tests/integration/test_persisted_task_flow.py
git commit -m "feat: add real search provider and persisted task flow"
```

### Task 4: Worker Auto-Execution on Task Creation

**Files:**
- Modify: `app/worker.py`
- Modify: `app/main.py`
- Modify: `app/schemas/task.py`
- Test: `tests/api/test_create_task.py`
- Test: `tests/worker/test_task_enqueue.py`

- [ ] **Step 1: Write the failing enqueue test**

```python
from app.worker import run_research_task


def test_worker_task_is_registered() -> None:
    assert run_research_task.name == "run_research_task"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/worker/test_task_enqueue.py tests/api/test_create_task.py -v`
Expected: FAIL because Celery task registration and enqueue hook are missing

- [ ] **Step 3: Register worker task and queue it from task creation**

```python
@celery_app.task(name="run_research_task")
def run_research_task(task_id: str) -> None:
    Orchestrator().run_task(task_id)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/worker/test_task_enqueue.py tests/api/test_create_task.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/worker.py app/main.py app/schemas/task.py tests/worker/test_task_enqueue.py tests/api/test_create_task.py
git commit -m "feat: auto trigger research worker on task creation"
```

## Self-Review

- Spec coverage: this plan covers the requested real search provider, PostgreSQL/Alembic support, persisted brief/finding/source-fragment graph, and automatic worker execution on task creation.
- Placeholder scan: there are no TODO markers or deferred “later” steps in the tasks.
- Type consistency: `SessionLocal`, `ResearchSourceFragment`, `SearchResult`, `TavilySearchProvider`, and `run_research_task` are named consistently across tasks.
