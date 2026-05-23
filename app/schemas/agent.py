from typing import Literal

from pydantic import BaseModel


class SupervisorDecision(BaseModel):
    round_goal: str
    selected_briefs: list[str]
    decision: Literal["continue", "finish", "revise"]
    decision_reason: str
    next_action: str
