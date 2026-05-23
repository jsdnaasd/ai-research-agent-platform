from app.models.task import ResearchTask, TaskStatus


def test_task_defaults_to_queued_status() -> None:
    task = ResearchTask(topic="OpenAI competitors", template_type="market_scan")

    assert task.status is TaskStatus.QUEUED
    assert task.current_round == 0
