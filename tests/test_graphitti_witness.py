"""Tests for M-O Graphitti binary witness harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_WITNESS = Path(__file__).resolve().parents[1] / "research" / "sci_flow" / "run_graphitti_witness.py"
_spec = importlib.util.spec_from_file_location("run_graphitti_witness", _WITNESS)
assert _spec and _spec.loader
_witness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _witness
_spec.loader.exec_module(_witness)

GOOD_OUTPUT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "vendor"
    / "graphitti"
    / "Testing"
    / "RegressionTesting"
    / "GoodOutput"
    / "Cpu"
    / "test-tiny-out.xml"
)


def test_build_payload_tier_c_stub() -> None:
    payload = _witness.build_payload()
    assert payload["claim_allowed"] is False
    assert payload["tier"] == "C"
    assert payload["cube_cell"] == "D2×L3"
    assert payload["tick"] in ("M-O-GRAPHITTI-BIN", "M-GRAPHITTI-CI")
    assert payload["binary_name"] == "cgraphitti"
    assert payload["ci_workflow"] == ".github/workflows/graphitti-witness.yml"
    sim = payload["simulation"]
    witness = payload["witness"]
    assert witness["witness_kind"] in ("stub", "binary_ok", "run_failed", "timeout")
    assert sim["binary_available"] is False or sim["status"] in ("ok", "run_failed", "timeout")


def test_parse_spike_metrics_regression_good_output() -> None:
    assert GOOD_OUTPUT.is_file()
    metrics = _witness.parse_spike_metrics(GOOD_OUTPUT, epoch_duration_s=1.0)
    assert metrics["parse_status"] == "ok"
    assert metrics["neuron_count"] >= 1
    assert metrics["spike_count_total"] > 0
    assert metrics["spike_rate_mean_hz"] > 0.0


def test_find_binary_none_when_unbuilt() -> None:
    binary = _witness.find_cgraphitti_binary()
    if binary is None:
        assert _witness.build_payload()["simulation"]["status"] == "build_blocked"
