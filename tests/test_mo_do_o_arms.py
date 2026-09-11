"""Tests for M-O paired do(O) arms harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ARMS = Path(__file__).resolve().parents[1] / "research" / "sci_flow" / "run_mo_do_o_arms.py"
_spec = importlib.util.spec_from_file_location("run_mo_do_o_arms", _ARMS)
assert _spec and _spec.loader
_arms = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _arms
_spec.loader.exec_module(_arms)


def test_build_payload_tier_c_paired() -> None:
    payload = _arms.build_payload(steps=10, seed=42)
    assert payload["claim_allowed"] is False
    assert payload["tier"] == "C"
    assert payload["cube_cell"] == "D2×L2"
    assert payload["artifact_id"] == "M-MO_do_o_arms_2026-09-02"
    assert set(payload["arms"]) == {
        "neuraxon_baseline",
        "do_o_neuraxon_plasticity_off",
        "do_o_graphitti_growth_off",
        "native_oscillatory_state",
    }
    assert payload["arms"]["neuraxon_baseline"]["status"] == "ok"
    assert payload["arms"]["do_o_neuraxon_plasticity_off"]["status"] == "ok"
    assert payload["crosswalk_feasible"] is True


def test_plasticity_off_reduces_weight_drift() -> None:
    payload = _arms.build_payload(steps=20, seed=42)
    baseline = payload["arms"]["neuraxon_baseline"]
    off = payload["arms"]["do_o_neuraxon_plasticity_off"]
    assert off["plasticity"]["w_fast_drift"] == 0.0
    assert off["plasticity"]["structural_events"] == 0
    assert baseline["plasticity"]["w_fast_drift"] != 0.0 or baseline["steps"] == 0


def test_paired_comparison_has_deltas() -> None:
    payload = _arms.build_payload(steps=15, seed=7)
    cmp = payload["paired_comparison"]
    assert "delta_plasticity_off_vs_baseline" in cmp["omega_t_final"]
    assert "falsifier_hints" in cmp
    assert cmp["falsifier_hints"]["F-KURAMOTO-AS-E"] in (True, False)


def test_native_oscillatory_bounded() -> None:
    native = _arms.arm_native_oscillatory(seed=1)
    assert 0.0 <= native["omega_t"]["final"] <= 1.0
    assert native["crosswalk"]["native_default_carriers"] is True
