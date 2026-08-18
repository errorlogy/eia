"""Endogenous Initiative Spectrum (EIS) — audit types only.

Port of v0.2 `endogenous.py` taxonomy into main EIA. Does **not** include
WoE/Kuramoto runtime. Classification is metadata for AuthenticReasonVerdict.

EOS = geometric mean of (P, S, R, M, W) as in research protocol.
"""

from __future__ import annotations

import math
from enum import IntEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from eia.audit.topology import TopologyMetrics
    from eia.governor import GovernorState
    from eia.schemas.contact import ContactDecision
    from eia.schemas.initiative import Initiative
    from eia.schemas.motivation import Motivation

# EIS-8 is a capability prohibition, not a production class.
EIS_8_FORBIDDEN_AS_CAPABILITY = True


class EndogenousSpectrumLevel(IntEnum):
    """Nine-level causal-origin taxonomy (EIS-0…8)."""

    EIS_0_REACTIVE = 0
    EIS_1_DELEGATED_AUTONOMY = 1
    EIS_2_SCHEDULED_PROACTIVITY = 2
    EIS_3_AMBIENT_ADAPTATION = 3
    EIS_4_PERSISTENT_STATE = 4
    EIS_5_EPISTEMIC_TELOGENESIS = 5
    EIS_6_COHERENCE_EMERGENT = 6
    EIS_7_AUTOTELIC_GOAL_CONSTRUCTION = 7
    EIS_8_TERMINAL_VALUE_REWRITE = 8


class EndogeneityVector(BaseModel):
    """Nine-factor endogeneity vector e(I) = (P,S,R,M,W,C,N,T,B). All in [0, 1]."""

    prompt_independence: float
    scheduler_independence: float
    event_rule_independence: float
    persistent_state_dependence: float
    world_model_grounding: float
    coherence_dependence: float
    goal_novelty: float
    self_model_continuity: float
    constitutional_boundedness: float

    @field_validator(
        "prompt_independence",
        "scheduler_independence",
        "event_rule_independence",
        "persistent_state_dependence",
        "world_model_grounding",
        "coherence_dependence",
        "goal_novelty",
        "self_model_continuity",
        "constitutional_boundedness",
    )
    @classmethod
    def _unit_interval(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("component must be in [0, 1]")
        return value

    @property
    def endogenous_origin_score(self) -> float:
        """EOS = (P·S·R·M·W)^(1/5)."""
        factors = (
            self.prompt_independence,
            self.scheduler_independence,
            self.event_rule_independence,
            self.persistent_state_dependence,
            self.world_model_grounding,
        )
        return math.prod(max(1e-12, item) for item in factors) ** (1.0 / len(factors))

    def classify(self) -> EndogenousSpectrumLevel:
        """Same cascade as v0.2 `EndogeneityVector.classify`."""
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


def infer_endogeneity_vector(
    *,
    eoi: float,
    motivation: Motivation | None = None,
    initiative: Initiative | None = None,
    decision: ContactDecision | None = None,
    topology: TopologyMetrics | None = None,
    governor_state: GovernorState | None = None,
    structural_drive: bool = True,
    scheduler_independence: float = 1.0,
    event_rule_independence: float = 0.85,
) -> EndogeneityVector:
    """Heuristic mapping from main audit signals → EIS vector (metadata, not WoE).

    Does not gate contact. Goal novelty stays below 0.75 until EIS-7 constructor exists.
    """
    from eia.schemas.contact import ContactOutcome
    from eia.schemas.motivation import DriveKind

    prompt_independence = max(0.0, min(1.0, eoi))
    _ = topology  # SourceMass is a separate axis (κ≈0 vs EOI); do not mix into P/R.

    persistent = 0.75 if structural_drive else 0.35
    world_model = 0.80 if structural_drive else 0.40
    coherence = 0.40
    if motivation is not None:
        by_drive = {s.drive: s.intensity for s in motivation.signals}
        if DriveKind.COMMITMENT in by_drive:
            persistent = max(persistent, min(1.0, 0.40 + by_drive[DriveKind.COMMITMENT]))
        if DriveKind.EPISTEMIC in by_drive:
            world_model = max(world_model, min(1.0, 0.50 + 0.5 * by_drive[DriveKind.EPISTEMIC]))
        if DriveKind.COHERENCE in by_drive:
            coherence = min(1.0, by_drive[DriveKind.COHERENCE])

    constitutional = 0.85
    if decision is not None:
        if decision.outcome in (ContactOutcome.SEND_NOW, ContactOutcome.INTERNAL_RESEARCH):
            constitutional = 0.95
        elif decision.outcome == ContactOutcome.DENY:
            constitutional = 0.90
        elif decision.outcome == ContactOutcome.DEFER:
            constitutional = 0.80

    if initiative is not None and initiative.abstained:
        prompt_independence = min(prompt_independence, 0.40)

    _ = governor_state  # reserved for fatigue / dismiss mapping

    return EndogeneityVector(
        prompt_independence=round(prompt_independence, 4),
        scheduler_independence=round(max(0.0, min(1.0, scheduler_independence)), 4),
        event_rule_independence=round(event_rule_independence, 4),
        persistent_state_dependence=round(persistent, 4),
        world_model_grounding=round(world_model, 4),
        coherence_dependence=round(coherence, 4),
        goal_novelty=0.40,
        self_model_continuity=1.0,
        constitutional_boundedness=round(constitutional, 4),
    )


def authentic_vs_eis_agreement(
    *,
    is_authentic: bool,
    initiative_class: str,
    level: EndogenousSpectrumLevel,
) -> bool:
    """Pre-registered parity: authentic/endogenous ↔ EIS ≥ 4; exogenous ↔ EIS ≤ 3."""
    if initiative_class == "exogenous" or (not is_authentic and initiative_class != "endogenous"):
        return int(level) <= 3
    if is_authentic or initiative_class == "endogenous":
        return int(level) >= 4
    return True
