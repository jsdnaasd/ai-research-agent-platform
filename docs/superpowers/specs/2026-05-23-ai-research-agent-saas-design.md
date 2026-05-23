# AI Research Agent SaaS Design

## Overview

`ai-research-agent-saas` is a single-tenant, demo-ready SaaS application for automated company and market research. A user submits a topic, company name, or market segment, selects a report template, and receives a structured report with citations, execution logs, and cost visibility.

The first release is intentionally scoped as an MVP for sales and portfolio use on Upwork. It should look like a polished product, but the implementation should stay narrow enough to build quickly and explain clearly in a GitHub repository.

## Goals

- Deliver a working web application that demonstrates AI agent orchestration beyond a simple chat UI.
- Produce structured research reports from public web sources with visible citations.
- Expose task execution steps, partial failures, and token or cost usage so the system feels trustworthy.
- Provide a codebase that can be extended later into multi-user SaaS or a vertical business intelligence tool.

## Non-Goals

- Multi-tenant account management
- Billing and subscription flows
- Team collaboration
- Deep CRM integrations
- Full browser automation for login-protected sources
- Complex multi-agent conversation between autonomous personas

## Target Users

### Primary

- Small and medium businesses that need faster company, competitor, or market research
- AI startup teams evaluating agent-based workflow products

### Secondary

- Upwork clients looking for custom research automation, AI workflow systems, or internal knowledge tools

## User Value

The product should answer a plain business question: "Can this system reduce hours of manual research into a repeatable workflow?" The MVP proves this by turning a research request into a report with traceable sources and clear execution history.

## MVP Scope

The MVP supports one asynchronous research workflow from form submission to final report delivery.

Included:

- Submit a research request through a web UI
- Choose one of three report templates:
  - `company_brief`
  - `competitor_snapshot`
  - `market_scan`
- Track task status from queued to completed or failed
- View execution steps and source citations
- View a final rendered report
- Record token and estimated cost metadata
- Retry failed steps at the workflow level

Excluded from MVP:

- Authentication
- Role-based access control
- Background notifications by email or Slack
- Collaborative editing
- File uploads
- Private data connectors

## Product Experience

### Submit Task

The user enters:

- research topic or company name
- optional context or business goal
- selected report template

The system creates a task immediately and redirects to a task detail page.

### Track Progress

The task detail page shows:

- current task status
- current workflow stage
- chronological execution log
- source count
- token and cost summary

### Review Report

When complete, the task detail page shows:

- rendered report
- cited sources with URLs
- report generation timestamp
- execution metadata

## System Architecture

The application is composed of six focused modules.

### 1. Web

Responsibilities:

- render pages for task creation, task detail, and report viewing
- provide a lightweight SaaS-like interface suitable for demos

Suggested implementation:

- `FastAPI` server-side rendered pages with `Jinja2`
- `HTMX` for lightweight polling and partial page updates

### 2. API

Responsibilities:

- create research tasks
- fetch task status
- fetch task report data

Suggested endpoints:

- `POST /api/tasks`
- `GET /api/tasks/{task_id}`
- `GET /api/tasks/{task_id}/report`

### 3. Orchestrator

Responsibilities:

- manage task lifecycle
- run the workflow stages in order
- handle retries and partial failures
- persist step results

Workflow stages:

1. `planner`
2. `search`
3. `extract`
4. `synthesize`
5. `report`

The orchestrator should behave like a deterministic workflow engine, not an open-ended agent loop. This keeps the MVP reliable and easier to test.

### 4. Tools

Responsibilities:

- search the public web
- fetch page content
- clean extracted text
- format report output

Initial tools:

- search provider adapter
- HTTP or browser-backed page fetcher
- content cleaner
- citation collector
- report formatter

### 5. Storage

Responsibilities:

- persist tasks, steps, sources, and reports
- support replay and debugging

Primary storage:

- `Postgres`

### 6. Worker

Responsibilities:

- execute long-running research jobs asynchronously
- isolate task processing from HTTP request latency

Suggested implementation:

- `Redis` as broker
- `Celery` or `Dramatiq` as job runner

## Data Model

The initial schema should include four core tables.

### `research_tasks`

Fields:

- `id`
- `topic`
- `user_context`
- `template_type`
- `status`
- `current_stage`
- `error_message`
- `token_usage_total`
- `estimated_cost_total`
- `created_at`
- `updated_at`

### `research_steps`

Fields:

- `id`
- `task_id`
- `stage_name`
- `status`
- `attempt_number`
- `input_payload`
- `output_payload`
- `error_message`
- `started_at`
- `finished_at`

### `research_sources`

Fields:

- `id`
- `task_id`
- `step_id`
- `source_url`
- `source_title`
- `source_type`
- `content_excerpt`
- `fetch_status`
- `created_at`

### `research_reports`

Fields:

- `id`
- `task_id`
- `template_type`
- `markdown_content`
- `html_content`
- `summary_json`
- `created_at`

## Workflow Design

### Planner

Input:

- topic
- optional user context
- selected template

Output:

- search sub-questions
- suggested source angles
- structured plan for downstream stages

The planner should produce a structured schema, not freeform text.

### Search

Input:

- planner output

Output:

- ranked candidate URLs
- titles and snippets

The search stage should gather more sources than the final report needs so later stages can discard weak material.

### Extract

Input:

- selected candidate URLs

Output:

- cleaned source content
- extraction metadata
- per-source success or failure status

Extraction failures should not fail the entire task unless the usable source count drops below a minimum threshold.

### Synthesize

Input:

- extracted source content
- report template

Output:

- structured findings
- citation mapping
- missing-information flags

This stage should explicitly separate evidence-backed statements from low-confidence inferences.

### Report

Input:

- structured findings
- citations

Output:

- final Markdown report
- final HTML rendering

## Report Templates

The MVP supports three report templates.

### `company_brief`

Sections:

- company overview
- products or services
- business signals
- risks or open questions
- source list

### `competitor_snapshot`

Sections:

- target company summary
- key competitors
- differentiators
- market positioning notes
- source list

### `market_scan`

Sections:

- market overview
- notable players
- trends and signals
- risks and unknowns
- source list

## Error Handling

The system must surface partial failure without becoming opaque.

Rules:

- search provider failure should produce a retry before hard failure
- page fetch failure should be recorded at the source level
- invalid model output should be schema-validated and retried once
- final task status should be:
  - `completed`
  - `failed`
  - `completed_with_warnings`

The user interface should expose warnings clearly so incomplete jobs still feel transparent.

## Observability

This project needs visible execution details because the portfolio goal is to prove engineering depth.

The MVP should record:

- per-step status
- timestamps
- retry counts
- source success or failure
- token usage
- estimated cost

Optional later extensions:

- OpenTelemetry traces
- Prometheus metrics
- structured external log sinks

## Security and Safety

The MVP should include baseline safeguards even without user accounts.

- validate and sanitize input fields
- restrict outbound fetch behavior to supported protocols
- set timeouts on network calls
- enforce structured output validation for model responses
- avoid storing secrets in code or logs

## Testing Strategy

The initial test suite should cover:

- task creation and lifecycle transitions
- orchestrator stage progression
- retry behavior on tool failure
- schema validation for planner and synthesizer outputs
- report generation for each template
- API responses for task status and report retrieval

Testing layers:

- unit tests for stage logic and adapters
- integration tests for workflow execution with mocked external providers

## Repository Positioning

This repository should be packaged as a client-ready product sample.

The README should emphasize:

- business problem
- product screenshots
- architecture diagram
- local setup
- demo workflow
- technical highlights
- extension ideas for client-specific customization

## Success Criteria

The MVP is successful when:

- a user can submit a task from the browser and receive a report end-to-end
- the report includes citations and a readable business-oriented structure
- task details show step-level logs and usage metadata
- failures are visible and non-catastrophic where possible
- the repository reads like a deployable product, not an experiment notebook

## Initial Delivery Plan

The first implementation cycle should prioritize:

1. project scaffolding and local environment
2. data model and persistence
3. asynchronous task execution
4. workflow stage interfaces
5. minimal search and fetch tool adapters
6. report rendering UI
7. baseline tests

This order supports an early end-to-end demo before deeper polish.
