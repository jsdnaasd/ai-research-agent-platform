# AI Research Agent Platform

A supervised multi-agent research backend for company intelligence, market scans, and evidence-backed reports.

中文简单说：这是一个可落地的 AI Agent 工程项目，不是聊天机器人套壳。它把一次 research job 拆成 planner、researcher、critic、report builder 几个阶段，用 Celery 跑后台任务，用 PostgreSQL 保存 brief、source、source fragment、finding 和 report。最后生成的结论可以回到原始来源片段，不只是给你一段看起来顺滑的总结。

[Project page / Demo](https://jsdnaasd.github.io/ai-research-agent-platform/) · [Repository](https://github.com/jsdnaasd/ai-research-agent-platform)

## What This Project Does

- Accepts research tasks from HTML pages or JSON APIs.
- Splits a topic into research briefs.
- Calls a real search provider through the Tavily provider interface.
- Stores sources and source fragments before writing the final report.
- Runs critic validation so weak findings do not silently enter the report.
- Persists task status, worker failures, briefs, findings, citation links, and final reports.
- Exposes the same artifacts through browser pages and API endpoints.

The important part is traceability. If a report says something, the app keeps the fragments used to support that claim.

## Architecture

```mermaid
flowchart LR
    User[User / curl / HTML form] --> FastAPI[FastAPI app]
    FastAPI --> Postgres[(PostgreSQL)]
    FastAPI --> Redis[(Redis broker)]
    Redis --> Celery[Celery worker]
    Celery --> Planner[Planner]
    Planner --> Researcher[Researcher]
    Researcher --> Tavily[Tavily search]
    Researcher --> Fragments[Sources + fragments]
    Fragments --> Critic[Critic]
    Critic --> Report[Report builder]
    Report --> Postgres
    Postgres --> API[HTML pages + JSON APIs]
```

## Why I Built It

Most AI research demos stop too early. They search the web, summarize a few snippets, and show a final paragraph. That looks fine in a demo, but it is hard to trust.

This repo keeps the boring pieces that matter in client work:

- What did the user ask for?
- Which briefs did the planner create?
- Which public sources did the researcher collect?
- Which exact source fragments support each accepted finding?
- Which findings did the critic reject or mark for expansion?
- If the worker crashed, where is the error recorded?

That makes the project useful as an AI Agent Engineer portfolio piece and as a starting point for real internal research tooling.

## Quick Start With Docker

Docker is the cleanest path because the app needs PostgreSQL, Redis, FastAPI, and Celery.

```bash
git clone https://github.com/jsdnaasd/ai-research-agent-platform.git
cd ai-research-agent-platform

cp .env.example .env
```

Edit `.env` and set `APP_TAVILY_API_KEY`.

```bash
docker compose up --build
```

Open these in the browser:

```text
http://localhost:8000
http://localhost:8000/health
http://localhost:8000/health/detailed
```

Watch the worker in another terminal:

```bash
docker compose logs -f worker
```

If you only want to restart the API:

```bash
docker compose restart api
```

Stop everything:

```bash
docker compose down
```

## Local Python Setup

Use this when you want to inspect the code, run tests quickly, or work without Docker for the API process.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Start the worker in a second terminal:

```bash
celery -A app.worker.celery_app worker --loglevel=info
```

Run tests:

```bash
pytest -v
```

## Make Commands

```bash
make install
make migrate
make run
make worker
make test
make docker-up
make docker-down
```

## Create A Research Task From Terminal

Create a task:

```bash
curl -s -X POST http://localhost:8000/api/tasks \
  -H "content-type: application/json" \
  -d '{
    "topic": "OpenAI competitors",
    "template_type": "market_scan",
    "user_context": "Focus on SMB pricing, positioning, and evidence quality."
  }' | jq
```

Typical response shape:

```json
{
  "id": "8a9f5c7e-8fd4-42db-93cf-9e20c8890a21",
  "topic": "OpenAI competitors",
  "template_type": "market_scan",
  "status": "queued",
  "created_at": "2026-06-25T10:21:14.120000Z",
  "updated_at": "2026-06-25T10:21:14.120000Z"
}
```

Save the id:

```bash
TASK_ID="8a9f5c7e-8fd4-42db-93cf-9e20c8890a21"
```

Check status:

```bash
curl -s "http://localhost:8000/api/tasks/$TASK_ID" | jq
```

List all tasks:

```bash
curl -s http://localhost:8000/api/tasks | jq
```

Read planner briefs:

```bash
curl -s "http://localhost:8000/api/tasks/$TASK_ID/briefs" | jq
```

Read evidence and citations:

```bash
curl -s "http://localhost:8000/api/tasks/$TASK_ID/evidence" | jq
```

Read the final report:

```bash
curl -s "http://localhost:8000/api/tasks/$TASK_ID/report" | jq -r .markdown_content
```

Open the same task in the browser:

```bash
open "http://localhost:8000/tasks/$TASK_ID"
open "http://localhost:8000/tasks/$TASK_ID/briefs"
open "http://localhost:8000/tasks/$TASK_ID/evidence"
open "http://localhost:8000/tasks/$TASK_ID/report"
```

## Inspect The Database

With Docker running:

```bash
docker compose exec db psql -U postgres -d research_agent
```

Useful queries:

```sql
select id, topic, status, created_at, updated_at
from research_tasks
order by created_at desc
limit 5;
```

```sql
select task_id, question, status
from research_briefs
order by created_at desc
limit 10;
```

```sql
select f.claim, s.title, sf.fragment_text
from research_findings f
join research_finding_source_fragments link on link.finding_id = f.id
join research_source_fragments sf on sf.id = link.source_fragment_id
join research_sources s on s.id = sf.source_id
limit 10;
```

## Main Routes

```text
GET  /
GET  /health
GET  /health/detailed
POST /api/tasks
GET  /api/tasks
GET  /api/tasks/{id}
GET  /api/tasks/{id}/briefs
GET  /api/tasks/{id}/evidence
GET  /api/tasks/{id}/report
GET  /tasks/{id}
GET  /tasks/{id}/briefs
GET  /tasks/{id}/evidence
GET  /tasks/{id}/report
```

## Data Model

The core tables are:

```text
research_tasks
research_rounds
research_briefs
research_sources
research_source_fragments
research_findings
research_finding_source_fragments
research_reports
```

`research_finding_source_fragments` is the table that matters most. It connects accepted findings to the exact fragments used as evidence.

## Environment Variables

```bash
APP_APP_NAME="AI Research Agent Platform"
APP_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/research_agent"
APP_REDIS_URL="redis://localhost:6379/0"
APP_TAVILY_API_KEY="your-tavily-api-key"
```

`.env.example` contains a Docker-oriented template.

## Troubleshooting

Check whether the API can reach the database:

```bash
curl -s http://localhost:8000/health/detailed | jq
```

Check worker logs:

```bash
docker compose logs -f worker
```

Run migrations again:

```bash
docker compose exec api alembic upgrade head
```

Rebuild from scratch:

```bash
docker compose down -v
docker compose up --build
```

Run one focused test file:

```bash
pytest tests/integration/test_persisted_task_flow.py -v
```

## Current Limits

- The critic is rule-based. It is written so model-assisted review can be added later.
- The browser UI is server-rendered. That keeps the repo easier to read.
- Tavily is the only real search provider wired in today.
- Auth is not included. A client deployment should add auth before exposing it publicly.

## Why This Is Worth Reading

The repo shows the practical side of AI agent engineering: background jobs, state transitions, persistence, evidence handling, API design, and failure visibility. The code is intentionally plain enough that another engineer can clone it, run it, and modify one layer without unpacking a giant framework first.
