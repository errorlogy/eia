"""Tests for K-HDC-01 agent HDC binding harness."""

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

_H = HARNESS_DIR / "k_hdc_01_agent_binding.py"
_spec = importlib.util.spec_from_file_location("k_hdc_01_test", _H)
assert _spec and _spec.loader
_h = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _h
_spec.loader.exec_module(_h)


def test_hdc_memory_bind_store_query():
    from hdc_memory import HDCEpisodicMemory

    mem = HDCEpisodicMemory(dim=512, seed=7)
    mem.store("tick_1", "action_a", tick=1)
    hit = mem.query("tick_1")
    assert hit["hit"] is True
    assert hit["value"] == "action_a"
    assert mem.stats()["retrieval_rate"] == 1.0


def test_tier_c_invariants():
    payload = _h.build_k_hdc_01_payload(seed=42, generated="2026-09-11", quiet_ticks=4)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["agi_star_claim"] is False
    assert payload["theory_strand"] == "kairologos_explore"


def test_three_arms_present():
    payload = _h.build_k_hdc_01_payload(seed=42, generated="2026-09-11", quiet_ticks=4)
    assert set(payload["arms"]) == {"full_eia", "full_eia_hdc", "reactive_only"}


def test_hdc_retrieval_works():
    payload = _h.build_k_hdc_01_payload(seed=42, generated="2026-09-11", quiet_ticks=6)
    assert payload["diagnostics"]["hdc_retrieval_works"] is True


def test_diagnostic_pass():
    payload = _h.build_k_hdc_01_payload(seed=42, generated="2026-09-11", quiet_ticks=6)
    assert payload["diagnostic_pass"] is True
