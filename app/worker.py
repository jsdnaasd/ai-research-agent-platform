from app.celery_compat import Celery
from app.config import settings
from app.services.orchestrator import Orchestrator

celery_app = Celery("ai_research_agent", broker=settings.redis_url)
celery_app.conf.task_always_eager = True


@celery_app.task(name="run_research_task")
def run_research_task(task_id: str) -> None:
    Orchestrator().run_task(task_id)
