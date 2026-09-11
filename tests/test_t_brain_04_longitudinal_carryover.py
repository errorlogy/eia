"""Tests for T-BRAIN-04 longitudinal shadow carryover harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BRAIN_AI = REPO / "research" / "brain_ai"
HARNESS_DIR = BRAIN_AI / "harnesses"
ADAPTERS = BRAIN_AI / "adapters"

for path in (str(HARNESS_DIR), str(ADAPTERS)):
    if path not in sys.path:
        sys.path.insert(0, path)

_HARNESS = HARNESS_DIR / "t_brain_04_longitudinal_carryover.py"
_spec = importlib.util.spec_from_file_location("t_brain_04_longitudinal_carryover_test", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)


def test_build_payload_tier_c_invariants():
    payload = _harness.build_t_brain_04_payload(seed=42, prefer_brian2=False)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["agi_star_claim"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["harness_id"] == "T-BRAIN-04"
    assert payload["x_trigger_zero"] is True
    assert payload["session_ticks"] == 2
    assert len(payload["arms"]) == 3


def test_endogenous_sustained_genesis_across_ticks():
    payload = _harness.build_t_brain_04_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    active = payload["arms"]["coupled_active"]
    assert all(t["has_novel_g_prime"] for t in active["ticks"])
    assert active["cumulative_genesis_delta"] >= 2.0


def test_passive_zero_initiatives_all_ticks():
    payload = _harness.build_t_brain_04_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    passive = payload["arms"]["passive_quiescent"]
    assert passive["eia_baseline"] == "reactive_only"
    for t in passive["ticks"]:
        assert t["n_initiatives"] == 0
        assert t["has_novel_g_prime"] is False


def test_phase_scramble_f_omega_decor():
    payload = _harness.build_t_brain_04_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    coupled = payload["arms"]["coupled_active"]
    scramble = payload["arms"]["phase_scramble_control"]
    assert scramble["inject_omega_psi_tick0"] is False
    assert abs(coupled["omega_t_tick0"] - scramble["omega_t_tick0"]) > 0.01
    assert payload["f_omega_decor"]["status"] == "confirmed"


def test_carryover_no_omega_reinjection():
    payload = _harness.build_t_brain_04_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    for arm in payload["arms"].values():
        carryover_ticks = [t for t in arm["ticks"] if t["used_carryover"]]
        assert carryover_ticks, "expected at least one carryover tick"
        for t in carryover_ticks:
            assert t["omega_t"] is None
            assert t["inject_omega_psi"] is False


def test_diagnostic_pass():
    payload = _harness.build_t_brain_04_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    assert payload["diagnostic_pass"] is True


def test_artifact_sha256_stable():
    p1 = _harness.build_t_brain_04_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    p2 = _harness.build_t_brain_04_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    assert _harness.artifact_sha256(p1) == _harness.artifact_sha256(p2)


def test_shadow_bridge_carryover_adapter():
    from connectome_export import load_subgraph
    from behavior_metrics import compute_behavior_metrics
    from ot_injection import inject_omega_from_spikes
    from shadow_bridge import (
        carryover_from_episode,
        run_brain_omega_bridged_carryover_tick,
        run_brain_omega_bridged_shadow_episode,
    )
    from spike_arms import run_spike_arm

    sg = load_subgraph(seed=1)
    spikes = run_spike_arm(sg, "coupled_active", seed=1)
    behavior = compute_behavior_metrics(spikes)
    omega = inject_omega_from_spikes(spikes, sg.node_ids)
    ep0 = run_brain_omega_bridged_shadow_episode(
        omega, behavior, seed=1, arm_key="coupled_active"
    )
    carryover = carryover_from_episode(ep0)
    ep1 = run_brain_omega_bridged_carryover_tick(
        carryover, behavior, seed=2, arm_key="coupled_active"
    )
    assert ep0["used_carryover"] is False
    assert ep1["used_carryover"] is True
    assert ep1["inject_omega_psi"] is False
    assert ep1["omega_t"] is None


def test_render_markdown_contains_invariants():
    payload = _harness.build_t_brain_04_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    payload["artifact_sha256"] = _harness.artifact_sha256(payload)
    md = _harness.render_t_brain_04_markdown(payload)
    assert "claim_allowed=false" in md
    assert "M-T-BRAIN-04" in md
    assert "F-CARRYOVER-BLEED" in md
