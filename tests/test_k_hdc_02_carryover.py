"""Tests for K-HDC-02 HDC carryover harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARNESS_DIR = REPO / "research" / "agent_eia" / "harnesses"
ADAPTERS = REPO / "research" / "agent_eia" / "adapters"

for path in (str(HARNESS_DIR), str(ADAPTERS), str(REPO / "src")):
    if path not in sys.path:
        sys.path.insert(0, path)

_H = HARNESS_DIR / "k_hdc_02_carryover.py"
_spec = importlib.util.spec_from_file_location("k_hdc_02_test", _H)
assert _spec and _spec.loader
_h = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _h
_spec.loader.exec_module(_h)


def test_hdc_evaluate_tick_retrieval():
    from hdc_memory import HDCEpisodicMemory

    mem = HDCEpisodicMemory(dim=512, seed=7)
    mem.store("tick_1", "action_a", tick=1)
    mem.store("tick_2", "action_b", tick=2)
    result = mem.evaluate_tick_retrieval(
        [{"tick": 2, "key": "tick_1", "expected_value": "action_a"}]
    )
    assert result["accuracy"] == 1.0


def test_tier_c_invariants():
    payload = _h.build_k_hdc_02_payload(seed=42, generated="2026-09-11", session_ticks=4)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["theory_strand"] == "kairologos_explore"


def test_two_arms_present():
    payload = _h.build_k_hdc_02_payload(seed=42, generated="2026-09-11", session_ticks=4)
    assert set(payload["arms"]) == {"full_eia", "full_eia_hdc"}


def test_session_ticks_minimum():
    payload = _h.build_k_hdc_02_payload(seed=42, generated="2026-09-11", session_ticks=4)
    assert payload["session_ticks"] >= 2


def test_diagnostic_pass():
    payload = _h.build_k_hdc_02_payload(seed=42, generated="2026-09-11", session_ticks=6)
    assert payload["diagnostic_pass"] is True
