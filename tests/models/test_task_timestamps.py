from app.models.task import ResearchTask


def test_task_sets_created_and_updated_timestamps() -> None:
    task = ResearchTask(topic="Timed task", template_type="market_scan")

    assert task.created_at is not None
    assert task.updated_at is not None
