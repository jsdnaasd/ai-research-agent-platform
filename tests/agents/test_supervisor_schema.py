from app.schemas.agent import SupervisorDecision


def test_supervisor_decision_limits_allowed_actions() -> None:
    decision = SupervisorDecision(
        round_goal="Find competitor pricing signals",
        selected_briefs=["brief-1"],
        decision="continue",
        decision_reason="Need more evidence",
        next_action="plan_followups",
    )

    assert decision.decision == "continue"
