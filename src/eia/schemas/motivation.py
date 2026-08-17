"""Motivation signals — drive engine output, not LLM mood."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DriveKind(str, Enum):
    EPISTEMIC = "epistemic"
    COHERENCE = "coherence"
    COMMITMENT = "commitment"


class MotivationSignal(BaseModel):
    """Single drive channel reading at time t."""

    drive: DriveKind
    intensity: float = Field(ge=0.0, le=1.0)
    error_term: float = 0.0
    saturation: float = 0.0
    decay_rate: float = 0.0
    target_belief_ids: list[str] = Field(default_factory=list)
    explanation: str = ""


class Motivation(BaseModel):
    """Aggregate motive snapshot — causal input to intention genesis."""

    id: str
    timestamp: datetime
    signals: list[MotivationSignal]
    composite_lex_score: tuple[float, float, float] = (0.0, 0.0, 0.0)
    dominant_drive: DriveKind | None = None
    parent_belief_update_ids: list[str] = Field(default_factory=list)
