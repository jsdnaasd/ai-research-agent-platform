from app.worker import run_research_task


def test_worker_task_is_registered() -> None:
    assert run_research_task.name == "run_research_task"
