"""AMAT M0-twin stub — architecture hook, not a bot persona.

Law: compute typicality sketch; do not emit M0 as the agent voice.
See research/sci_flow/M0_TWIN_AMAT_DESIGN.md and NAMM ANTI_MEDIAN_AI_TOPOLOGY.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class M0Sketch:
    """Typicality / M0 sketch for audit. emit_m0 is always False in v0."""

    distance_to_typical: float
    phase_hint: str
    generators: tuple[str, ...]
    emit_m0: bool = False

    def as_audit_dict(self) -> dict[str, Any]:
        return {
            "distance_to_typical": self.distance_to_typical,
            "phase_hint": self.phase_hint,
            "generators": list(self.generators),
            "emit_m0": False,
            "role": "architecture_audit_only",
        }


def compute_m0_sketch(
    *,
    epistemic_pressure: float,
    peak_coherence: float,
    self_prior_mismatch: float,
) -> M0Sketch:
    """Heuristic off-typical hint from WoE state (no embedding stack required).

    High pressure + self-prior mismatch with mid coherence → exploratory / nd hint.
    This is a placeholder until NAMM embedding d(h(y), B_*) is wired.
    """
    pressure = max(0.0, min(1.0, epistemic_pressure))
    r = max(0.0, min(1.0, peak_coherence))
    mismatch = max(0.0, min(1.0, self_prior_mismatch))
    # Proxy distance: larger when mismatch/pressure high and R not locked at 1.
    distance = max(0.0, min(2.0, mismatch + 0.5 * pressure + 0.3 * (1.0 - r)))
    if distance >= 1.2 and 0.05 < r < 0.97:
        phase = "K_AI_nd_hint"
    else:
        phase = "K_AI_mu_suspect"
    return M0Sketch(
        distance_to_typical=round(distance, 4),
        phase_hint=phase,
        generators=("epistemic_pressure", "self_prior_mismatch", "coherence_band"),
        emit_m0=False,
    )
