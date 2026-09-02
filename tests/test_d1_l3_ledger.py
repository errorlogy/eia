"""D1×L3 empirical proof ledger tests (CF-4 + D01 artifacts)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCI_FLOW = REPO / "research" / "sci_flow"

if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from run_d1_l3_ledger import _load_evidence_proofs, build_ledger  # noqa: E402

_ep = _load_evidence_proofs()
build_d1_l3_evidence_from_artifacts = _ep.build_d1_l3_evidence_from_artifacts
evaluate_d1_l3_proof_ledger = _ep.evaluate_d1_l3_proof_ledger
load_d1_l3_ledger_artifacts = _ep.load_d1_l3_ledger_artifacts


class D1L3LedgerTests(unittest.TestCase):
    def test_cf4_and_d01_evidence_batch(self) -> None:
        cf4_payload, d01_payload, sources, d01_do_z_payload = load_d1_l3_ledger_artifacts(
            SCI_FLOW
        )
        evidence = build_d1_l3_evidence_from_artifacts(
            cf4_payload,
            d01_payload,
            cf4_provenance=sources["cf4"],
            d01_provenance=sources["d01"],
            d01_do_z_payload=d01_do_z_payload,
            d01_do_z_provenance=sources.get("d01_do_z"),
        )
        self.assertGreaterEqual(len(evidence), 4)
        self.assertEqual(evidence[0].metric_id, "CF4_E_PARTIAL")
        self.assertEqual(evidence[0].evidence_id, "M-CF4-do_z-epistemic_gap")
        steered = [item for item in evidence if item.evidence_id.startswith("M-D01-eoi_k_steered")]
        self.assertEqual(len(steered), 3)
        self.assertTrue(any(item.trajectory_changed for item in steered))

    def test_ledger_partial_support_claim_disallowed(self) -> None:
        ledger = build_ledger(SCI_FLOW, generated="2026-09-02")
        self.assertEqual(ledger["tick_id"], "M-D1-L3-LEDGER")
        self.assertEqual(ledger["cell"], "D1×L3")
        self.assertEqual(ledger["e_endo_support"], "partial")
        self.assertFalse(ledger["claim_allowed"])
        self.assertFalse(ledger["c_ladder_raise_allowed"])
        self.assertFalse(ledger["agi_star_claim"])
        self.assertIn("M-CF4-do_z-epistemic_gap", ledger["proof"]["accepted_evidence_ids"])
        self.assertTrue(ledger["proof"]["rejected_evidence_ids"])
        do_z_accepted = [
            eid
            for eid in ledger["proof"]["accepted_evidence_ids"]
            if eid.startswith("M-D01-do_z")
        ]
        if SCI_FLOW.joinpath("M-D01_do_z_EOI_2026-09-02.json").is_file():
            self.assertTrue(do_z_accepted)

    def test_ledger_json_roundtrip_fields(self) -> None:
        cf4_payload, d01_payload, sources, d01_do_z_payload = load_d1_l3_ledger_artifacts(
            SCI_FLOW
        )
        evidence = build_d1_l3_evidence_from_artifacts(
            cf4_payload,
            d01_payload,
            cf4_provenance=sources["cf4"],
            d01_provenance=sources["d01"],
            d01_do_z_payload=d01_do_z_payload,
            d01_do_z_provenance=sources.get("d01_do_z"),
        )
        ledger = evaluate_d1_l3_proof_ledger(
            evidence,
            generated="2026-09-02",
            sources=sources,
        )
        parsed = json.loads(json.dumps(ledger))
        self.assertEqual(parsed["proof"]["protocol_version"], "sci-flow-eia-proof-v0.1")
        self.assertEqual(parsed["sources"]["cf4"], "research/sci_flow/cf4_results.json")


if __name__ == "__main__":
    unittest.main()
