"""DriveEngine — three drives from structural tension, NO LLM.

Drive dynamics follow spec §7.2:
  d_{k,t+1} = clip((1-ρ_k)d_{k,t} + α_k e_{k,t} + β_k n_{k,t} - γ_k s_{k,t}, 0, 1)

Antigravity: unlike embedding-based "curiosity" that regresses to median plateau,
each drive channel e_{k,t} is computed from BeliefField gradients — orthogonal
to token similarity space. K_A/K_H metaphor: machine-native structural signal
(K_A) is compact and precise; human narrative mood (K_H) is not used here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from eia.beliefs import BeliefField
from eia.schemas.motivation import DriveKind, Motivation, MotivationSignal


@dataclass
class DriveParams:
    """Per-drive dynamics parameters."""

    decay: float = 0.15
    excitability: float = 0.45
    novelty_gain: float = 0.25
    satisfaction_drain: float = 0.30
    saturation_threshold: float = 0.85


@dataclass
class DriveState:
    """Persistent drive levels — survive across ticks."""

    epistemic: float = 0.0
    coherence: float = 0.0
    commitment: float = 0.0
    tick: int = 0
    params: dict[DriveKind, DriveParams] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.params:
            self.params = {
                DriveKind.EPISTEMIC: DriveParams(decay=0.12, excitability=0.50),
                DriveKind.COHERENCE: DriveParams(decay=0.18, excitability=0.55),
                DriveKind.COMMITMENT: DriveParams(decay=0.10, excitability=0.40),
            }


class DriveEngine:
    """Deterministic drive computation from BeliefField gradients."""

    def __init__(self, state: DriveState | None = None) -> None:
        self.state = state or DriveState()

    def _update_channel(
        self,
        current: float,
        error: float,
        novelty: float,
        satisfaction: float,
        params: DriveParams,
    ) -> float:
        next_val = (
            (1 - params.decay) * current
            + params.excitability * error
            + params.novelty_gain * novelty
            - params.satisfaction_drain * satisfaction
        )
        if next_val > params.saturation_threshold:
            next_val = params.saturation_threshold + 0.05 * (next_val - params.saturation_threshold)
        return max(0.0, min(1.0, next_val))

    def compute(
        self,
        field: BeliefField,
        *,
        novelty_events: dict[DriveKind, float] | None = None,
        satisfaction: dict[DriveKind, float] | None = None,
        motivation_id: str = "mot-0",
    ) -> Motivation:
        """Compute motivation signals from current belief field."""
        gradients = field.gradient_snapshot()
        novelty_events = novelty_events or {}
        satisfaction = satisfaction or {}

        errors = {
            DriveKind.EPISTEMIC: gradients["epistemic"],
            DriveKind.COHERENCE: gradients["coherence"],
            DriveKind.COMMITMENT: gradients["commitment"],
        }

        levels = {
            DriveKind.EPISTEMIC: self.state.epistemic,
            DriveKind.COHERENCE: self.state.coherence,
            DriveKind.COMMITMENT: self.state.commitment,
        }

        signals: list[MotivationSignal] = []
        target_map: dict[DriveKind, list[str]] = {
            DriveKind.EPISTEMIC: [b.id for b in field.highest_entropy_beliefs(2)],
            DriveKind.COHERENCE: [c[0] for c in field.contradictions[:2]],
            DriveKind.COMMITMENT: [
                b.id for b in field.beliefs.values() if b.kind.value == "commitment"
            ],
        }

        for drive in DriveKind:
            params = self.state.params[drive]
            new_level = self._update_channel(
                levels[drive],
                errors[drive],
                novelty_events.get(drive, 0.0),
                satisfaction.get(drive, 0.0),
                params,
            )
            signals.append(
                MotivationSignal(
                    drive=drive,
                    intensity=new_level,
                    error_term=errors[drive],
                    saturation=max(0.0, new_level - params.saturation_threshold),
                    decay_rate=params.decay,
                    target_belief_ids=target_map.get(drive, []),
                    explanation=(
                        f"{drive.value} drive: error={errors[drive]:.3f} "
                        f"from BeliefField gradient (not embedding similarity)"
                    ),
                )
            )

        self.state.epistemic = signals[0].intensity
        self.state.coherence = signals[1].intensity
        self.state.commitment = signals[2].intensity
        self.state.tick += 1

        dominant = max(signals, key=lambda s: s.intensity)
        lex = (
            max(s.intensity for s in signals),
            gradients["coherence"],
            gradients["commitment"],
        )

        return Motivation(
            id=motivation_id,
            timestamp=datetime.now(timezone.utc),
            signals=signals,
            composite_lex_score=lex,
            dominant_drive=dominant.drive,
            parent_belief_update_ids=[u.id for u in field.updates[-3:]],
        )
