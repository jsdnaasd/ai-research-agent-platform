from app.agents.critic import CriticAgent
from app.schemas.finding import FindingInput


def test_critic_requests_expand_when_only_one_source_supports_claim() -> None:
    critic = CriticAgent()
    finding = FindingInput(
        brief_id="brief-1",
        claim="Competitor X targets SMBs",
        source_fragments=["fragment-1"],
        confidence=0.74,
    )

    verdict = critic.review([finding])

    assert verdict.verdict == "expand"
    assert verdict.gaps
