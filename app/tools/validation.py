from app.schemas.finding import FindingInput


def needs_more_sources(findings: list[FindingInput]) -> bool:
    return any(len(item.source_fragments) < 2 for item in findings)
