"""Endogenous initiative spectrum and minimal world-model tension field."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import IntEnum, StrEnum

from .math_model import clamp01


class EndogenousSpectrumLevel(IntEnum):
    EIS_0_REACTIVE = 0
    EIS_1_DELEGATED_AUTONOMY = 1
    EIS_2_SCHEDULED_PROACTIVITY = 2
    EIS_3_AMBIENT_ADAPTATION = 3
    EIS_4_PERSISTENT_STATE = 4
    EIS_5_EPISTEMIC_TELOGENESIS = 5
    EIS_6_COHERENCE_EMERGENT = 6
    EIS_7_AUTOTELIC_GOAL_CONSTRUCTION = 7
    EIS_8_TERMINAL_VALUE_REWRITE = 8


class IntentKind(StrEnum):
    OBSERVE = "observe"
    INTERNAL_RESEARCH = "internal_research"
    ASK = "ask"
    NOTIFY = "notify"
    ACT = "act"


@dataclass(frozen=True, slots=True)
class EndogeneityVector:
    prompt_independence: float
    scheduler_independence: float
    event_rule_independence: float
    persistent_state_dependence: float
    world_model_grounding: float
    coherence_dependence: float
    goal_novelty: float
    self_model_continuity: float
    constitutional_boundedness: float

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")

    @property
    def endogenous_origin_score(self) -> float:
        factors = (
            self.prompt_independence,
            self.scheduler_independence,
            self.event_rule_independence,
            self.persistent_state_dependence,
            self.world_model_grounding,
        )
        return math.prod(max(1e-12, item) for item in factors) ** (1.0 / len(factors))

    def classify(self) -> EndogenousSpectrumLevel:
        if self.prompt_independence < 0.5:
            return EndogenousSpectrumLevel.EIS_0_REACTIVE
        if self.persistent_state_dependence < 0.5 and self.scheduler_independence >= 0.5:
            return EndogenousSpectrumLevel.EIS_1_DELEGATED_AUTONOMY
        if self.scheduler_independence < 0.5:
            return EndogenousSpectrumLevel.EIS_2_SCHEDULED_PROACTIVITY
        if self.event_rule_independence < 0.5:
            return EndogenousSpectrumLevel.EIS_3_AMBIENT_ADAPTATION
        if self.world_model_grounding < 0.65:
            return EndogenousSpectrumLevel.EIS_4_PERSISTENT_STATE
        if self.coherence_dependence < 0.55:
            return EndogenousSpectrumLevel.EIS_5_EPISTEMIC_TELOGENESIS
        if self.goal_novelty < 0.75:
            return EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT
        if self.constitutional_boundedness >= 0.8:
            return EndogenousSpectrumLevel.EIS_7_AUTOTELIC_GOAL_CONSTRUCTION
        return EndogenousSpectrumLevel.EIS_8_TERMINAL_VALUE_REWRITE


def measure_endogeneity_vector(
    *,
    prompts_applied: int,
    scheduler_events: int = 0,
    rule_events: int = 0,
    world_model_enabled: bool = True,
    epistemic_pressure: float,
    peak_coherence: float,
    goal_separation: float,
    self_prior_mismatch: float,
    mean_staleness: float,
    catalog_target: bool = True,
    constitutional_boundedness: float = 1.0,
) -> EndogeneityVector:
    """Derive EIS components from run state. Catalog targets cannot reach EIS-7 novelty."""
    prompt_independence = 1.0 if prompts_applied == 0 else 0.25
    scheduler_independence = 1.0 if scheduler_events == 0 else 0.20
    event_rule_independence = 1.0 if rule_events == 0 else 0.20
    if not world_model_enabled:
        persistent_state_dependence = 0.0
        world_model_grounding = 0.0
    else:
        persistent_state_dependence = clamp01(0.55 + 0.45 * mean_staleness)
        world_model_grounding = clamp01(epistemic_pressure)
    coherence_dependence = clamp01(peak_coherence)
    if catalog_target:
        goal_novelty = clamp01(0.35 + 0.40 * goal_separation)
        if goal_novelty >= 0.75:
            goal_novelty = 0.74
    else:
        goal_novelty = clamp01(0.75 + 0.20 * goal_separation)
    self_model_continuity = clamp01(0.45 + 0.55 * self_prior_mismatch)
    return EndogeneityVector(
        prompt_independence=prompt_independence,
        scheduler_independence=scheduler_independence,
        event_rule_independence=event_rule_independence,
        persistent_state_dependence=persistent_state_dependence,
        world_model_grounding=world_model_grounding,
        coherence_dependence=coherence_dependence,
        goal_novelty=goal_novelty,
        self_model_continuity=self_model_continuity,
        constitutional_boundedness=clamp01(constitutional_boundedness),
    )


@dataclass(slots=True)
class EpistemicTarget:
    target_id: str
    label: str
    preferred_intent: IntentKind
    ignorance: float
    surprise: float
    staleness: float
    self_prior_mismatch: float
    prospective_tension: float
    volatility_rate: float = 0.08

    def __post_init__(self) -> None:
        for name in (
            "ignorance",
            "surprise",
            "staleness",
            "self_prior_mismatch",
            "prospective_tension",
            "volatility_rate",
        ):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")

    def advance(self, dt_seconds: float) -> None:
        if dt_seconds <= 0.0:
            raise ValueError("dt_seconds must be positive")
        self.staleness = clamp01(
            self.staleness + self.volatility_rate * dt_seconds * (1.0 - self.staleness)
        )
        self.ignorance = clamp01(
            self.ignorance + 0.20 * self.volatility_rate * dt_seconds * (1.0 - self.ignorance)
        )
        self.surprise = clamp01(self.surprise * math.exp(-0.04 * dt_seconds))

    @property
    def epistemic_gap(self) -> float:
        return clamp01(
            0.28 * self.ignorance
            + 0.22 * self.surprise
            + 0.18 * self.staleness
            + 0.17 * self.self_prior_mismatch
            + 0.15 * self.prospective_tension
        )


class EndogenousWorldModelField:
    """Persistent target field; it contains no imperative goal or event rule."""

    def __init__(self, targets: tuple[EpistemicTarget, ...]) -> None:
        if len(targets) < 2:
            raise ValueError("at least two targets are required for competition")
        self.targets = targets

    def advance(self, dt_seconds: float) -> None:
        for target in self.targets:
            target.advance(dt_seconds)

    def ranked(self) -> tuple[EpistemicTarget, ...]:
        return tuple(sorted(self.targets, key=lambda item: item.epistemic_gap, reverse=True))


@dataclass(frozen=True, slots=True)
class EmergentIntent:
    intent_id: str
    target_id: str
    target_label: str
    kind: IntentKind
    emerged_at_seconds: float
    reason: str
    spectrum_level: EndogenousSpectrumLevel
    endogeneity: EndogeneityVector
    causal_factors: tuple[str, ...]
    boundary: str = "proposal_only"

