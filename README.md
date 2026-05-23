# AI Research Agent Platform

Supervised multi-agent research platform for evidence-grounded company intelligence.

## What It Demonstrates

- Supervisor-driven round orchestration
- Planner-generated research briefs
- Researcher findings with source-fragment citations
- Critic validation before final synthesis
- Evidence explorer and final report pages

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

## Run tests

```bash
pytest
```

## Key routes

- `/health`
- `/api/tasks`
- `/tasks/demo-task`
- `/tasks/demo-task/briefs`
- `/tasks/demo-task/evidence`
- `/tasks/demo-task/report`

## Required environment

- `APP_DATABASE_URL`
- `APP_REDIS_URL`
- `APP_TAVILY_API_KEY`
