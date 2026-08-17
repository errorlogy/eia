"""Belief state — typed claims with uncertainty intervals."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class BeliefKind(str, Enum):
    CATEGORICAL = "categorical"
    NUMERIC = "numeric"
    COMMITMENT = "commitment"
    CONTRADICTION = "contradiction_marker"


class Belief(BaseModel):
    """A typed belief node in the BeliefField graph."""

    id: str
    kind: BeliefKind
    subject: str
    claim: str
    distribution: dict[str, float] = Field(default_factory=dict)
    uncertainty: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence_interval: tuple[float, float] | None = None
    source_observation_id: str | None = None
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class BeliefUpdate(BaseModel):
    """Record of a belief mutation — causal parent for motives."""

    id: str
    timestamp: datetime
    belief_id: str
    delta_entropy: float = 0.0
    delta_coherence: float = 0.0
    reason: str
    parent_observation_id: str | None = None
