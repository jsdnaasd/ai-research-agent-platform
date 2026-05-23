from typing import Literal

from pydantic import BaseModel


class FindingInput(BaseModel):
    brief_id: str
    claim: str
    source_fragments: list[str]
    confidence: float


class CriticVerdict(BaseModel):
    verdict: Literal["accept", "revise", "expand"]
    accepted_findings: list[str]
    rejected_findings: list[str]
    gaps: list[str]
    requested_followups: list[str]
    quality_score: float


class AcceptedFinding(BaseModel):
    brief_id: str
    claim: str
    citations: list[str]


class SourceFragmentPayload(BaseModel):
    citation_label: str
    content: str
    offset_start: int = 0
    offset_end: int = 0
