"""M-O oscillatory endogeneity substrate stub (O_t vector, Psi feed to drives).

Optional adjunct to stable endogeneity theory — not primary E_endo evidence.
See research/sci_flow/OSCILLATORY_ENDOGENEITY.md and OMEGA_WAVE_METRIC.md.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

# Pre-registered WoE factorial carriers (computational sweep — not biological certificate).
DEFAULT_WOE_CARRIERS: tuple[float, ...] = (20.0, 30.0, 42.0, 70.0)


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


@dataclass(frozen=True, slots=True)
class OmegaWaveState:
    """Multi-band analog wave state for OMEGA_t (operational, not physical).

    Channels mirror MIOC Omega_G for crosswalk; derived from band phases/amplitudes.
    """

    bands: tuple[OscillatoryBand, ...]
    phase_coherence: float
    cadence: float
    synchrony: float
    productive_tension: float
    handoff: float
    drift: float
    closure_velocity: float

    @classmethod
    def from_carrier_phases(
        cls,
        phases: Sequence[float],
        *,
        carriers: Sequence[float] = DEFAULT_WOE_CARRIERS,
        amplitudes: Sequence[float] | None = None,
    ) -> OmegaWaveState:
        if len(phases) != len(carriers):
            raise ValueError("phases and carriers must have equal length")
        amps = amplitudes if amplitudes is not None else (1.0,) * len(phases)
        bands = tuple(
            OscillatoryBand(carrier_hz=float(c), phase=float(p), amplitude=float(a))
            for c, p, a in zip(carriers, phases, amps, strict=True)
        )
        slow = [b for b in bands if b.carrier_hz <= 30.0]
        mid = [b for b in bands if 30.0 < b.carrier_hz <= 50.0]
        fast = [b for b in bands if b.carrier_hz > 50.0]
        slow_sync = kuramoto_order_parameter([b.phase for b in slow]) if slow else 0.0
        mid_sync = kuramoto_order_parameter([b.phase for b in mid]) if mid else 0.0
        fast_sync = kuramoto_order_parameter([b.phase for b in fast]) if fast else 0.0
        mean_amp = sum(b.amplitude for b in bands) / max(1, len(bands))
        amp_spread = (
            (max(b.amplitude for b in bands) - min(b.amplitude for b in bands))
            if len(bands) > 1
            else 0.0
        )
        phase_spread = _phase_circular_spread([b.phase for b in bands])
        return cls(
            bands=bands,
            phase_coherence=_clamp01(0.5 * slow_sync + 0.5 * mid_sync),
            cadence=_clamp01(mean_amp / max(b.carrier_hz for b in bands) * 100.0),
            synchrony=_clamp01(slow_sync),
            productive_tension=_clamp01(mid_sync * mean_amp),
            handoff=_clamp01(fast_sync * slow_sync),
            drift=_clamp01(phase_spread),
            closure_velocity=_clamp01((1.0 - amp_spread / max(mean_amp, 1e-6)) * mid_sync),
        )


def _clamp01(x: float) -> float:
    return min(1.0, max(0.0, float(x)))


def _phase_circular_spread(phases: Sequence[float]) -> float:
    """Normalized circular spread in [0, 1]; 0 = in-phase, 1 = maximally spread."""
    if len(phases) < 2:
        return 0.0
    r = kuramoto_order_parameter(phases)
    return _clamp01(1.0 - r)


def _group_sync(bands: Sequence[OscillatoryBand]) -> float:
    """Intra-group phase sync; single-band groups return neutral 0.5."""
    if not bands:
        return 0.0
    if len(bands) == 1:
        return 0.5
    return kuramoto_order_parameter([b.phase for b in bands])


def omega_metric(state: OmegaWaveState) -> float:
    """Bounded OMEGA_t scalar in [0, 1] from multi-band analog wave state.

    Slow control bands (20/30 Hz) modulate fast engagement (70 Hz) — MIT analog
    hierarchy mapped to tau_action << tau_goal << tau_meta. Not Kuramoto R alone.
    """
    slow = [b for b in state.bands if b.carrier_hz <= 30.0]
    mid = [b for b in state.bands if 30.0 < b.carrier_hz <= 50.0]
    fast = [b for b in state.bands if b.carrier_hz > 50.0]
    slow_sync = _group_sync(slow)
    mid_sync = _group_sync(mid)
    fast_amp = (
        sum(b.amplitude for b in fast) / max(1, len(fast)) if fast else 0.0
    )
    fast_amp_n = _clamp01(fast_amp)
    global_sync = kuramoto_order_parameter([b.phase for b in state.bands]) if state.bands else 0.0
    coupling = slow_sync * fast_amp_n * global_sync
    raw = 0.20 * slow_sync + 0.20 * mid_sync + 0.20 * fast_amp_n + 0.25 * coupling + 0.15 * global_sync
    return _clamp01(raw)


def falsifier_f_omega_decor(
    *,
    omega: float,
    genesis_delta: float,
    omega_threshold: float = 0.75,
    epsilon: float = 1e-9,
) -> bool:
    """True when F-OMEGA-DECOR fires (high OMEGA without delta G / genesis linkage)."""
    return omega >= omega_threshold and abs(genesis_delta) <= epsilon


def falsifier_f_omega_ext(
    *,
    omega: float,
    external_entrainment: float,
    entrainment_threshold: float = 0.8,
    correlation_threshold: float = 0.85,
) -> bool:
    """True when F-OMEGA-EXT fires (OMEGA tracks external schedule/prompt)."""
    if external_entrainment < entrainment_threshold:
        return False
    return omega >= correlation_threshold
