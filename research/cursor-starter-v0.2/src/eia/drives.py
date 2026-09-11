"""Bounded endogenous drive dynamics."""

from __future__ import annotations

from datetime import datetime, timedelta

from .math_model import drive_transition
from .models import DriveKind, DriveSpec, DriveState


DEFAULT_DRIVE_SPECS: tuple[DriveSpec, ...] = (
    DriveSpec(DriveKind.EPISTEMIC, 0.08, 0.62, 0.22, 0.75, 0.48, 900.0),
    DriveSpec(DriveKind.COHERENCE, 0.05, 0.72, 0.16, 0.70, 0.55, 1200.0),
    DriveSpec(DriveKind.COMMITMENT, 0.03, 0.58, 0.12, 0.65, 0.50, 1800.0),
    DriveSpec(DriveKind.CARE, 0.10, 0.42, 0.28, 0.80, 0.62, 3600.0),
    DriveSpec(DriveKind.SELF_MAINTENANCE, 0.02, 0.85, 0.05, 0.90, 0.60, 300.0),
)


class DriveEngine:
    def __init__(self, specs: tuple[DriveSpec, ...] = DEFAULT_DRIVE_SPECS) -> None:
        self.specs = {spec.kind: spec for spec in specs}
        self.states = {kind: DriveState(kind=kind) for kind in self.specs}

    def update(
        self,
        kind: DriveKind,
        now: datetime,
        *,
        error: float = 0.0,
        novelty: float = 0.0,
        satisfaction: float = 0.0,
        evidence_ids: tuple[str, ...] = (),
    ) -> DriveState:
        spec = self.specs[kind]
        state = self.states[kind]
        state.intensity = drive_transition(
            state.intensity,
            decay=spec.decay,
            error=error,
            novelty=novelty,
            satisfaction=satisfaction,
            error_gain=spec.error_gain,
            novelty_gain=spec.novelty_gain,
            satisfaction_gain=spec.satisfaction_gain,
        )
        state.last_updated_at = now
        if evidence_ids:
            state.evidence_ids = (*state.evidence_ids[-15:], *evidence_ids)
        return state

    def decay_all(self, now: datetime) -> None:
        for kind in self.specs:
            self.update(kind, now)

    def is_actionable(self, kind: DriveKind, now: datetime) -> bool:
        state = self.states[kind]
        spec = self.specs[kind]
        refractory = state.refractory_until
        return state.intensity >= spec.activation_threshold and (
            refractory is None or now >= refractory
        )

    def activate_refractory(self, kind: DriveKind, now: datetime) -> None:
        spec = self.specs[kind]
        self.states[kind].refractory_until = now + timedelta(seconds=spec.refractory_seconds)

    def satisfy(self, kind: DriveKind, now: datetime, amount: float = 1.0) -> None:
        self.update(kind, now, satisfaction=amount)
        self.activate_refractory(kind, now)

    def ranked(self, now: datetime) -> tuple[DriveState, ...]:
        actionable = [state for kind, state in self.states.items() if self.is_actionable(kind, now)]
        return tuple(sorted(actionable, key=lambda state: state.intensity, reverse=True))

