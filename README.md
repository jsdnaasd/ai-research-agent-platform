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

## Docker setup

```bash
docker compose up --build
```

This starts:

- `web` on `http://localhost:8000`
- `worker` for background research execution
- `db` on PostgreSQL 16
- `redis` on Redis 7

## Run tests

```bash
pytest
```

## Common commands

```bash
make install
make migrate
make run
make worker
make test
make docker-up
```

## Key routes

- `/health`
- `/health/detailed`
- `/api/tasks`
- `/api/tasks/{id}`
- `/api/tasks/{id}/briefs`
- `/api/tasks/{id}/evidence`
- `/api/tasks/{id}/report`
- `/`
- `/tasks/{id}`
- `/tasks/{id}/briefs`
- `/tasks/{id}/evidence`
- `/tasks/{id}/report`

## Required environment

- `APP_DATABASE_URL`
- `APP_REDIS_URL`
- `APP_TAVILY_API_KEY`
