"""Unit tests for OMEGA_t metric and F-OMEGA-DECOR falsifier."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

_MOD = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "cursor-starter-v0.2"
    / "src"
    / "eia"
    / "oscillatory_state.py"
)
_spec = importlib.util.spec_from_file_location("oscillatory_state_research", _MOD)
assert _spec and _spec.loader
_os = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _os
_spec.loader.exec_module(_os)


def test_omega_metric_bounded_in_phase() -> None:
    phases = (0.0, 0.05, 0.0, 0.02)
    state = _os.OmegaWaveState.from_carrier_phases(phases)
    omega = _os.omega_metric(state)
    assert 0.0 <= omega <= 1.0
    assert omega > 0.7


def test_omega_metric_low_when_scrambled() -> None:
    phases = (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)
    state = _os.OmegaWaveState.from_carrier_phases(phases)
    omega = _os.omega_metric(state)
    assert omega < 0.5


def test_f_omega_decor_fires_without_genesis_delta() -> None:
    phases = (0.0, 0.0, 0.0, 0.0)
    state = _os.OmegaWaveState.from_carrier_phases(phases)
    omega = _os.omega_metric(state)
    assert omega >= 0.75
    assert _os.falsifier_f_omega_decor(omega=omega, genesis_delta=0.0)
    assert not _os.falsifier_f_omega_decor(omega=omega, genesis_delta=0.15)


def test_omega_wave_state_mioc_channels_bounded() -> None:
    state = _os.OmegaWaveState.from_carrier_phases((0.1, 0.2, 0.3, 0.4))
    for attr in (
        "phase_coherence",
        "cadence",
        "synchrony",
        "productive_tension",
        "handoff",
        "drift",
        "closure_velocity",
    ):
        val = getattr(state, attr)
        assert 0.0 <= val <= 1.0, attr
