"""Tests for T-BRAIN-02 OMEGA vs behavior correlation harness."""

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

_HARNESS = HARNESS_DIR / "t_brain_02_omega_behavior.py"
_spec = importlib.util.spec_from_file_location("t_brain_02_omega_behavior_test", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)


def test_build_payload_tier_c_invariants():
    payload = _harness.build_t_brain_02_payload(seed=42, prefer_brian2=False)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["agi_star_claim"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["harness_id"] == "T-BRAIN-02"
    assert len(payload["arms"]) == 5


def test_arms_span_behavioral_variance():
    payload = _harness.build_t_brain_02_payload(seed=42, prefer_brian2=False, generated="2026-09-10")
    corr = payload["omega_behavior_correlation"]
    assert corr["behavioral_variance_ok"] is True
    assert corr["behavior_span"] >= _harness.BEHAVIOR_SPAN_MIN


def test_correlation_metrics_present():
    payload = _harness.build_t_brain_02_payload(seed=42, prefer_brian2=False, generated="2026-09-10")
    corr = payload["omega_behavior_correlation"]
    assert corr["r_omega_activity"] is not None
    assert -1.0 <= corr["r_omega_activity"] <= 1.0


def test_phase_scramble_decor_falsifier():
    payload = _harness.build_t_brain_02_payload(seed=42, prefer_brian2=False, generated="2026-09-10")
    arms = payload["arms"]
    coupled = arms["coupled_active"]
    scramble = arms["phase_scramble_control"]
    assert coupled["behavior"]["n_spikes"] == scramble["behavior"]["n_spikes"]
    assert abs(coupled["omega_t"] - scramble["omega_t"]) > 0.01
    assert payload["f_omega_decor"]["status"] == "confirmed"


def test_diagnostic_pass():
    payload = _harness.build_t_brain_02_payload(seed=42, prefer_brian2=False, generated="2026-09-10")
    assert payload["diagnostic_pass"] is True


def test_artifact_sha256_stable():
    p1 = _harness.build_t_brain_02_payload(seed=42, prefer_brian2=False, generated="2026-09-10")
    p2 = _harness.build_t_brain_02_payload(seed=42, prefer_brian2=False, generated="2026-09-10")
    assert _harness.artifact_sha256(p1) == _harness.artifact_sha256(p2)


def test_behavior_metrics_module():
    from behavior_metrics import compute_behavior_metrics, pearson_r
    from connectome_export import load_subgraph
    from spike_arms import run_spike_arm

    sg = load_subgraph(seed=1)
    spikes = run_spike_arm(sg, "coupled_active", seed=1)
    metrics = compute_behavior_metrics(spikes)
    assert "activity_rate_per_node_ms" in metrics
    assert pearson_r([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]) == pytest.approx(1.0)


def test_render_markdown_contains_invariants():
    payload = _harness.build_t_brain_02_payload(seed=42, prefer_brian2=False, generated="2026-09-10")
    payload["artifact_sha256"] = _harness.artifact_sha256(payload)
    md = _harness.render_t_brain_02_markdown(payload)
    assert "claim_allowed=false" in md
    assert "M-T-BRAIN-02" in md
