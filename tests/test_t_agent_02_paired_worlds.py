"""Tests for T-AGENT-02 paired worlds harness (offline / CI-safe)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENT_EIA = REPO / "research" / "agent_eia"
HARNESS_DIR = AGENT_EIA / "harnesses"
ADAPTERS = AGENT_EIA / "adapters"

for path in (str(REPO / "src"), str(HARNESS_DIR), str(ADAPTERS)):
    if path not in sys.path:
        sys.path.insert(0, path)

_HARNESS = HARNESS_DIR / "t_agent_02_paired_worlds.py"
_spec = importlib.util.spec_from_file_location("t_agent_02_paired_worlds_test", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)


def test_build_payload_tier_c_invariants():
    payload = _harness.build_t_agent_02_payload(generated="2026-09-11", num_worlds=8)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["agi_star_claim"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["harness_id"] == "T-AGENT-02"
    assert payload["num_worlds"] == 8
    assert set(payload["aggregates"]) == {"full_eia", "reactive_only", "schedule_entrained"}


def test_full_eia_gt_reactive_across_worlds():
    payload = _harness.build_t_agent_02_payload(generated="2026-09-11", num_worlds=8)
    full = payload["aggregates"]["full_eia"]
    reactive = payload["aggregates"]["reactive_only"]
    assert full["mean_initiative_count"] > reactive["mean_initiative_count"]
    assert full["mean_euir"] > reactive["mean_euir"]
    assert reactive["mean_initiative_count"] == 0.0
    assert reactive["mean_abstain_rate"] == 1.0


def test_schedule_entrained_distinct_from_full_eia():
    payload = _harness.build_t_agent_02_payload(generated="2026-09-11", num_worlds=8)
    full = payload["aggregates"]["full_eia"]
    sched = payload["aggregates"]["schedule_entrained"]
    assert sched["mean_euir"] < full["mean_euir"]
    assert sched["mean_initiative_count"] < full["mean_initiative_count"]


def test_world_separation_and_pass_count():
    payload = _harness.build_t_agent_02_payload(generated="2026-09-11", num_worlds=8)
    diag = payload["diagnostics"]
    assert diag["worlds_pass_count"] == diag["worlds_total"]
    assert diag["mean_separation"] > 0.5
    assert diag["f_reactive_collapse"] is True
    assert diag["f_schedule_as_endo"] is True


def test_diagnostic_pass():
    payload = _harness.build_t_agent_02_payload(generated="2026-09-11", num_worlds=8)
    assert payload["diagnostic_pass"] is True


def test_perturbation_worlds_present():
    payload = _harness.build_t_agent_02_payload(generated="2026-09-11", num_worlds=8)
    perturb = [w for w in payload["worlds"] if w["perturbation"]]
    assert len(perturb) >= 2
    assert payload["diagnostics"]["perturbation_resume"] is True


def test_artifact_sha256_stable():
    p1 = _harness.build_t_agent_02_payload(generated="2026-09-11", num_worlds=8)
    p2 = _harness.build_t_agent_02_payload(generated="2026-09-11", num_worlds=8)
    p1["artifact_sha256"] = _harness.artifact_sha256(p1)
    p2["artifact_sha256"] = _harness.artifact_sha256(p2)
    assert p1["artifact_sha256"] == p2["artifact_sha256"]
