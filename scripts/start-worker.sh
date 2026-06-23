#!/usr/bin/env bash
set -euo pipefail

alembic upgrade head
exec celery -A app.worker.celery_app worker --loglevel=info
