"""Tests for versioned EIA sci-flow proof protocol."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(_SRC))

_MOD = _SRC / "eia" / "evidence_proofs.py"
_spec = importlib.util.spec_from_file_location("eia_evidence_proofs_research", _MOD)
assert _spec and _spec.loader
_ep = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _ep
_spec.loader.exec_module(_ep)


def test_cf4_partial_proof_is_c2_scoped_not_agi_star() -> None:
    item = _ep.EvidenceItem(
        evidence_id="M-CF4-smoke",
        metric_id="CF4_E_PARTIAL",
        value=0.95,
        trajectory_changed=True,
        do_z_changes_g_distribution=True,
        x_non_triggering=True,
        matching_external_initiating_signal=False,
        falsifiers_triggered=(),
        provenance="unit-test",
    )

    proof = _ep.evaluate_eia_proof_version((item,))

    assert proof.protocol_version == "sci-flow-eia-proof-v0.1"
    assert proof.e_endo_support == "partial"
    assert proof.claim_ceiling == "C2"
    assert proof.c_ladder_raise_allowed is False
    assert proof.agi_star_claim is False
    assert proof.accepted_evidence_ids == ("M-CF4-smoke",)


def test_declaration_only_is_rejected_even_with_high_value() -> None:
    item = _ep.EvidenceItem(
        evidence_id="chat-agency-claim",
        metric_id="NM_DECL",
        value=1.0,
        trajectory_changed=False,
        do_z_changes_g_distribution=False,
        x_non_triggering=True,
        matching_external_initiating_signal=False,
        falsifiers_triggered=("F-DECL",),
        provenance="unit-test",
    )

    proof = _ep.evaluate_eia_proof_version((item,))

    assert proof.e_endo_support == "none"
    assert proof.accepted_evidence_ids == ()
    assert "F-DECL" in proof.falsifier_ids
    assert proof.agi_star_claim is False


def test_omega_sync_only_never_counts_as_tier_a_proof() -> None:
    item = _ep.EvidenceItem(
        evidence_id="omega-high-sync",
        metric_id="OMEGA_T",
        value=0.99,
        trajectory_changed=True,
        do_z_changes_g_distribution=False,
        x_non_triggering=True,
        matching_external_initiating_signal=False,
        falsifiers_triggered=("F-SYNC",),
        provenance="unit-test",
    )

    proof = _ep.evaluate_eia_proof_version((item,))

    assert proof.e_endo_support == "none"
    assert proof.accepted_evidence_ids == ()
    assert proof.claim_ceiling == "C2"
    assert proof.c_ladder_raise_allowed is False


def test_external_initiator_blocks_candidate_evidence() -> None:
    item = _ep.EvidenceItem(
        evidence_id="externally-entrained",
        metric_id="E_ENDO",
        value=0.9,
        trajectory_changed=True,
        do_z_changes_g_distribution=True,
        x_non_triggering=True,
        matching_external_initiating_signal=True,
        falsifiers_triggered=(),
        provenance="unit-test",
    )

    proof = _ep.evaluate_eia_proof_version((item,))

    assert proof.e_endo_support == "none"
    assert "F-EXT" in proof.falsifier_ids
    assert proof.accepted_evidence_ids == ()


def test_proof_report_is_stable_markdown() -> None:
    item = _ep.EvidenceItem(
        evidence_id="M-CF4-smoke",
        metric_id="CF4_E_PARTIAL",
        value=0.95,
        trajectory_changed=True,
        do_z_changes_g_distribution=True,
        x_non_triggering=True,
        matching_external_initiating_signal=False,
        falsifiers_triggered=(),
        provenance="unit-test",
    )
    report = _ep.render_proof_report(_ep.evaluate_eia_proof_version((item,)))

    assert "sci-flow-eia-proof-v0.1" in report
    assert "AGI*: false" in report
    assert "C-ladder raise allowed: false" in report
    assert "M-CF4-smoke" in report
