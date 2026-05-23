from app.services.orchestrator import Orchestrator


def test_orchestrator_runs_single_round_flow() -> None:
    orchestrator = Orchestrator()

    result = orchestrator.run_demo_task(topic="OpenAI competitors", template_type="market_scan")

    assert result.status == "completed"
    assert result.current_round == 1
    assert result.report is not None
