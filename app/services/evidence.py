from __future__ import annotations

from collections import defaultdict


class EvidenceGraph:
    def __init__(self) -> None:
        self._brief_findings: dict[str, list[str]] = defaultdict(list)
        self._finding_sources: dict[str, list[str]] = {}

    def add_finding(self, brief_id: str, claim: str, fragments: list[str]) -> None:
        self._brief_findings[brief_id].append(claim)
        self._finding_sources[claim] = fragments

    def findings_for_brief(self, brief_id: str) -> list[str]:
        return self._brief_findings[brief_id]

    def sources_for_claim(self, claim: str) -> list[str]:
        return self._finding_sources.get(claim, [])
