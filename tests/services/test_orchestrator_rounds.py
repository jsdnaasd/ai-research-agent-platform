from app.services.orchestrator import Orchestrator, TaskRuntimeState


def test_orchestrator_advances_to_critic_review_after_research() -> None:
    state = TaskRuntimeState(
        task_id="task-1",
        status="running",
        current_round=1,
        round_stage="researching",
    )

    next_state = Orchestrator().advance_round(state)

    assert next_state.round_stage == "critic_review"
