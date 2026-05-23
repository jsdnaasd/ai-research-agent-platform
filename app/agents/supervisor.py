from app.schemas.agent import SupervisorDecision


class SupervisorAgent:
    def decide(self, round_goal: str, selected_briefs: list[str]) -> SupervisorDecision:
        return SupervisorDecision(
            round_goal=round_goal,
            selected_briefs=selected_briefs,
            decision="continue",
            decision_reason="Initial research round should continue",
            next_action="research_briefs",
        )
