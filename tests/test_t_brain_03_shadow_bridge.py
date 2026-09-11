"""Tests for T-BRAIN-03 shadow bridge harness."""

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

_HARNESS = HARNESS_DIR / "t_brain_03_shadow_bridge.py"
_spec = importlib.util.spec_from_file_location("t_brain_03_shadow_bridge_test", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)


def test_build_payload_tier_c_invariants():
    payload = _harness.build_t_brain_03_payload(seed=42, prefer_brian2=False)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["agi_star_claim"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["harness_id"] == "T-BRAIN-03"
    assert payload["x_trigger_zero"] is True
    assert len(payload["arms"]) == 3


def test_active_vs_passive_genesis_difference():
    payload = _harness.build_t_brain_03_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    arms = payload["arms"]
    active = arms["coupled_active"]
    passive = arms["passive_quiescent"]
    assert active["genesis_delta"] != passive["genesis_delta"]
    assert active["has_novel_g_prime"] is True
    assert passive["has_novel_g_prime"] is False


def test_phase_scramble_f_omega_decor():
    payload = _harness.build_t_brain_03_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    arms = payload["arms"]
    coupled = arms["coupled_active"]
    scramble = arms["phase_scramble_control"]
    assert coupled["behavior"]["n_spikes"] == scramble["behavior"]["n_spikes"]
    assert abs(coupled["omega_t"] - scramble["omega_t"]) > 0.01
    assert scramble["genesis_delta"] == coupled["genesis_delta"]
    assert payload["f_omega_decor"]["status"] == "confirmed"


def test_diagnostic_pass():
    payload = _harness.build_t_brain_03_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    assert payload["diagnostic_pass"] is True


def test_att_r_comparison_present():
    payload = _harness.build_t_brain_03_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    att = payload["att_r_comparison"]
    assert "native_closed_loop" in att
    assert "omega_bridged_coupled_active" in att


def test_artifact_sha256_stable():
    p1 = _harness.build_t_brain_03_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    p2 = _harness.build_t_brain_03_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    assert _harness.artifact_sha256(p1) == _harness.artifact_sha256(p2)


def test_shadow_bridge_adapter():
    from connectome_export import load_subgraph
    from behavior_metrics import compute_behavior_metrics
    from ot_injection import inject_omega_from_spikes
    from shadow_bridge import (
        behavior_allows_novel_genesis,
        run_brain_omega_bridged_shadow_episode,
    )
    from spike_arms import run_spike_arm

    sg = load_subgraph(seed=1)
    spikes = run_spike_arm(sg, "passive_quiescent", seed=1)
    behavior = compute_behavior_metrics(spikes)
    assert behavior_allows_novel_genesis(behavior) is False
    omega = inject_omega_from_spikes(spikes, sg.node_ids)
    ep = run_brain_omega_bridged_shadow_episode(
        omega, behavior, seed=1, arm_key="passive_quiescent"
    )
    assert ep["behavior_gated_novel_genesis"] is False
    assert not any(e.get("kind") == "G_prime" and e.get("novel") for e in ep["events"])


def test_render_markdown_contains_invariants():
    payload = _harness.build_t_brain_03_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    payload["artifact_sha256"] = _harness.artifact_sha256(payload)
    md = _harness.render_t_brain_03_markdown(payload)
    assert "claim_allowed=false" in md
    assert "M-T-BRAIN-03" in md
