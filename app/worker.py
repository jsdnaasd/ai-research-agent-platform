from celery import Celery

from app.config import settings

celery_app = Celery("ai_research_agent", broker=settings.redis_url)
celery_app.conf.task_always_eager = True
