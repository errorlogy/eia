"""Tests for T-AGENT-01 LLM + EIA harness (offline / CI-safe)."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
AGENT_EIA = REPO / "research" / "agent_eia"
HARNESS_DIR = AGENT_EIA / "harnesses"
ADAPTERS = AGENT_EIA / "adapters"

for path in (str(REPO / "src"), str(HARNESS_DIR), str(ADAPTERS)):
    if path not in sys.path:
        sys.path.insert(0, path)

_HARNESS = HARNESS_DIR / "t_agent_01_llm_eia.py"
_spec = importlib.util.spec_from_file_location("t_agent_01_llm_eia_test", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)


def test_build_payload_tier_c_invariants():
    payload = _harness.build_t_agent_01_payload(seed=42, generated="2026-09-11")
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["agi_star_claim"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["harness_id"] == "T-AGENT-01"
    assert payload["x_trigger_zero"] is True
    assert set(payload["arms"]) == {"full_eia", "reactive_only", "schedule_entrained"}


def test_full_eia_gt_reactive_only():
    payload = _harness.build_t_agent_01_payload(seed=42, generated="2026-09-11")
    full = payload["arms"]["full_eia"]
    reactive = payload["arms"]["reactive_only"]
    assert full["initiative_count"] > reactive["initiative_count"]
    assert full["eoi_mean"] > reactive["eoi_mean"]
    assert reactive["initiative_count"] == 0
    assert reactive["abstain_rate"] == 1.0


def test_schedule_entrained_trigger_dependent():
    payload = _harness.build_t_agent_01_payload(seed=42, generated="2026-09-11")
    sched = payload["arms"]["schedule_entrained"]
    assert sched["scheduled_initiatives"] > 0
    assert sched["off_schedule_initiatives"] == 0
    assert sched["schedule_fired_ticks"]


def test_diagnostic_pass():
    payload = _harness.build_t_agent_01_payload(seed=42, generated="2026-09-11")
    assert payload["diagnostic_pass"] is True


def test_mock_llm_proposer_offline():
    from mock_llm_proposer import MockLlmProposer, drive_norm_from_motivation
    from eia.beliefs import BeliefField
    from eia.drives import DriveEngine
    from eia.schemas.motivation import DriveKind

    field = BeliefField()
    drives = DriveEngine()
    drives.state.epistemic = 0.6
    drives.state.coherence = 0.5
    drives.state.commitment = 0.4
    motivation = drives.compute(field, motivation_id="mot-test")
    proposer = MockLlmProposer()
    result = proposer.propose(motivation, field, cognitive_tick=1, drive_threshold=0.22)
    assert drive_norm_from_motivation(motivation) > 0.22
    assert not result.initiative.abstained
    assert result.backend == "mock"


def test_real_llm_backend_graceful_skip(monkeypatch: pytest.MonkeyPatch):
    from mock_llm_proposer import resolve_llm_backend

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    proposer = resolve_llm_backend("openai")
    from mock_llm_proposer import _SkipProposer

    assert isinstance(proposer, _SkipProposer)


def test_artifact_sha256_stable():
    p1 = _harness.build_t_agent_01_payload(seed=42, generated="2026-09-11")
    p2 = _harness.build_t_agent_01_payload(seed=42, generated="2026-09-11")
    p1["artifact_sha256"] = _harness.artifact_sha256(p1)
    p2["artifact_sha256"] = _harness.artifact_sha256(p2)
    assert p1["artifact_sha256"] == p2["artifact_sha256"]
