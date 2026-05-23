from dataclasses import dataclass

from app.agents.planner import PlannedBrief
from app.schemas.finding import FindingInput, SourceFragmentPayload
from app.tools.search import SearchResult


@dataclass(slots=True)
class ResearcherResult:
    finding: FindingInput
    sources: list[SearchResult]
    fragments: list[SourceFragmentPayload]


class ResearcherAgent:
    def __init__(self, search_provider: object) -> None:
        self.search_provider = search_provider

    def research(self, brief: PlannedBrief) -> ResearcherResult:
        query = brief.search_queries[0]
        sources = self.search_provider.search(query, max_results=2)
        fragments = [
            SourceFragmentPayload(
                citation_label=f"{brief.brief_id}-fragment-{index + 1}",
                content=result.content,
                offset_start=0,
                offset_end=len(result.content),
            )
            for index, result in enumerate(sources[:2])
        ]
        finding = FindingInput(
            brief_id=brief.brief_id,
            claim=f"{brief.question} validated from search evidence",
            source_fragments=[fragment.citation_label for fragment in fragments],
            confidence=0.82,
        )
        return ResearcherResult(finding=finding, sources=sources, fragments=fragments)
