"""Tests for M-LIVE-PATH shadow vs live carryover witness."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCI_FLOW = REPO / "research" / "sci_flow"

for path in (REPO / "src", SCI_FLOW):
    s = str(path)
    if s not in sys.path:
        sys.path.insert(0, s)

_HARNESS = SCI_FLOW / "live_path_witness_harness.py"
_spec = importlib.util.spec_from_file_location("live_path_witness_harness", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)

_WITNESS = SCI_FLOW / "run_live_path_witness.py"
_wspec = importlib.util.spec_from_file_location("run_live_path_witness", _WITNESS)
assert _wspec and _wspec.loader
_witness = importlib.util.module_from_spec(_wspec)
sys.modules[_wspec.name] = _witness
_wspec.loader.exec_module(_witness)

ARTIFACT = SCI_FLOW / "M-LIVE_PATH_witness_2026-09-02.json"


def test_live_path_witness_structural_pass() -> None:
    result = _harness.run_live_path_witness(seed=11, shadow_carryover_ticks=2)
    assert result.claim_allowed is False
    assert result.cube_cell == "D2×L3"
    assert result.witness_pass is True
    assert result.parity_checks["live_on_second_tick_hydrates"] is True
    assert result.parity_checks["live_off_no_store_beliefs"] is True
    assert result.gap_narrowed is True


def test_live_path_witness_artifact_schema() -> None:
    if not ARTIFACT.is_file():
        _witness.main()
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["milestone"] == "M-LIVE-PATH"
    assert payload["claim_allowed"] is False
    assert payload["witness_pass"] is True
    assert "shadow_snapshots" in payload
    assert "live_on_snapshots" in payload
    assert payload["parity_checks"]["live_on_beliefs_round_trip"] is True
