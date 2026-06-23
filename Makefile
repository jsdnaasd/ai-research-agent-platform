.PHONY: install test run migrate docker-up docker-down worker

install:
	pip install -e ".[dev]"

test:
	pytest -v

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head

worker:
	celery -A app.worker.celery_app worker --loglevel=info

docker-up:
	docker compose up --build

docker-down:
	docker compose down
