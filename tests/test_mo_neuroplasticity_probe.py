"""Tests for M-O Neuraxon/Graphitti neuroplasticity probe harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_PROBE = Path(__file__).resolve().parents[1] / "research" / "sci_flow" / "run_mo_neuroplasticity_probe.py"
_spec = importlib.util.spec_from_file_location("run_mo_neuroplasticity_probe", _PROBE)
assert _spec and _spec.loader
_probe = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _probe
_spec.loader.exec_module(_probe)


def test_build_payload_tier_c() -> None:
    payload = _probe.build_payload(steps=10)
    assert payload["claim_allowed"] is False
    assert payload["tier"] == "C"
    assert payload["cube_cell"] == "D2×L2"
    assert payload["neuraxon"]["status"] == "ok"
    assert payload["neuraxon"]["steps"] == 10
    assert "omega_t" in payload["neuraxon"]
    assert payload["graphitti"]["has_conn_growth"] is True
    assert "do_o_neuraxon_plasticity_off" in payload["do_o_interventions"]


def test_neuraxon_omega_bounded() -> None:
    payload = _probe.build_payload(steps=20)
    omega = payload["neuraxon"]["omega_t"]
    assert 0.0 <= omega["final"] <= 1.0
    assert omega["min"] <= omega["max"]
