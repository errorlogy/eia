"""Tests for OMEGA→ΔG bridge harness (F-OMEGA-DECOR probe)."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCI_FLOW = REPO / "research" / "sci_flow"

if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

_HARNESS = SCI_FLOW / "omega_delta_g_harness.py"
_spec = importlib.util.spec_from_file_location("omega_delta_g_harness_test", _HARNESS)
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
                "intervention_id": "do_o_neuraxon_plasticity_off",
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
                "omega_t": {"final": 0.897},
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
            "omega_t_final": {
                "delta_plasticity_off_vs_baseline": -0.013,
                "delta_native_vs_baseline": 0.604,
            },
            "falsifier_hints": {
                "F-OMEGA-DECOR": False,
                "F-KURAMOTO-AS-E": False,
                "F-STRUCT≠E": True,
            },
        },
    }


def test_phase_scramble_omega_low() -> None:
    osc_mod = _harness._load_oscillatory_module()
    ctx = _harness.build_phase_scramble_omega_ctx(osc_mod)
    assert ctx["omega_t"] < 0.5
    assert ctx["intervention_id"] == "do_o_phase_scramble"


def test_extract_genesis_metrics_detects_g_prime() -> None:
    ep = {
        "motive_ids": ["mot-a", "mot-b"],
        "events": [
            {"kind": "G", "label": "mot-a"},
            {"kind": "G_prime", "label": "mot-b", "novel": True},
            {"kind": "A", "label": "act_probe:allow"},
        ],
    }
    metrics = _harness.extract_genesis_metrics(ep)
    assert metrics["goal_symbol_changed"] is True
    assert metrics["genesis_delta"] == 1.0
    assert metrics["has_novel_g_prime"] is True
    assert metrics["x_trigger_zero"] is True


def test_evaluate_omega_g_correlation_decorrelation() -> None:
    probes = [
        {"omega_t": 0.9, "genesis_delta": 1.0, "initiative_fingerprint": "G:a|G_prime:b"},
        {"omega_t": 0.3, "genesis_delta": 1.0, "initiative_fingerprint": "G:a|G_prime:b"},
    ]
    corr = _harness.evaluate_omega_g_correlation(probes)
    assert corr.omega_span > 0.5
    assert corr.genesis_span == 0.0
    assert corr.fingerprint_parity is True
    assert corr.f_omega_decor_aggregate is True


def test_run_arm_shadow_probe_invariants() -> None:
    ctx = _harness.omega_ctx_for_arm("native_oscillatory", _sample_arms_payload())
    probe = _harness.run_arm_shadow_probe("native_oscillatory", ctx, seed=7)
    assert probe["claim_allowed"] is False
    assert probe["x_trigger_zero"] is True
    assert probe["has_novel_g_prime"] is True
    assert "initiative_fingerprint" in probe


def test_build_omega_delta_g_payload_invariants() -> None:
    payload = _harness.build_omega_delta_g_payload(_sample_arms_payload(), seed=5)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["cell"] == "D2×L2"
    assert payload["x_trigger_zero"] is True
    assert len(payload["arms"]) == 4
    decor = payload["f_omega_decor"]
    assert decor["status"] in ("confirmed", "not_confirmed")
    assert "omega_g_correlation" in payload


def test_artifact_sha256_stable() -> None:
    payload = _harness.build_omega_delta_g_payload(_sample_arms_payload(), seed=1)
    digest = _harness.artifact_sha256(payload)
    assert len(digest) == 64
    payload["artifact_sha256"] = digest
    assert _harness.artifact_sha256(payload) == digest


def test_arms_artifact_bridge_integration() -> None:
    arms_path = SCI_FLOW / "M-MO_do_o_arms_2026-09-02.json"
    if not arms_path.is_file():
        return
    payload = json.loads(arms_path.read_text(encoding="utf-8"))
    bridge = _harness.build_omega_delta_g_payload(payload, seed=42)
    assert bridge["e_endo_support"] == "none"
    assert bridge["claim_allowed"] is False
    corr = bridge["omega_g_correlation"]
    assert corr["omega_span"] > 0.1
