"""M-O oscillatory endogeneity substrate stub (O_t vector, Psi feed to drives).

Optional adjunct to stable endogeneity theory — not primary E_endo evidence.
See research/sci_flow/OSCILLATORY_ENDOGENEITY.md.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class OscillatoryBand:
    """One carrier band in O_t."""

    carrier_hz: float
    phase: float
    amplitude: float


@dataclass(frozen=True, slots=True)
class OscillatoryState:
    """Low-dimensional oscillatory field O_t = bands + summary order parameter R_t."""

    bands: tuple[OscillatoryBand, ...]
    order_parameter: float

    @classmethod
    def from_phases(
        cls,
        phases: Sequence[float],
        *,
        carrier_hz: float = 42.0,
        amplitudes: Sequence[float] | None = None,
    ) -> OscillatoryState:
        amps = amplitudes if amplitudes is not None else (1.0,) * len(phases)
        bands = tuple(
            OscillatoryBand(carrier_hz=carrier_hz, phase=float(p), amplitude=float(a))
            for p, a in zip(phases, amps, strict=True)
        )
        return cls(bands=bands, order_parameter=kuramoto_order_parameter(phases))


def kuramoto_order_parameter(phases: Sequence[float]) -> float:
    """Kuramoto R in [0, 1] — descriptive only; not E_endo proof."""
    if not phases:
        return 0.0
    re = sum(math.cos(p) for p in phases) / len(phases)
    im = sum(math.sin(p) for p in phases) / len(phases)
    return math.hypot(re, im)


def psi_oscillatory(
    state: OscillatoryState,
    *,
    saturation: float = 1.0,
    n_features: int = 5,
) -> tuple[float, ...]:
    """Bounded Psi(O_t) contribution to drive features Phi_t (stub)."""
    sat = max(1e-6, float(saturation))
    base = (
        min(sat, state.order_parameter),
        min(sat, sum(b.amplitude for b in state.bands) / max(1, len(state.bands))),
        min(sat, max((b.amplitude for b in state.bands), default=0.0)),
        min(sat, math.sin(state.bands[0].phase) if state.bands else 0.0),
        min(sat, state.bands[0].carrier_hz / 100.0 if state.bands else 0.0),
    )
    if n_features <= len(base):
        return base[:n_features]
    return base + (0.0,) * (n_features - len(base))


def merge_phi(base: Sequence[float], oscillatory: OscillatoryState, **psi_kwargs) -> tuple[float, ...]:
    """Phi_t <- Phi_t^base + Psi(O_t) elementwise (bounded)."""
    psi = psi_oscillatory(oscillatory, **psi_kwargs)
    n = max(len(base), len(psi))
    out: list[float] = []
    for i in range(n):
        b = base[i] if i < len(base) else 0.0
        p = psi[i] if i < len(psi) else 0.0
        out.append(b + p)
    return tuple(out)


def falsifier_f_sync(*, order_parameter: float, genesis_linked: bool, r_threshold: float = 0.85) -> bool:
    """True when F-SYNC fires (high sync without genesis linkage)."""
    return order_parameter >= r_threshold and not genesis_linked


def falsifier_f_phase_only(*, phase_coherent: bool, genesis_delta: float, epsilon: float = 1e-9) -> bool:
    """True when F-PHASE-ONLY fires (coherence without genesis effect)."""
    return phase_coherent and abs(genesis_delta) <= epsilon
