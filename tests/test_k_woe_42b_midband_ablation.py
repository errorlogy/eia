"""Tests for K-WOE-42b mid-band ablation harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARNESS_DIR = REPO / "research" / "brain_ai" / "harnesses"
ADAPTERS = REPO / "research" / "brain_ai" / "adapters"

for path in (str(HARNESS_DIR), str(ADAPTERS)):
    if path not in sys.path:
        sys.path.insert(0, path)

_H = HARNESS_DIR / "k_woe_42b_midband_ablation.py"
_spec = importlib.util.spec_from_file_location("k_woe_42b_test", _H)
assert _spec and _spec.loader
_h = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _h
_spec.loader.exec_module(_h)


def test_tier_c_invariants():
    payload = _h.build_k_woe_42b_payload(seed=42, generated="2026-09-11")
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["theory_strand"] == "kairologos_explore"


def test_weight_modes_present():
    payload = _h.build_k_woe_42b_payload(seed=42, generated="2026-09-11")
    assert set(payload["weight_modes"]) == {"default", "equal_weight", "mid_ablated"}


def test_spike_battery_genesis_invariant():
    payload = _h.build_k_woe_42b_payload(seed=42, generated="2026-09-11")
    for mode in ("default", "equal_weight", "mid_ablated"):
        assert payload["spike_battery"][mode]["genesis_invariant_under_swap"] is True


def test_ablation_verdict_present():
    payload = _h.build_k_woe_42b_payload(seed=42, generated="2026-09-11")
    assert "F-GAMMA-UNIQUE-ABLATION" in payload["ablation_verdict"]


def test_diagnostic_pass():
    payload = _h.build_k_woe_42b_payload(seed=42, generated="2026-09-11")
    assert payload["diagnostic_pass"] is True
