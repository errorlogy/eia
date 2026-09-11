"""Tests for M-O shadow bridge (Neuraxon → OmegaWaveState → shadow ATT-R)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCI_FLOW = REPO / "research" / "sci_flow"

if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

_HARNESS = SCI_FLOW / "mo_shadow_bridge_harness.py"
_spec = importlib.util.spec_from_file_location("mo_shadow_bridge_harness_test", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)


def _sample_arms_payload() -> dict:
    return {
        "artifact_id": "M-MO_do_o_arms_2026-09-02",
        "seed": 42,
        "steps": 50,
        "crosswalk_feasible": True,
        "arms": {
            "neuraxon_baseline": {
                "arm": "neuraxon_baseline",
                "status": "ok",
                "vendor": "neuraxon",
                "kuramoto_r_final": 0.604,
                "omega_t": {"final": 0.293},
                "omega_wave_state": {
                    "phase_coherence": 0.55,
                    "cadence": 0.12,
                    "synchrony": 0.48,
                    "productive_tension": 0.31,
                    "handoff": 0.22,
                    "drift": 0.18,
                    "closure_velocity": 0.27,
                    "n_bands": 4,
                },
                "crosswalk": {"neuraxon_bands_to_omega_wave_state": True},
            },
            "do_o_neuraxon_plasticity_off": {
                "arm": "do_o_neuraxon_plasticity_off",
                "status": "ok",
                "vendor": "neuraxon",
                "kuramoto_r_final": 0.590,
                "omega_t": {"final": 0.280},
                "omega_wave_state": {
                    "phase_coherence": 0.52,
                    "cadence": 0.11,
                    "synchrony": 0.45,
                    "productive_tension": 0.29,
                    "handoff": 0.20,
                    "drift": 0.19,
                    "closure_velocity": 0.25,
                    "n_bands": 4,
                },
                "crosswalk": {"neuraxon_bands_to_omega_wave_state": True},
            },
            "native_oscillatory_state": {
                "arm": "native_oscillatory_state",
                "status": "ok",
                "vendor": "eia.oscillatory_state",
                "kuramoto_r_final": 0.99,
                "omega_t": {"final": 0.65},
                "omega_wave_state": {
                    "phase_coherence": 0.7,
                    "cadence": 0.2,
                    "synchrony": 0.6,
                    "productive_tension": 0.4,
                    "handoff": 0.3,
                    "drift": 0.05,
                    "closure_velocity": 0.35,
                    "n_bands": 4,
                },
                "crosswalk": {"native_default_carriers": True},
            },
        },
        "paired_comparison": {
            "omega_t_final": {"delta_plasticity_off_vs_baseline": -0.013},
            "kuramoto_r_final": {"delta_plasticity_off_vs_baseline": -0.014},
            "falsifier_hints": {
                "F-OMEGA-DECOR": False,
                "F-KURAMOTO-AS-E": False,
                "F-STRUCT≠E": True,
            },
        },
    }


def test_extract_omega_crosswalk() -> None:
    arm = _sample_arms_payload()["arms"]["neuraxon_baseline"]
    ctx = _harness.extract_omega_crosswalk(arm)
    assert ctx["omega_t"] == 0.293
    assert ctx["omega_wave_state"]["phase_coherence"] == 0.55
    assert ctx["crosswalk"]["neuraxon_bands_to_omega_wave_state"] is True


def test_omega_bridged_shadow_has_o_event_and_g_prime() -> None:
    ctx = _harness.extract_omega_crosswalk(
        _sample_arms_payload()["arms"]["neuraxon_baseline"]
    )
    ep = _harness.run_omega_bridged_shadow_episode(ctx, seed=3)
    kinds = {e["kind"] for e in ep["events"]}
    assert any(e["label"].startswith("omega_bridge") for e in ep["events"])
    assert any(e["kind"] == "G_prime" and e.get("novel") for e in ep["events"])
    assert ep["shadow"] is True
    assert ep["claim_allowed"] is False
    assert ep["omega_t"] == 0.293


def test_build_shadow_bridge_payload_invariants() -> None:
    payload = _harness.build_shadow_bridge_payload(_sample_arms_payload(), seed=5)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["cell"] == "D2×L2"
    assert payload["omega_crosswalk"]["feasible"] is True
    att = payload["att_r_comparison"]
    assert "native_closed_loop" in att
    assert "omega_bridged_baseline" in att
    assert att["kuramoto_is_not_att_r"] is True


def test_att_r_scoring_on_bridged_episode() -> None:
    ctx = _harness.extract_omega_crosswalk(
        _sample_arms_payload()["arms"]["neuraxon_baseline"]
    )
    ep = _harness.run_omega_bridged_shadow_episode(ctx, seed=1)
    score = _harness.score_shadow_log(ep)
    assert "att_r_evidence" in score
    assert score.get("emit_m0") is False


def test_arms_artifact_bridge_integration() -> None:
    arms_path = SCI_FLOW / "M-MO_do_o_arms_2026-09-02.json"
    if not arms_path.is_file():
        return
    payload = json.loads(arms_path.read_text(encoding="utf-8"))
    bridge = _harness.build_shadow_bridge_payload(payload, seed=42)
    assert bridge["e_endo_support"] == "none"
    assert bridge["claim_allowed"] is False
