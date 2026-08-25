"""Unit tests for M-O oscillatory substrate falsifiers (F-SYNC, F-PHASE-ONLY)."""

from __future__ import annotations

import importlib.util
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


def test_kuramoto_in_phase_is_high_sync() -> None:
    r = _os.kuramoto_order_parameter((0.0, 0.05, -0.05))
    assert r > 0.95


def test_f_sync_fires_without_genesis_linkage() -> None:
    state = _os.OscillatoryState.from_phases((0.0, 0.0, 0.0))
    assert state.order_parameter > 0.85
    assert _os.falsifier_f_sync(order_parameter=state.order_parameter, genesis_linked=False)
    assert not _os.falsifier_f_sync(order_parameter=state.order_parameter, genesis_linked=True)


def test_f_phase_only_fires_when_genesis_flat() -> None:
    assert _os.falsifier_f_phase_only(phase_coherent=True, genesis_delta=0.0)
    assert not _os.falsifier_f_phase_only(phase_coherent=True, genesis_delta=0.2)


def test_psi_and_merge_phi_bounded() -> None:
    state = _os.OscillatoryState.from_phases((0.0, 1.0), amplitudes=(2.0, 2.0))
    psi = _os.psi_oscillatory(state, saturation=0.5)
    assert all(0.0 <= v <= 0.5 for v in psi)
    merged = _os.merge_phi((0.1, 0.2), state, saturation=0.5)
    assert len(merged) >= 2
