"""Tests for T-AGENT-03 Brain-AI + agent bridge harness (offline / CI-safe)."""

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

_HARNESS = HARNESS_DIR / "t_agent_03_brain_agent_bridge.py"
_spec = importlib.util.spec_from_file_location("t_agent_03_brain_agent_bridge_test", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)


def test_build_payload_tier_c_invariants():
    payload = _harness.build_t_agent_03_payload(seed=42, generated="2026-09-11")
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["agi_star_claim"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["harness_id"] == "T-AGENT-03"
    assert set(payload["arms"]) == {
        "brain_eia_endogenous",
        "brain_eia_no_psi",
        "brain_reactive",
        "agent_only_eia",
    }


def test_brain_eia_gt_brain_reactive():
    payload = _harness.build_t_agent_03_payload(seed=42, generated="2026-09-11")
    brain = payload["arms"]["brain_eia_endogenous"]
    reactive = payload["arms"]["brain_reactive"]
    assert brain["initiative_count"] > reactive["initiative_count"]
    assert brain["eoi_mean"] > reactive["eoi_mean"]
    assert reactive["initiative_count"] == 0
    assert reactive["abstain_rate"] == 1.0


def test_agent_only_matches_t_agent_01_magnitude():
    payload = _harness.build_t_agent_03_payload(seed=42, generated="2026-09-11")
    agent = payload["arms"]["agent_only_eia"]
    assert agent["initiative_count"] == 6
    assert agent["eoi_mean"] >= 0.75
    assert agent["euir_proxy_rate"] == 1.0


def test_psi_arm_differs_from_no_psi_or_decor_fires():
    payload = _harness.build_t_agent_03_payload(seed=42, generated="2026-09-11")
    diag = payload["diagnostics"]
    with_psi = payload["arms"]["brain_eia_endogenous"]
    no_psi = payload["arms"]["brain_eia_no_psi"]
    if diag["f_omega_decor"]:
        assert with_psi["initiative_count"] == no_psi["initiative_count"]
    else:
        assert diag["psi_changes_behavior"] is True


def test_per_source_bridge_section():
    payload = _harness.build_t_agent_03_payload(seed=42, generated="2026-09-11")
    per_source = payload["per_source"]
    assert "bundled_tiny" in per_source
    assert "google_male_cns" in per_source
    for src in ("bundled_tiny", "google_male_cns"):
        row = per_source[src]
        assert "bridge_delta" in row
        assert row["brain_eia_endogenous"]["omega_t"] is not None


def test_diagnostic_pass():
    payload = _harness.build_t_agent_03_payload(seed=42, generated="2026-09-11")
    assert payload["diagnostic_pass"] is True
    assert payload["bridge_parity"] is True
    assert payload["diagnostics"]["f_brain_agent_collapse"] is False


def test_brain_agent_bridge_adapter():
    from brain_agent_bridge import (
        build_connectome_omega_context,
        resolve_arm_config,
    )

    cfg = resolve_arm_config("brain_eia_endogenous")
    assert cfg["connectome_arm"] == "coupled_active"
    assert cfg["inject_omega_psi"] is True

    ctx = build_connectome_omega_context(
        "bundled_tiny", "coupled_active", seed=42, n_nodes=8
    )
    assert ctx["omega_ctx"]["omega_t"] > 0
    assert ctx["behavior"]["activity_rate_per_node_ms"] > 0


def test_artifact_sha256_stable():
    p1 = _harness.build_t_agent_03_payload(seed=42, generated="2026-09-11")
    p2 = _harness.build_t_agent_03_payload(seed=42, generated="2026-09-11")
    p1["artifact_sha256"] = _harness.artifact_sha256(p1)
    p2["artifact_sha256"] = _harness.artifact_sha256(p2)
    assert p1["artifact_sha256"] == p2["artifact_sha256"]
