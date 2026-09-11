"""Spike-phase extraction → OmegaWaveState / OMEGA_t injection (Tier C crosswalk)."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from typing import Any, Sequence

REPO = Path(__file__).resolve().parents[3]
WOE_OSCILLATORY = REPO / "research" / "cursor-starter-v0.2" / "src" / "eia" / "oscillatory_state.py"
DEFAULT_CARRIERS: tuple[float, ...] = (20.0, 30.0, 42.0, 70.0)


def _load_oscillatory_module() -> Any:
    spec = importlib.util.spec_from_file_location("oscillatory_state_brain_ai", WOE_OSCILLATORY)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {WOE_OSCILLATORY}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def spike_times_to_phase(
    spike_times_ms: Sequence[float],
    *,
    carrier_hz: float,
    duration_ms: float,
) -> float:
    """Map spike train to dominant phase at carrier frequency."""
    if not spike_times_ms:
        return 0.0
    period_ms = 1000.0 / max(carrier_hz, 1e-6)
    phases = [(t % period_ms) / period_ms * 2 * math.pi for t in spike_times_ms]
    if len(phases) == 1:
        return phases[0]
    re = sum(math.cos(p) for p in phases) / len(phases)
    im = sum(math.sin(p) for p in phases) / len(phases)
    return math.atan2(im, re) % (2 * math.pi)


def aggregate_node_phases(
    spike_times_ms: dict[str, list[float]],
    *,
    carriers: Sequence[float] = DEFAULT_CARRIERS,
    duration_ms: float = 100.0,
) -> list[float]:
    """Per-carrier phase from pooled node spike trains."""
    all_times: list[float] = []
    for times in spike_times_ms.values():
        all_times.extend(times)
    return [
        spike_times_to_phase(all_times, carrier_hz=c, duration_ms=duration_ms)
        for c in carriers
    ]


def node_phases_by_band(
    spike_times_ms: dict[str, list[float]],
    node_ids: Sequence[str],
    *,
    carriers: Sequence[float] = DEFAULT_CARRIERS,
    duration_ms: float = 100.0,
) -> dict[str, list[float]]:
    """Per-node phases at each carrier (for diagnostics)."""
    out: dict[str, list[float]] = {}
    for nid in node_ids:
        times = spike_times_ms.get(nid, [])
        out[nid] = [
            spike_times_to_phase(times, carrier_hz=c, duration_ms=duration_ms)
            for c in carriers
        ]
    return out


def inject_omega_from_spikes(
    spike_payload: dict[str, Any],
    node_ids: Sequence[str],
    *,
    carriers: Sequence[float] = DEFAULT_CARRIERS,
    osc_mod: Any | None = None,
) -> dict[str, Any]:
    """Build OmegaWaveState + OMEGA_t from spike dynamics payload."""
    mod = osc_mod or _load_oscillatory_module()
    spike_times = spike_payload.get("spike_times_ms") or {}
    duration_ms = float(spike_payload.get("duration_ms") or 100.0)

    phases = aggregate_node_phases(
        spike_times, carriers=carriers, duration_ms=duration_ms
    )
    amps = [min(1.0, 0.3 + 0.1 * len(spike_times.get(nid, []))) for nid in node_ids[: len(carriers)]]
    while len(amps) < len(carriers):
        amps.append(1.0)

    ows = mod.OmegaWaveState.from_carrier_phases(phases, carriers=carriers, amplitudes=amps)
    omega_t = float(mod.omega_metric(ows))
    kuramoto_r = float(mod.kuramoto_order_parameter(phases))

    return {
        "omega_t": omega_t,
        "kuramoto_r": kuramoto_r,
        "phases_rad": [round(p, 6) for p in phases],
        "carriers_hz": list(carriers),
        "omega_wave_state": {
            "phase_coherence": ows.phase_coherence,
            "cadence": ows.cadence,
            "synchrony": ows.synchrony,
            "productive_tension": ows.productive_tension,
            "handoff": ows.handoff,
            "drift": ows.drift,
            "closure_velocity": ows.closure_velocity,
            "n_bands": len(carriers),
        },
        "crosswalk": {
            "connectome_spike_phases_to_omega_wave_state": True,
            "backend": spike_payload.get("backend"),
        },
        "vendor": "brain_ai.ot_injection",
        "spike_backend": spike_payload.get("backend"),
        "n_spikes": spike_payload.get("n_spikes"),
    }
