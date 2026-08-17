"""Observation events — normalized world inputs, never system commands."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ObservationSource(str, Enum):
    USER_MESSAGE = "user_message"
    USER_ACTION = "user_action"
    WORLD_EVENT = "world_event"
    CLOCK_TICK = "clock_tick"
    INTERNAL = "internal"


class Observation(BaseModel):
    """Normalized observation with provenance — L3 output contract."""

    id: str
    timestamp: datetime
    source: ObservationSource
    topic: str
    payload: dict[str, Any] = Field(default_factory=dict)
    trust: float = Field(default=1.0, ge=0.0, le=1.0)
    is_user_trigger: bool = False
    trace_id: str = ""
