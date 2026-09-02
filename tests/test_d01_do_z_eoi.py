"""D01 do(Z)-mapped EOI harness + D1×L3 ledger admissibility tests."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCI_FLOW = REPO / "research" / "sci_flow"
MAIN_SRC = REPO / "src"

if str(MAIN_SRC) not in sys.path:
    sys.path.insert(0, str(MAIN_SRC))
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from d01_do_z_eoi_harness import (  # noqa: E402
    DEFAULT_DO_Z_IDS,
    run_do_z_eoi_evaluation,
)
from run_d1_l3_ledger import _load_evidence_proofs, build_ledger  # noqa: E402

_ep = _load_evidence_proofs()
build_d1_l3_evidence_from_artifacts = _ep.build_d1_l3_evidence_from_artifacts
evaluate_eia_proof_version = _ep.evaluate_eia_proof_version
evidence_item_from_d01_do_z_row = _ep.evidence_item_from_d01_do_z_row
load_d1_l3_ledger_artifacts = _ep.load_d1_l3_ledger_artifacts


class D01DoZEoiTests(unittest.TestCase):
    def test_do_z_rows_flag_internal_intervention(self) -> None:
        result = run_do_z_eoi_evaluation(REPO, scenario_ids=("eoi_k_steered",))
        self.assertFalse(result.claim_allowed)
        self.assertTrue(all(r.do_z_changes_g_distribution for r in result.rows))
        self.assertEqual(len(result.rows), len(DEFAULT_DO_Z_IDS))

    def test_steered_prospective_flips_trajectory(self) -> None:
        result = run_do_z_eoi_evaluation(REPO, scenario_ids=("eoi_k_steered",))
        row = next(
            r for r in result.rows if r.intervention_id == "do_z_zero_prospective"
        )
        self.assertTrue(row.trajectory_changed)
        self.assertEqual(row.original_target, "belief-commit-atlas")
        self.assertEqual(row.twin_target, "belief-deadline")

    def test_do_z_evidence_item_admissible_when_trajectory_changed(self) -> None:
        row = {
            "scenario_id": "eoi_k_steered",
            "intervention_id": "do_z_zero_prospective",
            "eoi": 0.5,
            "original_target": "belief-commit-atlas",
            "twin_target": "belief-deadline",
            "trajectory_changed": True,
            "x_non_triggering": True,
            "matching_external_initiating_signal": False,
        }
        item = evidence_item_from_d01_do_z_row(row, provenance="unit-test")
        proof = evaluate_eia_proof_version((item,))
        self.assertIn(item.evidence_id, proof.accepted_evidence_ids)
        self.assertTrue(item.do_z_changes_g_distribution)

    def test_ledger_includes_do_z_when_artifact_present(self) -> None:
        artifact = SCI_FLOW / "M-D01_do_z_EOI_2026-09-02.json"
        if not artifact.is_file():
            self.skipTest("run run_d01_do_z_eoi.py first")
        cf4_payload, d01_payload, sources, d01_do_z_payload = load_d1_l3_ledger_artifacts(
            SCI_FLOW
        )
        self.assertIsNotNone(d01_do_z_payload)
        evidence = build_d1_l3_evidence_from_artifacts(
            cf4_payload,
            d01_payload,
            cf4_provenance=sources["cf4"],
            d01_provenance=sources["d01"],
            d01_do_z_payload=d01_do_z_payload,
            d01_do_z_provenance=sources.get("d01_do_z"),
        )
        do_z_items = [e for e in evidence if e.evidence_id.startswith("M-D01-do_z")]
        self.assertGreaterEqual(len(do_z_items), 1)

    def test_ledger_json_has_do_z_acceptance(self) -> None:
        artifact = SCI_FLOW / "M-D01_do_z_EOI_2026-09-02.json"
        if not artifact.is_file():
            self.skipTest("run run_d01_do_z_eoi.py first")
        ledger = build_ledger(SCI_FLOW, generated="2026-09-02")
        accepted = ledger["proof"]["accepted_evidence_ids"]
        self.assertIn("M-CF4-do_z-epistemic_gap", accepted)
        do_z_accepted = [eid for eid in accepted if eid.startswith("M-D01-do_z")]
        self.assertTrue(do_z_accepted)
        self.assertFalse(ledger["claim_allowed"])
        parsed = json.loads(json.dumps(ledger))
        self.assertEqual(parsed["e_endo_support"], "partial")


if __name__ == "__main__":
    unittest.main()
