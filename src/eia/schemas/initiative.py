"""Initiative candidates — competing intentions with mandatory abstain."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from eia.schemas.motivation import DriveKind


class InitiativeKind(str, Enum):
    ASK_QUESTION = "ask_question"
    INTERNAL_RESEARCH = "internal_research"
    OBSERVE = "observe"
    ABSTAIN = "abstain"


class InitiativeCandidate(BaseModel):
    """Competing intention before selection."""

    id: str
    kind: InitiativeKind
    target_belief_id: str | None = None
    question_text: str | None = None
    expected_info_gain: float = 0.0
    coherence_relief: float = 0.0
    commitment_progress: float = 0.0
    interrupt_cost: float = 0.0
    risk: float = 0.0
    lex_score: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    source_drives: list[DriveKind] = Field(default_factory=list)


class Initiative(BaseModel):
    """Selected intention (or explicit abstain)."""

    id: str
    timestamp: datetime
    candidate: InitiativeCandidate
    abstained: bool = False
    parent_motivation_id: str
    competing_candidate_ids: list[str] = Field(default_factory=list)
    evsi: float = 0.0
