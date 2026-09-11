"""Tests for T-BRAIN-06 integrated EIA modeling harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRAIN_AI = REPO / "research" / "brain_ai"
HARNESS_DIR = BRAIN_AI / "harnesses"
ADAPTERS = BRAIN_AI / "adapters"

for path in (str(HARNESS_DIR), str(ADAPTERS)):
    if path not in sys.path:
        sys.path.insert(0, path)

_HARNESS = HARNESS_DIR / "t_brain_06_eia_integrated.py"
_spec = importlib.util.spec_from_file_location("t_brain_06_eia_integrated_test", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)


def test_build_payload_tier_c_invariants():
    payload = _harness.build_t_brain_06_payload(seed=42, prefer_brian2=False)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["agi_star_claim"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["harness_id"] == "T-BRAIN-06"
    assert payload["x_trigger_zero"] is True
    assert payload["session_ticks"] == 2
    assert len(payload["per_source"]) == 4
    assert payload["substrate_framing"]["not_mammalian_neocortex"] is True


def test_all_sources_valid_omega():
    payload = _harness.build_t_brain_06_payload(
        seed=42, prefer_brian2=False, generated="2026-09-11"
    )
    for key, src in payload["per_source"].items():
        for arm in src["arms"].values():
            omega0 = arm["omega_t_tick0"]
            assert 0.0 <= omega0 <= 1.0, f"{key}/{arm['arm_key']} omega out of range"


def test_endogenous_gt_passive_per_source():
    payload = _harness.build_t_brain_06_payload(
        seed=42, prefer_brian2=False, generated="2026-09-11"
    )
    for key, src in payload["per_source"].items():
        sep = src["separation"]
        assert sep["endogenous_gt_passive_genesis"], f"{key}: genesis separation failed"
        assert sep["endogenous_gt_passive_eoi"], f"{key}: EOI separation failed"
        endo = src["arms"]["coupled_active"]
        passive = src["arms"]["passive_quiescent"]
        assert endo["cumulative_genesis_delta"] > passive["cumulative_genesis_delta"]


def test_omega_span_measurable():
    payload = _harness.build_t_brain_06_payload(
        seed=42, prefer_brian2=False, generated="2026-09-11"
    )
    assert payload["aggregate_metrics"]["omega_span"] >= _harness.OMEGA_SPAN_MIN


def test_two_tick_carryover_per_arm():
    payload = _harness.build_t_brain_06_payload(
        seed=42, prefer_brian2=False, generated="2026-09-11"
    )
    for src in payload["per_source"].values():
        for arm in src["arms"].values():
            assert len(arm["ticks"]) == 2
            carryover = [t for t in arm["ticks"] if t["used_carryover"]]
            assert len(carryover) == 1
            assert carryover[0]["inject_omega_psi"] is False


def test_passive_zero_initiatives():
    payload = _harness.build_t_brain_06_payload(
        seed=42, prefer_brian2=False, generated="2026-09-11"
    )
    for src in payload["per_source"].values():
        passive = src["arms"]["passive_quiescent"]
        for t in passive["ticks"]:
            assert t["n_initiatives"] == 0
            assert t["has_novel_g_prime"] is False


def test_diagnostic_pass():
    payload = _harness.build_t_brain_06_payload(
        seed=42, prefer_brian2=False, generated="2026-09-11"
    )
    assert payload["diagnostic_pass"] is True


def test_claim_invariants_block():
    payload = _harness.build_t_brain_06_payload(
        seed=42, prefer_brian2=False, generated="2026-09-11"
    )
    inv = payload["claim_invariants"]
    assert inv["claim_allowed"] is False
    assert inv["e_endo_support"] == "none"
    assert inv["agi_star_claim"] is False


def test_artifact_sha256_stable():
    p1 = _harness.build_t_brain_06_payload(
        seed=42, prefer_brian2=False, generated="2026-09-11"
    )
    p2 = _harness.build_t_brain_06_payload(
        seed=42, prefer_brian2=False, generated="2026-09-11"
    )
    assert _harness.artifact_sha256(p1) == _harness.artifact_sha256(p2)


def test_render_markdown_contains_invariants():
    payload = _harness.build_t_brain_06_payload(
        seed=42, prefer_brian2=False, generated="2026-09-11"
    )
    payload["artifact_sha256"] = _harness.artifact_sha256(payload)
    md = _harness.render_t_brain_06_markdown(payload)
    assert "claim_allowed=false" in md
    assert "M-T-BRAIN-06" in md
    assert "not mammalian neocortex" in md
