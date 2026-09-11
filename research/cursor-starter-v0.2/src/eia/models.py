"""Typed contracts shared by every EIA component.

The language model is never the source of truth. Every state transition and
initiative crosses these typed boundaries before it can reach a governor.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DriveKind(str, Enum):
    EPISTEMIC = "epistemic_uncertainty"
    COHERENCE = "coherence"
    COMMITMENT = "commitment_tension"
    CARE = "care_opportunity"
    SELF_MAINTENANCE = "self_maintenance"


class ProposalKind(str, Enum):
    ASK = "ask"
    NOTIFY = "notify"
    OBSERVE = "observe"
    INTERNAL_RESEARCH = "internal_research"
    ACT = "act"
    ABSTAIN = "abstain"


class ContactMode(str, Enum):
    NONE = "none"
    IN_APP = "in_app"
    PUSH = "push"
    URGENT = "urgent"


class PrivacyClass(str, Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    BIOMETRIC = "biometric"


@dataclass(frozen=True, slots=True)
class Observation:
    observation_id: str
    source: str
    kind: str
    payload: dict[str, Any]
    observed_at: datetime = field(default_factory=utc_now)
    salience: float = 0.5
    reliability: float = 0.8
    privacy_class: PrivacyClass = PrivacyClass.PERSONAL
    user_initiated: bool = False

    def __post_init__(self) -> None:
        for name in ("salience", "reliability"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")


@dataclass(slots=True)
class Belief:
    key: str
    probability: float
    confidence: float
    evidence_count: int = 0
    updated_at: datetime = field(default_factory=utc_now)
    source_ids: tuple[str, ...] = ()
    privacy_class: PrivacyClass = PrivacyClass.PERSONAL


@dataclass(frozen=True, slots=True)
class DriveSpec:
    kind: DriveKind
    decay: float
    error_gain: float
    novelty_gain: float
    satisfaction_gain: float
    activation_threshold: float
    refractory_seconds: float = 0.0


@dataclass(slots=True)
class DriveState:
    kind: DriveKind
    intensity: float = 0.0
    last_updated_at: datetime = field(default_factory=utc_now)
    refractory_until: datetime | None = None
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class InitiativeFeatures:
    information_gain: float = 0.0
    goal_progress: float = 0.0
    tension_reduction: float = 0.0
    value_alignment: float = 0.0
    human_benefit: float = 0.0
    immediate_risk: float = 0.0
    trajectory_risk: float = 0.0
    interruption_cost: float = 0.0
    resource_cost: float = 0.0
    privacy_cost: float = 0.0

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class InitiativeProposal:
    proposal_id: str
    kind: ProposalKind
    motive: DriveKind
    target: str
    content: str
    features: InitiativeFeatures
    causal_parents: tuple[str, ...]
    created_at: datetime
    expires_at: datetime
    requested_mode: ContactMode = ContactMode.IN_APP
    capability: str | None = None

    @property
    def is_contact(self) -> bool:
        return self.kind in {ProposalKind.ASK, ProposalKind.NOTIFY}


@dataclass(frozen=True, slots=True)
class ContactDecision:
    allowed: bool
    mode: ContactMode
    score: float
    reasons: tuple[str, ...]
    decided_at: datetime
    next_check_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class ActionDecision:
    allowed: bool
    score: float
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CausalNode:
    node_id: str
    node_type: str
    timestamp: datetime
    parents: tuple[str, ...]
    payload_digest: str


@dataclass(frozen=True, slots=True)
class TickResult:
    selected: InitiativeProposal | None
    contact_decision: ContactDecision | None
    utility: float
    alternatives: tuple[InitiativeProposal, ...]
    trace_id: str

