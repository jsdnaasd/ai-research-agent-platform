from app.agents.planner import PlannerAgent


def test_planner_creates_prioritized_briefs() -> None:
    planner = PlannerAgent()

    briefs = planner.plan(
        topic="OpenAI competitors",
        template_type="market_scan",
        round_goal="Map top SMB rivals",
    )

    assert len(briefs) == 3
    assert briefs[0].priority == 1
    assert briefs[0].search_queries
