"""Tests for K-WOE-42 carrier surrogate harness."""

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

_H = HARNESS_DIR / "k_woe_42_carrier_surrogate.py"
_spec = importlib.util.spec_from_file_location("k_woe_42_test", _H)
assert _spec and _spec.loader
_h = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _h
_spec.loader.exec_module(_h)


def test_tier_c_invariants():
    payload = _h.build_k_woe_42_payload(seed=42, generated="2026-09-11")
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["theory_strand"] == "kairologos_explore"


def test_synthetic_battery_runs():
    payload = _h.build_k_woe_42_payload(seed=42, generated="2026-09-11")
    assert len(payload["synthetic_battery"]) == 4


def test_spike_battery_genesis_invariant():
    payload = _h.build_k_woe_42_payload(seed=42, generated="2026-09-11")
    assert payload["spike_battery"]["genesis_invariant_under_swap"] is True


def test_gamma_unique_verdict_present():
    payload = _h.build_k_woe_42_payload(seed=42, generated="2026-09-11")
    assert "F-GAMMA-UNIQUE" in payload["gamma_unique_verdict"]


def test_diagnostic_pass():
    payload = _h.build_k_woe_42_payload(seed=42, generated="2026-09-11")
    assert payload["diagnostic_pass"] is True
