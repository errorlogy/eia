"""Contact Governor decisions — independent of cognitive proposer."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ContactOutcome(str, Enum):
    SEND_NOW = "send_now"
    DEFER = "defer_until_context"
    INTERNAL_RESEARCH = "internal_research"
    DENY = "deny"
    ABSTAIN = "abstain"


class ContactDecision(BaseModel):
    """Governor verdict — structurally separate from initiative genesis."""

    id: str
    timestamp: datetime
    initiative_id: str
    outcome: ContactOutcome
    contact_score: float
    fatigue_penalty: float = 0.0
    budget_remaining: int = 0
    cooldown_active: bool = False
    reason: str = ""
    features: dict[str, float] = Field(default_factory=dict)
