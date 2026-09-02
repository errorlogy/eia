"""Tests for M-O proof adjunct bridge (D2×L3 witness ledger)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCI_FLOW = REPO / "research" / "sci_flow"
SRC = REPO / "research" / "cursor-starter-v0.2" / "src"

if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

_BRIDGE = SCI_FLOW / "mo_proof_bridge_harness.py"
_spec = importlib.util.spec_from_file_location("mo_proof_bridge_harness_test", _BRIDGE)
assert _spec and _spec.loader
_bridge = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _bridge
_spec.loader.exec_module(_bridge)


def _ep():
    return _bridge._load_evidence_proofs()


def _sample_arms_payload() -> dict:
    return {
        "artifact_id": "M-MO_do_o_arms_2026-09-02",
        "seed": 42,
        "steps": 50,
        "do_o_interventions": ["do_o_neuraxon_plasticity_off"],
        "arms": {
            "neuraxon_baseline": {"status": "ok", "vendor": "neuraxon"},
            "do_o_neuraxon_plasticity_off": {"status": "ok", "vendor": "neuraxon"},
        },
        "paired_comparison": {
            "omega_t_final": {
                "neuraxon_baseline": 0.293,
                "plasticity_off": 0.280,
            },
            "kuramoto_r_final": {
                "neuraxon_baseline": 0.604,
                "plasticity_off": 0.590,
            },
            "structural_events": {
                "neuraxon_baseline": 1,
                "plasticity_off": 0,
            },
            "w_fast_drift": {
                "neuraxon_baseline": 0.007,
                "plasticity_off": 0.0,
            },
            "falsifier_hints": {
                "F-OMEGA-DECOR": False,
                "F-STRUCT≠E": True,
                "F-KURAMOTO-AS-E": False,
            },
        },
    }


def test_mo_adjunct_never_raises_e_endo_or_c_ladder() -> None:
    ep = _ep()
    evidence = ep.build_mo_adjunct_evidence_from_arms_payload(
        _sample_arms_payload(),
        provenance="unit-test",
    )
    proof = ep.evaluate_mo_adjunct_proof_version(evidence)

    assert proof.e_endo_support == "none"
    assert proof.c_ladder_raise_allowed is False
    assert proof.agi_star_claim is False
    assert proof.claim_allowed is False
    assert proof.claim_ceiling == "C2"
    assert proof.protocol_version == "sci-flow-mo-adjunct-v0.1"


def test_mo_adjunct_accepts_paired_do_o_delta() -> None:
    ep = _ep()
    evidence = ep.build_mo_adjunct_evidence_from_arms_payload(
        _sample_arms_payload(),
        provenance="unit-test",
    )
    proof = ep.evaluate_mo_adjunct_proof_version(evidence)

    assert proof.witness_support == "partial"
    assert len(proof.accepted_evidence_ids) >= 2
    assert "M-MO-do_o-plasticity_off-structural_events" in proof.accepted_evidence_ids


def test_omega_decor_blocks_witness() -> None:
    ep = _ep()
    payload = _sample_arms_payload()
    payload["paired_comparison"]["omega_t_final"]["plasticity_off"] = 0.293
    payload["paired_comparison"]["falsifier_hints"]["F-OMEGA-DECOR"] = True

    evidence = ep.build_mo_adjunct_evidence_from_arms_payload(payload, provenance="unit-test")
    omega_items = [e for e in evidence if e.metric_id == "OMEGA_T"]
    assert omega_items
    proof = ep.evaluate_mo_adjunct_proof_version(evidence)
    assert "M-MO-do_o-plasticity_off-omega_t" in proof.rejected_evidence_ids
    assert "F-OMEGA-DECOR" in proof.falsifier_ids


def test_kuramoto_high_r_is_annotation_not_e_endo() -> None:
    ep = _ep()
    item = ep.mo_adjunct_item_from_paired_metric(
        evidence_id="kuramoto-high",
        metric_id="KURAMOTO_R",
        baseline_value=0.95,
        intervention_value=0.90,
        intervention_id="do_o_neuraxon_plasticity_off",
        arm="do_o_neuraxon_plasticity_off",
        vendor="neuraxon",
        provenance="unit-test",
        falsifier_hints={"F-KURAMOTO-AS-E": True},
    )
    proof = ep.evaluate_mo_adjunct_proof_version((item,))

    assert proof.e_endo_support == "none"
    assert "F-KURAMOTO-AS-E" in proof.annotation_falsifier_ids
    assert item.evidence_id in proof.accepted_evidence_ids


def test_d1_protocol_still_rejects_omega_tier_c() -> None:
    """M-O adjunct must not bleed into D1 e_endo ledger."""
    ep = _ep()
    item = ep.EvidenceItem(
        evidence_id="omega-bleed-check",
        metric_id="OMEGA_T",
        value=0.99,
        trajectory_changed=True,
        do_z_changes_g_distribution=False,
        x_non_triggering=True,
        matching_external_initiating_signal=False,
        falsifiers_triggered=("F-SYNC",),
        provenance="unit-test",
    )
    proof = ep.evaluate_eia_proof_version((item,))
    assert proof.e_endo_support == "none"
    assert proof.accepted_evidence_ids == ()


def test_build_adjunct_ledger_invariants() -> None:
    ledger = _bridge.build_adjunct_ledger(_sample_arms_payload(), generated="2026-09-02")

    assert ledger["cell"] == "D2×L3"
    assert ledger["evidence_class"] == "mo_tier_c_witness"
    assert ledger["tier"] == "C"
    assert ledger["e_endo_support"] == "none"
    assert ledger["claim_allowed"] is False
    assert ledger["witness_support"] == "partial"
    assert "admissibility" in ledger["sources"]


def test_arms_artifact_bridge_integration() -> None:
    arms_path = SCI_FLOW / "M-MO_do_o_arms_2026-09-02.json"
    if not arms_path.is_file():
        return
    payload = json.loads(arms_path.read_text(encoding="utf-8"))
    ledger = _bridge.build_adjunct_ledger(payload, generated="2026-09-02")
    assert ledger["e_endo_support"] == "none"
    assert ledger["claim_allowed"] is False
